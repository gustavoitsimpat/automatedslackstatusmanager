#!/usr/bin/env python3
"""
Gestor de estados de Slack - Ejecuta operaciones según instrucciones recibidas.
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Optional
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
        logging.FileHandler('logs/slack_status_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
SLACK_USER_TOKEN = os.getenv('SLACK_USER_TOKEN')
CONFIG_FILE = os.getenv('CONFIG_FILE', 'config/Config.json')
CURRENT_STATUS_FILE = os.getenv('CURRENT_STATUS_FILE', 'config/current_status.json')
DEFAULT_STATUS = os.getenv('DEFAULT_STATUS', 'At Simpat Tech Office')
STATUS_EMOJI = os.getenv('STATUS_EMOJI', ':simpat:')

class SlackStatusManager:
    def __init__(self):
        if not SLACK_USER_TOKEN:
            raise ValueError("SLACK_USER_TOKEN no configurado en .env")
        
        self.client = WebClient(token=SLACK_USER_TOKEN)
        logger.info("Cliente de Slack inicializado")
    
    def get_user_current_status(self, user_id: str) -> Optional[Dict]:
        """Obtiene el estado actual de un usuario en Slack."""
        try:
            response = self.client.users_profile_get(user=user_id)
            profile = response['profile']
            return {
                'status_text': profile.get('status_text', ''),
                'status_emoji': profile.get('status_emoji', '')
            }
        except SlackApiError as e:
            logger.error(f"Error obteniendo estado de usuario {user_id}: {e}")
            return None
    
    def set_user_status(self, user_id: str, status_text: str, status_emoji: str = STATUS_EMOJI) -> bool:
        """Establece el estado de un usuario en Slack."""
        try:
            self.client.users_profile_set(
                user=user_id,
                profile={
                    'status_text': status_text,
                    'status_emoji': status_emoji
                }
            )
            logger.info(f"Estado establecido para {user_id}: {status_text}")
            return True
        except SlackApiError as e:
            logger.error(f"Error estableciendo estado para {user_id}: {e}")
            return False
    
    def clear_user_status(self, user_id: str) -> bool:
        """Borra el estado de un usuario en Slack."""
        try:
            self.client.users_profile_set(
                user=user_id,
                profile={
                    'status_text': '',
                    'status_emoji': ''
                }
            )
            logger.info(f"Estado borrado para {user_id}")
            return True
        except SlackApiError as e:
            logger.error(f"Error borrando estado para {user_id}: {e}")
            return False
    
    def execute_instructions(self, instructions: List[Dict]) -> Dict:
        """Ejecuta las instrucciones recibidas para cada usuario."""
        results = {
            'success': [],
            'failed': [],
            'skipped': []
        }
        
        for instruction in instructions:
            user_id = instruction['user_id']
            action = instruction['action']
            
            try:
                if action == 'set_status':
                    success = self.set_user_status(user_id, DEFAULT_STATUS, STATUS_EMOJI)
                    if success:
                        results['success'].append(f"{user_id}: Estado establecido")
                    else:
                        results['failed'].append(f"{user_id}: Error estableciendo estado")
                
                elif action == 'clear_status':
                    success = self.clear_user_status(user_id)
                    if success:
                        results['success'].append(f"{user_id}: Estado borrado")
                    else:
                        results['failed'].append(f"{user_id}: Error borrando estado")
                
                elif action == 'skip':
                    results['skipped'].append(f"{user_id}: Saltado (lunch)")
                
                else:
                    logger.warning(f"Acción desconocida para {user_id}: {action}")
                    results['failed'].append(f"{user_id}: Acción desconocida")
                    
            except Exception as e:
                logger.error(f"Error procesando {user_id}: {e}")
                results['failed'].append(f"{user_id}: Error inesperado")
        
        return results

def main():
    """Función principal que ejecuta las instrucciones recibidas."""
    try:
        # Verificar que se recibieron instrucciones
        if len(sys.argv) < 2:
            logger.error("No se recibieron instrucciones")
            logger.info("Uso: python slack_status_manager.py <instrucciones_json>")
            sys.exit(1)
        
        # Cargar instrucciones desde argumento
        instructions_json = sys.argv[1]
        instructions = json.loads(instructions_json)
        
        logger.info(f"Ejecutando {len(instructions)} instrucciones")
        
        # Inicializar gestor de Slack
        slack_manager = SlackStatusManager()
        
        # Ejecutar instrucciones
        results = slack_manager.execute_instructions(instructions)
        
        # Mostrar resultados
        logger.info("=" * 50)
        logger.info("RESULTADOS DE LA EJECUCIÓN")
        logger.info("=" * 50)
        logger.info(f"✅ Exitosos: {len(results['success'])}")
        logger.info(f"❌ Fallidos: {len(results['failed'])}")
        logger.info(f"⏭️ Saltados: {len(results['skipped'])}")
        
        if results['success']:
            logger.info("\n✅ Operaciones exitosas:")
            for success in results['success']:
                logger.info(f"  - {success}")
        
        if results['failed']:
            logger.info("\n❌ Operaciones fallidas:")
            for failed in results['failed']:
                logger.info(f"  - {failed}")
        
        if results['skipped']:
            logger.info("\n⏭️ Operaciones saltadas:")
            for skipped in results['skipped']:
                logger.info(f"  - {skipped}")
        
        # Retornar código de salida apropiado
        if results['failed']:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except json.JSONDecodeError as e:
        logger.error(f"Error decodificando instrucciones JSON: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()