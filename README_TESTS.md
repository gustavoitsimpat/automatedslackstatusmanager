# 🧪 Scripts de Prueba para el Sistema de Gestión de Status de Slack

Este directorio contiene scripts de prueba para validar y verificar el funcionamiento del sistema de gestión automática de status de Slack.

## 📋 Scripts Disponibles

### 1. `test_integration.py` - Pruebas de Integración General
**Descripción:** Script principal que prueba todos los componentes del sistema de manera integrada.

**Funcionalidades:**
- ✅ Verificación de estructura de archivos
- ✅ Validación de configuración de archivos JSON
- ✅ Verificación de variables de entorno
- ✅ Prueba de protección de status de lunch
- ✅ Prueba de escaneo de red
- ✅ Prueba de gestor de status de Slack
- ✅ Prueba de integración completa

**Uso:**
```bash
python test_integration.py
```

### 2. `test_network_scan.py` - Pruebas de Escaneo de Red
**Descripción:** Script específico para probar las funcionalidades de red y escaneo.

**Funcionalidades:**
- ✅ Prueba de conectividad de red
- ✅ Verificación de comandos ping y ARP
- ✅ Prueba del script quick_ping.py
- ✅ Análisis de rango de red
- ✅ Pruebas de rendimiento

**Uso:**
```bash
python test_network_scan.py
```

### 3. `test_slack_status.py` - Pruebas de Gestión de Status de Slack
**Descripción:** Script específico para probar las funcionalidades de Slack.

**Funcionalidades:**
- ✅ Prueba del script slack_status_manager.py
- ✅ Validación de detección de lunch
- ✅ Prueba de borrado de status
- ✅ Verificación de carga de datos de usuario
- ✅ Validación de variables de entorno
- ✅ Prueba de formatos de status
- ✅ Manejo de errores

**Uso:**
```bash
python test_slack_status.py
```

### 4. `test_complete_system.py` - Pruebas del Sistema Completo
**Descripción:** Script que prueba la integración completa de todos los componentes.

**Funcionalidades:**
- ✅ Verificación de componentes del sistema
- ✅ Validación de configuración
- ✅ Prueba de escaneo de red
- ✅ Prueba de gestión de status
- ✅ Prueba de integración completa
- ✅ Análisis de rendimiento
- ✅ Prueba de escenarios de error

**Uso:**
```bash
python test_complete_system.py
```

### 5. `test_configuration.py` - Validación de Configuración
**Descripción:** Script para validar todos los archivos de configuración y su formato.

**Funcionalidades:**
- ✅ Validación de Config.json
- ✅ Verificación de archivo .env
- ✅ Validación de configuración de red
- ✅ Verificación de permisos de archivos
- ✅ Validación de dependencias

**Uso:**
```bash
python test_configuration.py
```

## 🚀 Ejecución de Pruebas

### Ejecución Individual
Para ejecutar un script específico:

```bash
# Pruebas de integración general
python test_integration.py

# Pruebas de red
python test_network_scan.py

# Pruebas de Slack
python test_slack_status.py

# Pruebas del sistema completo
python test_complete_system.py

# Validación de configuración
python test_configuration.py
```

### Ejecución Completa
Para ejecutar todas las pruebas en secuencia:

```bash
# Ejecutar todas las pruebas
python test_integration.py
python test_network_scan.py
python test_slack_status.py
python test_complete_system.py
python test_configuration.py
```

## 📊 Interpretación de Resultados

### ✅ Indicadores de Éxito
- **[OK]**: Prueba exitosa
- **[STATS]**: Información estadística
- **[SEARCH]**: Verificación completada

### ⚠️ Indicadores de Advertencia
- **[WARNING]**: Advertencia (no crítico)
- **[TEXT]**: Información adicional
- **[TIP]**: Sugerencia

### ❌ Indicadores de Error
- **[ERROR]**: Error crítico
- **[FIX]**: Requiere corrección
- **[CRASH]**: Problema de seguridad

## 🔧 Configuración para Pruebas

### Requisitos Previos
1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar archivo .env:**
   ```env
   SLACK_USER_TOKEN=xoxp-your-user-token-here
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   DEFAULT_STATUS=At Simpat Tech
   ```

3. **Verificar Config.json:**
   ```json
   {
     "users": [
       {
         "ip": "10.0.0.2",
         "hostname": "Usuario Ejemplo",
         "userID": "U1234567890"
       }
     ]
   }
   ```

### Archivos de Prueba Generados
Los scripts pueden generar archivos temporales de prueba:
- `test_current_status.json` - Datos de prueba para status
- Archivos de salida temporales

**Nota:** Estos archivos se eliminan automáticamente al finalizar las pruebas.

## 📈 Análisis de Resultados

### Métricas de Rendimiento
- **Tiempo de ejecución:** Duración de cada prueba
- **Tasa de detección:** Porcentaje de dispositivos detectados
- **Usuarios válidos:** Número de usuarios correctamente configurados
- **Errores encontrados:** Cantidad y tipo de errores

### Estadísticas del Sistema
- **Dispositivos detectados:** Total de IPs activas
- **Usuarios en oficina:** Usuarios actualmente presentes
- **Usuarios desconectados:** Usuarios que se desconectaron
- **Archivos generados:** Archivos de salida creados

## 🔍 Solución de Problemas

### Problemas Comunes

#### 1. Error: "Config.json no encontrado"
**Solución:**
- Verifica que el archivo Config.json existe en el directorio
- Asegúrate de que el formato JSON es válido

#### 2. Error: "Archivo .env no encontrado"
**Solución:**
- Crea un archivo .env con tus tokens de Slack
- Verifica que python-dotenv está instalado

#### 3. Error: "Timeout en escaneo de red"
**Solución:**
- Verifica la conectividad de red
- Ajusta los timeouts si es necesario
- Verifica que el firewall no bloquea los pings

#### 4. Error: "Token no configurado"
**Solución:**
- Configura SLACK_USER_TOKEN en el archivo .env
- Verifica que el token tiene permisos adecuados

### Logs de Debugging
Los scripts generan logs detallados que incluyen:
- Estado de cada prueba
- Errores específicos
- Recomendaciones de corrección
- Estadísticas de rendimiento

## 📋 Checklist de Pruebas

### Antes de Ejecutar
- [ ] Dependencias instaladas
- [ ] Archivo .env configurado
- [ ] Config.json válido
- [ ] Conectividad de red disponible
- [ ] Permisos de archivos correctos

### Durante la Ejecución
- [ ] Verificar salida de cada script
- [ ] Revisar errores y advertencias
- [ ] Confirmar archivos de salida generados
- [ ] Validar estadísticas de rendimiento

### Después de la Ejecución
- [ ] Revisar resumen final
- [ ] Corregir errores identificados
- [ ] Verificar configuración si es necesario
- [ ] Documentar problemas encontrados

## 🎯 Objetivos de las Pruebas

### Funcionalidad
- ✅ Verificar que todos los componentes funcionan correctamente
- ✅ Validar la integración entre módulos
- ✅ Confirmar la generación de archivos de salida

### Rendimiento
- ✅ Medir tiempos de ejecución
- ✅ Analizar eficiencia del escaneo de red
- ✅ Verificar manejo de errores

### Configuración
- ✅ Validar formatos de archivos
- ✅ Verificar variables de entorno
- ✅ Confirmar permisos de archivos

### Seguridad
- ✅ Validar manejo seguro de tokens
- ✅ Verificar protección de datos sensibles
- ✅ Confirmar validación de entrada

## 📞 Soporte

Si encuentras problemas con las pruebas:

1. **Revisa los logs** generados por cada script
2. **Verifica la configuración** según las recomendaciones
3. **Ejecuta las pruebas individuales** para aislar problemas
4. **Consulta la documentación** del sistema principal

---

**Desarrollado para asegurar la calidad y funcionamiento del Sistema de Gestión de Status de Slack.** 🧪✨
