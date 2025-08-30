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
├── auto_status_manager.py    # Script principal
├── quick_ping.py             # Escáner de red
├── Config.json               # Configuración de usuarios
├── current_status.json       # Salida JSON (hostname + userID)
├── current_status.csv        # Salida CSV (solo userIDs)
├── Simpat_Network.json       # Resultados del escaneo de red
└── README.md                 # Este archivo
```

## 🛠️ Instalación

### Requisitos
- Python 3.6+
- Windows/Linux/macOS
- Acceso a red local

### Configuración
1. Clona o descarga el proyecto
2. Configura el archivo `Config.json` con tus usuarios
3. Ejecuta el script principal

## ⚙️ Configuración

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
[
  {
    "hostname": "Gustavo Cárdenas",
    "userID": "U055JF3TRB8"
  },
  {
    "hostname": "Gilberto Campos",
    "userID": "UG39E9SSV"
  }
]
```

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
- Genera archivos de salida

**Funciones principales:**
- `run_network_scan()`: Ejecuta quick_ping.py
- `find_users_in_office()`: Compara IPs activas
- `save_current_status()`: Genera JSON y CSV

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
6. Generar current_status.json y current_status.csv
```

## 📈 Integración con Slack

### Usando JSON
```python
import json

with open('current_status.json', 'r') as f:
    users = json.load(f)
    
for user in users:
    user_id = user['userID']
    # Actualizar status en Slack usando user_id
```

### Usando CSV
```python
import csv

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
