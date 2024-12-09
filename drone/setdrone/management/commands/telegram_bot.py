import os
import django
from django.core.management.base import BaseCommand
from django.db.models import Model
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from asgiref.sync import sync_to_async  # Правильный импорт
import logging
from setdrone.models import Profile

# Настройка логирования
logging.basicConfig(
    filename='telegram_bot.log',  # Имя файла для логов
    level=logging.INFO,           # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат сообщений
)
logger = logging.getLogger(__name__)

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drone.settings')
django.setup()

# Словарь для хранения состояния пользователей
USER_STATE = {}

# Асинхронная функция для сохранения Telegram user_id в базе данных
@sync_to_async
def save_telegram_id(user_id, key):
    try:
        # Пытаемся найти профиль с данным ключом
        profile = Profile.objects.get(telegram_key=key)
        profile.telegram_user_id = user_id  # Сохраняем Telegram ID
        profile.save()
        logger.info(f"Telegram ID {user_id} saved successfully for profile with key {key}.")
        return True
    except Profile.DoesNotExist:
        logger.warning(f"Profile with key {key} does not exist.")
        return False

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = str(update.message.from_user.id)  # Получаем ID пользователя
    USER_STATE[telegram_user_id] = 'awaiting_key'  # Устанавливаем состояние ожидания ключа
    await update.message.reply_text("Привет! Пожалуйста, введи свой ключ для авторизации.")

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = str(update.message.from_user.id)  # Получаем ID пользователя
    user_message = update.message.text  # Текст сообщения (ключ)

    # Проверка состояния пользователя
    if USER_STATE.get(telegram_user_id) == 'awaiting_key':
        # Пытаемся сохранить Telegram ID с ключом
        if await save_telegram_id(telegram_user_id, user_message):
            await update.message.reply_text("Ты успешно авторизован!")
            USER_STATE[telegram_user_id] = 'authorized'  # Обновляем состояние пользователя
        else:
            await update.message.reply_text("Неверный ключ! Попробуй снова.")
            logger.warning(f"User {telegram_user_id} failed to provide a correct key.")

# Запуск Telegram-бота
def start_tg():
    application = Application.builder().token('7828718725:AAGUxM52TejUFvzs6sDuZnC4nUEP-eUn3QY').build()  # Замените на ваш токен
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Обрабатываем текстовые сообщения
    application.run_polling()

# Команда для запуска бота
class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **kwargs):
        self.stdout.write("Запуск Telegram-бота...")
        start_tg()
