# 🤖 Gestor Automático de Status de Slack

Sistema automatizado para detectar usuarios presentes en la oficina mediante escaneo de red y generar archivos de salida compatibles con APIs de Slack.

## 📋 Descripción

Este proyecto automatiza la detección de presencia en la oficina mediante:
- **Escaneo de red** usando ping y ARP
- **Comparación** con configuración de usuarios
- **Generación** de archivos JSON y CSV con userIDs de Slack

## 🚀 Características

- ✅ **Escaneo automático** de red completa (1-254 IPs)
- ✅ **Detección robusta** con ping + ARP como respaldo
- ✅ **Configuración flexible** de usuarios y IPs
- ✅ **Salida múltiple** en JSON y CSV
- ✅ **Ejecución silenciosa** sin output en consola
- ✅ **Integración Slack** con userIDs únicos
- ✅ **Logging estructurado** para debugging y monitoreo
- ✅ **Timeouts adaptativos** basados en latencia de red
- ✅ **Retry con backoff exponencial** para mayor confiabilidad
- ✅ **Validación robusta** de configuración y datos

## 📁 Estructura del Proyecto

```
automatedslackstatusmanager/
├── auto_status_manager.py        # Script principal
├── quick_ping.py                 # Escáner de red
├── slack_status_manager.py       # Gestor de status de Slack
├── Config.json                   # Configuración de usuarios
├── .env                          # Variables de entorno (crear)
├── requirements.txt              # Dependencias de Python
├── current_status.json           # Salida JSON (user_ids array)
├── current_status.csv            # Salida CSV (solo userIDs)
├── Simpat_Network.json           # Resultados del escaneo de red
├── *.log                         # Archivos de log (auto_status_manager.log, quick_ping.log, slack_status_manager.log)
├── README.md                     # Documentación principal
├── README_TESTS.md               # Documentación de pruebas
├── test_integration.py           # Pruebas de integración general
├── test_network_scan.py          # Pruebas de escaneo de red
├── test_slack_status.py          # Pruebas de gestión de Slack
├── test_complete_system.py       # Pruebas del sistema completo
├── test_configuration.py         # Validación de configuración
└── run_all_tests.py              # Ejecutar todas las pruebas
```

## 🛠️ Instalación

### Requisitos
- Python 3.6+
- Windows/Linux/macOS
- Acceso a red local

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Configuración
1. Clona o descarga el proyecto
2. Instala las dependencias: `pip install -r requirements.txt`
3. Configura el archivo `Config.json` con tus usuarios
4. Crea un archivo `.env` con tus tokens de Slack (ver sección Variables de Entorno)
5. Ejecuta el script principal

## ⚙️ Configuración

### Variables de Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Slack API Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_USER_TOKEN=xoxp-your-user-token-here

# Network Configuration
NETWORK_TIMEOUT=120
SCAN_WORKERS=10

# Status Configuration
DEFAULT_STATUS=At Simpat Tech
```

**Variables requeridas:**
- `SLACK_BOT_TOKEN`: Token de bot de Slack (xoxb-...)
- `SLACK_USER_TOKEN`: Token de usuario de Slack (xoxp-...)

**Variables opcionales:**
- `NETWORK_TIMEOUT`: Timeout para escaneo de red (default: 120)
- `SCAN_WORKERS`: Número de workers para escaneo paralelo (default: 10)
- `DEFAULT_STATUS`: Status por defecto para usuarios en oficina (default: "At Simpat Tech")

### Archivo Config.json
```json
{
  "users": [
    {
      "ip": "10.0.0.2",
      "hostname": "Gustavo Cárdenas",
      "userID": "U055JF3TRB8"
    },
    {
      "ip": "10.0.0.3",
      "hostname": "Gilberto Campos",
      "userID": "UG39E9SSV"
    }
  ]
}
```

**Campos:**
- `ip`: Dirección IP del usuario en la red
- `hostname`: Nombre del usuario
- `userID`: Identificador único de Slack

## 🚀 Uso

### Ejecución Simple
```bash
python auto_status_manager.py
```

### Proceso Automático
El script ejecuta automáticamente:
1. **Escaneo de red** (`quick_ping.py`)
2. **Carga de configuración** (`Config.json`)
3. **Comparación de IPs** activas vs configuradas
4. **Generación de archivos** de salida

## 📊 Archivos de Salida

### current_status.json
```json
{
  "user_ids": [
    "U055JF3TRB8",
    "UG39E9SSV",
    "UCW5N1XRP",
    "U02MTBP4V2T"
  ],
  "old_user_ids": [
    "U055JF3TRB8",
    "UG39E9SSV",
    "UCW5N1XRP",
    "U02MTBP4V2T",
    "U9999999999"
  ]
}
```

**Campos:**
- `user_ids`: Lista de userIDs de usuarios actualmente en la oficina
- `old_user_ids`: Lista de userIDs de usuarios de la ejecución anterior (para detectar desconexiones)

### current_status.csv
```csv
U055JF3TRB8
UG39E9SSV
UCW5N1XRP
U02MTBP4V2T
```

### Archivos de Log

El sistema genera archivos de log estructurados para debugging y monitoreo:

#### auto_status_manager.log
```
2024-01-15 10:30:15,123 - auto_status_manager - INFO - Iniciando gestor automático de status de Slack
2024-01-15 10:30:15,456 - auto_status_manager - INFO - Paso 1: Ejecutando escaneo de red
2024-01-15 10:30:18,789 - auto_status_manager - INFO - Ejecutando escaneo de red con timeout de 5s
2024-01-15 10:30:25,234 - auto_status_manager - INFO - Paso 2: Cargando archivos de configuración
2024-01-15 10:30:25,345 - auto_status_manager - INFO - Archivo Config.json cargado exitosamente
2024-01-15 10:30:25,456 - auto_status_manager - INFO - Validando configuración
2024-01-15 10:30:25,567 - auto_status_manager - INFO - Configuración válida
```

#### quick_ping.log
```
2024-01-15 10:30:16,123 - quick_ping - INFO - Iniciando escaneo de red
2024-01-15 10:30:16,234 - quick_ping - INFO - IP local detectada: 192.168.1.100
2024-01-15 10:30:16,345 - quick_ping - INFO - Escaneando red: 192.168.1.0/24
2024-01-15 10:30:16,456 - quick_ping - INFO - Usando 8 workers para escaneo paralelo
2024-01-15 10:30:20,567 - quick_ping - INFO - Progreso: 50/254 IPs escaneadas, 12 dispositivos encontrados
2024-01-15 10:30:25,678 - quick_ping - INFO - Progreso: 100/254 IPs escaneadas, 15 dispositivos encontrados
2024-01-15 10:30:30,789 - quick_ping - INFO - Escaneo completado en 14.56 segundos
2024-01-15 10:30:30,890 - quick_ping - INFO - Total de dispositivos encontrados: 18
```

#### slack_status_manager.log
```
2024-01-15 10:30:35,123 - slack_status_manager - INFO - Iniciando gestor de status de Slack
2024-01-15 10:30:35,234 - slack_status_manager - INFO - Tokens de configuración válidos
2024-01-15 10:30:35,345 - slack_status_manager - INFO - Datos cargados: 8 usuarios activos, 2 desconectados
2024-01-15 10:30:35,456 - slack_status_manager - INFO - Cliente de Slack inicializado
2024-01-15 10:30:35,567 - slack_status_manager - INFO - Procesando 8 usuarios en la oficina
2024-01-15 10:30:36,678 - slack_status_manager - INFO - Status actualizado para usuario U055JF3TRB8
2024-01-15 10:30:37,789 - slack_status_manager - INFO - Usuario UG39E9SSV está en lunch, saltando
2024-01-15 10:30:38,890 - slack_status_manager - INFO - Procesando 2 usuarios desconectados
2024-01-15 10:30:39,901 - slack_status_manager - INFO - Status borrado para usuario U9999999999
```

**Beneficios del logging estructurado:**
- ✅ **Debugging detallado** de cada paso del proceso
- ✅ **Monitoreo en tiempo real** del progreso
- ✅ **Identificación rápida** de errores y problemas
- ✅ **Análisis de rendimiento** con timestamps precisos
- ✅ **Auditoría completa** de todas las operaciones

## 🔧 Scripts

### auto_status_manager.py
**Script principal** que:
- Ejecuta el escaneo de red
- Compara con configuración
- Genera archivos de salida con historial
- Detecta desconexiones de usuarios
- Actualiza status en Slack (automático)

**Funciones principales:**
- `run_network_scan()`: Ejecuta quick_ping.py con timeout adaptativo
- `run_slack_status_update()`: Ejecuta slack_status_manager.py con retry
- `find_users_in_office()`: Compara IPs activas
- `save_current_status()`: Genera JSON y CSV con historial
- `detect_disconnections()`: Detecta usuarios desconectados
- `ConfigValidator`: Valida configuración robustamente
- `retry_with_backoff()`: Implementa retry con backoff exponencial
- `get_adaptive_timeout()`: Calcula timeouts basados en latencia de red

**Optimizaciones implementadas:**
- ✅ **Logging estructurado** en `auto_status_manager.log`
- ✅ **Validación de configuración** con reporte de errores detallado
- ✅ **Timeouts adaptativos** basados en latencia de red
- ✅ **Retry con backoff exponencial** para operaciones críticas

### quick_ping.py
**Escáner de red** que:
- Detecta IPs activas (1-254)
- Obtiene hostnames
- Guarda resultados en `Simpat_Network.json`

**Características:**
- Escaneo paralelo con workers dinámicos (CPU * 2)
- Timeout adaptativo basado en latencia de red
- Detección ARP como respaldo
- Sin output en consola

**Optimizaciones implementadas:**
- ✅ **Logging estructurado** en `quick_ping.log`
- ✅ **Timeouts adaptativos** (1-5 segundos según latencia)
- ✅ **Workers dinámicos** basados en CPU disponible
- ✅ **Retry con backoff** para ping y ARP
- ✅ **Progreso en tiempo real** cada 50 IPs escaneadas

### slack_status_manager.py
**Gestor de status de Slack** que:
- Lee userIDs desde `current_status.json`
- Actualiza status de usuarios en Slack
- Maneja desconexiones automáticamente
- Respeta status de lunch automáticamente
- Usa variables de entorno para tokens

**Características:**
- Validación de tokens
- Manejo de errores de API
- Status configurable desde variables de entorno
- **Detección automática de desconexiones**
- **Borrado de status para usuarios desconectados**
- **Status "At Simpat Tech" para usuarios en oficina**
- **🛡️ Protección de status de lunch** (no modifica usuarios en almuerzo)
- Ejecución única (no bucle infinito)
- Output minimalista con resumen de resultados

**Optimizaciones implementadas:**
- ✅ **Logging estructurado** en `slack_status_manager.log`
- ✅ **Validación robusta** de datos de usuario
- ✅ **Retry con backoff** para operaciones de API
- ✅ **Manejo mejorado de errores** con logging detallado
- ✅ **Validación de tokens** antes de ejecutar

**Nota:** Ejecutado automáticamente por `auto_status_manager.py`

## 🔄 Flujo de Trabajo

```
1. Ejecutar auto_status_manager.py
   ↓
2. Ejecutar quick_ping.py (escaneo de red)
   ↓
3. Generar Simpat_Network.json
   ↓
4. Cargar Config.json
   ↓
5. Comparar IPs activas vs configuradas
   ↓
6. Generar current_status.json (con historial) y current_status.csv
   ↓
7. Detectar desconexiones de usuarios
   ↓
8. Ejecutar slack_status_manager.py (automático)
   ↓
9. Actualizar status en Slack:
   - Usuarios en oficina → "At Simpat Tech"
   - Usuarios desconectados → Status borrado
   - Usuarios en lunch → NO SE MODIFICA
```

## 🔍 Detección y Manejo de Desconexiones

El sistema ahora mantiene un historial de usuarios para detectar desconexiones y actualizar automáticamente los status de Slack:

### Funcionamiento
- **Primera ejecución**: Crea `user_ids` y `old_user_ids` vacío
- **Ejecuciones posteriores**: Guarda `user_ids` anterior en `old_user_ids`
- **Detección**: Compara ambos arrays para encontrar diferencias
- **Actualización automática**: Cambia status según presencia

### Status Automáticos
- **🟢 Usuarios en oficina**: Status "At Simpat Tech" con emoji `:simpat:`
- **🔴 Usuarios desconectados**: **Status borrado** (sin texto ni emoji)
- **🛡️ Usuarios en lunch**: **NO SE MODIFICA** (respeta status existente)

### Ejemplo de Uso
```python
import json

# Cargar datos
with open('current_status.json', 'r') as f:
    data = json.load(f)

current_users = set(data['user_ids'])
old_users = set(data['old_user_ids'])

# Detectar desconexiones
disconnected = old_users - current_users
connected = current_users - old_users

print(f"Desconectados: {list(disconnected)}")
print(f"Conectados: {list(connected)}")
```

### Configuración de Status
```env
# Variables de entorno (.env)
DEFAULT_STATUS=At Simpat Tech
```

### Protección de Status de Lunch

El sistema detecta automáticamente usuarios en lunch y **NO modifica** su status:

**Palabras clave detectadas:**
- `lunch` (en cualquier idioma)
- `almuerzo`
- `comida`
- `break`

**Ejemplos de status protegidos:**
- "Lunch" :pizza:
- "En almuerzo" :fork_and_knife:
- "Comida con cliente" :hamburger:
- "Break time" :coffee:
- "LUNCH BREAK" :sandwich:

**Comportamiento:**
- ✅ **Usuarios en lunch**: Status NO se modifica
- ✅ **Usuarios en oficina**: Status → "At Simpat Tech"
- ✅ **Usuarios desconectados**: Status → **BORRADO** (sin texto ni emoji)

## 📈 Integración con Slack

### Integración Automática

El `auto_status_manager.py` ahora ejecuta automáticamente `slack_status_manager.py`:

```bash
# Ejecutar todo el proceso (escaneo + Slack automático)
python auto_status_manager.py
```

### Usando slack_status_manager.py (Independiente)

Si prefieres ejecutar solo la actualización de Slack:

```bash
# Ejecutar después de auto_status_manager.py
python slack_status_manager.py
```

### Usando Variables de Entorno

```python
import os
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

# Obtener tokens
bot_token = os.getenv('SLACK_BOT_TOKEN')
user_token = os.getenv('SLACK_USER_TOKEN')

# Leer userIDs
with open('current_status.json', 'r') as f:
    data = json.load(f)
    user_ids = data['user_ids']

# Actualizar status en Slack
for user_id in user_ids:
    # Usar bot_token o user_token según necesites
    update_slack_status(user_id, bot_token)
```

### Usando JSON
```python
import json

with open('current_status.json', 'r') as f:
    data = json.load(f)
    user_ids = data['user_ids']
    
for user_id in user_ids:
    # Actualizar status en Slack usando user_id
```

### Usando CSV
```python
with open('current_status.csv', 'r') as f:
    user_ids = [line.strip() for line in f]
    
for user_id in user_ids:
    # Actualizar status en Slack usando user_id
```

## ⚡ Optimizaciones

### Rendimiento
- **Escaneo paralelo**: 10 workers simultáneos
- **Timeouts optimizados**: 1-3 segundos por IP
- **Detección dual**: Ping + ARP como respaldo
- **Ejecución silenciosa**: Sin output innecesario

### Confiabilidad
- **Manejo de errores**: Try-catch en todas las operaciones
- **Validación de archivos**: Verificación de existencia y formato
- **Timeouts**: Prevención de bloqueos
- **Codificación**: UTF-8 para caracteres especiales

## 🔍 Solución de Problemas

### Validación Automática
Antes de reportar problemas, ejecuta los scripts de prueba:

```bash
# Validar configuración
python test_configuration.py

# Probar sistema completo
python test_complete_system.py
```

### Error: "No se encontró el archivo"
- Verifica que `Config.json` existe
- Asegúrate de que el formato JSON es válido
- Ejecuta `python test_configuration.py` para validar

### Escaneo lento o incompleto
- Verifica conectividad de red
- Ajusta timeouts en `quick_ping.py` si es necesario
- Ejecuta `python test_network_scan.py` para diagnosticar

### Usuarios no detectados
- Verifica que las IPs en `Config.json` son correctas
- Confirma que los dispositivos están en la red
- Ejecuta `python test_configuration.py` para validar IPs

### Problemas con Slack
- Verifica que `SLACK_USER_TOKEN` está configurado en `.env`
- Confirma que el token tiene permisos adecuados
- Ejecuta `python test_slack_status.py` para diagnosticar

## 📝 Logs y Debugging

El sistema está diseñado para ejecutarse silenciosamente. Para debugging:

1. **Verificar archivos generados**:
   - `Simpat_Network.json`: Resultados del escaneo
   - `current_status.json`: Usuarios detectados
   - `current_status.csv`: Lista de userIDs

2. **Verificar configuración**:
   - Formato de `Config.json`
   - IPs correctas de usuarios

## 🧪 Pruebas y Validación

El proyecto incluye un conjunto completo de scripts de prueba para validar el funcionamiento del sistema.

### Scripts de Prueba Disponibles

```bash
# Ejecutar todas las pruebas (recomendado)
python run_all_tests.py

# Pruebas individuales
python test_configuration.py      # Validación de configuración
python test_integration.py        # Pruebas de integración general
python test_network_scan.py       # Pruebas de escaneo de red
python test_slack_status.py       # Pruebas de gestión de Slack
python test_complete_system.py    # Pruebas del sistema completo
```

### Documentación de Pruebas
Para información detallada sobre las pruebas, consulta [`README_TESTS.md`](README_TESTS.md).

## 🔄 Automatización

### Programación de Tareas (Windows)
```batch
# Crear tarea programada
schtasks /create /tn "SlackStatus" /tr "python C:\ruta\auto_status_manager.py" /sc minute /mo 5
```

### Cron (Linux/macOS)
```bash
# Ejecutar cada 5 minutos
*/5 * * * * /usr/bin/python3 /ruta/auto_status_manager.py
```

## 🔒 Seguridad

### Protección de Tokens

**IMPORTANTE:** Nunca incluyas tokens de Slack directamente en el código.

✅ **Correcto:**
```env
# .env (archivo local, no subir a Git)
SLACK_BOT_TOKEN=xoxb-your-actual-token
```

❌ **Incorrecto:**
```python
# En el código
token = "xoxb-your-actual-token"  # NUNCA hacer esto
```

### Archivos a Ignorar

Asegúrate de que tu `.gitignore` incluya:
```
.env
*.log
__pycache__/
*.pyc
```

### Obtención de Tokens de Slack

1. **Bot Token (xoxb-...):**
   - Ve a [api.slack.com/apps](https://api.slack.com/apps)
   - Crea una nueva app
   - Ve a "OAuth & Permissions"
   - Copia el "Bot User OAuth Token"

2. **User Token (xoxp-...):**
   - Ve a [api.slack.com/custom-integrations/legacy-tokens](https://api.slack.com/custom-integrations/legacy-tokens)
   - Genera un token para tu workspace

## 📄 Licencia

Este proyecto es de uso libre para fines educativos y comerciales.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para soporte técnico o preguntas:
- Revisa la sección de solución de problemas
- Verifica la configuración de archivos
- Asegúrate de que todos los requisitos están cumplidos

---

**Desarrollado para automatizar la gestión de status de Slack basada en presencia en la oficina.** 🏢✨
