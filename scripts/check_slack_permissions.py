#!/usr/bin/env python3
"""
Script para verificar los permisos del token de Slack.
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

def check_slack_permissions():
    """Verifica los permisos del token de Slack."""
    
    # Obtener token
    token = os.getenv('SLACK_USER_TOKEN')
    if not token:
        logger.error("❌ SLACK_USER_TOKEN no encontrado en .env")
        return False
    
    logger.info("🔍 Verificando permisos del token de Slack...")
    
    try:
        # Crear cliente
        client = WebClient(token=token)
        
        # Verificar autenticación
        logger.info("📡 Probando conexión con Slack API...")
        auth_test = client.auth_test()
        logger.info(f"✅ Conectado como: {auth_test['user']} en {auth_test['team']}")
        
        # Verificar permisos específicos
        logger.info("🔐 Verificando permisos...")
        
        # Listar usuarios para verificar users:read
        try:
            users_response = client.users_list(limit=1)
            logger.info("✅ Permiso 'users:read' - OK")
        except SlackApiError as e:
            logger.error(f"❌ Permiso 'users:read' - FALLO: {e}")
            return False
        
        # Intentar leer perfil de usuario para verificar users.profile:read
        try:
            profile_response = client.users_profile_get(user=auth_test['user_id'])
            logger.info("✅ Permiso 'users.profile:read' - OK")
        except SlackApiError as e:
            logger.error(f"❌ Permiso 'users.profile:read' - FALLO: {e}")
            return False
        
        # Intentar actualizar perfil para verificar users.profile:write
        try:
            current_status = profile_response['profile'].get('status_text', '')
            current_emoji = profile_response['profile'].get('status_emoji', '')
            
            # Restaurar estado original después de la prueba
            client.users_profile_set(
                user=auth_test['user_id'],
                profile={
                    'status_text': current_status,
                    'status_emoji': current_emoji
                }
            )
            logger.info("✅ Permiso 'users.profile:write' - OK")
        except SlackApiError as e:
            logger.error(f"❌ Permiso 'users.profile:write' - FALLO: {e}")
            return False
        
        logger.info("🎉 Todos los permisos requeridos están configurados correctamente!")
        return True
        
    except SlackApiError as e:
        logger.error(f"❌ Error de Slack API: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal."""
    logger.info("=" * 60)
    logger.info("VERIFICADOR DE PERMISOS DE SLACK")
    logger.info("=" * 60)
    
    success = check_slack_permissions()
    
    if success:
        logger.info("✅ Verificación completada exitosamente")
        sys.exit(0)
    else:
        logger.error("❌ Verificación falló")
        logger.info("\n📋 Para solucionar problemas:")
        logger.info("1. Ve a https://api.slack.com/apps")
        logger.info("2. Selecciona tu app")
        logger.info("3. Ve a 'OAuth & Permissions'")
        logger.info("4. En 'User Token Scopes', agrega:")
        logger.info("   - users:read")
        logger.info("   - users.profile:read")
        logger.info("   - users.profile:write")
        logger.info("5. Reinstala la app en tu workspace")
        logger.info("6. Copia el nuevo User OAuth Token")
        logger.info("7. Actualiza tu archivo .env")
        sys.exit(1)

if __name__ == "__main__":
    main()
