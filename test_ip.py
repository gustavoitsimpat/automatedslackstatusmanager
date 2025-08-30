#!/usr/bin/env python3
"""
Script de prueba para verificar IP específica.
"""

import subprocess
import platform

def test_ip(ip):
    """Prueba una IP específica."""
    print(f"🔍 Probando IP: {ip}")
    
    # Método 1: Ping
    print("1. Probando con PING...")
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(["ping", "-n", "1", "-w", "2000", ip], 
                                  capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(["ping", "-c", "1", "-W", "3", ip], 
                                  capture_output=True, text=True, timeout=5)
        
        print(f"   Código de retorno: {result.returncode}")
        print(f"   Respuesta: {result.stdout[:200]}...")
        
        if result.returncode == 0:
            print("   ✅ PING EXITOSO")
            return True
        else:
            print("   ❌ PING FALLÓ")
    except Exception as e:
        print(f"   ❌ Error en PING: {e}")
    
    # Método 2: ARP
    print("2. Probando con ARP...")
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(["arp", "-a", ip], 
                                  capture_output=True, text=True, timeout=3)
        else:
            result = subprocess.run(["arp", "-n", ip], 
                                  capture_output=True, text=True, timeout=3)
        
        print(f"   Código de retorno: {result.returncode}")
        print(f"   Respuesta: {result.stdout}")
        
        if ip in result.stdout:
            print("   ✅ ARP ENCONTRÓ LA IP")
            return True
        else:
            print("   ❌ ARP NO ENCONTRÓ LA IP")
    except Exception as e:
        print(f"   ❌ Error en ARP: {e}")
    
    return False

if __name__ == "__main__":
    test_ip("10.0.0.3")
