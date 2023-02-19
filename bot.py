import config
import telebot

bot = telebot.TeleBot(token=config.TOKEN, threaded=True, num_threads=config.bot_num_threads)
print(bot.get_me()) # Вывод в консоле информации о боте
