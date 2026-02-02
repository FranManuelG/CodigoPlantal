import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from database import Database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PLANT_NAME, PLANT_DAYS, SELECTING_PLANT = range(3)

class PlantBot:
    def __init__(self, token: str):
        self.token = token
        self.db = Database()
        self.application = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('agregar', self.add_plant_start)],
            states={
                PLANT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_plant_name)],
                PLANT_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_plant_days)],
            },
            fallbacks=[CommandHandler('cancelar', self.cancel)],
        )
        
        regar_handler = ConversationHandler(
            entry_points=[CommandHandler('regar', self.water_plant_start)],
            states={
                SELECTING_PLANT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.water_plant_select)],
            },
            fallbacks=[CommandHandler('cancelar', self.cancel)],
        )
        
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('ayuda', self.help_command))
        self.application.add_handler(conv_handler)
        self.application.add_handler(regar_handler)
        self.application.add_handler(CommandHandler('plantas', self.list_plants))
        self.application.add_handler(CommandHandler('historial', self.watering_history))
        self.application.add_handler(CommandHandler('eliminar', self.delete_plant))
        self.application.add_handler(CommandHandler('pendientes', self.pending_plants))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(
            f'¡Hola {user.first_name}! 🌱\n\n'
            'Soy tu asistente para el cuidado de plantas.\n'
            'Usa /ayuda para ver todos los comandos disponibles.'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            '🌿 *Comandos disponibles:*\n\n'
            '/agregar - Agregar una nueva planta\n'
            '/plantas - Ver todas tus plantas\n'
            '/regar - Registrar que regaste una planta\n'
            '/historial - Ver historial de riegos\n'
            '/pendientes - Ver plantas que necesitan riego\n'
            '/eliminar - Eliminar una planta\n'
            '/ayuda - Mostrar este mensaje\n'
            '/cancelar - Cancelar operación actual'
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def add_plant_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            '🌱 ¿Cómo se llama tu planta?\n'
            '(Usa /cancelar para cancelar)'
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
            
            self.db.add_plant(user_id, plant_name, days)
            
            await update.message.reply_text(
                f'✅ ¡Planta "{plant_name}" agregada!\n'
                f'Frecuencia de riego: cada {days} día(s)\n\n'
                'Usa /plantas para ver todas tus plantas.'
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
        plants = self.db.get_user_plants(user_id)
        
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
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        user_id = update.effective_user.id
        plant_name = update.message.text
        
        plant = self.db.get_plant_by_name(user_id, plant_name)
        if not plant:
            await update.message.reply_text(
                'No encontré esa planta. Intenta de nuevo.',
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        self.db.record_watering(plant[0])
        
        await update.message.reply_text(
            f'✅ ¡Riego registrado para "{plant_name}"!\n'
            f'Próximo riego recomendado: en {plant[2]} día(s)',
            reply_markup=ReplyKeyboardRemove()
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
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    def run(self):
        logger.info('Bot iniciado...')
        self.application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')
    
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
    
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    bot = PlantBot(token)
    bot.run()

if __name__ == '__main__':
    main()
