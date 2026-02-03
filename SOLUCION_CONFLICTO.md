# 🔧 Solución al Error de Conflicto de Instancias

## ❌ Error que estás viendo:

```
telegram.error.Conflict: Conflict: terminated by other getUpdates request; 
make sure that only one bot instance is running
```

## 🔍 Causa del Problema

Este error ocurre cuando **hay múltiples instancias del bot ejecutándose simultáneamente**, intentando recibir actualizaciones de Telegram al mismo tiempo. Telegram solo permite una conexión de polling activa por bot.

**Esto también explica por qué las plantas desaparecen:** Cada instancia tiene su propia base de datos SQLite separada.

## ✅ Solución Paso a Paso

### 1. Verifica servicios en Render

Ve a [dashboard.render.com](https://dashboard.render.com) y:

1. Revisa cuántos servicios tienes con el bot de plantas
2. **Debes tener SOLO UNO activo**
3. Si ves múltiples servicios:
   - Deja solo uno activo
   - **Suspende o elimina los demás:**
     - Settings → Suspend Service (o Delete Service)

### 2. Verifica que no haya bot local ejecutándose

Aunque dijiste que no tienes bot local, verifica:

```powershell
# En PowerShell, busca procesos de Python
Get-Process python*
```

Si ves algún proceso de Python ejecutando el bot, detenlo con Ctrl+C.

### 3. Redeploy limpio en Render

Una vez que tengas SOLO un servicio:

1. Ve a tu servicio en Render
2. Click en **"Manual Deploy"** → **"Clear build cache & deploy"**
3. Espera a que termine el deploy (2-3 minutos)
4. Verifica los logs - deberías ver:
   ```
   Bot iniciado...
   Health check server running on port 10000
   Iniciando polling...
   ```

### 4. Prueba el bot

1. Abre Telegram
2. Busca tu bot
3. Envía `/start`
4. Prueba `/agregar` para agregar una planta
5. Usa `/plantas` para verificar que aparece

## 🛡️ Mejoras Implementadas

He actualizado el código con:

1. **Reintentos automáticos** - Si hay un conflicto temporal, el bot reintenta en 10 segundos
2. **Mejor logging** - Ahora puedes ver exactamente qué está pasando
3. **Manejo de errores** - El bot no se cae completamente ante errores

## ⚠️ Importante sobre SQLite en Render

**SQLite se reinicia con cada deploy** en Render. Esto significa:

- ✅ Funciona perfectamente para desarrollo/pruebas
- ❌ Los datos se pierden cuando redespliegas
- ❌ No es ideal para producción a largo plazo

### Opciones para persistencia de datos:

#### Opción A: Usar PostgreSQL (Recomendado para producción)
- Render ofrece PostgreSQL gratuito
- Los datos persisten entre deploys
- Más robusto para múltiples usuarios

#### Opción B: Mantener SQLite (OK para uso personal)
- Funciona bien si no redespliegas frecuentemente
- Simple y sin configuración adicional
- Los datos se mantienen mientras el servicio esté corriendo

## 🔍 Cómo Verificar que Solo Hay Una Instancia

En los logs de Render, busca líneas como:
```
Iniciando bot con PID: 12345
Bot iniciado...
Iniciando polling...
```

Deberías ver esto **solo una vez** al inicio. Si ves múltiples líneas "Bot iniciado..." en paralelo, significa que hay múltiples instancias.

## 📝 Checklist de Verificación

- [ ] Solo un servicio activo en Render
- [ ] No hay bot ejecutándose localmente
- [ ] Deploy limpio completado
- [ ] Logs muestran solo una instancia iniciándose
- [ ] Bot responde a `/start` en Telegram
- [ ] Puedes agregar plantas con `/agregar`
- [ ] Las plantas aparecen con `/plantas`

## 🆘 Si el Problema Persiste

1. **Elimina completamente el servicio en Render**
2. **Crea uno nuevo desde cero:**
   - New + → Web Service
   - Conecta tu repositorio
   - Configura las variables de entorno
   - Deploy

3. **Verifica el token del bot:**
   - Ve a @BotFather en Telegram
   - Usa `/mybots` → Selecciona tu bot
   - Verifica que el token sea correcto

---

## 📊 Próximos Pasos Recomendados

Una vez que el bot funcione correctamente:

1. **Considera migrar a PostgreSQL** si planeas usar el bot a largo plazo
2. **Configura backups** de la base de datos
3. **Monitorea los logs** regularmente en Render

¿Necesitas ayuda para configurar PostgreSQL? Avísame y te guío paso a paso.
