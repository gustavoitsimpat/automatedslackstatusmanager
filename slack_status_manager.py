#!/usr/bin/env python3
"""
Gestor de Status de Slack usando variables de entorno.
Actualiza el status de usuarios basado en presencia en la oficina.
"""

import sys
import json
import time
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

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

# --- FUNCIONES ---

def get_user_data_from_file(file_path):
    """
    Lee y carga los datos de usuario desde un archivo JSON local.
    Retorna (current_users, old_users, disconnected_users)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
            current_users = config_data.get("user_ids", [])
            old_users = config_data.get("old_user_ids", [])
            
            # Detectar usuarios desconectados
            disconnected_users = list(set(old_users) - set(current_users))
            
            return current_users, old_users, disconnected_users
    except FileNotFoundError:
        return [], [], []
    except json.JSONDecodeError:
        return [], [], []

def get_user_current_status(client, user_id):
    """
    Obtiene el status actual de un usuario en Slack.
    Retorna (status_text, status_emoji) o (None, None) si hay error.
    """
    try:
        response = client.users_profile_get(user=user_id)
        profile = response['profile']
        status_text = profile.get('status_text', '')
        status_emoji = profile.get('status_emoji', '')
        return status_text, status_emoji
    except SlackApiError as e:
        return None, None
    except Exception as e:
        return None, None

def is_user_on_lunch(status_text, status_emoji):
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

def set_slack_status(client, user_id, status_text, status_emoji):
    """
    Actualiza el estado de Slack de un usuario usando el token de usuario.
    Retorna True si fue exitoso, False si hubo error.
    """
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

def validate_tokens():
    """
    Valida que los tokens necesarios estén configurados.
    """
    if not SLACK_USER_TOKEN:
        return False
    return True

# --- LÓGICA PRINCIPAL ---

if __name__ == "__main__":
    # Validar tokens
    if not validate_tokens():
        sys.exit(1)
    
    # Obtener los datos de usuarios del archivo de configuración
    current_users, old_users, disconnected_users = get_user_data_from_file('current_status.json')
    
    # Si no hay usuarios para actualizar, salir
    if not current_users and not disconnected_users:
        sys.exit(1)

    # Crear una instancia del cliente de Slack usando el token de usuario
    slack_client = WebClient(token=SLACK_USER_TOKEN)

    # Contadores para el resumen
    successful_updates = 0
    failed_updates = 0
    skipped_lunch_users = 0
    error_messages = []

    # Actualizar status de usuarios conectados (en la oficina)
    try:
        for user_id in current_users:
            # Verificar si el usuario está en lunch
            current_status_text, current_status_emoji = get_user_current_status(slack_client, user_id)
            
            if is_user_on_lunch(current_status_text, current_status_emoji):
                skipped_lunch_users += 1
                continue  # Saltar usuarios en lunch
            
            success, error = set_slack_status(slack_client, user_id, STATUS_TEXT, STATUS_EMOJI)
            if success:
                successful_updates += 1
            else:
                failed_updates += 1
                error_messages.append(f"User {user_id} (Office): {error}")
        
        # Actualizar status de usuarios desconectados (Away)
        for user_id in disconnected_users:
            # Verificar si el usuario está en lunch
            current_status_text, current_status_emoji = get_user_current_status(slack_client, user_id)
            
            if is_user_on_lunch(current_status_text, current_status_emoji):
                skipped_lunch_users += 1
                continue  # Saltar usuarios en lunch
            
            success, error = set_slack_status(slack_client, user_id, AWAY_STATUS_TEXT, AWAY_STATUS_EMOJI)
            if success:
                successful_updates += 1
            else:
                failed_updates += 1
                error_messages.append(f"User {user_id} (Away): {error}")
        
        # Imprimir resumen final
        total_users = len(current_users) + len(disconnected_users)
        print(f"Slack Status Update Summary: {successful_updates} successful, {failed_updates} failed, {skipped_lunch_users} skipped (lunch)")
        print(f"Users in office: {len(current_users)}, Users set to away: {len(disconnected_users)}")
        if error_messages:
            print(f"Errors: {'; '.join(error_messages[:3])}{'...' if len(error_messages) > 3 else ''}")
        elif successful_updates == 0 and failed_updates == 0 and skipped_lunch_users == 0:
            print("No users to update or token not configured")
        
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)