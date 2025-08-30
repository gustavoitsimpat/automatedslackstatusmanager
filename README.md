# Quick Ping Scanner

Un escáner de red ultra simple que detecta dispositivos activos usando solo ping.

## 🚀 Características

- **Ultra simple**: Solo 50 líneas de código
- **Sin dependencias**: No requiere librerías externas
- **Muy rápido**: Timeout de 2 segundos por IP
- **Funciona en cualquier sistema**: Windows, Linux, Mac
- **No requiere privilegios especiales**: Usa solo comandos del sistema

## 📋 Requisitos

- Python 3.6 o superior
- Conexión a red

## 🎯 Uso

```bash
python quick_ping.py
```

## 📊 Salida de Ejemplo

```
🔍 ESCÁNER DE PING RÁPIDO
==============================
IP local: 10.0.0.2
Escaneando: 10.0.0.1 - 10.0.0.50

✅ 10.0.0.1
✅ 10.0.0.2
✅ 10.0.0.25
✅ 10.0.0.28
✅ 10.0.0.41
✅ 10.0.0.47

📊 RESULTADOS:
Dispositivos activos: 6

📱 IPs activas:
  • 10.0.0.1
  • 10.0.0.2
  • 10.0.0.25
  • 10.0.0.28
  • 10.0.0.41
  • 10.0.0.47
```

## 🔧 Cómo Funciona

1. **Detecta tu IP local** automáticamente
2. **Escanea el rango** de IPs de tu red (1-50)
3. **Hace ping** a cada IP para verificar si responde
4. **Muestra resultados** en tiempo real
5. **Lista todas las IPs activas** encontradas

## ⚡ Ventajas

- ✅ **No requiere Npcap/WinPcap**
- ✅ **No requiere privilegios de administrador**
- ✅ **No bloqueado por firewalls**
- ✅ **Muy confiable**
- ✅ **Código mínimo y limpio**

## 📁 Archivos del Proyecto

- **`quick_ping.py`** - Script principal
- **`LICENSE`** - Licencia del proyecto

## 🐛 Solución de Problemas

### No encuentra dispositivos
- Verifica que estés conectado a la red
- Comprueba que el firewall no esté bloqueando ping
- Asegúrate de que haya dispositivos activos en el rango 1-50

### Error de Python
- Asegúrate de tener Python 3.6+ instalado
- Verifica que Python esté en el PATH

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
