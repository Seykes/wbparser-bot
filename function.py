# -*- coding: utf-8 -*-
import telebot
import os

import time
from config import *
from keyboard import *
from database import *

from datetime import date


from ref_system import generate_referral_link
from send_ad import send_messages_all_users
from api import *

from traceback import format_exc

from bot import bot
from different_func import *
from db import MainDB
from yandexmoney import auth
from sub_system import sub_create

MainDB.create_tables()
bot.delete_webhook()
if yoomoney_token == '':
    auth()
    print('Enter your token in config')
    input()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        if UsersDBFunc.check(message.chat.id) is False:
            link = generate_referral_link()
            ReferalSystemDBFunc.user_create(message.chat.id, link)
            if len(message.text.split()) > 1:

                    link_data = message.text.split()[1]
                    call = link_data.split('-')[0]
                    data = link_data.split('-')[1]

                    if call == 'ref':
                        ref_code = data
                        link = generate_referral_link()
                        ReferalSystemDBFunc.update_user_in_system(message.chat.id, ref_code, link)

            bot.send_message(message.chat.id, 'Привет! Я бот для продавцов Wildberries. Я оповещаю о новых заказах, сделанных покупателями на маркетплейсе из вашего личного кабинета. Информация на сервере обновляется каждые полчаса, поэтому вы сможете узнавать обо всех новых заказах сразу же! Попробуйте меня бесплатно!', reply_markup=new_user_keys(message.chat.id))
        elif UsersDBFunc.check(message.chat.id) is True and UsersDBFunc.check_sub(message.chat.id) == False:
            link = generate_referral_link()
            ReferalSystemDBFunc.user_create(message.chat.id, link)
            bot.send_message(message.chat.id, 'Здравствуйте, у вас закончилась подписка\nПродлите ее в личном кабинете!\nПосле пополнения баланса средства спишутся в течении 5 минут и вы сможете продолжить пользоваться ботом', reply_markup=non_sub_keyboard(message.chat.id))
        else:
            link = generate_referral_link()
            ReferalSystemDBFunc.user_create(message.chat.id, link)
            bot.send_message(message.chat.id, 'Добро пожаловать обратно!', reply_markup=main_keyboard(message.chat.id))
    
    except Exception as e:
        print('Ошибка:\n', format_exc())

@bot.message_handler(commands=['stats'])
def stats_call(message):
    try:
        if message.chat.id in admin_ids:
            bot.send_chat_action(message.chat.id, 'typing')
            bot.send_message(message.chat.id, AdminsDBFunc.get_stats(), parse_mode='markdown')
    except Exception as e:
        print('Ошибка:\n', format_exc())

@bot.message_handler(commands=['proxies'])
def add_proxie(message):
    try:
        if message.chat.id in admin_ids:
            AdminsDBFunc.update_proxies(message.text.replace("/proxies ", ""))
            bot.send_message(message.chat.id, "Good!")
    except Exception as e:
        print('Ошибка:\n', format_exc())

@bot.message_handler(commands=['proxie'])
def get_proxie(message):
    try:
        if message.chat.id in admin_ids:
            bot.send_message(message.chat.id, str(AdminsDBFunc.get_proxies()))
    except Exception as e:
        print('Ошибка:\n', format_exc())

@bot.message_handler(commands=['addbalance'])
def addbalance_call_message(message):
    try:
        chat_id = message.chat.id
        
        if chat_id in admin_ids:
            
            bot.send_chat_action(chat_id, 'typing')
            user_id = message.text.split()[1]
            sum = int(message.text.split()[2])
            PaymentsDBFunc.addbalance(user_id, sum)
            if ReferalSystemDBFunc.check_pay_to_invited(user_id) == False:
                invited_to_user_id = ReferalSystemDBFunc.get_invited_to_user_id(user_id)
                if invited_to_user_id != False:
                    ReferalSystemDBFunc.update_balance_for_invited(user_id, invited_to_user_id)
                    bot.send_message(invited_to_user_id, f"Ваш баланс пополнен на {paysum}р за привлечение нового пользователя по реферальной ссылке! Благодарим вас за использование сервиса.")
            
            bot.send_message(chat_id, 'Баланс был выдан успешно!')
    except Exception as e:
        print('Ошибка:\n', format_exc())

@bot.message_handler(commands=['stats_user'])
def stats_user_call(message):
    try:
        if message.chat.id in admin_ids:
            bot.send_chat_action(message.chat.id, 'typing')
            filename = AdminsDBFunc.get_full_stats()
            with open(filename, 'rb') as f:
                bot.send_document(message.chat.id, f)
            bot.send_message(message.chat.id, 'Отчет успешно сформирован и был вам отправлен!', reply_markup=main_keyboard(message.chat.id))
            time.sleep(1)
            os.remove(filename)
    except Exception as e:
        print('Ошибка:\n', format_exc())

@bot.message_handler(content_types=['text'])
def text(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        chat_id = message.chat.id
        status = UsersDBFunc.check_sub(chat_id)
        if message.text == 'FAQ':
            fqa_text = (
                '*В: Сколько стоит подписка на бота?*\n' + \
                'О: Стоимость подписки зависит от продолжительности:\n*1 месяц - 500 руб.*\n*2 месяца - 800 руб.*\n*3 месяца - 1000 руб.*\nКаждому новому пользователю даётся 7 дней бесплатной подписки, чтобы оценить возможности бота.\n\n' + \
                '*Внимание*. Переводы с кредитных карт могут облагаться дополнительной комиссией, уточняйте тарифы у вашего банка!\n\n' + \
                '*В: Как оплатить подписку?*\n' + \
                'О: Для оплаты выберите «Профиль» и нажмите на кнопку «Пополнить баланс». В ответ вы получите ссылку, пройдя по которой сможете пополнить свой баланс для оплаты подписки. Баланс пополняется на любую сумму на ваше усмотрение и подписка активируется по наиболее выгодному тарифу.\n' + \
                'Пример 1: Вы пополнили баланс на 600 руб. - подписка активируется на 1 месяц и остаток на балансе будет 100 руб.\n' + \
                'Пример 2: Вы пополнили баланс на 1200 руб. - подписка активируется на 3 месяца и остаток на балансе будет 200 руб.\n' + \
                '*ВНИМАНИЕ!* После оплаты необходимо *ОБЯЗАТЕЛЬНО нажать кнопку "Проверить оплату"*, в противном случае баланс не будет пополнен!\n\n' + \
                '*В: Как подключить другой личный кабинет продавца?*\n' + \
                'О: Нажмите кнопку «Профиль», далее «Изменить API ключ» и введите новый ключ.\n\n' + \
                '*В: Можно ли подключить к боту несколько личных кабинетов?*\n' + \
                'О: К одному пользователю можно подключить только один личный кабинет продавца.\n\n' + \
                '*В: Уведомления о новых заказах приходят с опозданием или опережением.*\n' + \
                'О: Такое случается из-за различия передачи данных через API и в личном кабинете. Возможны ситуации при которых бот присылает уведомление о новом заказе, хотя в личном кабинете он еще не отображается.\n\n' + \
                '*В: Почему бот не всегда отвечает на запросы?*\n' + \
                'О: API Wildberries имеет ограничение по времени на количество обращений, пожалуйста повторите свой запрос только через несколько минут.'
            )
            bot.reply_to(message, fqa_text, parse_mode='Markdown')

        elif message.text == 'Получить последние заказы':
            bot.send_message(chat_id, 'Для вас генерируются все заказы по сегодняшней дате\nПожалуйста, ждите..')
            try:
                filename = generate_csv(chat_id)
                with open(filename, 'rb') as f:
                    bot.send_document(chat_id, f)
                bot.send_message(chat_id, 'Отчет успешно сформирован и был вам отправлен!', reply_markup=main_keyboard(chat_id))
                time.sleep(1)
                os.remove(filename)
            except:
                bot.send_message(chat_id, 'Подождите пару секунд и попробуйте снова', reply_markup=main_keyboard(chat_id))

        elif message.text == 'Профиль':
            profile = UsersDBFunc.get_profile(chat_id)
            user_id = profile[0]
            if profile[1] == None:
                username = 'Не указан'
            else:
                username = profile[1]
            balance = profile[3]
            if profile[4] == 1:
                subactive = 'Да'
            else:
                subactive = 'Нет'
            timeend = profile[5].strftime('%d.%m.%Y %H:%M')
            
            bot.send_message(chat_id, f'Ваш ID: `{user_id}`\nВаш никнейм: [{username}](tg://user?id={user_id})\nВаш баланс: *{balance}* руб\nАктивна ли подписка: *{subactive}*\nДата окончания подписки: *{timeend}*', reply_markup=profile_keys(chat_id), parse_mode='markdown')
                
        elif message.text == 'Сводка':
            bot.send_message(chat_id, "Выберите за какое время показать Сводку. При выборе 'Выбрать дату' будет отправлен календарь для выбора.", reply_markup=choice_date_keyboard('brief'))
        elif message.text == 'Реферальная ссылка':
            referral_link = ReferalSystemDBFunc.get_ref_code_by_user(chat_id)
            bot.send_message(chat_id, f'Ваша реферальная ссылка: https://t.me/wbzillabot?start=ref-{referral_link}\nОтправьте эту ссылку для подключения к боту своим друзьям и после оплаты ими подписки от 1 месяца вы получите месяц бесплатного использования в подарок!')
        #--- Уведомления
        elif message.text == 'Включить уведомления':
            if status is True:
                if UsersDBFunc.check_notifications(chat_id):
                    bot.send_message(chat_id, "Уведомления уже включены")
                else:
                    bot.send_message(
                        chat_id, 
                        "Моментальные уведомления это способ получения уведомлений о заказах покупателей в реальном времени. Бот подключается к серверу каждые полчаса и присылает информацию о совершенных заказах. Включить моментальные уведомления?",
                        reply_markup=change_notifications_keyboard()
                    )
            else:
                bot.send_message(chat_id, 'Информация доступна по подписке. Пополните ваш баланс на недостающую сумму. Для этого выберите пункт "Профиль" в меню.', reply_markup=main_keyboard(chat_id))
        elif message.text == 'Выключить уведомления':
            if UsersDBFunc.check_notifications(chat_id):
                UsersDBFunc.update_notifications(chat_id, False)
                if UsersDBFunc.check_sub(chat_id) == False:
                    bot.send_message(chat_id, "Уведомления выключены", reply_markup=non_sub_keyboard(chat_id))
                else:
                    bot.send_message(chat_id, "Уведомления выключены", reply_markup=main_keyboard(chat_id))
            else:
                if UsersDBFunc.check_sub(chat_id) == False:
                    bot.send_message(chat_id, "Уведомления уже выключены", reply_markup=non_sub_keyboard(chat_id))
                else:
                    bot.send_message(chat_id, "Уведомления уже выключены", reply_markup=non_sub_keyboard(chat_id))
        #--- Заказы
        elif message.text == 'Заказы':
            if status is True:
                bot.send_message(chat_id, "Выберите за какое время показать Заказы. При выборе 'Выбрать дату' будет отправлен календарь для выбора. ", reply_markup=choice_date_keyboard('orders'))
            else:
                bot.send_message(chat_id, 'Информация доступна по подписке. Пополните ваш баланс на недостающую сумму. Для этого выберите пункт "Профиль" в меню.', reply_markup=main_keyboard(chat_id))
        elif message.text == 'Выкупы':
            if status is True:
                bot.send_message(chat_id, "Выберите за какое время показать Выкупы. При выборе 'Выбрать дату' будет отправлен календарь для выбора.", reply_markup=choice_date_keyboard('sales'))
            else:
                bot.send_message(chat_id, 'Информация доступна по подписке. Пополните ваш баланс на недостающую сумму. Для этого выберите пункт "Профиль" в меню.', reply_markup=main_keyboard(chat_id))
        elif message.text == 'Остатки':
            if status is True:
                bot.send_message(chat_id, 'Получаю данные…')
                key = UsersDBFunc.return_wb_key(chat_id)
                remains_warehouse_count = check_remains_warehouse_count(key)
                if remains_warehouse_count == 1:
                    remains = get_data('remains', 'today', key, None)
                    send_long_message(chat_id, remains)
                elif remains_warehouse_count > 1:
                    all_warehouse_name = get_all_warehouse_name(key)
                    bot.send_message(chat_id, "Выберите склад", reply_markup=remains_keyboard(all_warehouse_name))
            else:
                bot.send_message(chat_id, 'Информация доступна по подписке. Пополните ваш баланс на недостающую сумму. Для этого выберите пункт "Профиль" в меню.', reply_markup=main_keyboard(chat_id))
        elif message.text == 'Обратная связь':
            bot.send_message(chat_id, "Отправьте сообщение, оно автоматически уйдет администратору.\nДля отмены напишите 'Отмена'")
            bot.register_next_step_handler(message, sendadmin)
        else:
            if message.chat.id in admin_ids:
                text = message.text.replace("/answer ", "")
                user_id = message.reply_to_message.text
                bot.send_message(user_id, text)
                bot.send_message(message.chat.id, "Отправил")
    except Exception as e:
        print('Ошибка:\n', format_exc())

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(call):
    chat_id = call.message.chat.id
    status = UsersDBFunc.check_sub(chat_id)
    result, key, step = DetailedTelegramCalendar(locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите дату",
                              chat_id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        if status is True:
            bot.send_message(chat_id, 'Получаю данные…')
            method = SelectedCalendarDBFunc.get(chat_id)
            key = UsersDBFunc.return_wb_key(chat_id)
            msg = get_data(method, result, key, None)
            send_long_message(chat_id, msg)
        else:
            bot.send_message(chat_id, 'Информация доступна по подписке. Пополните ваш баланс на недостающую сумму. Для этого выберите пункт "Профиль" в меню.', reply_markup=main_keyboard(chat_id))

@bot.callback_query_handler(func=lambda call: True)
def calling(call):
    try:
        chat_id = call.message.chat.id
        status = UsersDBFunc.check_sub(chat_id)
        bot.send_chat_action(chat_id, 'typing')
        message_id = call.message.message_id
        if 'acceptnewkey_' in call.data:
            UsersDBFunc.editkey(chat_id, call.data.split('_')[1])
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            bot.send_message(chat_id, 'Ключ был заменен!',
                            reply_markup=main_keyboard(chat_id))
        elif call.data == 'editkey':
            bot.edit_message_text(
                    chat_id=chat_id, 
                    message_id=message_id,
                    text='Хорошо, отправьте боту x64 API ключ из вашего личного кабинета продавца. Найти его можно в разделе «Мой профиль – Доступ к API». Это безопасно, все данные надежно зашифрованы и никому не доступны.'
                )
            bot.register_next_step_handler(call.message, newkey)
        elif 'testrequest_' in call.data:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Хорошо, отправьте боту x64 API ключ из вашего личного кабинета продавца. Найти его можно в разделе «Мой профиль – Доступ к API». Это безопасно, все данные надежно зашифрованы и никому не доступны.')
            bot.register_next_step_handler(call.message, trialactivate)
        elif 'acceptkey_' in call.data:
            UsersDBFunc.create(chat_id, call.message.chat.username,
                    call.data.split('_')[1], True)
            link = generate_referral_link()
            ReferalSystemDBFunc.user_create(chat_id, link)
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            bot.send_message(chat_id, 'Спасибо, ваша пробная подписка активирована. Желаю приятного использования',
                        reply_markup=main_keyboard(chat_id))

        elif 'declinekey' == call.data:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Хорошо, отправьте боту x64 API ключ из вашего личного кабинета продавца. Найти его можно в разделе «Мой профиль – Доступ к API». Это безопасно, все данные надежно зашифрованы и никому не доступны.')
            bot.register_next_step_handler(call.message, trialactivate)
        elif 'testrequestfail_' in call.data:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Жаль, что вы отказались. Если передумаете, то отправьте мне /start')
        elif 'addpay' == call.data:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            bot.send_message(chat_id, 'Пожалуйста, введите сумму пополения\nДля отмены введите 0')
            bot.register_next_step_handler(call.message, nextpay)
        elif 'checkpay_' in call.data:
            result = PaymentsDBFunc.check_pay(chat_id, call.data.split('_')[1])
            if UsersDBFunc.check_sub(chat_id) == False:
                if result is True:
                    if ReferalSystemDBFunc.check_pay_to_invited(chat_id) == False:
                        invited_to_user_id = ReferalSystemDBFunc.get_invited_to_user_id(chat_id)
                        if invited_to_user_id != False: 
                            ReferalSystemDBFunc.update_balance_for_invited(chat_id, invited_to_user_id)
                            bot.send_message(invited_to_user_id, f"Ваш баланс пополнен на {paysum}р за привлечение нового пользователя по реферальной ссылке! Благодарим вас за использование сервиса.")
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                    bot.send_message(chat_id, 'Ваш баланс пополнен, хорошего пользования!', reply_markup=non_sub_keyboard(chat_id))
                else:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    checkto = call.data.split('_')[1]
                    keyboard.add(
                        telebot.types.InlineKeyboardButton(text='Проверить оплату', callback_data=f'checkpay_{checkto}'),
                        telebot.types.InlineKeyboardButton(text='Отмена', callback_data=f'declinepay_{checkto}')
                    )
                    bot.send_message(chat_id, 'Ваша оплата еще не дошла до нас!', reply_markup=keyboard)
            else:
                if result is True:
                    if ReferalSystemDBFunc.check_pay_to_invited(chat_id) == False:
                        invited_to_user_id = ReferalSystemDBFunc.get_invited_to_user_id(chat_id)
                        if invited_to_user_id != False: 
                            ReferalSystemDBFunc.update_balance_for_invited(chat_id, invited_to_user_id)
                            bot.send_message(invited_to_user_id, f"Ваш баланс пополнен на {paysum}р за привлечение нового пользователя по реферальной ссылке! Благодарим вас за использование сервиса.")
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                    bot.send_message(chat_id, 'Ваш баланс пополнен, хорошего пользования!', reply_markup=main_keyboard(chat_id))
                else:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    checkto = call.data.split('_')[1]
                    keyboard.add(
                        telebot.types.InlineKeyboardButton(text='Проверить оплату', callback_data=f'checkpay_{checkto}'),
                        telebot.types.InlineKeyboardButton(text='Отмена', callback_data=f'declinepay_{checkto}')
                    )
                    bot.send_message(chat_id, 'Ваша оплата еще не дошла до нас!', reply_markup=keyboard)
        elif 'declinepay_' in call.data:
            if UsersDBFunc.check_sub(chat_id) == False:
                PaymentsDBFunc.delete(call.data.split('_')[1])
                bot.delete_message(chat_id=chat_id, message_id=message_id)
                bot.send_message(chat_id, 'Ваша оплата была отменена!', reply_markup=non_sub_keyboard(chat_id))
            else:
                PaymentsDBFunc.delete(call.data.split('_')[1])
                bot.delete_message(chat_id=chat_id, message_id=message_id)
                bot.send_message(chat_id, 'Ваша оплата была отменена!', reply_markup=main_keyboard(chat_id))

        elif 'brief_' in call.data or 'orders_' in call.data or 'sales_' in call.data:
            if status is True:
                method = call.data.split('_')[0]
                today = date.today()
                calendar, step = DetailedTelegramCalendar(locale='ru', min_date=date(today.year, 1, 1), max_date=date(today.year, today.month, 30), current_date=date(today.year, today.month, 1)).build()
                datetime = call.data.split('_')[1]
                if datetime == 'calendar':
                    SelectedCalendarDBFunc.create(chat_id, method)
                    bot.send_message(chat_id, "Выберите дату", reply_markup=calendar)
                else:
                    key = UsersDBFunc.return_wb_key(chat_id)
                    bot.send_message(chat_id, 'Получаю данные…')
                    msg = get_data(method, datetime, key, None)
                    send_long_message(chat_id, msg)
            else:
                bot.send_message(chat_id, 'Информация доступна по подписке. Пополните ваш баланс на недостающую сумму. Для этого выберите пункт "Профиль" в меню.', reply_markup=main_keyboard(chat_id))
            
        elif 'notify_on' == call.data:
            if status is True:
                UsersDBFunc.update_notifications(chat_id, True)
                if UsersDBFunc.check_sub(chat_id) == False:
                    bot.send_message(chat_id, "Уведомления включены", reply_markup=non_sub_keyboard(chat_id))
                else:
                    bot.send_message(chat_id, "Уведомления включены", reply_markup=main_keyboard(chat_id))
            else:
                bot.send_message(chat_id, 'Информация доступна по подписке. Пополните ваш баланс на недостающую сумму. Для этого выберите пункт "Профиль" в меню.', reply_markup=main_keyboard(chat_id))

        elif 'remain_' in call.data:
            if status is True:
                bot.send_message(chat_id, 'Получаю данные…')
                warehouse_name = call.data.split('_')[1]
                key = UsersDBFunc.return_wb_key(chat_id)
                remains = get_data('remains', 'today', key, warehouse_name)
                send_long_message(chat_id, remains)
            else:
                bot.send_message(chat_id, 'Информация доступна по подписке. Пополните ваш баланс на недостающую сумму. Для этого выберите пункт "Профиль" в меню.', reply_markup=main_keyboard(chat_id))

        elif 'all_remains' == call.data:
            if status is True:
                bot.send_message(chat_id, 'Получаю данные…')
                key = UsersDBFunc.return_wb_key(chat_id)
                remains = get_data('remains', 'today', key, None)
                send_long_message(chat_id, remains)
            else:
                bot.send_message(chat_id, 'Информация доступна по подписке. Пополните ваш баланс на недостающую сумму. Для этого выберите пункт "Профиль" в меню.', reply_markup=main_keyboard(chat_id))

    except Exception as e:
        print('Ошибка:\n', format_exc())

bot.enable_save_next_step_handlers(delay=0)
bot.load_next_step_handlers()
#Запуск бота с обработкой вылетов
if __name__ == "__main__":
	#bot.polling(none_stop = True, interval = 0)
	# на сервер
	while True:
		try:
			print("BOT was started!")
			bot.polling(none_stop = True, interval = 0)

		except requests.exceptions.ConnectionError:
			print("Скрипт получил ошибку соединения 'ConnectionError'")
			time.sleep(10)

		except requests.exceptions.ReadTimeout:
			print("Скрипт получил ошибку соединения 'ReadTimeout'")
			time.sleep(10)
			
		except Exception as e:
			print('Ошибка:\n', format_exc())
			time.sleep(10)
