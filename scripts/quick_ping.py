#!/usr/bin/env python3
"""
Escáner de ping optimizado para usuarios configurados en Config.json.
"""

import subprocess
import platform
import time
import json
import sys
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quick_ping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_config() -> List[Dict]:
    """Carga la configuración de usuarios desde Config.json."""
    try:
        with open('config/Config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('users', [])
    except Exception as e:
        logger.error(f"Error al cargar config/Config.json: {e}")
        return []

def ping(ip: str) -> bool:
    """Hace ping a una IP."""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], 
                                  capture_output=True, text=True, timeout=2)
        else:
            result = subprocess.run(["ping", "-c", "1", "-W", "1", ip], 
                                  capture_output=True, text=True, timeout=2)
        
        return result.returncode == 0
    except Exception:
        return False

def scan_user(user_config: Dict) -> Optional[Dict]:
    """Escanea un usuario específico."""
    ip = user_config['ip']
    hostname = user_config['hostname']
    user_id = user_config['userID']
    
    is_active = ping(ip)
    status = "Activo" if is_active else "Inactivo"
    
    logger.info(f"Usuario {status.lower()}: {hostname} ({ip})")
    
    return {
        "ip": ip,
        "hostname": hostname,
        "userID": user_id,
        "status": status
    }

def save_results_to_json(devices: List[Dict], filename: str = "config/current_status.json"):
    """Guarda los resultados en formato JSON."""
    # Separar usuarios activos e inactivos
    active_user_ids = []
    inactive_user_ids = []
    
    for device in devices:
        user_id = device.get("userID", "")
        if user_id:
            if device["status"] == "Activo":
                active_user_ids.append(user_id)
            else:
                inactive_user_ids.append(user_id)
    
    status_data = {
        "user_ids": active_user_ids,
        "old_user_ids": inactive_user_ids
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Estado guardado: {len(active_user_ids)} activos, {len(inactive_user_ids)} inactivos")
    except Exception as e:
        logger.error(f"Error guardando estado: {e}")

def main():
    start_time = time.time()
    logger.info("Iniciando escaneo de usuarios configurados")
    
    # Cargar configuración
    users_config = load_config()
    if not users_config:
        logger.error("No se pudo cargar la configuración de usuarios")
        return
    
    logger.info(f"Usuarios a escanear: {len(users_config)}")
    
    # Escanear usuarios en paralelo
    all_users = []
    max_workers = min(10, len(users_config))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scan_user, user_config) for user_config in users_config]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_users.append(result)
    
    # Guardar resultados
    if all_users:
        save_results_to_json(all_users)
        
        # Mostrar resumen
        active_count = len([u for u in all_users if u["status"] == "Activo"])
        scan_duration = time.time() - start_time
        
        logger.info(f"Escaneo completado en {scan_duration:.2f}s")
        logger.info(f"Total: {len(all_users)}, Activos: {active_count}, Inactivos: {len(all_users) - active_count}")
    else:
        logger.warning("No se encontraron usuarios en la configuración")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Escaneo interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        sys.exit(1)
