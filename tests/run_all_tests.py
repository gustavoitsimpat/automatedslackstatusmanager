#!/usr/bin/env python3
"""
Script para Ejecutar Todas las Pruebas del Sistema.
Ejecuta todos los scripts de prueba en secuencia y genera un reporte consolidado.
"""

import subprocess
import sys
import time
from datetime import datetime

def print_header(title):
    """Imprime un encabezado formateado."""
    print(f"\n{'='*70}")
    print(f"[ALL TESTS] {title}")
    print(f"{'='*70}")

def run_test_script(script_name, description):
    """Ejecuta un script de prueba y retorna el resultado."""
    print(f"\n[SECCION] Ejecutando: {script_name}")
    print(f"[TEXT] Descripción: {description}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"[OK] {script_name} completado exitosamente en {duration:.1f}s")
            if result.stdout:
                # Mostrar solo las últimas líneas del output
                lines = result.stdout.strip().split('\n')
                if len(lines) > 10:
                    print("   [STATS] Últimas líneas de salida:")
                    for line in lines[-10:]:
                        print(f"      {line}")
                else:
                    print("   [STATS] Salida:")
                    for line in lines:
                        print(f"      {line}")
            return True, duration, None
        else:
            print(f"[ERROR] {script_name} falló con código {result.returncode}")
            if result.stderr:
                print(f"   [FIX] Error: {result.stderr.strip()}")
            return False, duration, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {script_name} excedió el tiempo límite (5 minutos)")
        return False, 300, "Timeout"
    except Exception as e:
        print(f"[CRASH] {script_name} error: {e}")
        return False, 0, str(e)

def generate_summary_report(results):
    """Genera un reporte resumen de todas las pruebas."""
    print_header("REPORTE FINAL DE PRUEBAS")
    
    total_tests = len(results)
    successful_tests = sum(1 for success, _, _ in results if success)
    total_time = sum(duration for _, duration, _ in results)
    
    print(f"[STATS] Estadísticas Generales:")
    print(f"   [TARGET] Total de pruebas: {total_tests}")
    print(f"   [OK] Pruebas exitosas: {successful_tests}")
    print(f"   [ERROR] Pruebas fallidas: {total_tests - successful_tests}")
    print(f"   [TIMER] Tiempo total: {total_time:.1f} segundos")
    print(f"   [PERCENT] Tasa de éxito: {successful_tests/total_tests*100:.1f}%")
    
    print(f"\n[SECCION] Resultados Detallados:")
    test_names = [
        "test_configuration.py",
        "test_integration.py", 
        "test_network_scan.py",
        "test_slack_status.py",
        "test_complete_system.py"
    ]
    
    for i, (success, duration, error) in enumerate(results):
        status = "[OK]" if success else "[ERROR]"
        test_name = test_names[i] if i < len(test_names) else f"Test {i+1}"
        print(f"   {status} {test_name} ({duration:.1f}s)")
        if not success and error:
            print(f"      [FIX] Error: {error[:100]}{'...' if len(error) > 100 else ''}")
    
    print(f"\n[TARGET] Estado del Sistema:")
    if successful_tests == total_tests:
        print("   [SUCCESS] ¡Todas las pruebas pasaron!")
        print("   El sistema está funcionando correctamente")
    elif successful_tests >= total_tests * 0.8:
        print("   [WARNING] La mayoría de las pruebas pasaron")
        print("   Revisa los errores específicos")
    else:
        print("   [ERROR] Muchas pruebas fallaron")
        print("   Revisa la configuración del sistema")
    
    print(f"\n[SECCION] Próximos Pasos:")
    if successful_tests < total_tests:
        print("   1. Revisa los errores específicos mostrados arriba")
        print("   2. Ejecuta las pruebas individuales para más detalles")
        print("   3. Verifica la configuración según las recomendaciones")
        print("   4. Consulta la documentación de pruebas (README_TESTS.md)")
    else:
        print("   1. El sistema está listo para uso en producción")
        print("   2. Configura la automatización si es necesario")
        print("   3. Monitorea el funcionamiento regularmente")

def main():
    """Función principal que ejecuta todas las pruebas."""
    print_header("EJECUCIÓN COMPLETA DE PRUEBAS DEL SISTEMA")
    print(f"[TIME] Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lista de pruebas a ejecutar
    tests = [
        ("test_configuration.py", "Validación de configuración del sistema"),
        ("test_integration.py", "Pruebas de integración general"),
        ("test_network_scan.py", "Pruebas de escaneo de red"),
        ("test_slack_status.py", "Pruebas de gestión de status de Slack"),
        ("test_complete_system.py", "Pruebas del sistema completo")
    ]
    
    results = []
    
    for script_name, description in tests:
        success, duration, error = run_test_script(script_name, description)
        results.append((success, duration, error))
        
        # Pausa breve entre pruebas
        if script_name != tests[-1][0]:  # No pausar después de la última prueba
            print("   [WAIT] Pausa de 2 segundos...")
            time.sleep(2)
    
    # Generar reporte final
    generate_summary_report(results)
    
    print(f"\n[TIME] Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_header("FIN DE EJECUCIÓN")

if __name__ == "__main__":
    main()
