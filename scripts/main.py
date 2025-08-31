#!/usr/bin/env python3
"""
Script principal para ejecutar el sistema completo de gestión de estados de Slack.
Ejecuta en orden: quick_ping.py -> slack_status_manager.py
"""

import subprocess
import sys
import os
import time
import json
import logging
from datetime import datetime
from typing import Tuple, Optional, List, Dict
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
SLACK_USER_TOKEN = os.getenv('SLACK_USER_TOKEN')
CONFIG_FILE = os.getenv('CONFIG_FILE', 'config/Config.json')
CURRENT_STATUS_FILE = os.getenv('CURRENT_STATUS_FILE', 'config/current_status.json')
DEFAULT_STATUS = os.getenv('DEFAULT_STATUS', 'At Simpat Tech Office')

def run_script(script_name: str, description: str) -> Tuple[bool, Optional[str]]:
    """
    Ejecuta un script de Python y retorna el resultado.
    
    Args:
        script_name: Nombre del script a ejecutar
        description: Descripción del script para logging
    
    Returns:
        Tuple[bool, Optional[str]]: (éxito, mensaje de error si falla)
    """
    logger.info(f"Iniciando {description}...")
    
    try:
        # Construir la ruta del script
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        
        # Ejecutar el script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos de timeout
        )
        
        if result.returncode == 0:
            logger.info(f"{description} completado exitosamente")
            if result.stdout:
                logger.debug(f"Salida: {result.stdout}")
            return True, None
        else:
            error_msg = f"Error en {description}: {result.stderr}"
            logger.error(error_msg)
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = f"Timeout en {description} después de 5 minutos"
        logger.error(error_msg)
        return False, error_msg
    except FileNotFoundError:
        error_msg = f"Script no encontrado: {script_name}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error inesperado en {description}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def check_prerequisites() -> bool:
    """
    Verifica que los archivos necesarios existan.
    
    Returns:
        bool: True si todos los archivos existen
    """
    required_files = [
        'config/Config.json',
        'scripts/quick_ping.py',
        'scripts/slack_status_manager.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error("Archivos requeridos no encontrados:")
        for file_path in missing_files:
            logger.error(f"  - {file_path}")
        return False
    
    logger.info("Todos los archivos requeridos encontrados")
    return True

def check_env_file() -> bool:
    """
    Verifica que el archivo .env exista y tenga el token de Slack.
    
    Returns:
        bool: True si el archivo .env es válido
    """
    env_file = '.env'
    
    if not os.path.exists(env_file):
        logger.error(f"Archivo {env_file} no encontrado")
        logger.info("Copia env.minimal o env.example como .env y configura tu token de Slack")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'SLACK_USER_TOKEN' not in content:
            logger.error("SLACK_USER_TOKEN no encontrado en .env")
            return False
            
        if 'xoxp-your-user-token-here' in content:
            logger.error("Debes reemplazar el token de ejemplo en .env con tu token real")
            return False
            
        logger.info("Archivo .env válido")
        return True
        
    except Exception as e:
        logger.error(f"Error leyendo archivo .env: {e}")
        return False

def load_current_status() -> Tuple[List[str], List[str]]:
    """
    Carga el estado actual desde current_status.json.
    
    Returns:
        Tuple[List[str], List[str]]: (user_ids activos, old_user_ids)
    """
    try:
        with open(CURRENT_STATUS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            user_ids = data.get('user_ids', [])
            old_user_ids = data.get('old_user_ids', [])
            logger.info(f"Estado cargado: {len(user_ids)} activos, {len(old_user_ids)} total")
            return user_ids, old_user_ids
    except Exception as e:
        logger.error(f"Error cargando estado actual: {e}")
        return [], []

def get_user_current_status(client: WebClient, user_id: str) -> Optional[Dict]:
    """
    Obtiene el estado actual de un usuario en Slack.
    
    Returns:
        Optional[Dict]: Estado actual o None si hay error
    """
    try:
        response = client.users_profile_get(user=user_id)
        profile = response['profile']
        return {
            'status_text': profile.get('status_text', ''),
            'status_emoji': profile.get('status_emoji', '')
        }
    except SlackApiError as e:
        logger.error(f"Error obteniendo estado de usuario {user_id}: {e}")
        return None

def is_user_on_lunch(status_text: str) -> bool:
    """
    Verifica si el usuario está en status de lunch.
    
    Args:
        status_text: Texto del status actual
    
    Returns:
        bool: True si está en lunch
    """
    if not status_text:
        return False
    
    # Verificar si el texto contiene indicadores de lunch
    lunch_indicators = ['lunch', 'almuerzo', 'comida', 'break']
    status_lower = status_text.lower()
    
    for indicator in lunch_indicators:
        if indicator in status_lower:
            return True
    
    return False

def generate_instructions(user_ids: List[str], old_user_ids: List[str]) -> List[Dict]:
    """
    Genera las instrucciones para slack_status_manager.py basándose en la lógica requerida.
    
    Args:
        user_ids: Lista de usuarios activos
        old_user_ids: Lista de todos los usuarios (activos + inactivos)
    
    Returns:
        List[Dict]: Lista de instrucciones para cada usuario
    """
    if not SLACK_USER_TOKEN:
        logger.error("SLACK_USER_TOKEN no configurado")
        return []
    
    try:
        client = WebClient(token=SLACK_USER_TOKEN)
        logger.info("Cliente de Slack inicializado para análisis")
    except Exception as e:
        logger.error(f"Error inicializando cliente de Slack: {e}")
        return []
    
    instructions = []
    
    # Procesar usuarios activos
    logger.info(f"Analizando {len(user_ids)} usuarios activos")
    for user_id in user_ids:
        current_status = get_user_current_status(client, user_id)
        
        if current_status is None:
            logger.warning(f"No se pudo obtener estado de {user_id}, saltando")
            continue
        
        status_text = current_status['status_text']
        
        # Verificar si está en lunch
        if is_user_on_lunch(status_text):
            logger.info(f"Usuario {user_id} está en lunch, saltando")
            instructions.append({
                'user_id': user_id,
                'action': 'skip',
                'reason': 'lunch'
            })
            continue
        
        # Verificar si ya tiene el status correcto
        if status_text == DEFAULT_STATUS:
            logger.info(f"Usuario {user_id} ya tiene el status correcto")
            continue
        
        # Cambiar status a "At Simpat Tech Office"
        logger.info(f"Usuario {user_id} necesita cambio de status")
        instructions.append({
            'user_id': user_id,
            'action': 'set_status',
            'reason': 'active_user'
        })
    
    # Procesar usuarios desconectados (en old_user_ids pero no en user_ids)
    disconnected_users = list(set(old_user_ids) - set(user_ids))
    logger.info(f"Analizando {len(disconnected_users)} usuarios desconectados")
    
    for user_id in disconnected_users:
        current_status = get_user_current_status(client, user_id)
        
        if current_status is None:
            logger.warning(f"No se pudo obtener estado de {user_id}, saltando")
            continue
        
        status_text = current_status['status_text']
        
        # Verificar si está en lunch
        if is_user_on_lunch(status_text):
            logger.info(f"Usuario {user_id} está en lunch, saltando")
            instructions.append({
                'user_id': user_id,
                'action': 'skip',
                'reason': 'lunch'
            })
            continue
        
        # Verificar si ya no tiene status
        if not status_text:
            logger.info(f"Usuario {user_id} ya no tiene status")
            continue
        
        # Borrar status
        logger.info(f"Usuario {user_id} necesita borrar status")
        instructions.append({
            'user_id': user_id,
            'action': 'clear_status',
            'reason': 'disconnected_user'
        })
    
    logger.info(f"Generadas {len(instructions)} instrucciones")
    return instructions

def run_slack_status_manager(instructions: List[Dict]) -> bool:
    """
    Ejecuta slack_status_manager.py con las instrucciones generadas.
    
    Args:
        instructions: Lista de instrucciones a ejecutar
    
    Returns:
        bool: True si se ejecutó correctamente
    """
    if not instructions:
        logger.info("No hay instrucciones para ejecutar")
        return True
    
    try:
        # Convertir instrucciones a JSON
        instructions_json = json.dumps(instructions)
        
        # Construir comando
        script_path = os.path.join(os.path.dirname(__file__), 'slack_status_manager.py')
        cmd = [sys.executable, script_path, instructions_json]
        
        # Ejecutar
        logger.info("Ejecutando slack_status_manager.py con instrucciones")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info("slack_status_manager.py completado exitosamente")
            if result.stdout:
                logger.info(result.stdout)
            return True
        else:
            logger.error(f"Error en slack_status_manager.py: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout en slack_status_manager.py")
        return False
    except Exception as e:
        logger.error(f"Error ejecutando slack_status_manager.py: {e}")
        return False

def main():
    """
    Función principal que ejecuta el flujo completo.
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("INICIANDO SISTEMA DE GESTIÓN DE ESTADOS DE SLACK")
    logger.info("=" * 60)
    
    # Verificar prerrequisitos
    logger.info("Verificando prerrequisitos...")
    if not check_prerequisites():
        logger.error("Prerrequisitos no cumplidos, abortando")
        sys.exit(1)
    
    if not check_env_file():
        logger.error("Configuración de entorno inválida, abortando")
        sys.exit(1)
    
    # Ejecutar quick_ping.py
    logger.info("-" * 40)
    success, error = run_script('quick_ping.py', 'Escaneo de red')
    if not success:
        logger.error(f"Falló el escaneo de red: {error}")
        logger.error("Abortando ejecución")
        sys.exit(1)
    
    # Pequeña pausa entre scripts
    time.sleep(2)
    
    # Cargar estado actual
    logger.info("-" * 40)
    user_ids, old_user_ids = load_current_status()
    if not user_ids and not old_user_ids:
        logger.warning("No se pudo cargar el estado actual")
        sys.exit(1)
    
    # Generar instrucciones
    logger.info("-" * 40)
    instructions = generate_instructions(user_ids, old_user_ids)
    
    # Ejecutar slack_status_manager.py
    logger.info("-" * 40)
    success = run_slack_status_manager(instructions)
    if not success:
        logger.error("Falló la gestión de estados de Slack")
        sys.exit(1)
    
    # Resumen final
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info("=" * 60)
    logger.info("SISTEMA COMPLETADO")
    logger.info(f"Tiempo total de ejecución: {duration:.2f} segundos")
    logger.info(f"Instrucciones procesadas: {len(instructions)}")
    logger.info("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Ejecución interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error crítico en el script principal: {e}")
        sys.exit(1)
