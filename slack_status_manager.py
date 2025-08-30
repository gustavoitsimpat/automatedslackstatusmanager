#!/usr/bin/env python3
"""
Gestor de Status de Slack basado en presencia en la red.
Compara usuarios activos en la red con la configuración y simula cambios de status.
"""

import json
import time
from datetime import datetime

def load_json_file(filename):
    """Carga un archivo JSON y retorna su contenido."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {filename}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Formato JSON inválido en {filename}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error al cargar {filename}: {e}")
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
    print(f"🔄 Simulando cambio de status en Slack...")
    print(f"   👤 Usuario: {user['hostname']}")
    print(f"   📍 IP: {user['ip']}")
    print(f"   🏢 Status: {user['status']}")
    
    # Simular delay de API de Slack
    time.sleep(0.5)
    
    print(f"   ✅ Status actualizado exitosamente en Slack")
    print()

def generate_report(users_in_office, network_data, config_data):
    """Genera un reporte de la comparación."""
    print("📊 REPORTE DE PRESENCIA EN LA OFICINA")
    print("=" * 50)
    
    # Información del escaneo
    if network_data and 'scan_info' in network_data:
        scan_info = network_data['scan_info']
        print(f"🌐 Red escaneada: {scan_info.get('network', 'N/A')}")
        print(f"📱 Dispositivos totales: {scan_info.get('total_devices', 'N/A')}")
    
    print(f"👥 Usuarios configurados: {len(config_data.get('users', []))}")
    print(f"🏢 Usuarios en la oficina: {len(users_in_office)}")
    print()
    
    # Lista de usuarios en la oficina
    if users_in_office:
        print("✅ USUARIOS PRESENTES EN LA OFICINA:")
        print("-" * 40)
        for user in users_in_office:
            print(f"   • {user['hostname']} ({user['ip']}) - {user['status']}")
    else:
        print("❌ No hay usuarios configurados presentes en la oficina")
    
    print()
    
    # Lista de usuarios ausentes
    config_users = config_data.get('users', [])
    present_ips = {user['ip'] for user in users_in_office}
    absent_users = [user for user in config_users if user['ip'] not in present_ips]
    
    if absent_users:
        print("❌ USUARIOS AUSENTES:")
        print("-" * 40)
        for user in absent_users:
            print(f"   • {user['hostname']} ({user['ip']}) - No detectado")
    
    print("=" * 50)

def save_status_log(users_in_office, filename="status_log.json"):
    """Guarda el log de cambios de status."""
    log_entry = {
        "users_in_office": users_in_office,
        "total_users": len(users_in_office)
    }
    
    # Cargar log existente o crear nuevo
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log_data = {"logs": []}
    
    # Agregar nueva entrada
    log_data["logs"].append(log_entry)
    
    # Guardar log actualizado
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        print(f"📝 Log guardado en: {filename}")
    except Exception as e:
        print(f"⚠️  No se pudo guardar el log: {e}")

def main():
    print("🏢 GESTOR DE STATUS DE SLACK")
    print("=" * 40)
    print()
    
    # Cargar archivos
    print("📂 Cargando archivos de configuración...")
    network_data = load_json_file("Simpat_Network.json")
    config_data = load_json_file("Config.json")
    
    if not network_data or not config_data:
        print("❌ No se pueden procesar los archivos. Verifica que existan.")
        return
    
    print("✅ Archivos cargados exitosamente")
    print()
    
    # Encontrar usuarios en la oficina
    print("🔍 Analizando presencia en la oficina...")
    users_in_office = find_users_in_office(network_data, config_data)
    
    # Generar reporte
    generate_report(users_in_office, network_data, config_data)
    
    # Simular cambios de status en Slack
    if users_in_office:
        print("🚀 PROCESANDO CAMBIOS DE STATUS EN SLACK")
        print("=" * 50)
        
        for user in users_in_office:
            simulate_slack_status_change(user)
        
        print(f"✅ Procesados {len(users_in_office)} cambios de status")
    else:
        print("ℹ️  No hay usuarios para actualizar en Slack")
    
    # Guardar log
    save_status_log(users_in_office)
    
    print("\n🎉 Proceso completado exitosamente!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
