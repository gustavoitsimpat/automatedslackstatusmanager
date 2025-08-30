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
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurar codificación para Windows
if platform.system().lower() == "windows":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def get_local_ip():
    """Obtiene la IP local."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "192.168.1.1"

def ping(ip):
    """Hace ping a una IP con múltiples intentos."""
    for attempt in range(1):  # Solo 1 intento para mayor velocidad
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], 
                                      capture_output=True, text=True, timeout=3)
            else:
                result = subprocess.run(["ping", "-c", "1", "-W", "2", ip], 
                                      capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                return True
                
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    
    return False

def get_device_info(ip):
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
        except:
            pass
        
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
            except:
                pass
        
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
        except:
            pass
            
    except Exception as e:
        device_info["error"] = str(e)
    
    return device_info

def check_arp(ip):
    """Verifica si una IP está en la tabla ARP."""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(["arp", "-a", ip], 
                                  capture_output=True, text=True, timeout=2)
            return ip in result.stdout
        else:
            result = subprocess.run(["arp", "-n", ip], 
                                  capture_output=True, text=True, timeout=2)
            return ip in result.stdout
    except:
        return False

def scan_ip(args):
    """Escanea una IP específica."""
    network, i = args
    ip = f"{network}.{i}"
    
    # Intentar ping primero
    if ping(ip):
        return get_device_info(ip)
    
    # Si ping falla, verificar ARP como respaldo
    if check_arp(ip):
        return get_device_info(ip)
    
    return None



def save_results_to_json(devices, network, filename=None):
    """Guarda los resultados en formato JSON (solo IP y Hostname)."""
    if not filename:
        filename = "Simpat_Network.json"
    
    # Eliminar archivo JSON anterior si existe
    import os
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception:
            pass
    
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
    except Exception:
        pass

def main():
    # Obtener IP local
    local_ip = get_local_ip()
    
    # Obtener red base
    network = ".".join(local_ip.split(".")[:3])
    
    # Escanear con múltiples hilos para mayor velocidad
    active_devices = []
    
    # Usar ThreadPoolExecutor para escaneo paralelo
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Crear lista de tareas
        futures = []
        for i in range(1, 255):
            futures.append(executor.submit(scan_ip, (network, i)))
        
        # Procesar resultados
        for future in as_completed(futures):
            result = future.result()
            if result:
                active_devices.append(result)
    
    if active_devices:
        # Ordenar por IP para mejor visualización
        active_devices.sort(key=lambda x: [int(i) for i in x['ip'].split('.')])
        
        # Guardar resultados en archivo JSON
        save_results_to_json(active_devices, network)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, Exception):
        pass
