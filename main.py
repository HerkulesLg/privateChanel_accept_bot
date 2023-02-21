import asyncio
import logging
import config

from aiogram import Bot, Dispatcher, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = config.BOT_TOKEN
bot = Bot(TOKEN, parse_mode='HTML')
router = Router()


@router.chat_join_request()
async def chat_join_request(update):
    await update.approve()

    builder = InlineKeyboardBuilder()
    builder.button(text='YouTube канал', url='https://fucking-great-advice.ru/')
    builder.button(text='RuTube', url='https://fucking-great-advice.ru/')
    builder.button(text='Официальный сайт', url='https://fucking-great-advice.ru/')
    await bot.send_message(chat_id=update.from_user.id, text='Привет, спасибо что подписался на канал.\nИ еще было бы '
                                                             'круто, если ты посмотришь наши соц. сети',
                           reply_markup=builder.as_markup())


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())