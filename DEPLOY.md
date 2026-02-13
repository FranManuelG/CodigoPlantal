# 🚀 Desplegar Bot en Render.com

## Preparación

### 1. Crear repositorio en GitHub
Primero, sube tu código a GitHub:

```bash
cd c:\dev\CascadeProjects\windsurf-project\telegram_plant_bot
git init
git add .
git commit -m "Initial commit - Telegram Plant Bot"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/telegram-plant-bot.git
git push -u origin main
```

**IMPORTANTE:** Asegúrate de que el archivo `.env` NO se suba (ya está en `.gitignore`).

## Desplegar en Render.com

### 2. Crear cuenta en Render
1. Ve a [dashboard.render.com](https://dashboard.render.com)
2. Regístrate con tu cuenta de GitHub

### 3. Crear nuevo Background Worker
1. Click en **"New +"** → **"Background Worker"**
2. Conecta tu repositorio de GitHub
3. Selecciona el repositorio `telegram-plant-bot`

### 4. Configurar el servicio

**Build & Deploy:**
- **Name:** `telegram-plant-bot` (o el nombre que prefieras)
- **Region:** Frankfurt (o el más cercano a ti)
- **Branch:** `main`
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python bot.py`

**Plan:**
- Selecciona **Free** (suficiente para este bot)

### 5. Variables de entorno
En la sección **Environment Variables**, agrega:

- **Key:** `TELEGRAM_BOT_TOKEN`
- **Value:** `8597101676:AAGOa2tI5frprwUX3iINiSTGuoL4AMwBXKI`

- **Key:** `DATABASE_URL`
- **Value:** Tu URL de Supabase PostgreSQL (ver MIGRACION_SUPABASE.md)

### 6. Deploy
1. Click en **"Create Web Service"**
2. Render comenzará a construir y desplegar tu bot
3. Espera a que el estado cambie a **"Live"** (tarda 2-3 minutos)

## ⚠️ Importante sobre el plan Free de Render

El plan gratuito de Render tiene estas características:
- ✅ **750 horas gratis al mes** (suficiente para estar 24/7)
- ⚠️ **Se duerme después de 15 minutos de inactividad**
- ⚠️ **Tarda ~30 segundos en despertar**

### ¿Necesitas cron-job?

**NO necesitas cron-job** porque:
- Los bots de Telegram con **polling** mantienen una conexión activa
- Render detecta esta actividad y NO pone el servicio a dormir
- El bot estará siempre despierto recibiendo mensajes

Si aún así quieres usar cron-job (no recomendado para este caso):
1. Ve a [cron-job.org](https://cron-job.org)
2. Crea un job que haga ping a tu URL de Render cada 14 minutos
3. URL: `https://telegram-plant-bot.onrender.com` (tu URL de Render)

## 🔍 Verificar que funciona

1. Ve a los **Logs** en Render
2. Deberías ver: `Bot iniciado...`
3. Abre Telegram y busca tu bot
4. Envía `/start`

## 📊 Monitoreo

En el dashboard de Render puedes ver:
- **Logs en tiempo real**
- **Uso de CPU y memoria**
- **Estado del servicio**

## 🔄 Actualizar el bot

Cuando hagas cambios en el código:

```bash
git add .
git commit -m "Descripción de cambios"
git push
```

Render automáticamente detectará los cambios y redesplegará el bot.

## 🐛 Solución de problemas

**El bot no responde:**
- Revisa los logs en Render
- Verifica que `TELEGRAM_BOT_TOKEN` esté configurado correctamente
- Asegúrate de que el servicio esté en estado "Live"

**Error de base de datos:**
- Si usas SQLite local, la base de datos se reinicia con cada deploy
- **Recomendado:** Usa Supabase PostgreSQL para persistencia permanente (ver MIGRACION_SUPABASE.md)
- Supabase es gratuito y no expira (a diferencia de Render PostgreSQL que expira a los 90 días)

**El servicio se duerme:**
- Esto NO debería pasar con polling activo
- Si pasa, considera usar webhook en lugar de polling

## 🎯 Alternativa: Usar Webhook (Opcional)

Si prefieres usar webhook en lugar de polling (más eficiente):

1. Modifica `bot.py` para usar webhook
2. No necesitarás cron-job
3. El bot responderá instantáneamente

¿Quieres que te ayude a configurar webhook?

---

## 📝 Resumen de comandos

```bash
# Subir a GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/telegram-plant-bot.git
git push -u origin main

# Actualizar después de cambios
git add .
git commit -m "Descripción"
git push
```

¡Tu bot estará funcionando 24/7 en Render! 🌿
