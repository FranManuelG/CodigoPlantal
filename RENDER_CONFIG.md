# Configuración de Render para el Bot de Telegram

## ⚙️ Configuración del Servicio

### Tipo de Servicio
**IMPORTANTE**: El bot debe estar configurado como **Background Worker**, NO como Web Service.

### Variables de Entorno Requeridas

1. **TELEGRAM_BOT_TOKEN**
   - Tu token de bot de Telegram
   - Ejemplo: `8597101676:AAGOa2tI5frprwUX3iINiSTGuoL4AMwBXKI`

2. **DATABASE_URL**
   - URL de conexión a Supabase PostgreSQL
   - Formato: `postgresql://postgres.lfdmxoiwvopvxeyemgev:%3Fa8%2BNAS3%25V%40AbJ.@aws-1-eu-central-1.pooler.supabase.com:5432/postgres`
   - **NOTA**: Debe usar el Connection Pooler (Session mode) de Supabase

3. **PORT** (opcional)
   - Puerto para health check server
   - Default: `10000`

### Comandos de Build y Start

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python bot.py
```

## 🔍 Verificación de Logs

### Logs esperados al iniciar correctamente:

```
============================================================
Bot iniciando...
Python version: 3.13.x
PID: xxxxx
DATABASE_URL configurado: True
============================================================
Usando PostgreSQL. URL: postgresql://postgres.lfdmxoiwvopvxeyemgev...
Base de datos inicializada correctamente
Configurando comandos del bot...
✓ Comandos del bot configurados exitosamente
Iniciando tarea de notificaciones...
✓ Tarea de notificaciones iniciada
============================================================
BOT LISTO Y ESPERANDO MENSAJES
============================================================
Iniciando polling de Telegram...
```

### Logs al recibir comando /start:

```
Comando /start recibido de user_id=xxxxx, username=xxxxx, name=xxxxx
Probando conexión a base de datos...
Conexión a BD exitosa. Usuario tiene X plantas
Respuesta enviada exitosamente a user_id=xxxxx
```

## ⚠️ Problemas Comunes

### 1. Bot no responde
- **Causa**: Servicio configurado como Web Service en lugar de Background Worker
- **Solución**: Cambiar tipo de servicio a Background Worker en Render

### 2. Error de conexión a base de datos
- **Causa**: DATABASE_URL no configurado o incorrecto
- **Solución**: Verificar que DATABASE_URL esté en variables de entorno y use el Connection Pooler

### 3. Conflicto de instancias
- **Causa**: Múltiples instancias del bot corriendo simultáneamente
- **Solución**: Normal durante redespliegues, se resuelve automáticamente

### 4. Bot se detiene después de un tiempo
- **Causa**: Render puede dormir servicios gratuitos después de inactividad
- **Solución**: Usar plan de pago o mantener el bot activo con health checks

## 📊 Monitoreo

### Health Check Endpoint
El bot expone un endpoint de health check en el puerto configurado (default 10000):

```
GET http://tu-servicio.onrender.com:10000/
```

Respuesta esperada:
```json
{
  "status": "ok",
  "bot": "running",
  "timestamp": "2026-02-13T20:00:00.000000",
  "pid": 12345
}
```

## 🔄 Redespliegue

Cada vez que haces `git push`, Render automáticamente:
1. Detecta el cambio
2. Ejecuta `pip install -r requirements.txt`
3. Ejecuta `python bot.py`
4. El bot se reinicia con la nueva versión

**Tiempo estimado**: 2-3 minutos

## 📝 Notas Adicionales

- El bot usa polling (no webhooks) para recibir mensajes
- Las notificaciones se envían cada hora (3600 segundos)
- Los logs se mantienen en Render por tiempo limitado
- Para producción, considera usar un plan de pago para evitar que el servicio se duerma
