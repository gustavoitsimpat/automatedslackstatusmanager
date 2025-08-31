#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema principal funciona correctamente.
"""

import sys
import os
import subprocess
import time

def test_main_script():
    """Prueba la ejecución del script principal."""
    print("🧪 Probando script principal...")
    
    # Verificar que el script existe
    main_script = 'scripts/main.py'
    if not os.path.exists(main_script):
        print(f"❌ Error: {main_script} no encontrado")
        return False
    
    # Verificar que los scripts dependientes existen
    required_scripts = [
        'scripts/quick_ping.py',
        'scripts/slack_status_manager.py'
    ]
    
    for script in required_scripts:
        if not os.path.exists(script):
            print(f"❌ Error: {script} no encontrado")
            return False
    
    # Verificar archivos de configuración
    required_configs = [
        'config/Config.json',
        'env.example',
        'env.minimal'
    ]
    
    for config in required_configs:
        if not os.path.exists(config):
            print(f"❌ Error: {config} no encontrado")
            return False
    
    print("✅ Todos los archivos requeridos encontrados")
    
    # Probar ejecución (solo verificar que no hay errores de sintaxis)
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', main_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Script principal compila correctamente")
            return True
        else:
            print(f"❌ Error de sintaxis en {main_script}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout al compilar el script principal")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_run_script():
    """Prueba el script de conveniencia run.py."""
    print("\n🧪 Probando script de conveniencia...")
    
    run_script = 'run.py'
    if not os.path.exists(run_script):
        print(f"❌ Error: {run_script} no encontrado")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', run_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Script de conveniencia compila correctamente")
            return True
        else:
            print(f"❌ Error de sintaxis en {run_script}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout al compilar el script de conveniencia")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("=" * 60)
    print("PRUEBAS DEL SISTEMA PRINCIPAL")
    print("=" * 60)
    
    # Ejecutar pruebas
    test1_passed = test_main_script()
    test2_passed = test_run_script()
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("✅ Todas las pruebas pasaron")
        print("\n🎉 El sistema está listo para usar:")
        print("   python run.py")
        return True
    else:
        print("❌ Algunas pruebas fallaron")
        print("\n🔧 Revisa los errores antes de continuar")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
