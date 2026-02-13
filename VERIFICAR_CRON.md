# 🔍 Verificar que el Cron Job está Funcionando

## ⚠️ Problema: El bot se duerme periódicamente

Si el bot deja de responder cada cierto tiempo, el cron job probablemente no está funcionando correctamente.

## 📋 Checklist de Verificación

### 1. Verificar en cron-job.org

1. **Inicia sesión en [cron-job.org](http://cron-job.org/en/)**
2. **Ve a tu cron job "Keep Plant Bot Awake"**
3. **Verifica:**
   - ✅ Estado: **Enabled** (activo)
   - ✅ Frecuencia: **Every 14 minutes** o `*/14 * * * *`
   - ✅ URL: Tu URL de Render completa
   - ✅ Últimas ejecuciones: **200 OK** (verde)

### 2. Verificar la URL del Cron Job

**URL correcta debe ser:**
```
https://tu-servicio.onrender.com/
```

**Verifica que NO tenga:**
- ❌ Puerto al final (`:10000`)
- ❌ Doble barra (`//`)
- ❌ Espacios
- ❌ HTTP en lugar de HTTPS

### 3. Probar el Endpoint Manualmente

Abre en tu navegador:
```
https://tu-servicio.onrender.com/
```

**Deberías ver:**
```json
{
  "status": "ok",
  "bot": "running",
  "timestamp": "2026-02-13T21:00:00.000000",
  "pid": 12345,
  "uptime_seconds": 3600,
  "uptime_minutes": 60.0,
  "last_message": "2026-02-13T20:30:00.000000",
  "database": "connected"
}
```

### 4. Verificar Logs de Render

1. **Ve a Render Dashboard → Tu servicio → Logs**
2. **Busca:** `✓ Health check desde`
3. **Deberías ver entradas cada 14 minutos:**

```
2026-02-13 21:00:00 - __main__ - INFO - ✓ Health check desde 1.2.3.4 - Uptime: 60.0min
2026-02-13 21:14:00 - __main__ - INFO - ✓ Health check desde 1.2.3.4 - Uptime: 74.0min
2026-02-13 21:28:00 - __main__ - INFO - ✓ Health check desde 1.2.3.4 - Uptime: 88.0min
```

### 5. Verificar Tipo de Servicio en Render

**IMPORTANTE:** El servicio debe estar configurado como **Web Service** (no Background Worker) para que el cron job funcione.

1. Ve a tu servicio en Render
2. Settings → Service Type
3. Debe ser: **Web Service**

## 🚨 Problemas Comunes

### Problema 1: Cron Job muestra 503/504

**Causa:** El servicio ya se durmió antes de que llegara el ping

**Solución:**
1. Reduce el intervalo a **10 minutos** en lugar de 14
2. O añade un segundo cron job de respaldo

### Problema 2: Cron Job muestra 200 OK pero el bot no responde

**Causa:** El health check responde pero el bot de Telegram está caído

**Solución:**
1. Revisa los logs de Render para ver errores
2. Verifica que veas: `BOT LISTO Y ESPERANDO MENSAJES`
3. Prueba reiniciar el servicio manualmente en Render

### Problema 3: No veo logs de health check en Render

**Causa:** El cron job no está llegando al servidor

**Solución:**
1. Verifica la URL en cron-job.org
2. Asegúrate de que sea HTTPS (no HTTP)
3. Prueba la URL manualmente en tu navegador

### Problema 4: El bot funciona pero se duerme después de 15 minutos

**Causa:** Render en plan gratuito duerme servicios Web después de 15 minutos de inactividad

**Solución:**
1. El cron job debe estar activo y funcionando cada 14 minutos
2. Si no funciona, considera:
   - Upgrade a plan de pago ($7/mes)
   - Usar otro servicio de hosting (Railway, Fly.io)

## ✅ Configuración Correcta

Si todo está bien configurado, deberías ver:

**En cron-job.org:**
- Estado: Enabled ✅
- Últimas 10 ejecuciones: Todas 200 OK ✅
- Próxima ejecución: En menos de 14 minutos ✅

**En Render Logs:**
- Health checks cada 14 minutos ✅
- `BOT LISTO Y ESPERANDO MENSAJES` ✅
- Sin errores de conexión ✅

**En Telegram:**
- El bot responde instantáneamente ✅
- No hay demoras ✅

## 🔧 Solución Alternativa: Múltiples Cron Jobs

Para máxima confiabilidad, configura 2 servicios:

### Cron Job 1: cron-job.org
- Frecuencia: Cada 14 minutos
- URL: Tu servicio de Render

### Cron Job 2: UptimeRobot
1. Regístrate en [uptimerobot.com](https://uptimerobot.com)
2. Crea monitor HTTP(s)
3. URL: Tu servicio de Render
4. Intervalo: 5 minutos

Así si uno falla, el otro mantiene el servicio activo.

## 📊 Monitoreo Continuo

**Revisa cada día:**
1. Historial de cron-job.org (todas deben ser 200 OK)
2. Logs de Render (health checks regulares)
3. Prueba el bot en Telegram

**Si el bot deja de responder:**
1. Ve a Render y revisa los logs
2. Busca errores o el mensaje de que se durmió
3. Verifica el historial del cron job
4. Reinicia el servicio manualmente si es necesario

---

## 💡 Mejora Recomendada

Si el problema persiste, considera cambiar a **Railway.app** o **Fly.io** que tienen planes gratuitos más generosos y no duermen los servicios tan agresivamente.
