from datetime import datetime, timedelta
from traceback import format_exc

from bot import bot
from config import paysum, test_chat_id
from database import PaymentsDBFunc, UsersDBFunc
from keyboard import non_sub_keyboard

def get_tarif(balance):
    try:
        if balance >= 1000:
            tarif = 'three_month'
        elif balance >= 800:
            tarif = 'two_month'
        elif balance >= paysum:
            tarif = 'one_month'
        else:
            tarif = False

        return tarif

    except Exception as e:
        print('Ошибка:\n', format_exc())

def get_new_time(paid_for, chat_id):
    try:
        if paid_for == 'one_month':
            new_time = datetime.now()+timedelta(days=31) # days=31
        elif paid_for == 'two_month':
            new_time = datetime.now()+timedelta(days=61) # days=61
        elif paid_for == 'three_month':
            new_time = datetime.now()+timedelta(days=91) # days=91
            

        return new_time

    except Exception as e:
        print('Ошибка:\n', format_exc())

def get_pay_sum(tarif):
    try:
        if tarif == 'one_month':
            month_paysum = paysum
        elif tarif == 'two_month':
            month_paysum = 800
        elif tarif == 'three_month':
            month_paysum = 1000

        return month_paysum

    except Exception as e:
        print('Ошибка:\n', format_exc())

def sub_create(chat_id, tarif, balance, month_paysum):
    try:
        newbalance = balance - month_paysum
        newtime = get_new_time(tarif, chat_id)
        PaymentsDBFunc.balance_update(chat_id, newbalance)
        UsersDBFunc.editsubtime(chat_id, newtime)
        UsersDBFunc.editsub(chat_id, True)
        times = newtime.strftime('%d.%m.%Y %H:%M')
        UsersDBFunc.update_sent_message_about_end_subscription(chat_id, False)
        try:
            text = f'Активирована подписка до\n*{times}*\nБлагодарим за использование сервиса!'
            bot.send_message(chat_id, text, parse_mode='markdown')
        except:
            UsersDBFunc.update_bloked(chat_id, True)
            

    except Exception as e:
        print('Ошибка:\n', format_exc())

def subs_update(balance, chat_id, paid_for, month_paysum):
    try:
        newbalance = balance - month_paysum
        newtime = get_new_time(paid_for, chat_id)
        PaymentsDBFunc.balance_update(chat_id, newbalance)
        UsersDBFunc.editsubtime(chat_id, newtime)
        UsersDBFunc.update_sent_message_about_end_subscription(chat_id, False)
        times = newtime.strftime('%d.%m.%Y %H:%M')
        try:
            text = f'Ваша подписка была продлена до\n*{times}*\nБлагодарим за использование сервиса!'
            bot.send_message(chat_id, text, parse_mode='markdown')
        except:
            UsersDBFunc.update_bloked(chat_id, True)

    except Exception as e:
        print('Ошибка:\n', format_exc())

def subs_end(chat_id):
    try:
        UsersDBFunc.editsub(chat_id, False)
        UsersDBFunc.update_sent_message_about_end_subscription(chat_id, False)
        try:
            text = f'Ваша подписка закончилась, для продления пополните баланс. Подробнее о тарифах в разделе "FAQ"'
            bot.send_message(chat_id, text, reply_markup=non_sub_keyboard(chat_id), parse_mode='markdown')
        except:
            UsersDBFunc.update_bloked(chat_id, True)
    except Exception as e:
        print('Ошибка:\n', format_exc())

def send_message_about_end_subscription(chat_id, sub_end_date, balance, tarif):
    try:
        sub_end = sub_end_date.strftime('%d.%m.%Y %H:%M')
        if tarif == 'one_month':
            tarif_str = '1 месяц'
        elif tarif == 'two_month':
            tarif_str = '2 месяца'
        elif tarif == 'three_month':
            tarif_str = '3 месяца'

        try:
            text = f'Ваша подписка заканчивается {sub_end}. На вашем балансе {balance} руб. , этого достаточно для продления подписки на {tarif_str}. Для продления на более выгодных условиях пополните ваш баланс. Подробнее о тарифах в разделе "FAQ"'
            bot.send_message(chat_id, text)
            UsersDBFunc.update_sent_message_about_end_subscription(chat_id, True)
        except:
            UsersDBFunc.update_bloked(chat_id, True)

    except Exception as e:
        print('Ошибка:\n', format_exc())