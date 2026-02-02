# 🌱 Bot de Telegram para Control de Riego de Plantas

Bot de Telegram que te ayuda a gestionar el riego de tus plantas, registrar riegos y recibir recordatorios.

## 🚀 Características

- ✅ Agregar plantas con frecuencia de riego personalizada
- 💧 Registrar riegos de forma sencilla
- 📊 Ver historial de riegos
- ⚠️ Ver plantas que necesitan riego
- 🗑️ Eliminar plantas
- 📱 Interfaz intuitiva con teclados personalizados

## 📋 Requisitos

- Python 3.8 o superior
- Una cuenta de Telegram
- Token de bot de Telegram (obtenido de @BotFather)

## 🔧 Instalación

1. **Clona o descarga este proyecto**

2. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

3. **Crea tu bot en Telegram:**
   - Abre Telegram y busca @BotFather
   - Envía el comando `/newbot`
   - Sigue las instrucciones y guarda el token que te proporciona

4. **Configura el token:**
   - Copia el archivo `.env.example` a `.env`:
   ```bash
   copy .env.example .env
   ```
   - Edita el archivo `.env` y reemplaza `tu_token_aqui` con tu token real

5. **Ejecuta el bot:**
```bash
python bot.py
```

## 📱 Comandos Disponibles

- `/start` - Inicia el bot y muestra mensaje de bienvenida
- `/ayuda` - Muestra todos los comandos disponibles
- `/agregar` - Agrega una nueva planta
- `/plantas` - Lista todas tus plantas con su estado
- `/regar` - Registra que regaste una planta
- `/historial` - Muestra el historial de riegos
- `/pendientes` - Muestra plantas que necesitan riego
- `/eliminar <nombre>` - Elimina una planta
- `/cancelar` - Cancela la operación actual

## 💡 Uso Básico

1. **Agregar una planta:**
   - Envía `/agregar`
   - Escribe el nombre de tu planta
   - Indica cada cuántos días necesita riego

2. **Registrar un riego:**
   - Envía `/regar`
   - Selecciona la planta del teclado

3. **Ver estado de tus plantas:**
   - Envía `/plantas` para ver todas
   - Envía `/pendientes` para ver solo las que necesitan riego

## 🗄️ Base de Datos

El bot utiliza SQLite para almacenar:
- Información de plantas (nombre, frecuencia de riego)
- Historial de riegos
- Asociación con usuarios de Telegram

La base de datos se crea automáticamente en `plants.db`.

## 🔒 Seguridad

- Cada usuario solo puede ver y gestionar sus propias plantas
- El token del bot debe mantenerse privado
- No compartas tu archivo `.env`

## 🛠️ Estructura del Proyecto

```
telegram_plant_bot/
├── bot.py              # Lógica principal del bot
├── database.py         # Gestión de base de datos
├── requirements.txt    # Dependencias
├── .env.example       # Ejemplo de configuración
├── .env               # Tu configuración (no incluir en git)
└── README.md          # Esta documentación
```

## 🚀 Mejoras Futuras

Posibles extensiones del bot:
- Notificaciones automáticas cuando una planta necesite riego
- Agregar fotos de las plantas
- Estadísticas de riego
- Exportar datos a CSV
- Soporte para múltiples tipos de cuidados (fertilización, poda, etc.)

## 🐛 Solución de Problemas

**El bot no responde:**
- Verifica que el token en `.env` sea correcto
- Asegúrate de que el bot esté ejecutándose
- Revisa los logs en la consola

**Error de base de datos:**
- Elimina el archivo `plants.db` y reinicia el bot
- Se creará una nueva base de datos limpia

## 📝 Licencia

Este proyecto es de código abierto y está disponible para uso personal.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Siéntete libre de mejorar el código.

---

¡Disfruta cuidando tus plantas! 🌿💚
