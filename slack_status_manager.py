#!/usr/bin/env python3
"""
Gestor de Status de Slack usando variables de entorno.
Actualiza el status de usuarios basado en presencia en la oficina.
"""

import sys
import json
import time
import os
import logging
from typing import Dict, List, Optional, Tuple
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Configurar logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slack_status_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# --- CONFIGURACIÓN ---
# Obtener tokens desde variables de entorno
SLACK_USER_TOKEN = os.getenv('SLACK_USER_TOKEN')

# El mensaje de estado y el emoji que se establecerán
STATUS_TEXT = os.getenv('DEFAULT_STATUS', 'At Simpat Tech')
STATUS_EMOJI = ":simpat:"
AWAY_STATUS_TEXT = os.getenv('AWAY_STATUS', 'Away')
AWAY_STATUS_EMOJI = ":afk:"

class ConfigValidator:
    """Validador de configuración para Slack."""
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """Valida que el token de Slack esté configurado."""
        return bool(token and len(token) > 0)
    
    @staticmethod
    def validate_user_data(user_data: Dict) -> Tuple[bool, List[str]]:
        """Valida los datos de usuario cargados."""
        errors = []
        
        if not isinstance(user_data, dict):
            errors.append("current_status.json debe ser un objeto JSON válido")
            return False, errors
        
        required_keys = ["user_ids", "old_user_ids"]
        for key in required_keys:
            if key not in user_data:
                errors.append(f"Falta campo requerido: {key}")
            elif not isinstance(user_data[key], list):
                errors.append(f"Campo {key} debe ser una lista")
        
        return len(errors) == 0, errors

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """
    Ejecuta una función con retry y backoff exponencial.
    
    Args:
        func: Función a ejecutar
        max_retries: Número máximo de reintentos
        base_delay: Delay base en segundos
    
    Returns:
        Resultado de la función o None si falla después de todos los reintentos
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"Función falló después de {max_retries} reintentos: {e}")
                return None
            
            delay = base_delay * (2 ** attempt)  # 1, 2, 4 segundos
            logger.warning(f"Intento {attempt + 1} falló, reintentando en {delay}s: {e}")
            time.sleep(delay)
    
    return None

# --- FUNCIONES ---

def get_user_data_from_file(file_path: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Lee y carga los datos de usuario desde un archivo JSON local.
    Retorna (current_users, old_users, disconnected_users)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
            
            # Validar datos
            is_valid, errors = ConfigValidator.validate_user_data(config_data)
            if not is_valid:
                logger.error("Errores en datos de usuario:")
                for error in errors:
                    logger.error(f"  - {error}")
                return [], [], []
            
            current_users = config_data.get("user_ids", [])
            old_users = config_data.get("old_user_ids", [])
            
            # Detectar usuarios desconectados
            disconnected_users = list(set(old_users) - set(current_users))
            
            logger.info(f"Datos cargados: {len(current_users)} usuarios activos, {len(disconnected_users)} desconectados")
            return current_users, old_users, disconnected_users
            
    except FileNotFoundError:
        logger.error(f"Archivo {file_path} no encontrado")
        return [], [], []
    except json.JSONDecodeError as e:
        logger.error(f"Error de formato JSON en {file_path}: {e}")
        return [], [], []
    except Exception as e:
        logger.error(f"Error inesperado cargando {file_path}: {e}")
        return [], [], []

def get_user_current_status(client: WebClient, user_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Obtiene el status actual de un usuario en Slack.
    Retorna (status_text, status_emoji) o (None, None) si hay error.
    """
    def _get_status():
        try:
            response = client.users_profile_get(user=user_id)
            profile = response['profile']
            status_text = profile.get('status_text', '')
            status_emoji = profile.get('status_emoji', '')
            return status_text, status_emoji
        except SlackApiError as e:
            logger.error(f"Error de API de Slack para usuario {user_id}: {e.response['error']}")
            return None, None
        except Exception as e:
            logger.error(f"Error inesperado obteniendo status de {user_id}: {e}")
            return None, None
    
    return retry_with_backoff(_get_status, max_retries=2, base_delay=1.0) or (None, None)

def is_user_on_lunch(status_text: str, status_emoji: str) -> bool:
    """
    Verifica si el usuario está en status de lunch.
    Retorna True si está en lunch, False en caso contrario.
    """
    if not status_text:
        return False
    
    # Verificar si el texto contiene "lunch" (case insensitive)
    lunch_indicators = ['lunch', 'almuerzo', 'comida', 'break']
    status_lower = status_text.lower()
    
    for indicator in lunch_indicators:
        if indicator in status_lower:
            return True
    
    return False

def set_slack_status(client: WebClient, user_id: str, status_text: str, status_emoji: str) -> Tuple[bool, Optional[str]]:
    """
    Actualiza el estado de Slack de un usuario usando el token de usuario.
    Retorna True si fue exitoso, False si hubo error.
    """
    def _set_status():
        try:
            profile_data = {
                "status_text": status_text,
                "status_emoji": status_emoji
            }
            client.users_profile_set(
                user=user_id,
                profile=json.dumps(profile_data)
            )
            return True, None
        except SlackApiError as e:
            return False, f"Slack API Error: {e.response['error']}"
        except Exception as e:
            return False, f"Unexpected Error: {str(e)}"
    
    return retry_with_backoff(_set_status, max_retries=2, base_delay=1.0) or (False, "Retry failed")

def clear_slack_status(client: WebClient, user_id: str) -> Tuple[bool, Optional[str]]:
    """
    Borra el estado de Slack de un usuario (establece status vacío).
    Retorna True si fue exitoso, False si hubo error.
    """
    def _clear_status():
        try:
            profile_data = {
                "status_text": "",
                "status_emoji": ""
            }
            client.users_profile_set(
                user=user_id,
                profile=json.dumps(profile_data)
            )
            return True, None
        except SlackApiError as e:
            return False, f"Slack API Error: {e.response['error']}"
        except Exception as e:
            return False, f"Unexpected Error: {str(e)}"
    
    return retry_with_backoff(_clear_status, max_retries=2, base_delay=1.0) or (False, "Retry failed")

def validate_tokens() -> bool:
    """
    Valida que los tokens necesarios estén configurados.
    """
    if not ConfigValidator.validate_token(SLACK_USER_TOKEN):
        logger.error("SLACK_USER_TOKEN no está configurado o es inválido")
        return False
    
    logger.info("Tokens de configuración válidos")
    return True

# --- LÓGICA PRINCIPAL ---

if __name__ == "__main__":
    logger.info("Iniciando gestor de status de Slack")
    
    # Validar tokens
    if not validate_tokens():
        logger.error("Configuración de tokens inválida, abortando")
        sys.exit(1)
    
    # Obtener los datos de usuarios del archivo de configuración
    current_users, old_users, disconnected_users = get_user_data_from_file('current_status.json')
    
    # Si no hay usuarios para actualizar, salir
    if not current_users and not disconnected_users:
        logger.info("No hay usuarios para actualizar")
        sys.exit(0)

    # Crear una instancia del cliente de Slack usando el token de usuario
    try:
        slack_client = WebClient(token=SLACK_USER_TOKEN)
        logger.info("Cliente de Slack inicializado")
    except Exception as e:
        logger.error(f"Error inicializando cliente de Slack: {e}")
        sys.exit(1)

    # Contadores para el resumen
    successful_updates = 0
    failed_updates = 0
    skipped_lunch_users = 0
    error_messages = []

    # Actualizar status de usuarios conectados (en la oficina)
    try:
        logger.info(f"Procesando {len(current_users)} usuarios en la oficina")
        for user_id in current_users:
            # Verificar si el usuario está en lunch
            current_status_text, current_status_emoji = get_user_current_status(slack_client, user_id)
            
            if current_status_text is None:
                logger.warning(f"No se pudo obtener status actual de {user_id}")
                continue
            
            if is_user_on_lunch(current_status_text, current_status_emoji):
                logger.info(f"Usuario {user_id} está en lunch, saltando")
                skipped_lunch_users += 1
                continue  # Saltar usuarios en lunch
            
            success, error = set_slack_status(slack_client, user_id, STATUS_TEXT, STATUS_EMOJI)
            if success:
                logger.info(f"Status actualizado para usuario {user_id}")
                successful_updates += 1
            else:
                logger.error(f"Error actualizando status de {user_id}: {error}")
                failed_updates += 1
                error_messages.append(f"User {user_id} (Office): {error}")
        
        # Borrar status de usuarios desconectados
        logger.info(f"Procesando {len(disconnected_users)} usuarios desconectados")
        for user_id in disconnected_users:
            # Verificar si el usuario está en lunch
            current_status_text, current_status_emoji = get_user_current_status(slack_client, user_id)
            
            if current_status_text is None:
                logger.warning(f"No se pudo obtener status actual de {user_id}")
                continue
            
            if is_user_on_lunch(current_status_text, current_status_emoji):
                logger.info(f"Usuario {user_id} está en lunch, saltando")
                skipped_lunch_users += 1
                continue  # Saltar usuarios en lunch
            
            success, error = clear_slack_status(slack_client, user_id)
            if success:
                logger.info(f"Status borrado para usuario {user_id}")
                successful_updates += 1
            else:
                logger.error(f"Error borrando status de {user_id}: {error}")
                failed_updates += 1
                error_messages.append(f"User {user_id} (Clear): {error}")
        
        # Imprimir resumen final
        total_users = len(current_users) + len(disconnected_users)
        print(f"Slack Status Update Summary: {successful_updates} successful, {failed_updates} failed, {skipped_lunch_users} skipped (lunch)")
        print(f"Users in office: {len(current_users)}, Users status cleared: {len(disconnected_users)}")
        if error_messages:
            print(f"Errors: {'; '.join(error_messages[:3])}{'...' if len(error_messages) > 3 else ''}")
        elif successful_updates == 0 and failed_updates == 0 and skipped_lunch_users == 0:
            print("No users to update or token not configured")
        
        logger.info(f"Proceso completado: {successful_updates} exitosos, {failed_updates} fallidos, {skipped_lunch_users} saltados")
        
    except KeyboardInterrupt:
        logger.info("Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error crítico durante la actualización: {e}")
        sys.exit(1)