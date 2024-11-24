import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранение вопросов и идентификаторов пользователей
questions = []
admin_chat_id = '2079770501'  # Замените на ваш ID


# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Вы можете задать анонимный вопрос.')


# Обработка вопросов
async def handle_question(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "незнакомец"
    question = update.message.text
    questions.append((user_id, username, question))
    await update.message.reply_text('Ваш вопрос отправлен анонимно.')
    # Информируем администратора о новом вопросе
    message = f"Новый вопрос от {username} (ID: {user_id}): {question}"
    await context.bot.send_message(chat_id=admin_chat_id, text=message)


# Ответ на вопрос (от администратора)
async def answer_question(update: Update, context: CallbackContext) -> None:
    if not questions:
        await update.message.reply_text('Нет новых вопросов.')
        return

    user_id, username, question = questions.pop(0)  # Извлекаем первый вопрос
    answer = ' '.join(context.args)

    # Отправка ответа пользователю
    await context.bot.send_message(chat_id=user_id, text=f"Ответ на ваш вопрос от администратора: {answer}")
    await update.message.reply_text('Ответ отправлен!')


# Обработка медиафайлов
async def handle_media(update: Update, context: CallbackContext) -> None:
    if update.message.photo:
        file = update.message.photo[-1].get_file()
        await file.download_to_drive(f'photo_{update.message.photo[-1].file_id}.jpg')
    elif update.message.video:
        file = update.message.video.get_file()
        await file.download_to_drive(f'video_{update.message.video.file_id}.mp4')
    else:
        await update.message.reply_text('Пожалуйста, отправьте текст, фото или видео.')


# Основная функция
def main() -> None:
    # Создаем Updater и передаем ему токен вашего бота
    application = ApplicationBuilder().token("7656610041:AAEd6H_bTsJf93iA5KR4xACrCk5VzO94KKE").build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    application.add_handler(CommandHandler("answer", answer_question))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()
