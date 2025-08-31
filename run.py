#!/usr/bin/env python3
"""
Script de conveniencia para ejecutar el sistema completo desde la raíz del proyecto.
"""

import sys
import os
from pathlib import Path

# Agregar la carpeta scripts al path de manera más robusta
project_root = Path(__file__).parent
scripts_dir = project_root / 'scripts'
sys.path.insert(0, str(scripts_dir))

# Importar y ejecutar el script principal
if __name__ == "__main__":
    try:
        # Importación explícita para mejor compatibilidad con analizadores de tipos
        from scripts.main import main
        main()
    except ImportError as e:
        print(f"Error importando el script principal: {e}")
        print("Asegúrate de que el archivo scripts/main.py existe")
        print(f"Directorio scripts: {scripts_dir}")
        print(f"Archivos en scripts: {list(scripts_dir.glob('*.py'))}")
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando el sistema: {e}")
        sys.exit(1)
