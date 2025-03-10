import logging
import requests
import pytz  # Импортируем библиотеку pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ваш API ключ от OpenRouter
OPENROUTER_API_KEY = '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'
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# Модель DeepSeek-V3
MODEL_NAME = "deepseek/deepseek-chat:free"

# Кастомный промпт для нейросети
CUSTOM_PROMPT = (
    "Ты — пьяный русский батя, который любит пошутить, иногда поругаться, но в целом остаётся добрым и общительным. "
    "Ты отвечаешь дерзко, но не переходишь границы. Твой тон — это смесь сарказма, шуток и лёгкой грубости. "
    "Ты можешь использовать нецензурные слова, но редко и только для выразительности. "
    "Ты всегда поддерживаешь диалог, даже если тебе задают глупые вопросы. "
    "Твой стиль общения — это пьяная мудрость с налётом хулиганства. "
    "Не объясняй свои действия, просто отвечай как пьяный батя."
)

# Функция для отправки запроса в OpenRouter
async def send_to_openrouter(prompt: str) -> str:
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": MODEL_NAME,  # Указываем модель DeepSeek-V3
        "messages": [
            {"role": "system", "content": CUSTOM_PROMPT},  # Системный промпт для задания поведения
            {"role": "user", "content": prompt}  # Сообщение пользователя
        ]
    }
    try:
        response = requests.post(OPENROUTER_API_URL, json=data, headers=headers)
        response.raise_for_status()  # Проверка на ошибки HTTP
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к OpenRouter: {e}")
        return "Произошла ошибка при обработке вашего запроса."

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text.startswith("дядя"):
        prompt = text[len("дядя"):].strip()
        if prompt:
            response = await send_to_openrouter(prompt)
            await update.message.reply_text(response)


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот, который отвечает на ваши вопросы. Используйте слово "дядя" для активации.')

# Основная функция
def main() -> None:
    # Вставьте сюда ваш токен от Telegram BotFather
    application = Application.builder().token("7779461205:AAFykPTAvsxoUF5LsKIVRWVihXVQaGUb6Sc").build()

    # Установка временной зоны для JobQueue
    application.job_queue.scheduler.configure(timezone=pytz.UTC)

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
