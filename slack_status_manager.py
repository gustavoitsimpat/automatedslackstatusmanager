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

# --- FUNCIONES ---

def get_user_ids_from_file(file_path):
    """
    Lee y carga los IDs de usuario desde un archivo JSON local.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
            user_ids = config_data.get("user_ids", [])
            return user_ids
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

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
    
    # Obtener la lista de usuarios del archivo de configuración
    users_to_update = get_user_ids_from_file('current_status.json')
    if not users_to_update:
        sys.exit(1)

    # Crear una instancia del cliente de Slack usando el token de usuario
    slack_client = WebClient(token=SLACK_USER_TOKEN)

    # Contadores para el resumen
    successful_updates = 0
    failed_updates = 0
    error_messages = []

    # Actualizar status de todos los usuarios
    try:
        for user_id in users_to_update:
            success, error = set_slack_status(slack_client, user_id, STATUS_TEXT, STATUS_EMOJI)
            if success:
                successful_updates += 1
            else:
                failed_updates += 1
                error_messages.append(f"User {user_id}: {error}")
        
        # Imprimir resumen final
        print(f"Slack Status Update Summary: {successful_updates} successful, {failed_updates} failed")
        if error_messages:
            print(f"Errors: {'; '.join(error_messages[:3])}{'...' if len(error_messages) > 3 else ''}")
        elif successful_updates == 0 and failed_updates == 0:
            print("No users to update or token not configured")
        
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)