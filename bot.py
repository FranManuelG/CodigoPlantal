import os
import logging
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)
from database import Database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PLANT_NAME, PLANT_DAYS, SELECTING_PLANT, PHOTO_PLANT, GROUP_NAME, GROUP_ASSIGN = range(6)

menu_buttons = ['🌱 Agregar Planta', '💧 Regar', '📋 Mis Plantas', '⏰ Pendientes', '📊 Estadísticas', '📸 Fotos', '❓ Ayuda']
menu_filter = ~filters.Regex('^(' + '|'.join([btn.replace('(', r'\(').replace(')', r'\)').replace('?', r'\?') for btn in menu_buttons]) + ')$')

class PlantBot:
    def __init__(self, token: str):
        self.token = token
        self.db = Database()
        self.application = Application.builder().token(token).build()
        self._setup_handlers()
        self.notification_task = None
    
    def get_main_menu(self):
        keyboard = [
            ['🌱 Agregar Planta', '💧 Regar'],
            ['📋 Mis Plantas', '⏰ Pendientes'],
            ['📊 Estadísticas', '📸 Fotos'],
            ['❓ Ayuda']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    def _setup_handlers(self):
        add_plant_handler = ConversationHandler(
            entry_points=[
                CommandHandler('agregar', self.add_plant_start),
                MessageHandler(filters.Regex('^🌱 Agregar Planta$'), self.add_plant_start)
            ],
            states={
                PLANT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & menu_filter, self.add_plant_name)],
                PLANT_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND & menu_filter, self.add_plant_days)],
            },
            fallbacks=[CommandHandler('cancelar', self.cancel)],
        )
        
        regar_handler = ConversationHandler(
            entry_points=[
                CommandHandler('regar', self.water_plant_start),
                MessageHandler(filters.Regex('^💧 Regar$'), self.water_plant_start)
            ],
            states={
                SELECTING_PLANT: [MessageHandler(filters.TEXT & ~filters.COMMAND & menu_filter, self.water_plant_select)],
            },
            fallbacks=[CommandHandler('cancelar', self.cancel)],
        )
        
        photo_handler = ConversationHandler(
            entry_points=[CommandHandler('foto', self.add_photo_start)],
            states={
                PHOTO_PLANT: [MessageHandler(filters.TEXT & ~filters.COMMAND & menu_filter, self.add_photo_select_plant)],
            },
            fallbacks=[CommandHandler('cancelar', self.cancel)],
        )
        
        group_handler = ConversationHandler(
            entry_points=[CommandHandler('crear_grupo', self.create_group_start)],
            states={
                GROUP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & menu_filter, self.create_group_name)],
            },
            fallbacks=[CommandHandler('cancelar', self.cancel)],
        )
        
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('menu', self.show_menu))
        self.application.add_handler(CommandHandler('ayuda', self.help_command))
        self.application.add_handler(CommandHandler('plantas', self.list_plants))
        self.application.add_handler(CommandHandler('historial', self.watering_history))
        self.application.add_handler(CommandHandler('eliminar', self.delete_plant))
        self.application.add_handler(CommandHandler('pendientes', self.pending_plants))
        self.application.add_handler(CommandHandler('fotos', self.view_photos))
        self.application.add_handler(CommandHandler('grupos', self.list_groups))
        self.application.add_handler(CommandHandler('estadisticas', self.show_stats))
        self.application.add_handler(CommandHandler('notificaciones', self.toggle_notifications))
        self.application.add_handler(MessageHandler(filters.Regex('^📋 Mis Plantas$'), self.list_plants))
        self.application.add_handler(MessageHandler(filters.Regex('^⏰ Pendientes$'), self.pending_plants))
        self.application.add_handler(MessageHandler(filters.Regex('^📊 Estadísticas$'), self.show_stats))
        self.application.add_handler(MessageHandler(filters.Regex('^📸 Fotos$'), self.view_photos))
        self.application.add_handler(MessageHandler(filters.Regex('^❓ Ayuda$'), self.help_command))
        self.application.add_handler(add_plant_handler)
        self.application.add_handler(regar_handler)
        self.application.add_handler(photo_handler)
        self.application.add_handler(group_handler)
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.receive_photo))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(
            f'¡Hola {user.first_name}! 🌱\n\n'
            'Soy tu asistente para el cuidado de plantas.\n'
            'Usa los botones del menú o /ayuda para ver todos los comandos.',
            reply_markup=self.get_main_menu()
        )
    
    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            '🌿 Menú principal:',
            reply_markup=self.get_main_menu()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            '🌿 *Comandos disponibles:*\n\n'
            '*Gestión de Plantas:*\n'
            '/agregar \\- Agregar una nueva planta\n'
            '/plantas \\- Ver todas tus plantas\n'
            '/eliminar \\- Eliminar una planta\n\n'
            '*Riego:*\n'
            '/regar \\- Registrar que regaste una planta\n'
            '/historial \\- Ver historial de riegos\n'
            '/pendientes \\- Ver plantas que necesitan riego\n\n'
            '*Fotos:*\n'
            '/foto \\- Agregar foto a una planta\n'
            '/fotos \\- Ver fotos de tus plantas\n\n'
            '*Grupos:*\n'
            '/crear\\_grupo \\- Crear grupo/ubicación\n'
            '/grupos \\- Ver grupos y plantas\n\n'
            '*Otros:*\n'
            '/estadisticas \\- Ver estadísticas de riego\n'
            '/notificaciones \\- Activar/desactivar recordatorios\n'
            '/ayuda \\- Mostrar este mensaje\n'
            '/cancelar \\- Cancelar operación actual'
        )
        await update.message.reply_text(help_text, parse_mode='MarkdownV2', reply_markup=self.get_main_menu())
    
    async def add_plant_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            '🌱 ¿Cómo se llama tu planta?\n'
            '(Usa /cancelar para cancelar)',
            reply_markup=ReplyKeyboardRemove()
        )
        return PLANT_NAME
    
    async def add_plant_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['plant_name'] = update.message.text
        await update.message.reply_text(
            f'Perfecto! ¿Cada cuántos días necesita riego "{update.message.text}"?\n'
            '(Escribe un número, por ejemplo: 3)'
        )
        return PLANT_DAYS
    
    async def add_plant_days(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            days = int(update.message.text)
            if days <= 0:
                await update.message.reply_text('Por favor, ingresa un número mayor a 0.')
                return PLANT_DAYS
            
            plant_name = context.user_data['plant_name']
            user_id = update.effective_user.id
            
            logger.info(f'Agregando planta: user_id={user_id}, name={plant_name}, days={days}')
            plant_id = self.db.add_plant(user_id, plant_name, days)
            logger.info(f'Planta agregada con ID: {plant_id}')
            
            plants = self.db.get_user_plants(user_id)
            logger.info(f'Usuario {user_id} ahora tiene {len(plants)} plantas')
            
            await update.message.reply_text(
                f'✅ ¡Planta "{plant_name}" agregada!\n'
                f'Frecuencia de riego: cada {days} día(s)\n\n'
                'Usa /foto para agregar una foto de tu planta.',
                reply_markup=self.get_main_menu()
            )
            
            context.user_data.clear()
            return ConversationHandler.END
            
        except ValueError:
            await update.message.reply_text(
                'Por favor, ingresa un número válido.\n'
                '¿Cada cuántos días necesita riego?'
            )
            return PLANT_DAYS
    
    async def list_plants(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        logger.info(f'Listando plantas para user_id={user_id}')
        plants = self.db.get_user_plants(user_id)
        logger.info(f'Encontradas {len(plants)} plantas para user_id={user_id}')
        
        if not plants:
            await update.message.reply_text(
                '🌵 No tienes plantas registradas aún.\n'
                'Usa /agregar para agregar tu primera planta.'
            )
            return
        
        message = '🌿 *Tus plantas:*\n\n'
        for plant in plants:
            plant_id, name, days, last_watered = plant
            
            if last_watered:
                last_date = datetime.fromisoformat(last_watered)
                days_ago = (datetime.now() - last_date).days
                next_water = last_date + timedelta(days=days)
                days_until = (next_water - datetime.now()).days
                
                if days_until < 0:
                    status = f'⚠️ Necesita riego (hace {abs(days_until)} días)'
                elif days_until == 0:
                    status = '💧 Necesita riego hoy'
                else:
                    status = f'✅ Próximo riego en {days_until} día(s)'
                
                message += f'🌱 *{name}*\n'
                message += f'   Frecuencia: cada {days} día(s)\n'
                message += f'   Último riego: hace {days_ago} día(s)\n'
                message += f'   {status}\n\n'
            else:
                message += f'🌱 *{name}*\n'
                message += f'   Frecuencia: cada {days} día(s)\n'
                message += f'   ⚠️ Nunca regada - ¡Riégala pronto!\n\n'
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def water_plant_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        plants = self.db.get_user_plants(user_id)
        
        if not plants:
            await update.message.reply_text(
                '🌵 No tienes plantas registradas.\n'
                'Usa /agregar para agregar una planta primero.'
            )
            return ConversationHandler.END
        
        keyboard = [[plant[1]] for plant in plants]
        keyboard.append(['Cancelar'])
        
        await update.message.reply_text(
            '💧 ¿Qué planta regaste?',
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        )
        return SELECTING_PLANT
    
    async def water_plant_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == 'Cancelar':
            await update.message.reply_text(
                'Operación cancelada.',
                reply_markup=self.get_main_menu()
            )
            return ConversationHandler.END
        
        user_id = update.effective_user.id
        plant_name = update.message.text
        
        plant = self.db.get_plant_by_name(user_id, plant_name)
        if not plant:
            await update.message.reply_text(
                'No encontré esa planta. Intenta de nuevo.',
                reply_markup=self.get_main_menu()
            )
            return ConversationHandler.END
        
        self.db.record_watering(plant[0])
        
        await update.message.reply_text(
            f'✅ ¡Riego registrado para "{plant_name}"!\n'
            f'Próximo riego recomendado: en {plant[2]} día(s)',
            reply_markup=self.get_main_menu()
        )
        return ConversationHandler.END
    
    async def watering_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        history = self.db.get_watering_history(user_id, limit=20)
        
        if not history:
            await update.message.reply_text('📊 No hay historial de riegos aún.')
            return
        
        message = '📊 *Historial de riegos:*\n\n'
        for record in history:
            plant_name, watered_at = record
            date = datetime.fromisoformat(watered_at)
            formatted_date = date.strftime('%d/%m/%Y %H:%M')
            message += f'💧 {plant_name} - {formatted_date}\n'
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def pending_plants(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        plants = self.db.get_user_plants(user_id)
        
        if not plants:
            await update.message.reply_text('🌵 No tienes plantas registradas.')
            return
        
        pending = []
        for plant in plants:
            plant_id, name, days, last_watered = plant
            
            if not last_watered:
                pending.append((name, -1))
            else:
                last_date = datetime.fromisoformat(last_watered)
                next_water = last_date + timedelta(days=days)
                days_until = (next_water - datetime.now()).days
                
                if days_until <= 0:
                    pending.append((name, days_until))
        
        if not pending:
            await update.message.reply_text(
                '✅ ¡Todas tus plantas están al día con el riego! 🌿'
            )
            return
        
        message = '⚠️ *Plantas que necesitan riego:*\n\n'
        for name, days_overdue in sorted(pending, key=lambda x: x[1]):
            if days_overdue == -1:
                message += f'🌱 {name} - Nunca regada\n'
            elif days_overdue == 0:
                message += f'🌱 {name} - Necesita riego hoy\n'
            else:
                message += f'🌱 {name} - Hace {abs(days_overdue)} día(s)\n'
        
        message += '\nUsa /regar para registrar un riego.'
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def add_photo_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        plants = self.db.get_user_plants(user_id)
        
        if not plants:
            await update.message.reply_text(
                '🌵 No tienes plantas registradas.\n'
                'Usa /agregar para agregar una planta primero.'
            )
            return ConversationHandler.END
        
        keyboard = [[plant[1]] for plant in plants]
        keyboard.append(['Cancelar'])
        
        await update.message.reply_text(
            '📸 ¿A qué planta quieres agregar una foto?',
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        )
        return PHOTO_PLANT
    
    async def add_photo_select_plant(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == 'Cancelar':
            await update.message.reply_text(
                'Operación cancelada.',
                reply_markup=self.get_main_menu()
            )
            return ConversationHandler.END
        
        user_id = update.effective_user.id
        plant_name = update.message.text
        
        plant = self.db.get_plant_by_name(user_id, plant_name)
        if not plant:
            await update.message.reply_text(
                'No encontré esa planta.',
                reply_markup=self.get_main_menu()
            )
            return ConversationHandler.END
        
        context.user_data['photo_plant_id'] = plant[0]
        context.user_data['photo_plant_name'] = plant_name
        
        await update.message.reply_text(
            f'📸 Perfecto! Ahora envía una foto de "{plant_name}"',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    async def receive_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'photo_plant_id' not in context.user_data:
            await update.message.reply_text(
                '📸 Para agregar una foto, usa primero /foto'
            )
            return
        
        plant_id = context.user_data['photo_plant_id']
        plant_name = context.user_data['photo_plant_name']
        
        photo = update.message.photo[-1]
        file_id = photo.file_id
        caption = update.message.caption
        
        self.db.add_plant_photo(plant_id, file_id, caption)
        
        await update.message.reply_text(
            f'✅ ¡Foto agregada a "{plant_name}"!\n'
            'Usa /fotos para ver todas las fotos.',
            reply_markup=self.get_main_menu()
        )
        
        context.user_data.clear()
    
    async def view_photos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        plants = self.db.get_user_plants(user_id)
        
        if not plants:
            await update.message.reply_text('🌵 No tienes plantas registradas.')
            return
        
        keyboard = []
        for plant in plants:
            plant_id, name, _, _ = plant
            photos = self.db.get_plant_photos(plant_id)
            if photos:
                keyboard.append([InlineKeyboardButton(f"📸 {name} ({len(photos)} fotos)", callback_data=f"photos_{plant_id}")])
        
        if not keyboard:
            await update.message.reply_text(
                '📸 No tienes fotos aún.\n'
                'Usa /foto para agregar fotos a tus plantas.'
            )
            return
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            '📸 *Selecciona una planta para ver sus fotos:*',
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def create_group_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            '📍 ¿Cómo quieres llamar al grupo/ubicación?\n'
            'Ejemplos: Sala, Balcón, Jardín, Oficina\n\n'
            '(Usa /cancelar para cancelar)'
        )
        return GROUP_NAME
    
    async def create_group_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        group_name = update.message.text
        user_id = update.effective_user.id
        
        self.db.create_group(user_id, group_name)
        
        await update.message.reply_text(
            f'✅ Grupo "{group_name}" creado!\n'
            'Usa /grupos para ver todos tus grupos.',
            reply_markup=self.get_main_menu()
        )
        
        context.user_data.clear()
        return ConversationHandler.END
    
    async def list_groups(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        groups = self.db.get_user_groups(user_id)
        
        if not groups:
            await update.message.reply_text(
                '📍 No tienes grupos creados.\n'
                'Usa /crear_grupo para crear uno.'
            )
            return
        
        message = '📍 *Tus grupos:*\n\n'
        for group in groups:
            group_id, name, plant_count = group
            message += f'📦 *{name}* - {plant_count} planta(s)\n'
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        stats = self.db.get_watering_stats(user_id)
        
        message = '📊 *Tus estadísticas:*\n\n'
        message += f'🌱 Total de plantas: *{stats["total_plants"]}*\n'
        message += f'💧 Total de riegos: *{stats["total_waterings"]}*\n'
        message += f'📅 Días activo: *{stats["days_active"]}*\n'
        
        if stats['most_watered'] and stats['most_watered'][0]:
            message += f'🏆 Planta más regada: *{stats["most_watered"][0]}* ({stats["most_watered"][1]} riegos)\n'
        
        if stats['total_plants'] > 0:
            avg = stats['total_waterings'] / stats['total_plants']
            message += f'📈 Promedio de riegos por planta: *{avg:.1f}*\n'
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def toggle_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        settings = self.db.get_user_settings(user_id)
        
        if settings:
            enabled, time = settings
            new_state = not enabled
        else:
            new_state = True
            time = '09:00'
        
        self.db.update_notification_settings(user_id, new_state, time)
        
        if new_state:
            await update.message.reply_text(
                f'🔔 Notificaciones activadas!\n'
                f'Recibirás recordatorios a las {time} cuando tus plantas necesiten riego.'
            )
        else:
            await update.message.reply_text(
                '🔕 Notificaciones desactivadas.'
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith('photos_'):
            plant_id = int(query.data.split('_')[1])
            photos = self.db.get_plant_photos(plant_id)
            
            for photo in photos[:5]:
                _, file_id, caption, uploaded_at = photo
                date = datetime.fromisoformat(uploaded_at).strftime('%d/%m/%Y')
                caption_text = f"📅 {date}\n{caption}" if caption else f"📅 {date}"
                
                await query.message.reply_photo(
                    photo=file_id,
                    caption=caption_text
                )
    
    async def delete_plant(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        plants = self.db.get_user_plants(user_id)
        
        if not plants:
            await update.message.reply_text('🌵 No tienes plantas para eliminar.')
            return
        
        message = '🗑️ Para eliminar una planta, usa:\n/eliminar <nombre>\n\n*Tus plantas:*\n'
        for plant in plants:
            message += f'• {plant[1]}\n'
        
        args = context.args
        if not args:
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        plant_name = ' '.join(args)
        plant = self.db.get_plant_by_name(user_id, plant_name)
        
        if not plant:
            await update.message.reply_text(f'No encontré la planta "{plant_name}".')
            return
        
        self.db.delete_plant(plant[0])
        await update.message.reply_text(f'✅ Planta "{plant_name}" eliminada.')
    
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            'Operación cancelada.',
            reply_markup=self.get_main_menu()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    async def send_notifications(self):
        while True:
            try:
                await asyncio.sleep(3600)
                
                users = self.db.get_all_users_for_notifications()
                
                for user_id in users:
                    plants = self.db.get_user_plants(user_id)
                    pending = []
                    
                    for plant in plants:
                        plant_id, name, days, last_watered = plant
                        
                        if not last_watered:
                            pending.append(name)
                        else:
                            last_date = datetime.fromisoformat(last_watered)
                            next_water = last_date + timedelta(days=days)
                            days_until = (next_water - datetime.now()).days
                            
                            if days_until <= 0:
                                pending.append(name)
                    
                    if pending:
                        message = '🔔 *Recordatorio de riego:*\n\n'
                        message += 'Las siguientes plantas necesitan riego:\n'
                        for name in pending:
                            message += f'💧 {name}\n'
                        message += '\nUsa /regar para registrar el riego.'
                        
                        try:
                            await self.application.bot.send_message(
                                chat_id=user_id,
                                text=message,
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f'Error sending notification to {user_id}: {e}')
                
            except Exception as e:
                logger.error(f'Error in notification loop: {e}')
    
    def run(self):
        logger.info('Bot iniciado...')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.notification_task = loop.create_task(self.send_notifications())
        
        while True:
            try:
                logger.info('Iniciando polling...')
                self.application.run_polling(
                    allowed_updates=Update.ALL_TYPES, 
                    drop_pending_updates=True,
                    close_loop=False
                )
            except Exception as e:
                logger.error(f'Error en polling: {e}')
                logger.info('Reintentando en 10 segundos...')
                import time
                time.sleep(10)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        import json
        response = {
            'status': 'ok',
            'bot': 'running',
            'timestamp': datetime.now().isoformat(),
            'pid': os.getpid()
        }
        self.wfile.write(json.dumps(response).encode())
        logger.info(f'Health check recibido desde {self.client_address[0]}')
    
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.getenv('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f'Health check server running on port {port}')
    server.serve_forever()

def main():
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print('Error: No se encontró TELEGRAM_BOT_TOKEN en las variables de entorno.')
        print('Crea un archivo .env con tu token de bot de Telegram.')
        return
    
    logger.info(f'Iniciando bot con PID: {os.getpid()}')
    
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    try:
        bot = PlantBot(token)
        bot.run()
    except KeyboardInterrupt:
        logger.info('Bot detenido por usuario')
    except Exception as e:
        logger.error(f'Error fatal: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
