# 🎉 Nuevas Funcionalidades del Bot

## 📸 Sistema de Fotos

### Comandos:
- `/foto` - Agregar foto a una planta
- `/fotos` - Ver galería de fotos de tus plantas

### Cómo usar:
1. Usa `/foto` y selecciona la planta
2. Envía la foto (puedes agregar un texto como descripción)
3. La foto se guarda con fecha automáticamente
4. Usa `/fotos` para ver todas las fotos organizadas por planta

### Características:
- Múltiples fotos por planta
- Historial visual del crecimiento
- Captions opcionales para cada foto
- Fecha automática de cada foto

---

## 📍 Grupos y Ubicaciones

### Comandos:
- `/crear_grupo` - Crear un nuevo grupo/ubicación
- `/grupos` - Ver todos tus grupos con cantidad de plantas

### Cómo usar:
1. Crea grupos como "Sala", "Balcón", "Jardín", "Oficina"
2. Organiza tus plantas por ubicación
3. Ve cuántas plantas tienes en cada lugar

### Ejemplos de grupos:
- 🏠 Por habitación: Sala, Cocina, Dormitorio
- 🌞 Por luz: Sol directo, Sombra, Semi-sombra
- 💧 Por riego: Mucha agua, Poca agua
- 🌱 Por tipo: Suculentas, Helechos, Flores

---

## 🔔 Notificaciones Automáticas

### Comando:
- `/notificaciones` - Activar/desactivar recordatorios

### Cómo funciona:
1. El bot revisa cada hora qué plantas necesitan riego
2. Si tienes notificaciones activadas, te envía un recordatorio
3. El mensaje incluye todas las plantas que necesitan agua
4. Puedes activar/desactivar cuando quieras

### Características:
- Recordatorios automáticos cada hora
- Solo te notifica si hay plantas pendientes
- Lista clara de qué plantas necesitan riego
- Fácil de activar/desactivar

---

## 📊 Estadísticas

### Comando:
- `/estadisticas` - Ver tus estadísticas de riego

### Información que muestra:
- 🌱 **Total de plantas** - Cuántas plantas tienes
- 💧 **Total de riegos** - Cuántos riegos has registrado
- 📅 **Días activo** - Cuántos días diferentes has regado
- 🏆 **Planta más regada** - Cuál has regado más veces
- 📈 **Promedio** - Riegos promedio por planta

### Ejemplo de salida:
```
📊 Tus estadísticas:

🌱 Total de plantas: 5
💧 Total de riegos: 47
📅 Días activo: 23
🏆 Planta más regada: Pothos (15 riegos)
📈 Promedio de riegos por planta: 9.4
```

---

## 🆕 Comandos Actualizados

### Comando de ayuda mejorado:
El comando `/ayuda` ahora está organizado por categorías:
- Gestión de Plantas
- Riego
- Fotos
- Grupos
- Otros

---

## 💡 Consejos de Uso

### Workflow recomendado:

1. **Al agregar una planta:**
   - `/agregar` → Nombre y frecuencia
   - `/foto` → Agrega una foto inicial
   - `/crear_grupo` → Asígnala a un grupo/ubicación

2. **Uso diario:**
   - Activa `/notificaciones` para recordatorios
   - Cuando riegues, usa `/regar`
   - Revisa `/pendientes` para ver qué falta

3. **Seguimiento:**
   - Agrega fotos periódicas con `/foto` para ver el progreso
   - Revisa `/estadisticas` para ver tu desempeño
   - Usa `/grupos` para organizar mejor

4. **Mantenimiento:**
   - `/historial` para ver todos los riegos
   - `/plantas` para ver estado general
   - `/fotos` para ver la evolución visual

---

## 🔄 Migración desde Versión Anterior

Si ya tenías plantas en la versión anterior:
- ✅ Todas tus plantas se mantienen
- ✅ Todo el historial de riegos se conserva
- ✅ Solo se agregan nuevas funcionalidades
- ✅ No necesitas hacer nada especial

Las nuevas tablas se crean automáticamente al iniciar el bot.

---

## 🐛 Solución de Problemas

**Las fotos no se guardan:**
- Asegúrate de usar primero `/foto` antes de enviar la imagen
- El bot te dirá a qué planta agregar la foto

**No recibo notificaciones:**
- Verifica que estén activadas con `/notificaciones`
- El bot revisa cada hora, ten paciencia
- Asegúrate de tener plantas que necesiten riego

**No veo mis grupos:**
- Primero crea un grupo con `/crear_grupo`
- Luego asigna plantas a ese grupo

---

## 📝 Próximas Mejoras Sugeridas

Ideas para futuras versiones:
- Asignar plantas a grupos desde el menú
- Gráficos de estadísticas
- Exportar datos a CSV
- Recordatorios a hora específica
- Integración con sensores IoT
- Compartir fotos de plantas

---

¡Disfruta las nuevas funcionalidades! 🌿💚
