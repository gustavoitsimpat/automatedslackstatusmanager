# Automated Slack Status Manager

Sistema automatizado para gestionar estados de Slack basado en la presencia de usuarios en la oficina.

## 📁 Estructura del Proyecto

```
automatedslackstatusmanager/
├── 📁 config/                 # Archivos de configuración
│   ├── Config.json           # Configuración de usuarios
│   ├── current_status.json   # Estado actual de usuarios
│   ├── current_status.csv    # Estado en formato CSV
│   └── Simpat_Network.json   # Resultados de escaneo de red
├── 📁 scripts/               # Scripts principales
│   ├── main.py               # Script principal (ejecuta todo el sistema)
│   ├── quick_ping.py         # Escáner de red optimizado
│   └── slack_status_manager.py # Gestor de estados de Slack
├── 📁 tests/                 # Archivos de prueba
│   ├── test_*.py            # Scripts de prueba
│   ├── test_config.json     # Configuración de prueba
│   ├── test_current_status.json # Estado de prueba
│   └── run_all_tests.py     # Ejecutor de todas las pruebas
├── 📁 logs/                  # Archivos de log
│   ├── auto_status_manager.log
│   ├── slack_status_manager.log
│   └── quick_ping.log
├── 📁 docs/                  # Documentación
│   ├── README.md            # Este archivo
│   ├── README_TESTING.md    # Guía de pruebas
│   ├── README_TESTS.md      # Documentación de pruebas
│   └── OPTIMIZACIONES_IMPLEMENTADAS.md
├── requirements.txt          # Dependencias de Python
├── run.py                   # Script de conveniencia (ejecuta todo el sistema)
├── .env                     # Variables de entorno
├── env.example              # Ejemplo completo de variables de entorno
├── env.minimal              # Configuración mínima de variables de entorno
└── LICENSE                  # Licencia del proyecto
```

## 🚀 Instalación

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd automatedslackstatusmanager
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
   
   **Opción A - Configuración mínima:**
   ```bash
   # Copiar archivo de configuración mínima
   cp env.minimal .env
   # Editar .env y agregar tu token de Slack
   ```
   
   **Opción B - Configuración completa:**
   ```bash
   # Copiar archivo de ejemplo completo
   cp env.example .env
   # Editar .env según tus necesidades
   ```
   
   **Configuración manual:**
   Crear un archivo `.env` en la raíz del proyecto:
   ```env
   SLACK_USER_TOKEN=xoxp-your-token-here
   CONFIG_FILE=config/Config.json
   CURRENT_STATUS_FILE=config/current_status.json
   DEFAULT_STATUS="At Simpat Tech Office"
   STATUS_EMOJI=":simpat:"
   ```

## 📋 Uso

### 🚀 Ejecutar Sistema Completo (Recomendado)
```bash
# Opción 1: Desde la raíz del proyecto
python run.py

# Opción 2: Usando el script principal directamente
python scripts/main.py
```

### 🔧 Ejecutar Scripts Individuales

#### 1. Escaneo de Red
```bash
# Desde la raíz del proyecto
python scripts/quick_ping.py
```

#### 2. Gestión de Estados de Slack
```bash
# Usar archivos principales
python scripts/slack_status_manager.py

# Usar archivos de prueba
CONFIG_FILE=tests/test_config.json CURRENT_STATUS_FILE=tests/test_current_status.json python scripts/slack_status_manager.py
```

#### 3. Ejecutar Pruebas
```bash
# Ejecutar todas las pruebas
python tests/run_all_tests.py

# Probar el sistema principal
python tests/test_main.py

# Ejecutar pruebas específicas
python tests/test_configuration.py
python tests/test_slack_status.py
```

## 🔧 Configuración

### Archivo Config.json
```json
{
  "users": [
    {
      "ip": "192.168.1.100",
      "hostname": "Usuario Ejemplo",
      "userID": "U1234567890"
    }
  ]
}
```

### Archivo current_status.json
```json
{
  "user_ids": ["U1234567890"],
  "old_user_ids": ["U1234567890", "U0987654321"]
}
```

## 📊 Funcionalidades

### Escáner de Red (`quick_ping.py`)
- Escaneo optimizado de IPs configuradas
- Detección de usuarios activos en la red
- Generación de `current_status.json`

### Analizador y Decisor (`main.py`)
- Analiza estados actuales de usuarios en Slack
- Aplica lógica de negocio (lunch, estados correctos)
- Genera instrucciones específicas para cada usuario
- Coordina la ejecución de todo el sistema

### Ejecutor de Estados (`slack_status_manager.py`)
- Ejecuta operaciones específicas de Slack
- Recibe instrucciones detalladas (set_status, clear_status, skip)
- Manejo robusto de errores de API
- Logging detallado de operaciones

### Flujo de Trabajo del Sistema
1. **Escaneo de red** (`quick_ping.py`): Detecta usuarios activos en la red
2. **Análisis y decisión** (`main.py`): Analiza estados actuales y genera instrucciones
3. **Ejecución de cambios** (`slack_status_manager.py`): Ejecuta las operaciones de Slack

### Lógica de Estados
- **Usuarios activos** (`user_ids`): Status → "At Simpat Tech Office"
- **Usuarios desconectados** (`old_user_ids` - `user_ids`): Status → borrado
- **Usuarios en lunch**: No se modifican

## 🧪 Pruebas

### Archivos de Prueba Incluidos
- `tests/test_config.json`: Configuración de usuarios de prueba
- `tests/test_current_status.json`: Estado de prueba
- `tests/test_*.py`: Scripts de prueba automatizados

### Ejecutar Pruebas
```bash
# Usar archivos de prueba
CONFIG_FILE=tests/test_config.json CURRENT_STATUS_FILE=tests/test_current_status.json python scripts/slack_status_manager.py
```

## 📝 Logs

Los archivos de log se guardan en la carpeta `logs/`:
- `auto_status_manager.log`: Logs del gestor automático
- `slack_status_manager.log`: Logs del gestor de Slack
- `quick_ping.log`: Logs del escáner de red

## 🔍 Variables de Entorno

### Variables Principales

| Variable | Descripción | Por Defecto | Requerido |
|----------|-------------|-------------|-----------|
| `SLACK_USER_TOKEN` | Token de usuario de Slack | - | ✅ Sí |
| `CONFIG_FILE` | Archivo de configuración | `config/Config.json` | ❌ No |
| `CURRENT_STATUS_FILE` | Archivo de estado | `config/current_status.json` | ❌ No |
| `DEFAULT_STATUS` | Status por defecto | `"At Simpat Tech Office"` | ❌ No |
| `STATUS_EMOJI` | Emoji del status | `:simpat:` | ❌ No |

### Variables Opcionales

| Variable | Descripción | Por Defecto |
|----------|-------------|-------------|
| `AWAY_STATUS` | Status para usuarios ausentes | `"Away"` |
| `AWAY_STATUS_EMOJI` | Emoji para usuarios ausentes | `:afk:` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `PING_TIMEOUT` | Timeout para ping (ms) | `1000` |
| `MAX_WORKERS` | Workers para escaneo paralelo | `10` |
| `MAX_RETRIES` | Reintentos para operaciones | `3` |
| `RETRY_BASE_DELAY` | Delay base para retry (s) | `1.0` |

### Archivos de Configuración

- **`env.example`**: Configuración completa con todas las opciones
- **`env.minimal`**: Configuración mínima con solo lo esencial
- **`.env`**: Tu archivo de configuración personal (no se incluye en git)

## 📚 Documentación Adicional

- **`docs/ARQUITECTURA_SISTEMA.md`**: Arquitectura detallada del sistema
- **`docs/README_TESTING.md`**: Guía completa de pruebas
- **`docs/README_TESTS.md`**: Documentación de pruebas
- **`docs/OPTIMIZACIONES_IMPLEMENTADAS.md`**: Optimizaciones realizadas

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Para soporte técnico o preguntas, revisa la documentación en la carpeta `docs/` o abre un issue en el repositorio.
