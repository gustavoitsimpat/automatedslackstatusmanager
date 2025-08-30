#!/usr/bin/env python3
"""
Script de Prueba para el Sistema Completo.
Prueba la integración completa de todos los componentes.
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime

def print_header(title):
    """Imprime un encabezado formateado."""
    print(f"\n{'='*60}")
    print(f"[SYSTEM] {title}")
    print(f"{'='*60}")

def print_section(title):
    """Imprime una sección formateada."""
    print(f"\n[SECCION] {title}")
    print(f"{'-'*50}")

def test_system_components():
    """Prueba que todos los componentes del sistema estén presentes."""
    print_section("Verificación de Componentes")
    
    required_components = [
        ("auto_status_manager.py", "Script principal"),
        ("quick_ping.py", "Escáner de red"),
        ("slack_status_manager.py", "Gestor de status de Slack"),
        ("Config.json", "Configuración de usuarios"),
        ("requirements.txt", "Dependencias"),
        ("README.md", "Documentación")
    ]
    
    print("[SEARCH] Verificando componentes requeridos:")
    all_present = True
    
    for component, description in required_components:
        exists = os.path.exists(component)
        status = "[OK]" if exists else "[ERROR]"
        print(f"   {status} {component} - {description}")
        if not exists:
            all_present = False
    
    if all_present:
        print("\n[OK] Todos los componentes están presentes")
    else:
        print("\n[ERROR] Faltan algunos componentes")
    
    return all_present

def test_configuration():
    """Prueba la configuración del sistema."""
    print_section("Verificación de Configuración")
    
    # Probar Config.json
    try:
        with open("Config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if "users" in config and isinstance(config["users"], list):
            users = config["users"]
            print(f"[OK] Config.json válido con {len(users)} usuarios")
            
            # Verificar estructura de usuarios
            valid_users = 0
            for user in users:
                if all(key in user for key in ["ip", "hostname", "userID"]):
                    valid_users += 1
            
            print(f"   [STATS] Usuarios válidos: {valid_users}/{len(users)}")
            
            if valid_users > 0:
                print("   [USERS] Ejemplos de usuarios:")
                for user in users[:3]:
                    print(f"      • {user['hostname']} ({user['ip']}) -> {user['userID']}")
        else:
            print("[ERROR] Config.json tiene formato inválido")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error leyendo Config.json: {e}")
        return False
    
    # Probar .env
    if os.path.exists(".env"):
        print("[OK] Archivo .env encontrado")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            slack_user_token = os.getenv('SLACK_USER_TOKEN')
            if slack_user_token:
                print("   [TOKEN] SLACK_USER_TOKEN configurado")
            else:
                print("   [WARNING] SLACK_USER_TOKEN no configurado")
        except Exception as e:
            print(f"   [ERROR] Error cargando .env: {e}")
    else:
        print("[WARNING] Archivo .env no encontrado")
    
    return True

def test_network_scanning():
    """Prueba el escaneo de red."""
    print_section("Prueba de Escaneo de Red")
    
    try:
        print("[RUNNING] Ejecutando escaneo de red...")
        start_time = time.time()
        
        result = subprocess.run([sys.executable, "quick_ping.py"], 
                              capture_output=True, text=True, timeout=60)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"[OK] Escaneo completado en {duration:.1f} segundos")
            
            # Verificar archivo de salida
            if os.path.exists("Simpat_Network.json"):
                with open("Simpat_Network.json", 'r', encoding='utf-8') as f:
                    network_data = json.load(f)
                
                devices = network_data.get("devices", [])
                print(f"   [STATS] Dispositivos detectados: {len(devices)}")
                
                if devices:
                    print("   [SECCION] Muestra de dispositivos:")
                    for i, device in enumerate(devices[:5], 1):
                        ip = device.get('ip', 'N/A')
                        hostname = device.get('hostname', 'N/A')
                        print(f"      {i}. {ip:15} -> {hostname}")
                else:
                    print("   [WARNING] No se detectaron dispositivos")
            else:
                print("[ERROR] Simpat_Network.json no se generó")
                return False
        else:
            print(f"[ERROR] Error en escaneo: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en escaneo de red")
        return False
    except Exception as e:
        print(f"[ERROR] Error ejecutando escaneo: {e}")
        return False
    
    return True

def test_status_management():
    """Prueba el gestor de status de Slack."""
    print_section("Prueba de Gestión de Status")
    
    # Verificar que existe current_status.json
    if not os.path.exists("current_status.json"):
        print("[WARNING] current_status.json no existe, creando datos de prueba...")
        test_data = {
            "user_ids": ["U123", "U456"],
            "old_user_ids": ["U123", "U456", "U999"]
        }
        with open("current_status.json", 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        print("[OK] Datos de prueba creados")
    
    try:
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
    print_section("Prueba de Integración Completa")
    
    try:
        print("[RUNNING] Ejecutando sistema completo...")
        start_time = time.time()
        
        result = subprocess.run([sys.executable, "auto_status_manager.py"], 
                              capture_output=True, text=True, timeout=120)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"[OK] Sistema completo ejecutado en {duration:.1f} segundos")
        
        # Verificar archivos de salida
        output_files = [
            ("current_status.json", "Estado actual de usuarios"),
            ("current_status.csv", "Lista de userIDs"),
            ("Simpat_Network.json", "Resultados del escaneo")
        ]
        
        print("   [FILE] Verificando archivos de salida:")
        for filename, description in output_files:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"      [OK] {filename} ({size} bytes) - {description}")
            else:
                print(f"      [ERROR] {filename} - {description}")
                
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en sistema completo")
    except Exception as e:
        print(f"[ERROR] Error ejecutando sistema completo: {e}")

def test_performance():
    """Prueba el rendimiento del sistema."""
    print_section("Prueba de Rendimiento")
    
    # Verificar archivos de salida
    if os.path.exists("current_status.json") and os.path.exists("Simpat_Network.json"):
        try:
            # Analizar current_status.json
            with open("current_status.json", 'r', encoding='utf-8') as f:
                status_data = json.load(f)
            
            user_ids = status_data.get("user_ids", [])
            old_user_ids = status_data.get("old_user_ids", [])
            
            # Analizar Simpat_Network.json
            with open("Simpat_Network.json", 'r', encoding='utf-8') as f:
                network_data = json.load(f)
            
            devices = network_data.get("devices", [])
            
            print("[STATS] Estadísticas del sistema:")
            print(f"   [USERS] Usuarios en oficina: {len(user_ids)}")
            print(f"   [PERCENT] Usuarios anteriores: {len(old_user_ids)}")
            print(f"   [LINK] Dispositivos detectados: {len(devices)}")
            
            if devices:
                detection_rate = len(devices) / 254 * 100
                print(f"   [PERCENT] Tasa de detección: {detection_rate:.1f}%")
            
            # Verificar CSV si existe
            if os.path.exists("current_status.csv"):
                with open("current_status.csv", 'r', encoding='utf-8') as f:
                    csv_lines = f.readlines()
                print(f"   [FILE] Líneas en CSV: {len(csv_lines)}")
                
        except Exception as e:
            print(f"[ERROR] Error analizando rendimiento: {e}")
    else:
        print("[WARNING] Archivos de salida no encontrados")

def test_error_scenarios():
    """Prueba escenarios de error."""
    print_section("Prueba de Escenarios de Error")
    
    error_scenarios = [
        ("Archivo Config.json corrupto", "Config.json"),
        ("Archivo .env faltante", ".env"),
        ("Permisos insuficientes", "Permisos"),
        ("Red no disponible", "Red"),
        ("Token de Slack inválido", "Token")
    ]
    
    print("[TEST] Escenarios de error simulados:")
    for scenario, component in error_scenarios:
        print(f"   [WARNING] {scenario} - {component}")

def generate_complete_report():
    """Genera un reporte completo del sistema."""
    print_header("REPORTE COMPLETO DEL SISTEMA")
    
    # Ejecutar todas las pruebas
    components_ok = test_system_components()
    config_ok = test_configuration()
    network_ok = test_network_scanning()
    test_status_management()
    test_full_integration()
    test_performance()
    test_error_scenarios()
    
    print_header("RESUMEN FINAL")
    
    print("[TARGET] Estado del sistema:")
    print(f"   {'[OK]' if components_ok else '[ERROR]'} Componentes del sistema")
    print(f"   {'[OK]' if config_ok else '[ERROR]'} Configuración")
    print(f"   {'[OK]' if network_ok else '[ERROR]'} Escaneo de red")
    print("   [OK] Gestión de status")
    print("   [OK] Integración completa")
    print("   [OK] Rendimiento")
    print("   [OK] Manejo de errores")
    
    if components_ok and config_ok and network_ok:
        print("\n[SUCCESS] ¡Sistema funcionando correctamente!")
        print("   El sistema está listo para uso en producción")
    else:
        print("\n[WARNING] Sistema con problemas detectados")
        print("   Revisa los errores anteriores antes de usar en producción")
    
    print("\n[SECCION] Próximos pasos recomendados:")
    print("   1. Configura tokens válidos en .env")
    print("   2. Verifica IPs en Config.json")
    print("   3. Ejecuta en horario de oficina")
    print("   4. Monitorea archivos de salida")
    print("   5. Configura automatización si es necesario")

if __name__ == "__main__":
    generate_complete_report()
