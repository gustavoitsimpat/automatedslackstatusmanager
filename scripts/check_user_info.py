#!/usr/bin/env python3
"""
Script para verificar información de usuarios específicos.
"""

import os
import sys
import logging
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
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_user_info(user_id: str):
    """Verifica información de un usuario específico."""
    
    token = os.getenv('SLACK_USER_TOKEN')
    if not token:
        logger.error("❌ SLACK_USER_TOKEN no encontrado en .env")
        return
    
    try:
        client = WebClient(token=token)
        
        logger.info(f"🔍 Verificando información del usuario: {user_id}")
        
        # Obtener información del usuario
        user_info = client.users_info(user=user_id)
        user = user_info['user']
        
        logger.info("=" * 60)
        logger.info("INFORMACIÓN DEL USUARIO")
        logger.info("=" * 60)
        logger.info(f"ID: {user['id']}")
        logger.info(f"Nombre: {user.get('name', 'N/A')}")
        logger.info(f"Nombre real: {user.get('real_name', 'N/A')}")
        logger.info(f"Email: {user.get('profile', {}).get('email', 'N/A')}")
        logger.info(f"Es bot: {user.get('is_bot', False)}")
        logger.info(f"Es admin: {user.get('is_admin', False)}")
        logger.info(f"Es owner: {user.get('is_owner', False)}")
        logger.info(f"Es primary owner: {user.get('is_primary_owner', False)}")
        logger.info(f"Es restricted: {user.get('is_restricted', False)}")
        logger.info(f"Es ultra restricted: {user.get('is_ultra_restricted', False)}")
        logger.info(f"Es deleted: {user.get('deleted', False)}")
        
        # Verificar estado actual
        try:
            profile = client.users_profile_get(user=user_id)
            current_status = profile['profile'].get('status_text', '')
            current_emoji = profile['profile'].get('status_emoji', '')
            logger.info(f"Estado actual: {current_status} {current_emoji}")
        except SlackApiError as e:
            logger.error(f"Error obteniendo estado: {e}")
        
        # Intentar actualizar estado
        logger.info("\n🧪 Probando actualización de estado...")
        try:
            client.users_profile_set(
                user=user_id,
                profile={
                    'status_text': 'Test Status',
                    'status_emoji': ':test:'
                }
            )
            logger.info("✅ Actualización exitosa")
            
            # Restaurar estado original
            client.users_profile_set(
                user=user_id,
                profile={
                    'status_text': current_status,
                    'status_emoji': current_emoji
                }
            )
            logger.info("✅ Estado restaurado")
            
        except SlackApiError as e:
            logger.error(f"❌ Error actualizando estado: {e}")
            if e.response['error'] == 'cannot_update_admin_user':
                logger.warning("⚠️ Este usuario es administrador y no se puede actualizar su estado")
                logger.info("💡 Soluciones posibles:")
                logger.info("1. El usuario debe actualizar su propio estado")
                logger.info("2. Usar un token con permisos de workspace admin")
                logger.info("3. Excluir usuarios administradores del sistema")
        
    except SlackApiError as e:
        logger.error(f"❌ Error de Slack API: {e}")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")

def main():
    """Función principal."""
    if len(sys.argv) < 2:
        logger.error("Uso: python check_user_info.py <user_id>")
        logger.info("Ejemplo: python check_user_info.py UG39E9SSV")
        sys.exit(1)
    
    user_id = sys.argv[1]
    check_user_info(user_id)

if __name__ == "__main__":
    main()
