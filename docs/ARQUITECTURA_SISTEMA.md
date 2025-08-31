# Arquitectura del Sistema de Gestión de Estados de Slack

## 📋 Resumen de la Arquitectura

El sistema está diseñado con una arquitectura modular donde cada componente tiene una responsabilidad específica y bien definida:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   quick_ping.py │───▶│    main.py      │───▶│slack_status_mgr │
│                 │    │                 │    │      .py        │
│ • Escanea IPs   │    │ • Analiza       │    │ • Ejecuta       │
│ • Detecta       │    │ • Decide        │    │ • Cambia        │
│ • Genera estado │    │ • Genera        │    │ • Borra         │
└─────────────────┘    │   instrucciones │    │ • Salta         │
                       └─────────────────┘    └─────────────────┘
```

## 🔧 Responsabilidades de Cada Componente

### 1. **quick_ping.py** - Escáner de Red
**Responsabilidad única:** Detectar usuarios activos en la red

**Funciones:**
- ✅ Lee configuración de `Config.json`
- ✅ Hace ping a las IPs configuradas
- ✅ Detecta usuarios activos/inactivos
- ✅ Genera `current_status.json` con formato:
  ```json
  {
    "user_ids": ["U1234567890"],
    "old_user_ids": ["U1234567890", "U0987654321"]
  }
  ```

**No hace:**
- ❌ No toma decisiones de lógica
- ❌ No interactúa con Slack
- ❌ No modifica estados

### 2. **main.py** - Analizador y Decisor
**Responsabilidad única:** Tomar decisiones de lógica de negocio

**Funciones:**
- ✅ Carga estado actual de `current_status.json`
- ✅ Obtiene estados actuales de usuarios en Slack
- ✅ Aplica lógica de negocio:
  - **Usuarios activos** → Cambiar a "At Simpat Tech Office" (si no está en lunch)
  - **Usuarios desconectados** → Borrar estado (si no está en lunch)
  - **Usuarios en lunch** → No hacer nada
- ✅ Genera instrucciones específicas para `slack_status_manager.py`

**Lógica de Decisiones:**
```python
# Para usuarios activos
if user in user_ids:
    if is_on_lunch(current_status):
        action = "skip"
    elif current_status == "At Simpat Tech Office":
        action = "none"  # Ya está correcto
    else:
        action = "set_status"

# Para usuarios desconectados
if user in old_user_ids and user not in user_ids:
    if is_on_lunch(current_status):
        action = "skip"
    elif current_status == "":
        action = "none"  # Ya está borrado
    else:
        action = "clear_status"
```

### 3. **slack_status_manager.py** - Ejecutor de Operaciones
**Responsabilidad única:** Ejecutar operaciones específicas en Slack

**Funciones:**
- ✅ Recibe instrucciones JSON como argumento
- ✅ Ejecuta operaciones específicas:
  - `set_status`: Establece "At Simpat Tech Office"
  - `clear_status`: Borra el estado
  - `skip`: No hace nada (lunch)
- ✅ Maneja errores de API de Slack
- ✅ Reporta resultados detallados

**Formato de Instrucciones:**
```json
[
  {
    "user_id": "U1234567890",
    "action": "set_status",
    "reason": "active_user"
  },
  {
    "user_id": "U0987654321",
    "action": "clear_status",
    "reason": "disconnected_user"
  },
  {
    "user_id": "U1111111111",
    "action": "skip",
    "reason": "lunch"
  }
]
```

## 🔄 Flujo de Datos

### Paso 1: Escaneo
```
Config.json → quick_ping.py → current_status.json
```

### Paso 2: Análisis
```
current_status.json + Slack API → main.py → instructions.json
```

### Paso 3: Ejecución
```
instructions.json → slack_status_manager.py → Slack API
```

## 🎯 Ventajas de esta Arquitectura

### **1. Separación de Responsabilidades**
- Cada script tiene una función específica
- Fácil de mantener y debuggear
- Posibilidad de reemplazar componentes individuales

### **2. Escalabilidad**
- `quick_ping.py` puede optimizarse independientemente
- `main.py` puede agregar nuevas reglas de negocio
- `slack_status_manager.py` puede agregar nuevas operaciones

### **3. Testabilidad**
- Cada componente puede probarse de forma aislada
- Fácil crear mocks para pruebas
- Instrucciones JSON permiten pruebas sin API real

### **4. Flexibilidad**
- Fácil cambiar la lógica de decisiones sin tocar Slack
- Posibilidad de agregar nuevos tipos de operaciones
- Soporte para diferentes configuraciones

## 🔍 Detección de Lunch

El sistema detecta usuarios en lunch mediante palabras clave:

```python
lunch_indicators = ['lunch', 'almuerzo', 'comida', 'break']
```

**Ejemplos de estados que se consideran "lunch":**
- "Lunch"
- "En almuerzo"
- "Comida"
- "Coffee break"
- "Almorzando"

## 📊 Logging y Monitoreo

Cada componente genera logs específicos:

- **quick_ping.py**: `quick_ping.log`
- **main.py**: `logs/main.log`
- **slack_status_manager.py**: `logs/slack_status_manager.log`

Los logs incluyen:
- Operaciones realizadas
- Decisiones tomadas
- Errores y excepciones
- Tiempos de ejecución
- Resúmenes finales

## 🚀 Ejecución del Sistema

### Comando Principal
```bash
python run.py
```

### Flujo Interno
1. `run.py` → `scripts/main.py`
2. `main.py` → `quick_ping.py`
3. `main.py` → Análisis y generación de instrucciones
4. `main.py` → `slack_status_manager.py` con instrucciones

### Ejecución Individual
```bash
# Solo escaneo
python scripts/quick_ping.py

# Solo gestión (con instrucciones manuales)
python scripts/slack_status_manager.py '[{"user_id":"U123","action":"set_status"}]'
```

## 🔧 Configuración

### Variables de Entorno Principales
- `SLACK_USER_TOKEN`: Token de usuario de Slack
- `CONFIG_FILE`: Archivo de configuración de usuarios
- `CURRENT_STATUS_FILE`: Archivo de estado actual
- `DEFAULT_STATUS`: Status por defecto ("At Simpat Tech Office")

### Archivos de Configuración
- `config/Config.json`: Lista de usuarios a monitorear
- `config/current_status.json`: Estado actual (generado automáticamente)

Esta arquitectura garantiza que el sistema sea robusto, mantenible y fácil de extender según las necesidades futuras.
