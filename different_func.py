import requests
from datetime import datetime
from traceback import format_exc

from telebot import util
from telebot import types

from bot import bot
from keyboard import *
from database import *
from editor import *

count_error = 0

def send_long_message(chat_id, msg):
	try:
		limit = 3000

		if len(msg) < limit:
			bot.send_message(chat_id, msg)
		else:
			large_text = msg
			splitted_text = util.smart_split(large_text, chars_per_string=limit)
			for text in splitted_text:
				bot.send_message(chat_id, text, parse_mode="markdown")

	except Exception as e:
		print('Ошибка:\n', format_exc())

def nextpay(message):
    try:
        balance = int(message.text)
        chat_id = message.chat.id
        if balance == 0:
            if UsersDBFunc.check_sub(chat_id) == False:
                bot.send_message(chat_id, 'Отмена', reply_markup=non_sub_keyboard(chat_id))
            else:
                bot.send_message(chat_id, 'Отмена', reply_markup=main_keyboard(chat_id))
        else:
            result = PaymentsDBFunc.create(chat_id, balance)
            checkto = result[1]
            key = types.InlineKeyboardMarkup()
            key.add(
                types.InlineKeyboardButton(text='Оплатить счет', url=result[0]),
                types.InlineKeyboardButton(text='Проверить оплату', callback_data=f'checkpay_{checkto}')
            )
            bot.send_message(chat_id, 'Ссылка на оплату была сгенерированна!\nПосле оплаты нажмите на кнопку "*Проверить оплату*"', parse_mode='markdown', reply_markup=key)
    except Exception as e:
        print(e)
        if UsersDBFunc.check_sub(chat_id) == False:
            bot.send_message(chat_id, 'Отмена', reply_markup=non_sub_keyboard(chat_id))
        else:
            bot.send_message(chat_id, 'Отмена', reply_markup=main_keyboard(chat_id))

def generate_csv(chat_id):
    global count_error
    try:
        proxies = AdminsDBFunc.get_proxies()
        date = datetime.now().strftime('%Y-%m-%dT00:00:00')
        r = requests.get(
            f'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders?dateFrom={date}&flag=0&key={UsersDBFunc.return_wb_key(chat_id)}', proxies={"all": proxies[count_error]})
        if r.status_code == 200:
            cache = []
            for i in r.json():
                cache.append({
                    'number': i['number'],
                    'date': i['date'],
                    'supplierArticle': i['supplierArticle'],
                    'techSize': i['techSize'],
                    'barcode': i['barcode'],
                    'quantity': i['quantity'],
                    'totalPrice': i['totalPrice'],
                    'discountPercent': i['discountPercent'],
                    'warehouseName': i['warehouseName'],
                    'oblast': i['oblast'],
                    'incomeID': i['incomeID'],
                    'odid': i['odid'],
                    'subject': i['subject'],
                    'category': i['category'],
                    'brand': i['brand'],
                    'is_cancel': i['isCancel'],
                    'cancel_dt': i['cancel_dt']
                    })
            filename = addfile(f'{chat_id}WB.csv', cache)
            return filename
        else:
            count_error += 1
            if count_error >= len(proxies): count_error = 0
    except Exception as e:
        count_error += 1
        if count_error >= len(proxies): count_error = 0
        print('Ошибка:\n', format_exc())

def trialactivate(message):
    try:
        date = datetime.now().strftime('%Y-%m-%dT00:00:00')
        r = requests.get(f'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders?dateFrom={date}&flag=0&key={message.text}')
        if r.status_code == 200:
            key = types.InlineKeyboardMarkup()
            key.add(
                types.InlineKeyboardButton(text='Да', callback_data=f'acceptkey_{message.text}'),
                types.InlineKeyboardButton(text='Нет', callback_data='declinekey')
            )
            bot.send_message(message.chat.id, f'Вы уверены, что ваш ключ: *{message.text}*', parse_mode='markdown', reply_markup=key)
        else:
            bot.send_message(message.chat.id, f'Вы ввели неверный ключ, попробуйте снова')
            bot.register_next_step_handler(message, trialactivate)
    except Exception as e:
        print('Ошибка:\n', format_exc())

def newkey(message):
    try:
        date = datetime.now().strftime('%Y-%m-%dT00:00:00')
        r = requests.get(f'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders?dateFrom={date}&flag=0&key={message.text}')
        if r.status_code == 200:
            key = types.InlineKeyboardMarkup()
            key.add(
                types.InlineKeyboardButton(text='Да', callback_data=f'acceptnewkey_{message.text}'),
                types.InlineKeyboardButton(text='Нет', callback_data='declinekey')
            )
            bot.send_message(message.chat.id, f'Вы уверены, что ваш ключ: *{message.text}*', parse_mode='markdown', reply_markup=key)
        else:
            bot.send_message(message.chat.id, f'Вы ввели неверный ключ, попробуйте снова')
            bot.register_next_step_handler(message, trialactivate)
    except Exception as e:
        print('Ошибка:\n', format_exc())

def sendadmin(message):
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, "Отменил.")
    bot.send_message(1950117283, message.chat.id)
    bot.forward_message(1950117283, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "Ваше сообщение отправлено администратору, в скором времени вам придет ответ")