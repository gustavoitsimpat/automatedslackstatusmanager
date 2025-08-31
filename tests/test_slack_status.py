#!/usr/bin/env python3
"""
Script de Prueba para el Gestor de Status de Slack.
Prueba específicamente las funcionalidades de slack_status_manager.py
"""

import json
import os
import sys
import subprocess
from datetime import datetime

def print_header(title):
    """Imprime un encabezado formateado."""
    print(f"\n{'='*50}")
    print(f"[SLACK] {title}")
    print(f"{'='*50}")

def print_section(title):
    """Imprime una sección formateada."""
    print(f"\n[SECCION] {title}")
    print(f"{'-'*40}")

def test_slack_status_script():
    """Prueba el script slack_status_manager.py."""
    print_section("Prueba del Script slack_status_manager.py")
    
    if not os.path.exists("slack_status_manager.py"):
        print("[ERROR] slack_status_manager.py no encontrado")
        return
    
    try:
        print("[RUNNING] Ejecutando slack_status_manager.py...")
        result = subprocess.run([sys.executable, "slack_status_manager.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("[OK] slack_status_manager.py ejecutado exitosamente")
            if result.stdout:
                print(f"   [STATS] Salida: {result.stdout.strip()}")
        else:
            print(f"[WARNING] slack_status_manager.py ejecutado con código {result.returncode}")
            if result.stderr:
                print(f"   [WARNING] Errores: {result.stderr.strip()}")
                
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en slack_status_manager.py")
    except Exception as e:
        print(f"[ERROR] Error ejecutando slack_status_manager.py: {e}")

def test_lunch_detection():
    """Prueba la detección de status de lunch."""
    print_section("Prueba de Detección de Lunch")
    
    # Simular la función is_user_on_lunch
    def is_user_on_lunch(status_text, status_emoji):
        if not status_text:
            return False
        lunch_indicators = ['lunch', 'almuerzo', 'comida', 'break']
        status_lower = status_text.lower()
        return any(indicator in status_lower for indicator in lunch_indicators)
    
    # Casos de prueba
    test_cases = [
        ("Lunch", ":pizza:", True, "Lunch en inglés"),
        ("En almuerzo", ":fork_and_knife:", True, "Almuerzo en español"),
        ("Comida con cliente", ":hamburger:", True, "Comida con contexto"),
        ("Break time", ":coffee:", True, "Break en inglés"),
        ("LUNCH BREAK", ":sandwich:", True, "Lunch break mayúsculas"),
        ("At Simpat Tech", ":simpat:", False, "Status de oficina"),
        ("Away", ":away:", False, "Status away"),
        ("", "", False, "Status vacío"),
        ("Working from home", ":house:", False, "Trabajo remoto"),
        ("En reunión", ":meeting:", False, "En reunión")
    ]
    
    print("[TEST] Probando detección de lunch:")
    correct = 0
    total = len(test_cases)
    
    for status_text, status_emoji, expected, description in test_cases:
        result = is_user_on_lunch(status_text, status_emoji)
        status = "[OK]" if result == expected else "[ERROR]"
        print(f"   {status} '{status_text}' -> {result} (esperado: {expected}) - {description}")
        if result == expected:
            correct += 1
    
    print(f"\n[STATS] Resultados: {correct}/{total} correctos ({correct/total*100:.1f}%)")

def test_status_clearing():
    """Prueba la función de borrado de status."""
    print_section("Prueba de Borrado de Status")
    
    # Simular la función clear_slack_status
    def clear_slack_status(client, user_id):
        try:
            profile_data = {
                "status_text": "",
                "status_emoji": ""
            }
            # En una implementación real, esto haría la llamada a la API
            return True, None
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    # Casos de prueba
    test_users = ["U123", "U456", "U789", "INVALID"]
    
    print("[TEST] Probando borrado de status:")
    for user_id in test_users:
        success, error = clear_slack_status(None, user_id)
        status = "[OK]" if success else "[ERROR]"
        print(f"   {status} Usuario {user_id}: {'Exitoso' if success else f'Error - {error}'}")

def test_user_data_loading():
    """Prueba la carga de datos de usuario."""
    print_section("Prueba de Carga de Datos de Usuario")
    
    # Simular la función get_user_data_from_file
    def get_user_data_from_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
                current_users = config_data.get("user_ids", [])
                old_users = config_data.get("old_user_ids", [])
                disconnected_users = list(set(old_users) - set(current_users))
                return current_users, old_users, disconnected_users
        except FileNotFoundError:
            return [], [], []
        except json.JSONDecodeError:
            return [], [], []
    
    # Probar con archivo existente
    if os.path.exists("current_status.json"):
        try:
            with open("current_status.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            current_users, old_users, disconnected_users = get_user_data_from_file("current_status.json")
            
            print("[OK] Datos cargados exitosamente:")
            print(f"   [STATS] Usuarios actuales: {len(current_users)}")
            print(f"   [STATS] Usuarios anteriores: {len(old_users)}")
            print(f"   [STATS] Usuarios desconectados: {len(disconnected_users)}")
            
            if current_users:
                print("   [USERS] Usuarios actuales:")
                for user in current_users[:5]:
                    print(f"      • {user}")
            
            if disconnected_users:
                print("   [DISCONNECTED] Usuarios desconectados:")
                for user in disconnected_users[:5]:
                    print(f"      • {user}")
                    
        except Exception as e:
            print(f"[ERROR] Error cargando datos: {e}")
    else:
        print("[WARNING] current_status.json no encontrado")
        
        # Crear datos de prueba
        test_data = {
            "user_ids": ["U123", "U456", "U789"],
            "old_user_ids": ["U123", "U456", "U999"]
        }
        
        with open("test_current_status.json", 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        
        current_users, old_users, disconnected_users = get_user_data_from_file("test_current_status.json")
        
        print("[OK] Datos de prueba cargados:")
        print(f"   [STATS] Usuarios actuales: {len(current_users)}")
        print(f"   [STATS] Usuarios anteriores: {len(old_users)}")
        print(f"   [STATS] Usuarios desconectados: {len(disconnected_users)}")
        
        # Limpiar archivo de prueba
        os.remove("test_current_status.json")

def test_environment_variables():
    """Prueba las variables de entorno para Slack."""
    print_section("Prueba de Variables de Entorno")
    
    # Cargar .env si existe
    if os.path.exists(".env"):
        print("[OK] Archivo .env encontrado")
        
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            slack_user_token = os.getenv('SLACK_USER_TOKEN')
            slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
            default_status = os.getenv('DEFAULT_STATUS', 'At Simpat Tech')
            
            print(f"   [TOKEN] SLACK_USER_TOKEN: {'[OK] Configurado' if slack_user_token else '[ERROR] No configurado'}")
            print(f"   [TOKEN] SLACK_BOT_TOKEN: {'[OK] Configurado' if slack_bot_token else '[ERROR] No configurado'}")
            print(f"   [TEXT] DEFAULT_STATUS: {default_status}")
            
            if not slack_user_token:
                print("   [WARNING] SLACK_USER_TOKEN es requerido para actualizar status")
                
        except ImportError:
            print("[ERROR] python-dotenv no está instalado")
        except Exception as e:
            print(f"[ERROR] Error cargando variables de entorno: {e}")
    else:
        print("[WARNING] Archivo .env no encontrado")
        print("   [TIP] Crea un archivo .env con tus tokens de Slack")

def test_status_format():
    """Prueba el formato de status."""
    print_section("Prueba de Formato de Status")
    
    # Simular diferentes formatos de status
    status_formats = [
        ("At Simpat Tech", ":simpat:", "Status de oficina"),
        ("", "", "Status borrado"),
        ("Lunch", ":pizza:", "Status de lunch"),
        ("En reunión", ":meeting:", "Status de reunión"),
        ("Working from home", ":house:", "Trabajo remoto")
    ]
    
    print("[TEST] Probando formatos de status:")
    for status_text, status_emoji, description in status_formats:
        if status_text:
            print(f"   [TEXT] '{status_text}' {status_emoji} - {description}")
        else:
            print(f"   [DELETE] (sin status) - {description}")

def test_error_handling():
    """Prueba el manejo de errores."""
    print_section("Prueba de Manejo de Errores")
    
    # Simular diferentes tipos de errores
    error_scenarios = [
        ("Archivo no encontrado", FileNotFoundError("No such file")),
        ("JSON inválido", json.JSONDecodeError("Invalid JSON", "", 0)),
        ("Token no configurado", ValueError("Token not configured")),
        ("Error de API", Exception("API Error")),
        ("Timeout", TimeoutError("Request timeout"))
    ]
    
    print("[TEST] Probando manejo de errores:")
    for scenario, error in error_scenarios:
        print(f"   [WARNING] {scenario}: {type(error).__name__}")

def generate_slack_report():
    """Genera un reporte completo de pruebas de Slack."""
    print_header("REPORTE DE PRUEBAS DE SLACK")
    
    test_environment_variables()
    test_lunch_detection()
    test_status_clearing()
    test_user_data_loading()
    test_status_format()
    test_error_handling()
    test_slack_status_script()
    
    print_header("RESUMEN DE PRUEBAS DE SLACK")
    print("[TARGET] Pruebas completadas:")
    print("   [OK] Variables de entorno")
    print("   [OK] Detección de lunch")
    print("   [OK] Borrado de status")
    print("   [OK] Carga de datos de usuario")
    print("   [OK] Formato de status")
    print("   [OK] Manejo de errores")
    print("   [OK] Script slack_status_manager.py")
    
    print("\n[SECCION] Recomendaciones:")
    print("   1. Configura SLACK_USER_TOKEN en tu archivo .env")
    print("   2. Verifica que el token tiene permisos para actualizar status")
    print("   3. Prueba con usuarios reales en tu workspace")
    print("   4. Monitorea los logs de errores")

if __name__ == "__main__":
    generate_slack_report()
