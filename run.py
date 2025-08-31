#!/usr/bin/env python3
"""
Script de conveniencia para ejecutar el sistema completo desde la raíz del proyecto.
"""

import sys
import os

# Agregar la carpeta scripts al path
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, scripts_dir)

# Importar y ejecutar el script principal
if __name__ == "__main__":
    try:
        from main import main
        main()
    except ImportError as e:
        print(f"Error importando el script principal: {e}")
        print("Asegúrate de que el archivo scripts/main.py existe")
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando el sistema: {e}")
        sys.exit(1)
