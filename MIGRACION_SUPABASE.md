# 🌱 Migración a Supabase PostgreSQL

## ¿Por qué Supabase?

- ✅ **Gratuito permanente** (500MB de base de datos)
- ✅ PostgreSQL completo con todas las funcionalidades
- ✅ Dashboard web para gestionar datos
- ✅ No expira (a diferencia de Render que expira a los 90 días)
- ✅ Fácil de configurar

---

## Paso 1: Crear cuenta en Supabase

1. Ve a **https://supabase.com**
2. Click en **"Start your project"**
3. Regístrate con GitHub o email
4. Verifica tu email

---

## Paso 2: Crear un nuevo proyecto

1. Click en **"New Project"**
2. Configura:
   - **Name:** `plant-bot` (o el nombre que prefieras)
   - **Database Password:** Genera una contraseña segura (guárdala bien)
   - **Region:** Elige el más cercano a ti (ej: Europe West)
   - **Pricing Plan:** **Free** (seleccionado por defecto)
3. Click en **"Create new project"**
4. Espera 2-3 minutos mientras se crea el proyecto

---

## Paso 3: Obtener la URL de conexión

1. En tu proyecto, ve a **Settings** (⚙️) en el menú lateral
2. Click en **"Database"**
3. Busca la sección **"Connection string"**
4. Selecciona el modo **"URI"**
5. Copia la URL que se ve así:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```
6. **IMPORTANTE:** Reemplaza `[YOUR-PASSWORD]` con la contraseña que creaste en el paso 2

---

## Paso 4: Configurar variables de entorno

### En desarrollo local:

Crea o edita el archivo `.env`:

```env
TELEGRAM_TOKEN=tu_token_de_telegram
DATABASE_URL=postgresql://postgres.xxxxx:TU_PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

### En Render.com:

1. Ve a tu Web Service en Render
2. Click en **"Environment"**
3. Añade la variable:
   - **Key:** `DATABASE_URL`
   - **Value:** La URL completa de Supabase
4. Click en **"Save Changes"**

---

## Paso 5: Migrar datos existentes (OPCIONAL)

Si ya tienes datos en SQLite (`plants.db`), ejecuta el script de migración:

```bash
python migrate_to_postgres.py
```

Este script:
- Lee todos los datos de `plants.db`
- Los inserta en Supabase PostgreSQL
- Mantiene todos los IDs y relaciones

**NOTA:** Si es la primera vez que usas el bot, puedes saltarte este paso.

---

## Paso 6: Desplegar en Render

1. Haz commit de los cambios:
   ```bash
   git add .
   git commit -m "Migración a Supabase PostgreSQL"
   git push
   ```

2. Render detectará los cambios y redesplegará automáticamente

3. Verifica los logs en Render para asegurarte de que todo funciona

---

## Verificación

Para verificar que todo funciona:

1. Envía `/start` al bot en Telegram
2. Añade una planta de prueba con `/add`
3. Ve al dashboard de Supabase:
   - Click en **"Table Editor"** en el menú lateral
   - Deberías ver las tablas: `plants`, `watering_log`, `plant_photos`, etc.
   - Verifica que tu planta aparece en la tabla `plants`

---

## Ventajas de Supabase

- **Dashboard visual:** Puedes ver y editar datos directamente desde el navegador
- **SQL Editor:** Ejecuta queries SQL personalizadas
- **Backups automáticos:** Supabase hace backups automáticos
- **API REST automática:** Si en el futuro quieres hacer una app web
- **Sin límite de tiempo:** El plan gratuito no expira

---

## Solución de problemas

### Error: "could not connect to server"
- Verifica que la URL de conexión sea correcta
- Asegúrate de haber reemplazado `[YOUR-PASSWORD]` con tu contraseña real

### Error: "password authentication failed"
- La contraseña en la URL está incorrecta
- Ve a Supabase → Settings → Database → Reset database password

### Las tablas no se crean
- El código crea las tablas automáticamente al iniciar
- Verifica los logs en Render para ver si hay errores

---

## Comandos útiles

Ver logs en Render:
```bash
# Los logs se ven automáticamente en el dashboard de Render
```

Conectarse a la base de datos desde terminal (opcional):
```bash
psql "postgresql://postgres.xxxxx:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
```

---

## Próximos pasos

Una vez migrado a Supabase:
- ✅ Tu bot funcionará igual que antes
- ✅ Los datos estarán en la nube de forma permanente
- ✅ Puedes eliminar el archivo `plants.db` local
- ✅ Puedes gestionar datos desde el dashboard de Supabase
