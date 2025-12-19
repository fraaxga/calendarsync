import os
import asyncio

from telebot.async_telebot import AsyncTeleBot
bot = AsyncTeleBot(os.environ['CSYNC_TELEGRAM_TOKEN'])

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)


asyncio.run(bot.polling())