import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateDatabase, DuplicateTable

from traceback import format_exc

from config import (
	db_user,
	db_password,
	db_host,
	db_port
)

class PostgresDB(object):
	try:

		def connect():
			conn = psycopg2.connect(
				user = db_user,
				password = db_password,
				host = db_host,
				port = db_port,
				database = 'wb_main_db'
			)

			conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
			cursor = conn.cursor()

			return conn, cursor

	except Exception as e:
		print('Ошибка:\n', format_exc())

class MainDB(object):
	try:

		def connect():
			""" Подключение к таблице пользователей """
			conn, cursor = PostgresDB.connect()
   

			conn = psycopg2.connect(
				user = db_user,
				password = db_password,
				host = db_host,
				port = db_port,
				database = 'wb_db'
			)
			conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
			cursor = conn.cursor()

			return conn, cursor

		def create_tables():
			conn, cursor = PostgresDB.connect()
	
			try:
				cursor.execute('CREATE DATABASE wb_db')
				print('База wb_db создана')

			except DuplicateDatabase:
				print('База wb_db уже создана')

			conn, cursor = MainDB.connect()
			
			try:
				cursor.execute(""" CREATE TABLE users(
						user_id INTEGER,
						username TEXT,
						wb_key_hash TEXT,
						balance INTEGER,
						sub_acitvate BOOL,
						sub_end TIMESTAMP,
						notify BOOL, 
						bloked BOOL,
						sent_message_about_end_subscription BOOL,
						reg_time INTEGER ); """)
				print('Таблица users создана')
			except DuplicateTable:
				print('Таблица users уже создана')

			try:
				cursor.execute(""" CREATE TABLE payments(
						user_id INTEGER,
						sum INTEGER,
						bill_id INTEGER,
						time INTEGER); """)
				print('Таблица payments создана')
			except DuplicateTable:
				print('Таблица payments уже создана')

			try:
				cursor.execute(""" CREATE TABLE statistic(
						all_sum_payments INTEGER,
						user_id_last_payment INTEGER,
						last_sum_payment INTEGER); """)
				print('Таблица statistic создана')
			except DuplicateTable:
				print('Таблица statistic уже создана')

			try:
				cursor.execute(""" CREATE TABLE referal_system(
						user_id INTEGER,
						invited TEXT,
						pay_to_invited BOOL,
						referal_code_for_link TEXT); """)
				print('Таблица referal_system создана')
			except DuplicateTable:
				print('Таблица referal_system уже создана')

			try:
				cursor.execute(""" CREATE TABLE company(
						main_user_id INTEGER,
						access_users TEXT); """)
				print('Таблица company создана')
			except DuplicateTable:
				print('Таблица company уже создана')
			
			try:
				cursor.execute(""" CREATE TABLE selected_calendar_method(
						user_id INTEGER,
						selected_method TEXT) """)
				print('Таблица selected_calendar_method создана')
			except DuplicateTable:
				print('Таблица selected_calendar_method уже создана')

			try:
				cursor.execute(""" CREATE TABLE all_payments_label(
						label INTEGER) """)
				print('Таблица all_payments_label создана')
			except DuplicateTable:
				print('Таблица all_payments_label уже создана')

			try:
				cursor.execute(""" CREATE TABLE new_orders(
						day BIGINT,
						chat_id INTEGER,
						new_orders_array BIGINT[] NULL,
						orders_count INTEGER,
						all_sum_orders DECIMAL,
						new_orders_array_numeric NUMERIC[] NULL) """)
				print('Таблица new_orders создана')
			except DuplicateTable:
				print('Таблица new_orders уже создана')	

			try:
				cursor.execute(""" CREATE TABLE proxys(
					proxy TEXT) """)
				print("Таблица proxys создана")
			except DuplicateTable:
				print("Таблица proxys уже создана")

	except Exception as e:
		print('Ошибка:\n', format_exc())
