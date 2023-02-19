import time

from datetime import datetime, timedelta

from traceback import format_exc

from bot import bot
from keyboard import non_sub_keyboard, main_keyboard
from database import UsersDBFunc, PaymentsDBFunc
from sub_system import get_pay_sum, subs_update, subs_end, get_tarif, send_message_about_end_subscription, sub_create
from config import paysum, test_chat_id


def check_sub():
	try:
		while True:
			try:
				
				data = UsersDBFunc.get_all_data()
				for user in data:
					chat_id = user[0]
					balance = user[3]
					status = user[4]
					sent_message_about_end_subscription = user[8]
						
					if status == True:
						if user[5] <= datetime.now():								
							if balance >= paysum:
								tarif = get_tarif(balance)
								if tarif != False:
									month_paysum = get_pay_sum(tarif)
									subs_update(balance, chat_id, tarif, month_paysum)
							else:
								subs_end(chat_id)
							
						elif user[5]+timedelta(days=2) >= datetime.now():

							if balance >= paysum:
								if sent_message_about_end_subscription == False:
									if balance < 1000:
										tarif = get_tarif(balance)
										if tarif != False:
											send_message_about_end_subscription(chat_id, user[5], balance, tarif)
					else:
						if balance >= paysum:
							tarif = get_tarif(balance)
							if tarif != False:
								month_paysum = get_pay_sum(tarif)
								sub_create(chat_id, tarif, balance, month_paysum)

			except Exception as e:
				print('Ошибка:\n', format_exc())
				continue
			time.sleep(15)
	except Exception as e:
		print('Ошибка:\n', format_exc())

check_sub()
