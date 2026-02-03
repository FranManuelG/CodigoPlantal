# ⏰ Configurar Cron-Job para Mantener el Bot Activo

## 🎯 Objetivo

El plan gratuito de Render pone los servicios a dormir después de 15 minutos de inactividad. Aunque el bot tiene polling activo, necesitamos un cron-job externo que haga ping al servidor HTTP cada 10-14 minutos para mantenerlo despierto.

## 📋 Pasos para Configurar

### 1. Obtén la URL de tu servicio en Render

1. Ve a tu servicio en [dashboard.render.com](https://dashboard.render.com)
2. Copia la URL del servicio (algo como: `https://telegram-plant-bot.onrender.com`)
3. **Importante:** Anota esta URL completa

### 2. Configura Cron-Job.org (Gratuito)

#### Opción A: Cron-Job.org (Recomendado)

1. **Regístrate en [cron-job.org](https://cron-job.org/en/)**
   - Es gratuito
   - Permite hasta 50 cron jobs
   - Muy confiable

2. **Crea un nuevo Cron Job:**
   - Click en **"Create cronjob"**
   
3. **Configuración:**
   - **Title:** `Keep Plant Bot Awake`
   - **URL:** `https://TU-SERVICIO.onrender.com/` (reemplaza con tu URL)
   - **Schedule:**
     - Selecciona **"Every 14 minutes"**
     - O configura manualmente: `*/14 * * * *`
   - **Request method:** `GET`
   - **Request timeout:** `30 seconds`
   
4. **Configuración avanzada (opcional):**
   - **Notifications:** Activa para recibir alertas si falla
   - **Execution history:** Mantén activado para ver el historial

5. **Guarda y activa** el cron job

#### Opción B: UptimeRobot (Alternativa)

1. **Regístrate en [uptimerobot.com](https://uptimerobot.com/)**
   - Gratuito para hasta 50 monitores
   - Revisa cada 5 minutos

2. **Crea un nuevo Monitor:**
   - Click en **"Add New Monitor"**
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `Plant Bot`
   - **URL:** `https://TU-SERVICIO.onrender.com/`
   - **Monitoring Interval:** `5 minutes` (mínimo en plan gratuito)

3. **Guarda** el monitor

#### Opción C: Cron-Job.de

1. **Regístrate en [cron-job.de](https://cron-job.de/)**
2. **Crea un nuevo Cron Job:**
   - **URL:** Tu URL de Render
   - **Interval:** Cada 10 minutos
   - **Method:** GET

### 3. Verifica que Funciona

#### En los Logs de Render:

Deberías ver cada 10-14 minutos:
```
Health check recibido desde [IP del servicio de cron]
```

#### En el Dashboard del Cron-Job:

- Estado: ✅ Success (200 OK)
- Response: `{"status":"ok","bot":"running","timestamp":"...","pid":...}`

### 4. Prueba el Endpoint Manualmente

Abre en tu navegador:
```
https://TU-SERVICIO.onrender.com/
```

Deberías ver algo como:
```json
{
  "status": "ok",
  "bot": "running",
  "timestamp": "2026-02-03T15:30:00.123456",
  "pid": 12345
}
```

## 📊 Configuración Recomendada

### Frecuencia Óptima:
- **Cada 10-14 minutos** es ideal
- No uses menos de 5 minutos (innecesario)
- No uses más de 14 minutos (el servicio se dormirá)

### Múltiples Servicios de Cron (Redundancia):
Para máxima confiabilidad, puedes usar 2 servicios:
1. **Cron-Job.org** - Cada 14 minutos
2. **UptimeRobot** - Cada 5 minutos

Así si uno falla, el otro mantiene el bot despierto.

## 🔍 Monitoreo

### En Render:
1. Ve a tu servicio → **Logs**
2. Busca: `Health check recibido`
3. Deberías ver entradas regulares cada 10-14 minutos

### En el Servicio de Cron:
- Revisa el historial de ejecuciones
- Todas deberían mostrar **200 OK**
- Si ves errores 503/504, el servicio se durmió

## ⚠️ Solución de Problemas

### El bot sigue durmiéndose:

1. **Verifica que el cron esté activo:**
   - Revisa el dashboard del servicio de cron
   - Confirma que las ejecuciones están ocurriendo

2. **Verifica la URL:**
   - Debe ser la URL completa de Render
   - Debe incluir `https://`
   - No debe tener `/` extra al final

3. **Revisa los logs de Render:**
   - ¿Ves los health checks llegando?
   - ¿Hay errores en el bot?

### El cron falla (503/504):

- Esto significa que el servicio ya se durmió
- Reduce el intervalo a 10 minutos
- Considera usar múltiples servicios de cron

### El bot responde lento:

- Normal en plan gratuito de Render
- Si se durmió, tarda ~30 segundos en despertar
- El cron debería prevenir esto

## 💡 Alternativas al Cron-Job

### Opción 1: Upgrade a Plan Pagado de Render
- $7/mes por servicio
- No se duerme nunca
- Más recursos (CPU/RAM)

### Opción 2: Usar Webhook en lugar de Polling
- Más eficiente
- No necesita estar "despierto" constantemente
- Requiere modificar el código del bot

### Opción 3: Otros Servicios de Hosting
- **Railway.app** - 500 horas gratis/mes
- **Fly.io** - Plan gratuito generoso
- **Heroku** - Ya no tiene plan gratuito

## 📝 Resumen de Configuración

```
Servicio: Cron-Job.org
URL: https://tu-bot.onrender.com/
Frecuencia: Cada 14 minutos
Método: GET
Timeout: 30 segundos
```

## ✅ Checklist Final

- [ ] Bot desplegado en Render y funcionando
- [ ] URL del servicio copiada
- [ ] Cuenta creada en servicio de cron
- [ ] Cron job configurado y activo
- [ ] Frecuencia: cada 10-14 minutos
- [ ] Health checks visibles en logs de Render
- [ ] Bot responde en Telegram sin demoras
- [ ] Notificaciones configuradas (opcional)

---

## 🎉 ¡Listo!

Una vez configurado, tu bot permanecerá activo 24/7 y responderá instantáneamente a los comandos en Telegram.

**Tiempo de configuración:** ~5 minutos  
**Costo:** $0 (completamente gratuito)  
**Mantenimiento:** Ninguno (automático)
