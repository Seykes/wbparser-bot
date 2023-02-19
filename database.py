from random import randint
from datetime import datetime, timedelta
from time import time as time_unix

from traceback import format_exc

from more_itertools import last

from yoomoney import Quickpay, Client

from cryptor import encrypt_xor, decrypt_xor
from config import yoomoney_token, paysum, test_chat_id
from editor import adminile
from db import MainDB

class UsersDBFunc(object):
	try:
		
		def create(chat_id, username, wb_key, sub_activate):
			conn, cursor = MainDB.connect()
			key = encrypt_xor(wb_key, str(chat_id))
			sub_end = datetime.now()+timedelta(weeks=1)
			reg_time = time_unix()
			cursor.execute(f"INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (chat_id, username, key, 0, sub_activate, str(sub_end), True, False, False, reg_time))
			conn.commit()

		def check(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT user_id FROM users WHERE user_id = %s", (chat_id, ))
			result = cursor.fetchall()
			if len(result) == 0:
				return False
			else:
				return True

		def check_sub(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT user_id FROM users WHERE user_id = %s and sub_acitvate = %s", (chat_id, True, ))
			result = cursor.fetchall()
			if len(result) == 0:
				return False
			else:
				return True

		def update_sub_status(chat_id, update):
			conn, cursor = MainDB.connect()
			cursor.execute(f"UPDATE users SET sub_acitvate = %s WHERE user_id = %s", (update, chat_id, ))
			conn.commit()

		def return_wb_key(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT wb_key_hash FROM users WHERE user_id = %s", (chat_id, ))
			result = cursor.fetchone()[0]
			return decrypt_xor(result, str(chat_id))

		def editsub(chat_id, substats):
			conn, cursor = MainDB.connect()
			cursor.execute(f"UPDATE users SET sub_acitvate = %s WHERE user_id = %s", (substats, chat_id, ))
			conn.commit()

		def editsubtime(chat_id, subtime):
			conn, cursor = MainDB.connect()
			cursor.execute(f"UPDATE users SET sub_end = %s WHERE user_id = %s", (subtime, chat_id, ))
			conn.commit()

		def get_profile(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT * FROM users WHERE user_id = %s", (chat_id, ))
			result = cursor.fetchone()
			return result

		def editkey(chat_id, key):
			conn, cursor = MainDB.connect()
			key = encrypt_xor(key, str(chat_id))
			cursor.execute(f"UPDATE users SET wb_key_hash = %s WHERE user_id = %s", (key, chat_id, ))
			conn.commit()

		def check_notifications(chat_id):
			""" Проверка на разрешение получения уведомлений о новых заказах """
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT notify FROM users WHERE user_id = %s", (chat_id, ))
			result = cursor.fetchall()
			if len(result) == 0:
				return False
			else:
				return result[0][0]

		def update_notifications(chat_id, update):
			""" Изменение разрешения получения уведомлений о новых закахах """
			conn, cursor = MainDB.connect()
			cursor.execute(f"UPDATE users SET notify = %s WHERE user_id = %s", (update, chat_id, ))
			conn.commit()

		def get_all_data():
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT * FROM users")
			result = cursor.fetchall()
			return result

		def get_all_data_no_bloked():
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT * FROM users WHERE bloked = %s", (False, ))
			result = cursor.fetchall()
			return result

		def check_bloked(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT user_id FROM users WHERE user_id = %s AND bloked = %s", (chat_id, True, ))
			result = cursor.fetchall()
			if len(result) == 0:
				return True
			else:
				return False
				
		def update_bloked(chat_id, update):
			if UsersDBFunc.check_bloked(chat_id):
				conn, cursor = MainDB.connect()
				cursor.execute(f"UPDATE users SET bloked = %s WHERE user_id = %s", (update, chat_id, ))
				conn.commit()

		def get_balance(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT balance FROM users WHERE user_id = %s", (chat_id, ))
			result = cursor.fetchall()
			return result

		def update_sent_message_about_end_subscription(chat_id, update):
			conn, cursor = MainDB.connect()
			cursor.execute(f"UPDATE users SET sent_message_about_end_subscription = %s WHERE user_id = %s", (update, chat_id, ))
			conn.commit()

		def get_sent_message_about_end_subscription(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT sent_message_about_end_subscription FROM users WHERE user_id = %s", (chat_id, ))
			result = cursor.fetchall()
			return result

	except Exception as e:
		print('Ошибка:\n', format_exc())

class ReferalSystemDBFunc(object):
	try:

		def check_unique_code(link):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT referal_code_for_link FROM referal_system WHERE referal_code_for_link = %s", (link, ))
			result = cursor.fetchall()
			if len(result) == 0:
				return True
			else:
				return False

		def get_ref_code_by_user(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT referal_code_for_link FROM referal_system WHERE user_id = %s", (chat_id, ))
			result = cursor.fetchone()[0]
			return result
				
		def check_user_in_system(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT user_id FROM referal_system WHERE user_id = %s", (chat_id, ))
			result = cursor.fetchall()
			if len(result) == 0:
				return True
			else:
				return False

		def user_create(chat_id, link):
			if ReferalSystemDBFunc.check_user_in_system(chat_id):
				conn, cursor = MainDB.connect()
				cursor.execute(f"INSERT INTO referal_system VALUES(%s, %s, %s, %s)", (chat_id, '-', False, str(link), ))
				conn.commit()

		def update_user_in_system(chat_id, ref_code, link):
			if ReferalSystemDBFunc.check_user_in_system(chat_id):
				conn, cursor = MainDB.connect()
				cursor.execute(f"INSERT INTO referal_system VALUES(%s, %s, %s, %s)", (chat_id, '-', False, str(link), ))
				conn.commit()

			conn, cursor = MainDB.connect()
			cursor.execute(f"UPDATE referal_system SET invited = %s WHERE user_id = %s", (ref_code, chat_id, ))
			conn.commit()

		def check_pay_to_invited(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT pay_to_invited FROM referal_system WHERE user_id = %s", (chat_id, ))
			result = cursor.fetchone()[0]
			return result

		def update_balance_for_invited(chat_id, invited_to_user_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT invited FROM referal_system WHERE user_id = %s", (chat_id, ))
			invited_code = cursor.fetchone()[0]
			if invited_code != '-':
				cursor.execute(f"SELECT user_id FROM referal_system WHERE referal_code_for_link = %s", (invited_code, ))
				refer_id = cursor.fetchone()[0]
				cursor.execute(f'SELECT balance FROM users WHERE user_id= %s', (refer_id, ))
				balance = cursor.fetchone()[0]
				cursor.execute(f'UPDATE users SET balance= %s WHERE user_id= %s', (balance+paysum, refer_id))
				cursor.execute(f'UPDATE referal_system SET pay_to_invited= %s WHERE user_id= %s', (True, chat_id, ))

		def get_invited_to_user_id(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f'SELECT invited FROM referal_system WHERE user_id= %s', (chat_id, ))
			invited_code = cursor.fetchone()[0]
			if invited_code != '-':
				cursor.execute(f'SELECT user_id FROM referal_system WHERE referal_code_for_link= %s', (invited_code, ))
				result = cursor.fetchone()[0]
				return result
			else:
				return False

	except Exception as e:
		print('Ошибка:\n', format_exc())

class PaymentsDBFunc(object):
	try:

		def check_label(label):
			conn, cursor = MainDB.connect()
			cursor.execute(f'SELECT COUNT(*) FROM all_payments_label WHERE label =  %s', (label, ))
			result = cursor.fetchone()[0]
			if result == 0:
				return False
			else:
				return True

		def delete_label(label):
			conn, cursor = MainDB.connect()
			cursor.execute(f'DELETE FROM all_payments_label WHERE label = %s', (label, ))
			conn.commit()
			cursor.close()

		def create(chat_id, sum):
			conn, cursor = MainDB.connect()

			true_label = None
			while true_label != False:
				label = randint(111111, 999999)
				if PaymentsDBFunc.check_label(label) == False:
					label = label
					true_label = False
				else:
					true_label = None

			client = Client(yoomoney_token)
			user = client.account_info()
			quickpay = Quickpay(
				receiver=user.account,
				quickpay_form="shop",
				targets="Пополнение баланса Wbzillabot",
				paymentType="SB",
				sum=int(sum),
				label=label
			)
			cursor.execute(f"INSERT INTO payments VALUES(%s, %s, %s, %s)", (chat_id, sum, label, time_unix()))
			conn.commit()

			return quickpay.redirected_url, label

		def balance_update(chat_id, update):
			conn, cursor = MainDB.connect()
			cursor.execute(f'UPDATE users SET balance = %s WHERE user_id = %s', (update, chat_id, ))
			conn.commit()

		def addbalance(chat_id, sum):
			
			conn, cursor = MainDB.connect()
			cursor.execute(f'SELECT balance FROM users WHERE user_id =  %s', (chat_id, ))
			balance = cursor.fetchone()[0]
			cursor.execute(f'UPDATE users SET balance = %s WHERE user_id = %s', (balance+sum, chat_id, ))
			conn.commit()
			cursor.execute('SELECT all_sum_payments FROM statistic')
			allbalance = cursor.fetchone()[0]
			cursor.execute(f'UPDATE statistic SET last_sum_payment = %s', (sum, ))
			cursor.execute(f'UPDATE statistic SET user_id_last_payment = %s', (chat_id, ))
			cursor.execute(f'UPDATE statistic SET all_sum_payments = %s', (allbalance+sum, ))
			conn.commit()
		
		def check_pay(chat_id, label):
			conn, cursor = MainDB.connect()
			client = Client(yoomoney_token)
			history = client.operation_history(label=label)
			for operation in history.operations:
				if operation.status == 'success':
					cursor.execute(f'SELECT sum FROM payments WHERE user_id = %s AND bill_id = %s', (chat_id, label, ))
					sum = cursor.fetchone()[0]
					#cursor.execute(f'DELETE FROM payments WHERE bill_id = %s', (label, ))
					#conn.commit()
					#cursor.close()
					#PaymentsDBFunc.delete_label(label)
					conn, cursor = MainDB.connect()
					cursor.execute(f'SELECT balance FROM users WHERE user_id = %s', (chat_id, ))
					balance = cursor.fetchone()[0]
					cursor.execute(f'UPDATE users SET balance = %s WHERE user_id = %s', (balance+sum, chat_id, ))
					conn.commit()
					conn, cursor = MainDB.connect()
					cursor.execute('SELECT all_sum_payments FROM statistic')
					allbalance = cursor.fetchone()[0]
					cursor.execute(f'UPDATE statistic SET last_sum_payment = %s', (sum, ))
					cursor.execute(f'UPDATE statistic SET user_id_last_payment = %s', (chat_id, ))
					cursor.execute(f'UPDATE statistic SET all_sum_payments = %s', (allbalance+sum, ))
					conn.commit()
					return True
				else:
					return False

		def delete(label):
			conn, cursor = MainDB.connect()
			cursor.execute(f'DELETE FROM payments WHERE bill_id= %s', (label, ))
			conn.commit()
			cursor.close()

	except Exception as e:
		print('Ошибка:\n', format_exc())

class AdminsDBFunc(object):
	try:

		def get_stats():
			conn, cursor = MainDB.connect()
			cursor.execute(f'SELECT all_sum_payments FROM statistic')
			all_sum_payments = cursor.fetchone()[0]
			cursor.execute(f'SELECT user_id_last_payment FROM statistic')
			user_id_last_payment = cursor.fetchone()[0]
			if user_id_last_payment == 0:
				text = (
					'Статистика проекта:\n' + \
					f'Общая сумма пополнения: *{all_sum_payments}* руб'
				)
			else:
				cursor.execute(f'SELECT last_sum_payment FROM statistic')
				last_sum_payment = cursor.fetchone()[0]
				cursor.execute(f'SELECT username FROM users WHERE user_id={user_id_last_payment}')
				username = cursor.fetchone()[0]
				text = (
					'Статистика проекта:\n' + \
					f'Общая сумма пополнения: *{all_sum_payments}* руб\n' + \
					f'Имя пользователя, который последний пополнил баланс: [{username}](tg://user?id={user_id_last_payment})\n' + \
					f'Сумма, на которую последний раз пополняли бота *{last_sum_payment}* руб'
				)

			return text

		def get_proxies():
			conn, cursor = MainDB.connect()
			cursor.execute("SELECT * FROM proxys")
			proxys = cursor.fetchall()
			return proxys

		def update_proxies(proxies):
			conn, cursor = MainDB.connect()
			cursor.execute("DELETE FROM proxys")
			conn.commit()
			for url in proxies.split(" "):
				cursor.execute("INSERT INTO proxys(proxy) VALUES(%s)", (url,))
				conn.commit()
			return

		def get_full_stats():
			conn, cursor = MainDB.connect()
			cursor.execute('SELECT * FROM users')
			users = cursor.fetchall()
			data = []
			users_id = []
			for user in users:
				if user[0] not in users_id:
					cursor.execute(f"SELECT * FROM payments WHERE user_id = {user[0]}")
					last_pay = cursor.fetchall()
					if not last_pay:
						last_pay = [0, 0, 0, time_unix()]
					else:
						last_pay = last_pay[-1]
					try:
						data.append(
							{
								'user_id': user[0],
								'username': user[1],
								'balance': user[3],
								'statussub': user[4],
								'endsub': user[5],
								'notify':user[6],
								'bloked':user[7],
								'reg_time': datetime.fromtimestamp(user[8]).strftime("%Y-%m-%d %H:%M:%S") if user[8] else '0',
								'last_pay': last_pay[1],
								'date_last_pay': datetime.fromtimestamp(last_pay[3]).strftime("%Y-%m-%d %H:%M:%S") if last_pay[3] else 'None'
							}
						)
						users_id.append(user[0])
					except:
						print(last_pay)
			return adminile('WB_bot admin_statistic.csv', data)

	except Exception as e:
		print('Ошибка:\n', format_exc())

class SelectedCalendarDBFunc(object):
	try:

		def check(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f'SELECT * FROM selected_calendar_method WHERE user_id = %s', (chat_id, ))
			result = cursor.fetchall()
			if len(result) == 0: 
				return True
			else:
				return False

		def create(chat_id, selected_method):
			if SelectedCalendarDBFunc.check(chat_id):
				conn, cursor = MainDB.connect()
				cursor.execute(f"INSERT INTO selected_calendar_method VALUES(%s, %s)", (chat_id, selected_method, ))
				conn.commit()
			else:
				conn, cursor = MainDB.connect()
				cursor.execute(f'UPDATE selected_calendar_method SET selected_method= %s WHERE user_id = %s', (selected_method, chat_id, ))
				conn.commit()

		def get(chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f'SELECT selected_method FROM selected_calendar_method WHERE user_id = %s ', (chat_id, ))
			result = cursor.fetchone()[0]
			return result

	except Exception as e:
		print('Ошибка:\n', format_exc())

class NewOrdersDBFunc(object):
	try:
		def check(day, chat_id):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT COUNT(*) FROM new_orders WHERE day = %s AND chat_id = %s", (day, chat_id, ))
			return cursor.fetchone()[0] == 0

		def update_orders_array(day, chat_id, new_order, is_numeric):
			conn, cursor = MainDB.connect()
			if is_numeric:
				cursor.execute(f"UPDATE new_orders SET new_orders_array_numeric = array_append(new_orders_array_numeric, %s) WHERE chat_id = %s AND day = %s" , (new_order, chat_id, day, ))
			else:
				cursor.execute(f"UPDATE new_orders SET new_orders_array = array_append(new_orders_array, %s) WHERE chat_id = %s AND day = %s" , (new_order, chat_id, day, ))
			conn.commit()
			conn.close()

		def update_orders_count(chat_id, day, count):
			conn, cursor = MainDB.connect()
			cursor.execute(f"UPDATE new_orders SET orders_count = %s WHERE chat_id = %s AND day = %s" , (count, chat_id, day, ))
			conn.commit()
			conn.close()

		def update_all_sum_orders(chat_id, day, sum_order):
			conn, cursor = MainDB.connect()
			cursor.execute(f"UPDATE new_orders SET all_sum_orders = %s WHERE chat_id = %s AND day = %s" , (sum_order, chat_id, day, ))
			conn.commit()
			conn.close()

		def get_all_sum_orders(chat_id, day):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT all_sum_orders FROM new_orders WHERE day = %s AND chat_id = %s", (day, chat_id, ))
			result = cursor.fetchall()
			
			if len(result) == 0:
				return 0
			else:
				return result[0][0]


		def get_orders_count(chat_id, day):
			conn, cursor = MainDB.connect()
			cursor.execute(f"SELECT orders_count FROM new_orders WHERE day = %s AND chat_id = %s", (day, chat_id, ))
			result = cursor.fetchall()
			
			if len(result) == 0:
				return 0
			else:
				return result[0][0]

		def create(day, chat_id, new_order, sum_order, is_numeric):
			if NewOrdersDBFunc.check(day, chat_id):
				conn, cursor = MainDB.connect()
				if is_numeric:
					cursor.execute(f"INSERT INTO new_orders (day, chat_id, new_orders_array_numeric, orders_count, all_sum_orders) VALUES(%s, %s, %s, %s, %s)", (day, chat_id, [new_order], 1, float(sum_order), ))
				else:
					cursor.execute(f"INSERT INTO new_orders (day, chat_id, new_orders_array, orders_count, all_sum_orders) VALUES(%s, %s, %s, %s, %s)", (day, chat_id, [new_order], 1, float(sum_order), ))
				conn.commit()
				
			else:
				orders_count = NewOrdersDBFunc.get_orders_count(chat_id, day)
				NewOrdersDBFunc.update_orders_count(chat_id, day, orders_count+1)
				all_sum_orders = NewOrdersDBFunc.get_all_sum_orders(chat_id, day)
				NewOrdersDBFunc.update_all_sum_orders(chat_id, day, float(sum_order+float(all_sum_orders)))
				NewOrdersDBFunc.update_orders_array(day, chat_id, new_order, is_numeric)

		def check_order(chat_id, day, order_id, is_numeric):
			conn, cursor = MainDB.connect()
			if is_numeric:
				cursor.execute(f"SELECT COUNT(*) FROM new_orders WHERE day = %s AND chat_id = %s AND %s = ANY(new_orders_array_numeric)", (day, chat_id, order_id, ))
			else:
				cursor.execute(f"SELECT COUNT(*) FROM new_orders WHERE day = %s AND chat_id = %s AND %s = ANY(new_orders_array)", (day, chat_id, order_id, ))
			return cursor.fetchone()[0] == 0


		def delete(day):
			conn, cursor = MainDB.connect()
			cursor.execute(f"DELETE FROM new_orders WHERE day != %s ", (day, ))
			conn.commit()
			cursor.close()
			
	except Exception as e:
		print('Ошибка:\n', format_exc())