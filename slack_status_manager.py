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
            if user_ids:
                print(f"[*] Cargados {len(user_ids)} IDs de usuario.")
            return user_ids
    except FileNotFoundError:
        print(f"[!] Error: El archivo '{file_path}' no fue encontrado.")
        return []
    except json.JSONDecodeError:
        print(f"[!] Error: El archivo '{file_path}' no es un JSON válido.")
        return []

def set_slack_status(client, user_id, status_text, status_emoji):
    """
    Actualiza el estado de Slack de un usuario usando el token de usuario.
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
        print(f"[*] Estado de Slack actualizado para el usuario {user_id}: {status_text} {status_emoji}")
    except SlackApiError as e:
        print(f"[!] Error al actualizar el estado del usuario {user_id}: {e.response['error']}")
    except Exception as e:
        print(f"[!] Ocurrió un error inesperado: {e}")

def validate_tokens():
    """
    Valida que los tokens necesarios estén configurados.
    """
    if not SLACK_USER_TOKEN:
        print("[!] Error: SLACK_USER_TOKEN no está configurado en el archivo .env")
        return False
    
    print("[*] Tokens validados correctamente")
    return True

# --- LÓGICA PRINCIPAL ---

if __name__ == "__main__":
    print("--- Gestor de Status de Slack ---")
    
    # Validar tokens
    if not validate_tokens():
        sys.exit(1)
    
    # Obtener la lista de usuarios del archivo de configuración
    users_to_update = get_user_ids_from_file('current_status.json')
    if not users_to_update:
        print("[!] No se pudo cargar la lista de usuarios.")
        sys.exit(1)

    # Crear una instancia del cliente de Slack usando el token de usuario
    slack_client = WebClient(token=SLACK_USER_TOKEN)

    print(f"[*] Actualizando status para {len(users_to_update)} usuarios...")
    print(f"[*] Status: {STATUS_TEXT} {STATUS_EMOJI}")

    # Actualizar status de todos los usuarios
    try:
        for user_id in users_to_update:
            set_slack_status(slack_client, user_id, STATUS_TEXT, STATUS_EMOJI)
        
        print("[*] Proceso completado exitosamente.")
        
    except KeyboardInterrupt:
        print("\n[!] Proceso interrumpido por el usuario.")
    except Exception as e:
        print(f"[!] Error en el proceso principal: {e}")
        sys.exit(1)