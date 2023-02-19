from config import *
from bot import bot
import telebot.apihelper
from database import UsersDBFunc
from traceback import format_exc
from keyboard import choice_cancel_keyboard, main_keyboard

@bot.message_handler(commands=['send_message'])
def send_message_call(message):
	""" Рассылка сообщения всем пользователям """
	try:
		chat_id = message.chat.id
		if chat_id in admin_ids:
			bot.send_chat_action(message.chat.id, 'typing')
			msg = bot.send_message(chat_id, "Отправьте ваше сообщение", reply_markup=choice_cancel_keyboard())
			bot.register_next_step_handler(msg, send_messages_all_users)

	except Exception as e:
		print('Ошибка:\n', format_exc())

def send_messages_all_users(message):
	try:
		chat_id = message.chat.id
		if chat_id in admin_ids:
			Users = UsersDBFunc.get_all_data()
			Count = 0
			Count_bloked = 0
			
			ad_text = message.text
			if ad_text == 'Отмена':
				bot.send_message(chat_id, "Процесс остановлен.", reply_markup=main_keyboard(chat_id))
			else:
				ad_caption = message.caption
				content_type = message.content_type

				for user in Users:
					user_id = user[0]
						
					
					res = sending_ad(chat_id, ad_text, user_id, content_type, message, ad_caption)
					if res == True:
						Count += 1
					elif res == False:
						Count_bloked += 1
				bot.send_message(chat_id, f"Сообщение отправлено {Count} пользователям.\nНедоступных пользователей: {Count_bloked}", reply_markup=main_keyboard(chat_id))

	except Exception as e:
		bot.reply_to(message, e)
	

def sending_ad(chat_id, ad_text, user_id, content_type, message, ad_caption):
	try:
		
		try:
			if content_type == 'photo':
				bot.send_photo(user_id, message.photo[len(message.photo)-1].file_id, caption = ad_caption)
			elif content_type == 'text':
				bot.send_message(user_id, ad_text, disable_web_page_preview=False)

			return True

		except telebot.apihelper.ApiTelegramException:
			
			return False

		
			

	except Exception as e:
		bot.send_message(chat_id, e)
