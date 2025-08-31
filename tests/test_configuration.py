#!/usr/bin/env python3
"""
Script de Prueba para Validar la Configuración del Sistema.
Valida todos los archivos de configuración y su formato.
"""

import json
import os
import sys
import ipaddress
from datetime import datetime

def print_header(title):
    """Imprime un encabezado formateado."""
    print(f"\n{'='*50}")
    print(f"[CONFIG] {title}")
    print(f"{'='*50}")

def print_section(title):
    """Imprime una sección formateada."""
    print(f"\n[SECCION] {title}")
    print(f"{'-'*40}")

def validate_ip_address(ip_str):
    """Valida que una dirección IP sea válida."""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def validate_user_id(user_id):
    """Valida que un userID tenga el formato correcto."""
    if not user_id:
        return False
    # Los userIDs de Slack típicamente empiezan con U y tienen 9-11 caracteres
    return user_id.startswith('U') and len(user_id) >= 9

def test_config_json():
    """Prueba la configuración de Config.json."""
    print_section("Validación de Config.json")
    
    if not os.path.exists("Config.json"):
        print("[ERROR] Config.json no encontrado")
        return False
    
    try:
        with open("Config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("[OK] Config.json cargado exitosamente")
        
        # Verificar estructura básica
        if "users" not in config:
            print("[ERROR] Config.json no contiene la clave 'users'")
            return False
        
        if not isinstance(config["users"], list):
            print("[ERROR] La clave 'users' no es una lista")
            return False
        
        users = config["users"]
        print(f"[STATS] Usuarios configurados: {len(users)}")
        
        if len(users) == 0:
            print("[WARNING] No hay usuarios configurados")
            return True
        
        # Validar cada usuario
        valid_users = 0
        invalid_users = []
        
        for i, user in enumerate(users, 1):
            print(f"\n[USER] Usuario {i}:")
            
            # Verificar campos requeridos
            required_fields = ["ip", "hostname", "userID"]
            missing_fields = [field for field in required_fields if field not in user]
            
            if missing_fields:
                print(f"   [ERROR] Campos faltantes: {missing_fields}")
                invalid_users.append(i)
                continue
            
            # Validar IP
            ip = user["ip"]
            if not validate_ip_address(ip):
                print(f"   [ERROR] IP inválida: {ip}")
                invalid_users.append(i)
                continue
            else:
                print(f"   [OK] IP válida: {ip}")
            
            # Validar hostname
            hostname = user["hostname"]
            if not hostname or not isinstance(hostname, str):
                print(f"   [ERROR] Hostname inválido: {hostname}")
                invalid_users.append(i)
                continue
            else:
                print(f"   [OK] Hostname válido: {hostname}")
            
            # Validar userID
            user_id = user["userID"]
            if not validate_user_id(user_id):
                print(f"   [ERROR] UserID inválido: {user_id}")
                invalid_users.append(i)
                continue
            else:
                print(f"   [OK] UserID válido: {user_id}")
            
            valid_users += 1
            print(f"   [OK] Usuario {i} válido")
        
        print(f"\n[STATS] Resumen de validación:")
        print(f"   [OK] Usuarios válidos: {valid_users}")
        print(f"   [ERROR] Usuarios inválidos: {len(invalid_users)}")
        
        if invalid_users:
            print(f"   [TEXT] Usuarios con errores: {invalid_users}")
        
        return len(invalid_users) == 0
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error de formato JSON: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error leyendo Config.json: {e}")
        return False

def test_env_file():
    """Prueba la configuración del archivo .env."""
    print_section("Validación de .env")
    
    if not os.path.exists(".env"):
        print("[WARNING] Archivo .env no encontrado")
        print("   [TIP] Crea un archivo .env con tus tokens de Slack")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        print("[OK] Archivo .env cargado exitosamente")
        
        # Verificar variables requeridas
        required_vars = {
            "SLACK_USER_TOKEN": "Token de usuario de Slack (xoxp-...)",
            "SLACK_BOT_TOKEN": "Token de bot de Slack (xoxb-...)"
        }
        
        optional_vars = {
            "DEFAULT_STATUS": "Status por defecto (default: 'At Simpat Tech')",
            "NETWORK_TIMEOUT": "Timeout de red (default: 120)",
            "SCAN_WORKERS": "Workers de escaneo (default: 10)"
        }
        
        print("\n[TOKEN] Variables requeridas:")
        all_required_present = True
        
        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            if value:
                # Ocultar parte del token por seguridad
                masked_value = value[:10] + "..." if len(value) > 10 else value
                print(f"   [OK] {var_name}: {masked_value}")
            else:
                print(f"   [ERROR] {var_name}: No configurado")
                all_required_present = False
        
        print("\n[CONFIG] Variables opcionales:")
        for var_name, description in optional_vars.items():
            value = os.getenv(var_name)
            if value:
                print(f"   [OK] {var_name}: {value}")
            else:
                print(f"   [WARNING] {var_name}: No configurado (usará valor por defecto)")
        
        return all_required_present
        
    except ImportError:
        print("[ERROR] python-dotenv no está instalado")
        print("   [TIP] Instala con: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"[ERROR] Error cargando .env: {e}")
        return False

def test_network_configuration():
    """Prueba la configuración de red."""
    print_section("Validación de Configuración de Red")
    
    try:
        # Verificar que Config.json existe y tiene usuarios
        if not os.path.exists("Config.json"):
            print("[ERROR] Config.json no encontrado")
            return False
        
        with open("Config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        users = config.get("users", [])
        if not users:
            print("[WARNING] No hay usuarios configurados para validar red")
            return True
        
        # Extraer IPs
        ips = [user["ip"] for user in users if "ip" in user]
        
        if not ips:
            print("[ERROR] No se encontraron IPs en la configuración")
            return False
        
        print(f"[STATS] IPs configuradas: {len(ips)}")
        
        # Verificar que todas las IPs están en el mismo rango
        try:
            networks = []
            for ip in ips:
                ip_obj = ipaddress.ip_address(ip)
                network = ipaddress.ip_network(f"{ip}/24", strict=False)
                networks.append(network)
            
            # Verificar si todas las IPs están en el mismo rango /24
            base_network = networks[0]
            all_same_network = all(network == base_network for network in networks)
            
            if all_same_network:
                print(f"[OK] Todas las IPs están en el mismo rango: {base_network}")
            else:
                print("[WARNING] Las IPs están en diferentes rangos de red")
                for i, network in enumerate(networks):
                    print(f"   [LOCATION] IP {i+1}: {network}")
            
            # Mostrar rango de escaneo
            print(f"[NETWORK] Rango de escaneo: {base_network.network_address} - {base_network.broadcast_address}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error analizando rangos de red: {e}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error validando configuración de red: {e}")
        return False

def test_file_permissions():
    """Prueba los permisos de archivos."""
    print_section("Validación de Permisos de Archivos")
    
    files_to_check = [
        ("Config.json", "Configuración de usuarios"),
        ("auto_status_manager.py", "Script principal"),
        ("quick_ping.py", "Escáner de red"),
        ("slack_status_manager.py", "Gestor de status")
    ]
    
    all_readable = True
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            if os.access(filename, os.R_OK):
                print(f"   [OK] {filename} - Legible")
            else:
                print(f"   [ERROR] {filename} - No legible")
                all_readable = False
        else:
            print(f"   [ERROR] {filename} - No encontrado")
            all_readable = False
    
    return all_readable

def test_dependencies():
    """Prueba las dependencias del sistema."""
    print_section("Validación de Dependencias")
    
    required_packages = [
        "json",
        "os",
        "sys",
        "subprocess",
        "socket",
        "platform",
        "concurrent.futures",
        "datetime",
        "time"
    ]
    
    optional_packages = [
        ("dotenv", "python-dotenv"),
        ("slack_sdk", "slack-sdk")
    ]
    
    print("[PACKAGE] Paquetes requeridos (incluidos en Python):")
    all_required_available = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   [OK] {package}")
        except ImportError:
            print(f"   [ERROR] {package}")
            all_required_available = False
    
    print("\n[PACKAGE] Paquetes opcionales:")
    for package, pip_name in optional_packages:
        try:
            __import__(package)
            print(f"   [OK] {package} ({pip_name})")
        except ImportError:
            print(f"   [WARNING] {package} ({pip_name}) - No instalado")
    
    return all_required_available

def generate_configuration_report():
    """Genera un reporte completo de configuración."""
    print_header("REPORTE DE VALIDACIÓN DE CONFIGURACIÓN")
    
    # Ejecutar todas las validaciones
    config_ok = test_config_json()
    env_ok = test_env_file()
    network_ok = test_network_configuration()
    permissions_ok = test_file_permissions()
    dependencies_ok = test_dependencies()
    
    print_header("RESUMEN DE VALIDACIÓN")
    
    print("[TARGET] Estado de la configuración:")
    print(f"   {'[OK]' if config_ok else '[ERROR]'} Config.json")
    print(f"   {'[OK]' if env_ok else '[ERROR]'} Archivo .env")
    print(f"   {'[OK]' if network_ok else '[ERROR]'} Configuración de red")
    print(f"   {'[OK]' if permissions_ok else '[ERROR]'} Permisos de archivos")
    print(f"   {'[OK]' if dependencies_ok else '[ERROR]'} Dependencias")
    
    all_valid = config_ok and env_ok and network_ok and permissions_ok and dependencies_ok
    
    if all_valid:
        print("\n[SUCCESS] ¡Configuración válida!")
        print("   El sistema está correctamente configurado")
    else:
        print("\n[WARNING] Problemas de configuración detectados")
        print("   Revisa los errores anteriores")
    
    print("\n[SECCION] Recomendaciones:")
    if not config_ok:
        print("   • Verifica el formato de Config.json")
        print("   • Asegúrate de que todas las IPs son válidas")
        print("   • Verifica que los userIDs tienen el formato correcto")
    
    if not env_ok:
        print("   • Crea un archivo .env con tus tokens de Slack")
        print("   • Instala python-dotenv: pip install python-dotenv")
    
    if not network_ok:
        print("   • Verifica que las IPs están en el mismo rango de red")
        print("   • Asegúrate de que las IPs son accesibles")
    
    if not permissions_ok:
        print("   • Verifica los permisos de lectura de los archivos")
    
    if not dependencies_ok:
        print("   • Instala las dependencias faltantes")
        print("   • Ejecuta: pip install -r requirements.txt")

if __name__ == "__main__":
    generate_configuration_report()
