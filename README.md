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

## 📁 Estructura del Proyecto

```
automatedslackstatusmanager/
├── auto_status_manager.py        # Script principal
├── quick_ping.py                 # Escáner de red
├── slack_status_manager.py       # Gestor de status de Slack
├── Config.json                   # Configuración de usuarios
├── .env                          # Variables de entorno (crear)
├── env_example.txt               # Ejemplo de variables de entorno
├── requirements.txt              # Dependencias de Python
├── current_status.json           # Salida JSON (user_ids array)
├── current_status.csv            # Salida CSV (solo userIDs)
├── Simpat_Network.json           # Resultados del escaneo de red
└── README.md                     # Este archivo
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
DEFAULT_STATUS=En la Oficina
AWAY_STATUS=No disponible
```

**Variables requeridas:**
- `SLACK_BOT_TOKEN`: Token de bot de Slack (xoxb-...)
- `SLACK_USER_TOKEN`: Token de usuario de Slack (xoxp-...)

**Variables opcionales:**
- `NETWORK_TIMEOUT`: Timeout para escaneo de red (default: 120)
- `SCAN_WORKERS`: Número de workers para escaneo paralelo (default: 10)
- `DEFAULT_STATUS`: Status por defecto para usuarios en oficina (default: "En la Oficina")
- `AWAY_STATUS`: Status para usuarios ausentes (default: "No disponible")

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

## 🔧 Scripts

### auto_status_manager.py
**Script principal** que:
- Ejecuta el escaneo de red
- Compara con configuración
- Genera archivos de salida con historial
- Detecta desconexiones de usuarios
- Actualiza status en Slack (automático)

**Funciones principales:**
- `run_network_scan()`: Ejecuta quick_ping.py
- `run_slack_status_update()`: Ejecuta slack_status_manager.py
- `find_users_in_office()`: Compara IPs activas
- `save_current_status()`: Genera JSON y CSV con historial
- `detect_disconnections()`: Detecta usuarios desconectados

### quick_ping.py
**Escáner de red** que:
- Detecta IPs activas (1-254)
- Obtiene hostnames
- Guarda resultados en `Simpat_Network.json`

**Características:**
- Escaneo paralelo (10 workers)
- Timeout optimizado (1-3 segundos)
- Detección ARP como respaldo
- Sin output en consola

### slack_status_manager.py
**Gestor de status de Slack** que:
- Lee userIDs desde `current_status.json`
- Actualiza status de usuarios en Slack
- Usa variables de entorno para tokens

**Características:**
- Validación de tokens
- Manejo de errores de API
- Status configurable desde variables de entorno
- Ejecución única (no bucle infinito)
- Output minimalista con resumen de resultados

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
9. Actualizar status de usuarios en Slack
```

## 🔍 Detección de Desconexiones

El sistema ahora mantiene un historial de usuarios para detectar desconexiones:

### Funcionamiento
- **Primera ejecución**: Crea `user_ids` y `old_user_ids` vacío
- **Ejecuciones posteriores**: Guarda `user_ids` anterior en `old_user_ids`
- **Detección**: Compara ambos arrays para encontrar diferencias

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

### Error: "No se encontró el archivo"
- Verifica que `Config.json` existe
- Asegúrate de que el formato JSON es válido

### Escaneo lento o incompleto
- Verifica conectividad de red
- Ajusta timeouts en `quick_ping.py` si es necesario

### Usuarios no detectados
- Verifica que las IPs en `Config.json` son correctas
- Confirma que los dispositivos están en la red

## 📝 Logs y Debugging

El sistema está diseñado para ejecutarse silenciosamente. Para debugging:

1. **Verificar archivos generados**:
   - `Simpat_Network.json`: Resultados del escaneo
   - `current_status.json`: Usuarios detectados
   - `current_status.csv`: Lista de userIDs

2. **Verificar configuración**:
   - Formato de `Config.json`
   - IPs correctas de usuarios

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
