#!/usr/bin/env python3
"""
Gestor Automático de Status de Slack.
Ejecuta el escaneo de red y compara automáticamente con la configuración.
"""

import subprocess
import json
import time
import sys
import os
from datetime import datetime

def run_network_scan():
    """Ejecuta el escaneo de red usando quick_ping.py."""
    try:
        # Ejecutar quick_ping.py directamente (sin capturar salida)
        result = subprocess.run([sys.executable, "quick_ping.py"], 
                              timeout=120, capture_output=True)
        
        return result.returncode == 0
            
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False

def run_slack_status_update():
    """Ejecuta la actualización de status de Slack usando slack_status_manager.py."""
    try:
        # Ejecutar slack_status_manager.py directamente (sin capturar salida)
        result = subprocess.run([sys.executable, "slack_status_manager.py"], 
                              timeout=60, capture_output=True)
        
        return result.returncode == 0
            
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False

def load_json_file(filename):
    """Carga un archivo JSON y retorna su contenido."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return None

def find_users_in_office(network_data, config_data):
    """Encuentra usuarios que están en la oficina comparando IPs."""
    if not network_data or not config_data:
        return []
    
    # Obtener IPs activas de la red
    active_ips = set()
    if 'devices' in network_data:
        for device in network_data['devices']:
            if 'ip' in device:
                active_ips.add(device['ip'])
    
    # Buscar usuarios configurados que están activos
    users_in_office = []
    if 'users' in config_data:
        for user in config_data['users']:
            if user.get('ip') in active_ips:
                users_in_office.append({
                    'ip': user['ip'],
                    'hostname': user['hostname'],
                    'status': 'En la Oficina'
                })
    
    return users_in_office

def save_current_status(users_in_office, config_data, json_filename="current_status.json", csv_filename="current_status.csv"):
    """Guarda el status actual en formato JSON y CSV."""
    # Crear lista de userIDs de usuarios en la oficina
    user_ids = []
    
    if 'users' in config_data:
        for user in config_data['users']:
            # Buscar si el usuario está en la oficina
            is_in_office = any(u['ip'] == user['ip'] for u in users_in_office)
            
            # Solo incluir usuarios que están en la oficina
            if is_in_office:
                user_ids.append(user['userID'])
    
    # Guardar archivo JSON con formato específico
    try:
        json_data = {"user_ids": user_ids}
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
    
    # Guardar archivo CSV con solo userIDs
    try:
        with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
            for user_id in user_ids:
                f.write(f"{user_id}\n")
    except Exception:
        pass
    
    return user_ids

def main():
    # Paso 1: Ejecutar escaneo de red
    if not run_network_scan():
        return
    
    # Paso 2: Cargar archivos
    network_data = load_json_file("Simpat_Network.json")
    config_data = load_json_file("Config.json")
    
    if not network_data or not config_data:
        return
    
    # Paso 3: Analizar presencia y guardar status
    users_in_office = find_users_in_office(network_data, config_data)
    user_ids = save_current_status(users_in_office, config_data)
    
    # Paso 4: Actualizar status en Slack (si hay usuarios detectados)
    if user_ids:
        run_slack_status_update()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, Exception):
        pass
