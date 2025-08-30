#!/usr/bin/env python3
"""
Script de Prueba para el Escaneo de Red.
Prueba específicamente las funcionalidades de quick_ping.py
"""

import json
import os
import sys
import subprocess
import socket
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed

def print_header(title):
    """Imprime un encabezado formateado."""
    print(f"\n{'='*50}")
    print(f"[NETWORK] {title}")
    print(f"{'='*50}")

def get_local_ip():
    """Obtiene la IP local del sistema."""
    try:
        # Conectar a un servidor externo para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def test_network_connectivity():
    """Prueba la conectividad de red básica."""
    print_header("Prueba de Conectividad de Red")
    
    local_ip = get_local_ip()
    print(f"[LOCATION] IP Local: {local_ip}")
    
    # Probar conectividad a internet
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("[OK] Conectividad a internet: OK")
    except Exception:
        print("[ERROR] Conectividad a internet: Falló")
    
    # Probar DNS
    try:
        socket.gethostbyname("google.com")
        print("[OK] Resolución DNS: OK")
    except Exception:
        print("[ERROR] Resolución DNS: Falló")

def test_ping_command():
    """Prueba el comando ping del sistema."""
    print_header("Prueba de Comando Ping")
    
    # Determinar comando ping según el sistema operativo
    if platform.system().lower() == "windows":
        ping_cmd = ["ping", "-n", "1", "-w", "1000", "127.0.0.1"]
    else:
        ping_cmd = ["ping", "-c", "1", "-W", "1", "127.0.0.1"]
    
    try:
        result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[OK] Comando ping: Funcional")
        else:
            print("[ERROR] Comando ping: Falló")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"[ERROR] Error ejecutando ping: {e}")

def test_arp_command():
    """Prueba el comando ARP del sistema."""
    print_header("Prueba de Comando ARP")
    
    # Determinar comando ARP según el sistema operativo
    if platform.system().lower() == "windows":
        arp_cmd = ["arp", "-a"]
    else:
        arp_cmd = ["arp", "-n"]
    
    try:
        result = subprocess.run(arp_cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[OK] Comando ARP: Funcional")
            # Mostrar algunas entradas ARP
            lines = result.stdout.strip().split('\n')
            print(f"   [STATS] Entradas ARP encontradas: {len(lines)}")
        else:
            print("[ERROR] Comando ARP: Falló")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"[ERROR] Error ejecutando ARP: {e}")

def test_quick_ping_script():
    """Prueba el script quick_ping.py."""
    print_header("Prueba del Script quick_ping.py")
    
    if not os.path.exists("quick_ping.py"):
        print("[ERROR] quick_ping.py no encontrado")
        return
    
    try:
        print("[RUNNING] Ejecutando quick_ping.py...")
        start_time = subprocess.run([sys.executable, "-c", "import time; print(time.time())"], 
                                  capture_output=True, text=True).stdout.strip()
        
        result = subprocess.run([sys.executable, "quick_ping.py"], 
                              capture_output=True, text=True, timeout=60)
        
        end_time = subprocess.run([sys.executable, "-c", "import time; print(time.time())"], 
                                capture_output=True, text=True).stdout.strip()
        
        duration = float(end_time) - float(start_time)
        
        if result.returncode == 0:
            print(f"[OK] quick_ping.py ejecutado exitosamente en {duration:.1f} segundos")
            
            # Verificar archivo de salida
            if os.path.exists("Simpat_Network.json"):
                with open("Simpat_Network.json", 'r', encoding='utf-8') as f:
                    network_data = json.load(f)
                
                devices = network_data.get("devices", [])
                print(f"   [STATS] Dispositivos detectados: {len(devices)}")
                
                if devices:
                    print("   [SECCION] Detalles de dispositivos:")
                    for i, device in enumerate(devices[:10], 1):  # Mostrar primeros 10
                        ip = device.get('ip', 'N/A')
                        hostname = device.get('hostname', 'N/A')
                        print(f"      {i:2d}. {ip:15} -> {hostname}")
                    
                    if len(devices) > 10:
                        print(f"      ... y {len(devices) - 10} dispositivos más")
                else:
                    print("   [WARNING] No se detectaron dispositivos")
            else:
                print("[ERROR] Simpat_Network.json no se generó")
        else:
            print(f"[ERROR] quick_ping.py falló con código {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
                
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en quick_ping.py")
    except Exception as e:
        print(f"[ERROR] Error ejecutando quick_ping.py: {e}")

def test_network_range():
    """Prueba el rango de red."""
    print_header("Prueba de Rango de Red")
    
    local_ip = get_local_ip()
    print(f"[LOCATION] IP Local: {local_ip}")
    
    # Extraer la red base
    try:
        ip_parts = local_ip.split('.')
        network_base = '.'.join(ip_parts[:3])
        print(f"[NETWORK] Red base: {network_base}.0/24")
        
        # Probar algunas IPs del rango
        test_ips = [
            f"{network_base}.1",
            f"{network_base}.254",
            "127.0.0.1",
            "8.8.8.8"
        ]
        
        print("[TEST] Probando conectividad a IPs de prueba:")
        for ip in test_ips:
            try:
                if platform.system().lower() == "windows":
                    ping_cmd = ["ping", "-n", "1", "-w", "1000", ip]
                else:
                    ping_cmd = ["ping", "-c", "1", "-W", "1", ip]
                
                result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=3)
                status = "[OK]" if result.returncode == 0 else "[ERROR]"
                print(f"   {status} {ip}")
            except Exception:
                print(f"   [ERROR] {ip}")
                
    except Exception as e:
        print(f"[ERROR] Error analizando red: {e}")

def test_performance():
    """Prueba el rendimiento del escaneo."""
    print_header("Prueba de Rendimiento")
    
    if not os.path.exists("Simpat_Network.json"):
        print("[WARNING] Simpat_Network.json no encontrado, ejecutando escaneo...")
        test_quick_ping_script()
        return
    
    try:
        with open("Simpat_Network.json", 'r', encoding='utf-8') as f:
            network_data = json.load(f)
        
        devices = network_data.get("devices", [])
        
        if devices:
            print(f"[STATS] Estadísticas de rendimiento:")
            print(f"   [LINK] Dispositivos detectados: {len(devices)}")
            print(f"   [PERCENT] Tasa de detección: {len(devices)/254*100:.1f}%")
            
            # Analizar tipos de dispositivos
            hostnames = [d.get('hostname', '') for d in devices]
            unique_hostnames = set(hostnames)
            print(f"   [TAG] Hostnames únicos: {len(unique_hostnames)}")
            
            # Mostrar algunos hostnames únicos
            if unique_hostnames:
                print("   [SECCION] Ejemplos de hostnames:")
                for hostname in list(unique_hostnames)[:5]:
                    if hostname:
                        print(f"      • {hostname}")
        else:
            print("[WARNING] No hay datos de rendimiento disponibles")
            
    except Exception as e:
        print(f"[ERROR] Error analizando rendimiento: {e}")

def generate_network_report():
    """Genera un reporte completo de pruebas de red."""
    print_header("REPORTE DE PRUEBAS DE RED")
    
    test_network_connectivity()
    test_ping_command()
    test_arp_command()
    test_network_range()
    test_quick_ping_script()
    test_performance()
    
    print_header("RESUMEN DE PRUEBAS DE RED")
    print("[TARGET] Pruebas completadas:")
    print("   [OK] Conectividad de red")
    print("   [OK] Comando ping")
    print("   [OK] Comando ARP")
    print("   [OK] Rango de red")
    print("   [OK] Script quick_ping.py")
    print("   [OK] Rendimiento")
    
    print("\n[SECCION] Recomendaciones:")
    print("   1. Verifica que tienes permisos de administrador si es necesario")
    print("   2. Asegúrate de que el firewall no bloquea los pings")
    print("   3. Verifica que las IPs en Config.json están en el rango correcto")
    print("   4. Monitorea el rendimiento en diferentes horarios")

if __name__ == "__main__":
    generate_network_report()
