"""### Подключение библиотек"""
import telebot
from google import genai

"""### Указание токенов и создание экземпляров (бот и ИИ агент)"""

TOKEN = '8183367130:AAHw9eqIZTHV13fd6yxiIcceZ4ImF75AFFs'
api_key = "AIzaSyAPRgK8jXW2gUFvzqnyIW7qoLFejB2z4Ic"
bot = telebot.TeleBot(TOKEN)
client = genai.Client(api_key = api_key)

"""### Хендлер команды /start"""

# Реакция бота на команды пользователя
@bot.message_handler(commands=['start'])
def on_start(message):
  bot.send_message(message.chat.id, f'Привет, я чат бот!')
  bot.send_message(message.chat.id, f'Для генерации текста используй команду /text')
  bot.send_message(message.chat.id, f'Для генерации картинки используй команду /img')

"""### Хендлер команды /text (генерация текста)"""

# Реакция бота на команду /text
@bot.message_handler(commands=['text'])
def on_text_generation(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # 1. Извлекаем промпт из сообщения
    # message.text содержит всю строку, например "/text Привет, мир!"
    # Убираем команду '/text ' из начала строки
    command_parts = message.text.split(maxsplit=1) # Разделяем по первому пробелу

    if len(command_parts) < 2 or not command_parts[1].strip():
        # Если после команды /text ничего нет или только пробелы
        bot.reply_to(message, "Пожалуйста, введите текст промпта после команды /text.\nПример: `/text Напиши стих о лете`")
        return # Прекращаем выполнение функции

    prompt = command_parts[1].strip() # Убираем лишние пробелы по краям

    # Опционально: сообщение о том, что бот "думает"
    thinking_message = bot.reply_to(message, "🧠 Генерирую ответ...")

    try:
        # 2. Отправляем промпт в GenAI
        response = client.models.generate_content(
            model="gemini-2.5-pro-exp-03-25",
            contents=prompt,
        )

        # 3. Получаем сгенерированный текст
        generated_text = response.text

        # 4. Отправляем ответ пользователю
        # Редактируем сообщение "Думаю..." на финальный ответ - это выглядит лучше
        bot.edit_message_text(chat_id=chat_id,
                              message_id=thinking_message.message_id,
                              text=generated_text)

    except Exception as e:
        # 5. Обработка ошибок API или других проблем
        # Сообщаем пользователю об ошибке
        try:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=thinking_message.message_id,
                                  text="Произошла ошибка при генерации текста. Попробуйте позже или измените запрос.")
        except Exception as edit_error: # Если даже редактирование не удалось
             bot.reply_to(message, "Произошла ошибка при генерации текста. Попробуйте позже или измените запрос.")

"""### Хендлер команды /img (генерация картинок)"""

# Реакция бота на команду /img
@bot.message_handler(commands=['img'])
def on_img_generation(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # 1. Извлекаем промпт из сообщения
    # message.text содержит всю строку, например "/img Сгенерируй картинку где акуда стоит на пляже в кроссовках найк"
    # Убираем команду '/img ' из начала строки
    command_parts = message.text.split(maxsplit=1) # Разделяем по первому пробелу

    if len(command_parts) < 2 or not command_parts[1].strip():
        # Если после команды /img ничего нет или только пробелы
        bot.reply_to(message, "Пожалуйста, введите текст промпта после команды /img.\nПример: /img Сгенерируй картинку где акула стоит на пляже в кроссовках найк")
        return # Прекращаем выполнение функции

    prompt = command_parts[1].strip() # Убираем лишние пробелы по краям

    # Опционально: сообщение о том, что бот "думает"
    thinking_message = bot.reply_to(message, "🧠 Генерирую изображение...")

    try:
        # 2. Отправляем промпт в GenAI
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
              response_modalities=['Text', 'Image']
            )
        )

        # 3. Получаем сгенерированный текст
        for part in response.candidates[0].content.parts:
          if part.text is not None:
            print(part.text)
          elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save('gemini.png')

        # 4. Отправляем ответ пользователю
        # Редактируем сообщение "Думаю..." на финальный ответ - это выглядит лучше
        bot.edit_message_text(chat_id=chat_id,
                              message_id=thinking_message.message_id,
                              text=f"Картинка по запросу {prompt}")

        bot.send_photo(chat_id=chat_id, photo=open('gemini.png', 'rb'))

    except Exception as e:
        # 5. Обработка ошибок API или других проблем
        # Сообщаем пользователю об ошибке
        try:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=thinking_message.message_id,
                                  text="Произошла ошибка при генерации картинки. Попробуйте позже или измените запрос.")
        except Exception as edit_error: # Если даже редактирование не удалось
             bot.reply_to(message, "Произошла ошибка при генерации картинки. Попробуйте позже или измените запрос.")

"""### Хендлер для обработки обычного текста от пользователя"""

# Реакция бота на все текстовые сообщения
@bot.message_handler(content_types=['text'])
def text_answer(message):
  bot.send_message(message.chat.id, f'Не понимаю тебя. Начни с начала --> /start')

"""### Функция запуска бота (последняя ячейка)"""

# Запуск бота
bot.polling(none_stop=True)