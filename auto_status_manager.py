#!/usr/bin/env python3
"""
Gestor Automático de Status de Slack.
Ejecuta el escaneo de red y compara automáticamente con la configuración.
"""

import subprocess
import json
import time
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configurar logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_status_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validador de configuración con validaciones robustas."""
    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        """Valida formato de IP."""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            return all(0 <= int(part) <= 255 for part in parts)
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Valida formato de User ID de Slack."""
        return isinstance(user_id, str) and len(user_id) > 0 and user_id.startswith('U')
    
    @staticmethod
    def validate_config(config_data: Dict) -> Tuple[bool, List[str]]:
        """Valida configuración completa y retorna errores encontrados."""
        errors = []
        
        if not isinstance(config_data, dict):
            errors.append("Config.json debe ser un objeto JSON válido")
            return False, errors
        
        if "users" not in config_data:
            errors.append("Config.json debe contener una sección 'users'")
            return False, errors
        
        if not isinstance(config_data["users"], list):
            errors.append("La sección 'users' debe ser una lista")
            return False, errors
        
        if len(config_data["users"]) == 0:
            errors.append("La lista de usuarios no puede estar vacía")
            return False, errors
        
        # Validar cada usuario
        for i, user in enumerate(config_data["users"]):
            if not isinstance(user, dict):
                errors.append(f"Usuario {i+1}: debe ser un objeto")
                continue
            
            # Validar IP
            if "ip" not in user:
                errors.append(f"Usuario {i+1}: falta campo 'ip'")
            elif not ConfigValidator.validate_ip(user["ip"]):
                errors.append(f"Usuario {i+1}: IP inválida '{user['ip']}'")
            
            # Validar hostname
            if "hostname" not in user or not user["hostname"]:
                errors.append(f"Usuario {i+1}: falta o está vacío el campo 'hostname'")
            
            # Validar userID
            if "userID" not in user:
                errors.append(f"Usuario {i+1}: falta campo 'userID'")
            elif not ConfigValidator.validate_user_id(user["userID"]):
                errors.append(f"Usuario {i+1}: UserID inválido '{user['userID']}'")
        
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

def get_adaptive_timeout() -> int:
    """
    Calcula timeout adaptativo basado en latencia de red.
    
    Returns:
        Timeout en segundos (mínimo 30, máximo 120)
    """
    try:
        # Medir latencia básica con ping a gateway
        start_time = time.time()
        subprocess.run(["ping", "-n", "1", "8.8.8.8"], 
                      capture_output=True, timeout=5)
        latency = time.time() - start_time
        
        # Calcular timeout basado en latencia (más conservador)
        base_timeout = max(30, int(latency * 50))  # Mínimo 30 segundos
        return min(base_timeout, 120)  # Máximo 120 segundos
        
    except Exception as e:
        logger.warning(f"No se pudo medir latencia de red: {e}")
        return 60  # Timeout por defecto más conservador

def run_network_scan():
    """Ejecuta el escaneo de red usando quick_ping.py con timeout adaptativo."""
    timeout = get_adaptive_timeout()
    logger.info(f"Ejecutando escaneo de red con timeout de {timeout}s")
    
    def _run_scan():
        try:
            result = subprocess.run([sys.executable, "quick_ping.py"], 
                                  timeout=timeout, capture_output=True)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error(f"Escaneo de red expiró después de {timeout}s")
            return False
        except Exception as e:
            logger.error(f"Error ejecutando escaneo de red: {e}")
            return False
    
    return retry_with_backoff(_run_scan, max_retries=2, base_delay=2.0)

def run_slack_status_update():
    """Ejecuta la actualización de status de Slack usando slack_status_manager.py."""
    logger.info("Ejecutando actualización de status de Slack")
    
    def _run_slack_update():
        try:
            result = subprocess.run([sys.executable, "slack_status_manager.py"], 
                                  timeout=60, capture_output=True)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error("Actualización de Slack expiró después de 60s")
            return False
        except Exception as e:
            logger.error(f"Error ejecutando actualización de Slack: {e}")
            return False
    
    return retry_with_backoff(_run_slack_update, max_retries=2, base_delay=3.0)

def load_json_file(filename: str) -> Optional[Dict]:
    """Carga un archivo JSON y retorna su contenido con validación."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Archivo {filename} cargado exitosamente")
        return data
    except FileNotFoundError:
        logger.error(f"Archivo {filename} no encontrado")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error de formato JSON en {filename}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado cargando {filename}: {e}")
        return None

def find_users_in_office(network_data: Dict, config_data: Dict) -> List[Dict]:
    """Encuentra usuarios que están en la oficina comparando IPs."""
    if not network_data or not config_data:
        logger.warning("Datos de red o configuración no disponibles")
        return []
    
    # Obtener IPs activas de la red
    active_ips = set()
    if 'devices' in network_data:
        for device in network_data['devices']:
            if 'ip' in device:
                active_ips.add(device['ip'])
    
    logger.info(f"IPs activas encontradas: {len(active_ips)}")
    
    # Buscar usuarios configurados que están activos
    users_in_office = []
    if 'users' in config_data:
        for user in config_data['users']:
            if user.get('ip') in active_ips:
                users_in_office.append({
                    'ip': user['ip'],
                    'hostname': user['hostname'],
                    'status': 'En la Oficina'
                })
    
    logger.info(f"Usuarios en oficina detectados: {len(users_in_office)}")
    return users_in_office

def save_current_status(users_in_office: List[Dict], config_data: Dict, 
                       json_filename: str = "current_status.json", 
                       csv_filename: str = "current_status.csv") -> Tuple[List[str], List[str]]:
    """Guarda el status actual en formato JSON y CSV con historial."""
    # Crear lista de userIDs de usuarios en la oficina
    user_ids = []
    
    if 'users' in config_data:
        for user in config_data['users']:
            # Buscar si el usuario está en la oficina
            is_in_office = any(u['ip'] == user['ip'] for u in users_in_office)
            
            # Solo incluir usuarios que están en la oficina
            if is_in_office:
                user_ids.append(user['userID'])
    
    # Cargar el estado anterior para crear el historial
    old_user_ids = []
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            previous_data = json.load(f)
            # Si el archivo tiene el formato nuevo, usar old_user_ids
            if "old_user_ids" in previous_data:
                old_user_ids = previous_data.get("old_user_ids", [])
            else:
                # Si es el formato antiguo, usar user_ids como old_user_ids
                old_user_ids = previous_data.get("user_ids", [])
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        logger.info(f"No se encontró estado anterior o error al cargar: {e}")
        # Si no existe el archivo o hay error, old_user_ids queda como lista vacía
        pass
    
    # Guardar archivo JSON con formato específico incluyendo historial
    try:
        json_data = {
            "user_ids": user_ids,
            "old_user_ids": old_user_ids
        }
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Estado actual guardado en {json_filename}")
    except Exception as e:
        logger.error(f"Error guardando {json_filename}: {e}")
    
    # Guardar archivo CSV con solo userIDs actuales
    try:
        with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
            for user_id in user_ids:
                f.write(f"{user_id}\n")
        logger.info(f"Estado actual guardado en {csv_filename}")
    except Exception as e:
        logger.error(f"Error guardando {csv_filename}: {e}")
    
    return user_ids, old_user_ids

def detect_disconnections(user_ids: List[str], old_user_ids: List[str]) -> List[str]:
    """Detecta usuarios que se desconectaron entre ejecuciones."""
    if not old_user_ids:
        return []
    
    # Encontrar usuarios que estaban antes pero no están ahora
    disconnected_users = list(set(old_user_ids) - set(user_ids))
    if disconnected_users:
        logger.info(f"Usuarios desconectados detectados: {len(disconnected_users)}")
    return disconnected_users

def main():
    logger.info("Iniciando gestor automático de status de Slack")
    
    # Paso 1: Ejecutar escaneo de red
    logger.info("Paso 1: Ejecutando escaneo de red")
    if not run_network_scan():
        logger.error("Falló el escaneo de red, abortando")
        return
    
    # Paso 2: Cargar archivos
    logger.info("Paso 2: Cargando archivos de configuración")
    network_data = load_json_file("Simpat_Network.json")
    config_data = load_json_file("Config.json")
    
    if not network_data or not config_data:
        logger.error("No se pudieron cargar los archivos necesarios")
        return
    
    # Validar configuración
    logger.info("Validando configuración")
    is_valid, errors = ConfigValidator.validate_config(config_data)
    if not is_valid:
        logger.error("Errores de configuración encontrados:")
        for error in errors:
            logger.error(f"  - {error}")
        return
    
    logger.info("Configuración válida")
    
    # Paso 3: Analizar presencia y guardar status
    logger.info("Paso 3: Analizando presencia de usuarios")
    users_in_office = find_users_in_office(network_data, config_data)
    user_ids, old_user_ids = save_current_status(users_in_office, config_data)
    
    # Paso 4: Detectar desconexiones
    logger.info("Paso 4: Detectando desconexiones")
    disconnected_users = detect_disconnections(user_ids, old_user_ids)
    
    # Paso 5: Actualizar status en Slack (si hay usuarios detectados)
    if user_ids or disconnected_users:
        logger.info("Paso 5: Actualizando status en Slack")
        run_slack_status_update()
    else:
        logger.info("No hay cambios de status para procesar")
    
    logger.info("Proceso completado exitosamente")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Proceso interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error crítico en el proceso: {e}")
        sys.exit(1)
