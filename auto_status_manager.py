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

def simulate_slack_status_change(user):
    """Simula el cambio de status en Slack para un usuario."""
    # Simular delay de API de Slack
    time.sleep(0.1)

def generate_report(users_in_office, network_data, config_data):
    """Genera un reporte de la comparación."""
    pass

def save_current_status(users_in_office, config_data, filename="current_status.json"):
    """Guarda el status actual en formato JSON simple."""
    # Crear lista completa con todos los usuarios configurados
    all_users = []
    
    if 'users' in config_data:
        for user in config_data['users']:
            # Buscar si el usuario está en la oficina
            is_in_office = any(u['ip'] == user['ip'] for u in users_in_office)
            
            all_users.append({
                "ip": user['ip'],
                "hostname": user['hostname'],
                "status": "En la Oficina" if is_in_office else "No detectado"
            })
    
    # Guardar archivo JSON simple
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_users, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def main():
    # Paso 1: Ejecutar escaneo de red
    if not run_network_scan():
        return
    
    # Paso 2: Cargar archivos
    network_data = load_json_file("Simpat_Network.json")
    config_data = load_json_file("Config.json")
    
    if not network_data or not config_data:
        return
    
    # Paso 3: Analizar presencia
    users_in_office = find_users_in_office(network_data, config_data)
    
    # Paso 4: Procesar cambios de status
    for user in users_in_office:
        simulate_slack_status_change(user)
    
    # Paso 5: Guardar status actual
    save_current_status(users_in_office, config_data)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, Exception):
        pass
