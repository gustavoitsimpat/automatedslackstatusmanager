#!/usr/bin/env python3
"""
Escáner de ping ultra rápido y simple.
Detecta IPs activas en toda la red (1-254) y guarda información detallada.
"""

import subprocess
import socket
import platform
import threading
import time
import json
import sys
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

# Configurar logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quick_ping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configurar codificación para Windows
if platform.system().lower() == "windows":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def get_adaptive_timeout() -> int:
    """
    Calcula timeout adaptativo basado en latencia de red.
    
    Returns:
        Timeout en segundos (mínimo 1, máximo 5)
    """
    try:
        # Medir latencia básica con ping a gateway
        start_time = time.time()
        subprocess.run(["ping", "-n", "1", "8.8.8.8"], 
                      capture_output=True, timeout=3)
        latency = time.time() - start_time
        
        # Calcular timeout basado en latencia
        base_timeout = max(1, int(latency * 2))
        return min(base_timeout, 5)  # Máximo 5 segundos
        
    except Exception as e:
        logger.warning(f"No se pudo medir latencia de red: {e}")
        return 3  # Timeout por defecto

def retry_with_backoff(func, max_retries: int = 2, base_delay: float = 0.5):
    """
    Ejecuta una función con retry y backoff exponencial.
    
    Args:
        func: Función a ejecutar
        max_retries: Número máximo de reintentos
        base_delay: Delay base en segundos
    
    Returns:
        Resultado de la función o None si falla después de todos los reintentos
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                return None
            
            delay = base_delay * (2 ** attempt)  # 0.5, 1, 2 segundos
            time.sleep(delay)
    
    return None

def get_local_ip():
    """Obtiene la IP local."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        logger.warning(f"No se pudo obtener IP local: {e}")
        return "192.168.1.1"

def ping(ip: str) -> bool:
    """Hace ping a una IP con timeout adaptativo y retry."""
    timeout = get_adaptive_timeout()
    
    def _ping_attempt():
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["ping", "-n", "1", "-w", str(timeout * 1000), ip], 
                                      capture_output=True, text=True, timeout=timeout + 1)
            else:
                result = subprocess.run(["ping", "-c", "1", "-W", str(timeout), ip], 
                                      capture_output=True, text=True, timeout=timeout + 1)
            
            return result.returncode == 0
                
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    return retry_with_backoff(_ping_attempt, max_retries=1, base_delay=0.2) or False

def get_device_info(ip: str) -> Dict:
    """Obtiene información detallada del dispositivo."""
    device_info = {
        "ip": ip,
        "hostname": "Desconocido",
        "name": "Desconocido",
        "status": "Activo",
        "ping_response": "Sí",
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        # Intentar obtener hostname
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            device_info["hostname"] = hostname
            device_info["name"] = hostname
        except Exception as e:
            logger.debug(f"No se pudo obtener hostname para {ip}: {e}")
        
        # Intentar obtener información adicional con nslookup (Windows)
        if platform.system().lower() == "windows":
            try:
                result = subprocess.run(["nslookup", ip], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "Name:" in line and "Desconocido" in device_info["name"]:
                            name = line.split("Name:")[1].strip()
                            if name and name != ip:
                                device_info["name"] = name
            except Exception as e:
                logger.debug(f"Error en nslookup para {ip}: {e}")
        
        # Intentar obtener información con ping para obtener TTL
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["ping", "-n", "1", ip], 
                                      capture_output=True, text=True, timeout=3)
            else:
                result = subprocess.run(["ping", "-c", "1", ip], 
                                      capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                output = result.stdout
                # Extraer TTL si está disponible
                if "TTL=" in output:
                    ttl_line = [line for line in output.split('\n') if "TTL=" in line]
                    if ttl_line:
                        device_info["ttl"] = ttl_line[0].split("TTL=")[1].split()[0]
                
                # Extraer tiempo de respuesta
                if "tiempo=" in output or "time=" in output:
                    time_line = [line for line in output.split('\n') if "tiempo=" in line or "time=" in line]
                    if time_line:
                        time_part = time_line[0].split("tiempo=")[1] if "tiempo=" in time_line[0] else time_line[0].split("time=")[1]
                        device_info["response_time"] = time_part.split()[0]
        except Exception as e:
            logger.debug(f"Error obteniendo TTL para {ip}: {e}")
            
    except Exception as e:
        device_info["error"] = str(e)
        logger.error(f"Error procesando información de {ip}: {e}")
    
    return device_info

def check_arp(ip: str) -> bool:
    """Verifica si una IP está en la tabla ARP."""
    def _arp_check():
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["arp", "-a", ip], 
                                      capture_output=True, text=True, timeout=2)
                return ip in result.stdout
            else:
                result = subprocess.run(["arp", "-n", ip], 
                                      capture_output=True, text=True, timeout=2)
                return ip in result.stdout
        except Exception:
            return False
    
    return retry_with_backoff(_arp_check, max_retries=1, base_delay=0.1) or False

def scan_ip(args: Tuple[str, int]) -> Optional[Dict]:
    """Escanea una IP específica."""
    network, i = args
    ip = f"{network}.{i}"
    
    # Intentar ping primero
    if ping(ip):
        logger.debug(f"Dispositivo encontrado: {ip}")
        return get_device_info(ip)
    
    # Si ping falla, verificar ARP como respaldo
    if check_arp(ip):
        logger.debug(f"Dispositivo encontrado via ARP: {ip}")
        return get_device_info(ip)
    
    return None

def save_results_to_json(devices: List[Dict], network: str, filename: str = None):
    """Guarda los resultados en formato JSON (solo IP y Hostname)."""
    if not filename:
        filename = "Simpat_Network.json"
    
    # Eliminar archivo JSON anterior si existe
    import os
    if os.path.exists(filename):
        try:
            os.remove(filename)
            logger.info(f"Archivo anterior {filename} eliminado")
        except Exception as e:
            logger.error(f"Error eliminando archivo anterior {filename}: {e}")
    
    # Crear lista simplificada con solo IP y Hostname
    simplified_devices = []
    for device in devices:
        simplified_devices.append({
            "ip": device["ip"],
            "hostname": device["hostname"]
        })
    
    scan_data = {
        "scan_info": {
            "date": datetime.now().isoformat(),
            "network": f"{network}.0/24",
            "range_scanned": f"{network}.1 - {network}.254",
            "total_devices": len(devices),
            "scan_duration": "Calculado al final"
        },
        "devices": simplified_devices
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(scan_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Resultados guardados en {filename}: {len(devices)} dispositivos")
    except Exception as e:
        logger.error(f"Error guardando resultados en {filename}: {e}")

def main():
    start_time = time.time()
    logger.info("Iniciando escaneo de red")
    
    # Obtener IP local
    local_ip = get_local_ip()
    logger.info(f"IP local detectada: {local_ip}")
    
    # Obtener red base
    network = ".".join(local_ip.split(".")[:3])
    logger.info(f"Escaneando red: {network}.0/24")
    
    # Escanear con múltiples hilos para mayor velocidad
    active_devices = []
    
    # Usar ThreadPoolExecutor para escaneo paralelo
    max_workers = min(20, os.cpu_count() * 2)  # Workers dinámicos
    logger.info(f"Usando {max_workers} workers para escaneo paralelo")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Crear lista de tareas
        futures = []
        for i in range(1, 255):
            futures.append(executor.submit(scan_ip, (network, i)))
        
        # Procesar resultados
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            if result:
                active_devices.append(result)
            completed += 1
            
            # Log progreso cada 50 IPs
            if completed % 50 == 0:
                logger.info(f"Progreso: {completed}/254 IPs escaneadas, {len(active_devices)} dispositivos encontrados")
    
    scan_duration = time.time() - start_time
    
    if active_devices:
        # Ordenar por IP para mejor visualización
        active_devices.sort(key=lambda x: [int(i) for i in x['ip'].split('.')])
        
        # Guardar resultados en archivo JSON
        save_results_to_json(active_devices, network)
        
        logger.info(f"Escaneo completado en {scan_duration:.2f} segundos")
        logger.info(f"Total de dispositivos encontrados: {len(active_devices)}")
    else:
        logger.warning("No se encontraron dispositivos activos en la red")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Escaneo interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error crítico durante el escaneo: {e}")
        sys.exit(1)
