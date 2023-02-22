import asyncio
import logging
import config
import openai

from deep_translator import GoogleTranslator
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command

TOKEN = config.BOT_TOKEN
openai.api_key = config.openai_token
bot = Bot(TOKEN, parse_mode='HTML')
router = Router()


async def GPT_request(message):
    settings = """. Напиши ответ кратко от лица человека, который занимается исследованиями в области психологии"""
    prompt = str(message.text) + settings
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=await translate_message(prompt, 'en'),
        temperature=0.5,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0,
    )
    return await translate_message(response['choices'][0]['text'], 'ru')


async def translate_message(message, language):  # переводит текст на определенный язык
    return GoogleTranslator(source='auto', target=f'{language}').translate(message)


@router.message(Command(commands=['start']))  # если бота запускают напрямую
async def start(message):
    await bot.send_message(chat_id=message.chat.id, text=f'Рад тебя выдеть {message.from_user.full_name}\n'
                                                         f'Я психолог с большим стажем. Какой у тебя вопрос?')


@router.chat_join_request()  # бот стоит админом, который принимает заявки на вступление в группу и отправляет
# сообщение пользователю с предложением пообщаться.
async def chat_join_request(update):
    await update.approve()
    text = f"Моё уважение, {update.from_user.full_name}!\n" \
           "Рад, что присоединились к моему каналу.\n" \
           "Буду рад, если Вы останетесь с нами надолго.\n" \
           "Не забудьте прочитать <a href='https://t.me/c/1655748830/4'>закрепленное сообщение</a>.\n\n" \
           "А еще помимо канала я могу ответить на твои вопросы лично. Напиши свой вопрос и я дам на него ответ."
    await bot.send_message(chat_id=update.from_user.id, text=text)


@router.message()  # принимает все вводимые сообщения от пользователя и выдает ответ GPT бота с определенными
# параметрами
async def GPT_answer(message):
    await bot.send_message(chat_id=message.chat.id, text='Думаю...\nСкоро напишу.')
    answer = await GPT_request(message)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)
    await bot.send_message(chat_id=message.chat.id, text=answer)


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
