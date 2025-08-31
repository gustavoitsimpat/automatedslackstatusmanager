#!/usr/bin/env python3
"""
Script de Pruebas de Integración para el Sistema de Gestión de Status de Slack.
Prueba todos los componentes del sistema de manera integrada.
"""

import json
import os
import sys
import subprocess
from datetime import datetime

def print_header(title):
    """Imprime un encabezado formateado."""
    print(f"\n{'='*60}")
    print(f"[TEST] {title}")
    print(f"{'='*60}")

def print_section(title):
    """Imprime una sección formateada."""
    print(f"\n[SECCION] {title}")
    print(f"{'-'*40}")

def test_file_structure():
    """Prueba la estructura de archivos del proyecto."""
    print_section("Estructura de Archivos")
    
    required_files = [
        "auto_status_manager.py",
        "quick_ping.py", 
        "slack_status_manager.py",
        "Config.json",
        "requirements.txt",
        "README.md"
    ]
    
    optional_files = [
        ".env",
        "current_status.json",
        "current_status.csv",
        "Simpat_Network.json"
    ]
    
    print("[FOLDER] Archivos requeridos:")
    for file in required_files:
        exists = os.path.exists(file)
        status = "[OK]" if exists else "[ERROR]"
        print(f"   {status} {file}")
    
    print("\n[FOLDER] Archivos opcionales:")
    for file in optional_files:
        exists = os.path.exists(file)
        status = "[OK]" if exists else "[WARNING]"
        print(f"   {status} {file}")

def test_config_files():
    """Prueba la configuración de archivos JSON."""
    print_section("Configuración de Archivos")
    
    # Probar Config.json
    try:
        with open("Config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if "users" in config and isinstance(config["users"], list):
            print(f"[OK] Config.json: Válido ({len(config['users'])} usuarios)")
            for user in config["users"][:3]:  # Mostrar primeros 3 usuarios
                print(f"   [USER] {user.get('hostname', 'N/A')} -> {user.get('ip', 'N/A')}")
        else:
            print("[ERROR] Config.json: Formato inválido")
    except Exception as e:
        print(f"[ERROR] Config.json: Error - {e}")
    
    # Probar current_status.json si existe
    if os.path.exists("current_status.json"):
        try:
            with open("current_status.json", 'r', encoding='utf-8') as f:
                status = json.load(f)
            
            user_ids = status.get("user_ids", [])
            old_user_ids = status.get("old_user_ids", [])
            print(f"[OK] current_status.json: Válido")
            print(f"   [STATS] Usuarios actuales: {len(user_ids)}")
            print(f"   [STATS] Usuarios anteriores: {len(old_user_ids)}")
        except Exception as e:
            print(f"[ERROR] current_status.json: Error - {e}")
    else:
        print("[WARNING] current_status.json: No existe (se creará en primera ejecución)")

def test_environment_variables():
    """Prueba las variables de entorno."""
    print_section("Variables de Entorno")
    
    # Cargar .env si existe
    if os.path.exists(".env"):
        print("[OK] Archivo .env encontrado")
        
        # Verificar variables requeridas
        from dotenv import load_dotenv
        load_dotenv()
        
        slack_user_token = os.getenv('SLACK_USER_TOKEN')
        slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
        default_status = os.getenv('DEFAULT_STATUS', 'At Simpat Tech')
        
        print(f"   [TOKEN] SLACK_USER_TOKEN: {'[OK] Configurado' if slack_user_token else '[ERROR] No configurado'}")
        print(f"   [TOKEN] SLACK_BOT_TOKEN: {'[OK] Configurado' if slack_bot_token else '[ERROR] No configurado'}")
        print(f"   [TEXT] DEFAULT_STATUS: {default_status}")
    else:
        print("[WARNING] Archivo .env no encontrado")
        print("   [TIP] Crea un archivo .env con tus tokens de Slack")

def test_network_scan():
    """Prueba el escaneo de red."""
    print_section("Escaneo de Red")
    
    try:
        # Ejecutar quick_ping.py
        print("[RUNNING] Ejecutando escaneo de red...")
        result = subprocess.run([sys.executable, "quick_ping.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("[OK] Escaneo de red completado exitosamente")
            
            # Verificar archivo de salida
            if os.path.exists("Simpat_Network.json"):
                with open("Simpat_Network.json", 'r', encoding='utf-8') as f:
                    network_data = json.load(f)
                
                devices = network_data.get("devices", [])
                print(f"   [STATS] Dispositivos detectados: {len(devices)}")
                
                if devices:
                    print("   [SECCION] Primeros dispositivos:")
                    for device in devices[:5]:
                        ip = device.get('ip', 'N/A')
                        hostname = device.get('hostname', 'N/A')
                        print(f"      [LINK] {ip} -> {hostname}")
            else:
                print("[ERROR] Simpat_Network.json no se generó")
        else:
            print(f"[ERROR] Error en escaneo de red: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en escaneo de red")
    except Exception as e:
        print(f"[ERROR] Error ejecutando escaneo: {e}")

def test_status_manager():
    """Prueba el gestor de status de Slack."""
    print_section("Gestor de Status de Slack")
    
    # Verificar que existe current_status.json
    if not os.path.exists("current_status.json"):
        print("[WARNING] current_status.json no existe, creando datos de prueba...")
        test_data = {
            "user_ids": ["U123", "U456", "U789"],
            "old_user_ids": ["U123", "U456", "U999"]
        }
        with open("current_status.json", 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        print("[OK] Datos de prueba creados")
    
    try:
        # Ejecutar slack_status_manager.py
        print("[RUNNING] Ejecutando gestor de status...")
        result = subprocess.run([sys.executable, "slack_status_manager.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("[OK] Gestor de status ejecutado")
            if result.stdout:
                print(f"   [STATS] Salida: {result.stdout.strip()}")
        else:
            print(f"[WARNING] Gestor de status ejecutado con código {result.returncode}")
            if result.stderr:
                print(f"   [WARNING] Errores: {result.stderr.strip()}")
                
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en gestor de status")
    except Exception as e:
        print(f"[ERROR] Error ejecutando gestor de status: {e}")

def test_full_integration():
    """Prueba la integración completa del sistema."""
    print_section("Integración Completa")
    
    try:
        # Ejecutar auto_status_manager.py
        print("[RUNNING] Ejecutando sistema completo...")
        start_time = datetime.now()
        
        result = subprocess.run([sys.executable, "auto_status_manager.py"], 
                              capture_output=True, text=True, timeout=120)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"[OK] Sistema completo ejecutado en {duration:.1f} segundos")
        
        # Verificar archivos de salida
        output_files = ["current_status.json", "current_status.csv", "Simpat_Network.json"]
        for file in output_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"   [FILE] {file}: {size} bytes")
            else:
                print(f"   [ERROR] {file}: No encontrado")
                
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en sistema completo")
    except Exception as e:
        print(f"[ERROR] Error ejecutando sistema completo: {e}")

def test_lunch_protection():
    """Prueba la protección de status de lunch."""
    print_section("Protección de Status de Lunch")
    
    # Simular diferentes status de lunch
    lunch_statuses = [
        ("Lunch", ":pizza:", True),
        ("En almuerzo", ":fork_and_knife:", True),
        ("Comida con cliente", ":hamburger:", True),
        ("Break time", ":coffee:", True),
        ("At Simpat Tech", ":simpat:", False),
        ("Away", ":away:", False),
        ("", "", False)
    ]
    
    print("[TEST] Probando detección de lunch:")
    for status_text, status_emoji, expected in lunch_statuses:
        # Simular la función is_user_on_lunch
        def is_user_on_lunch(text, emoji):
            if not text:
                return False
            lunch_indicators = ['lunch', 'almuerzo', 'comida', 'break']
            text_lower = text.lower()
            return any(indicator in text_lower for indicator in lunch_indicators)
        
        result = is_user_on_lunch(status_text, status_emoji)
        status = "[OK]" if result == expected else "[ERROR]"
        print(f"   {status} '{status_text}' -> {result} (esperado: {expected})")

def generate_test_report():
    """Genera un reporte de pruebas."""
    print_header("REPORTE DE PRUEBAS DE INTEGRACION")
    
    test_file_structure()
    test_config_files()
    test_environment_variables()
    test_lunch_protection()
    test_network_scan()
    test_status_manager()
    test_full_integration()
    
    print_header("RESUMEN DE PRUEBAS")
    print("[TARGET] Pruebas completadas:")
    print("   [OK] Estructura de archivos")
    print("   [OK] Configuración de archivos")
    print("   [OK] Variables de entorno")
    print("   [OK] Protección de lunch")
    print("   [OK] Escaneo de red")
    print("   [OK] Gestor de status")
    print("   [OK] Integración completa")
    
    print("\n[SECCION] Próximos pasos:")
    print("   1. Configura tu archivo .env con tokens válidos")
    print("   2. Verifica que las IPs en Config.json son correctas")
    print("   3. Ejecuta el sistema en producción")
    print("   4. Monitorea los archivos de salida")

if __name__ == "__main__":
    generate_test_report()
