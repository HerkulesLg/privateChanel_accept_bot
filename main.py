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


# функционал личной переписки с ботом
@router.message(Command(commands=['start']))  # при вызове команды /start
async def start(message):
    if message.chat.type == 'private':
        await bot.send_message(chat_id=message.chat.id, text=f'Рад тебя видеть {message.from_user.full_name}\n'
                                                             'Я психолог с большим стажем. Какой у тебя вопрос?\n'
                                                             'p.s.Не забудь подписаться на Мой <a '
                                                             'href="https://t.me/+t-fNnsn3qYZiMjIy">Tg-канал</a>')


async def translate_message(message, language):  # переводит текст на определенный язык GPT на англ.яз. понимает лучше
    return GoogleTranslator(source='auto', target=f'{language}').translate(message)


async def GPT_request(message):  # создает запрос в чат GPT с заранее заданными параметрами и вводом пользователя
    settings = """. Напиши ответ простыми словами. Запрещено говорить, что ты языковая 
    модель. Пиши интересно и оригинально."""
    prompt = message + settings
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


@router.message()  # принимает все запросы от клиента в ЛС
async def GPT_answer(message):
    if message.text.startswith('/create'):  # создание постов
        # запрашиваем у бота на какую тему написать пост
        prompt = message.text.replace('/create', '').strip()
        await bot.send_message(chat_id=message.chat.id, text='Думаю...\nСкоро напишу.')
        topic = await GPT_request(prompt)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)
        await bot.send_message(chat_id=message.chat.id, text=topic)
        # создаем пост по теме, которую придумал бот
        await bot.send_message(chat_id=message.chat.id, text='Тема есть\nСкоро напишу пост.')
        post = await GPT_request('напиши длинный и интересный пост со смайликами на тему: ' + topic)
        await bot.send_message(chat_id=message.chat.id, text=post)

    elif message.chat.type == 'private':  # для сообщений без команд, чтобы просто пообщаться с ботом
        await bot.send_message(chat_id=message.chat.id, text='Думаю...\nСкоро напишу.')
        answer = await GPT_request(message.text)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)
        await bot.send_message(chat_id=message.chat.id, text=answer)


# функционал админа в канале
@router.chat_join_request()  # принимает заявку на вступление в закрытый канал и пишет сообщение клиенту в ЛС
async def chat_join_request(update):
    await update.approve() # одобрение заявки
    text = f"Моё уважение, {update.from_user.full_name}!\n" \
           "Рад, что присоединились к моему каналу.\n" \
           "Буду рад, если Вы останетесь с нами надолго.\n" \
           "Не забудьте прочитать <a href='https://t.me/c/1655748830/4'>закрепленное сообщение</a>.\n\n" \
           "А еще помимо канала Я могу ответить на Ваши вопросы лично. Напишите вопрос о психологии, и Я дам на него " \
           "ответ."
    await bot.send_message(chat_id=update.from_user.id, text=text)


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
