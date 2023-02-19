import requests
import time

from datetime import datetime, timedelta

from cryptor import decrypt_xor
from bot import bot
from dateparser import parse
from database import UsersDBFunc, NewOrdersDBFunc, AdminsDBFunc
from traceback import format_exc

from product_parser import get_data

count_error = 0

def checker():
	global count_error
	while True:
		proxies = AdminsDBFunc.get_proxies()
		try:
			data = UsersDBFunc.get_all_data()
			time.sleep(666) # Должно быть 666
			for user in data:
				chat_id = user[0]
				if UsersDBFunc.check_notifications(chat_id) == True:
					status = UsersDBFunc.check_sub(chat_id)
					if status == True:
						key = decrypt_xor(user[2], str(chat_id))
						start = datetime.strftime(datetime.now(), '%Y-%m-%dT00:00:00')
						
						requests_data = requests.get(
							f'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders?dateFrom={start}&flag=1&key={key}', proxies={"all": proxies[count_error]})
						
						date_for_print = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M') 
						print(f'WB status: {requests_data.status_code} Time {date_for_print}')
						if requests_data.status_code == 200 and len(requests_data.json()) != 0:
							for i in range(len(requests_data.json())):
								if requests_data.json()[i]['number'] != 0:
									order_number = requests_data.json()[i]['number']
									is_num_type_numeric = False
									day = datetime.strptime(datetime.now().strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp()
									if NewOrdersDBFunc.check_order(chat_id, day, order_number, is_num_type_numeric) is True:
										date_order = parse(requests_data.json()[i]['date']).strftime('%d.%m.%Y %H:%M')
										brand = requests_data.json()[i]['brand']
										quality = requests_data.json()[i]['quantity']
										acticle = requests_data.json()[i]['supplierArticle']
										category = requests_data.json()[i]['category']
										try:
											techSize = requests_data.json()[i]['techSize']
										except:
											techSize = False
										name = requests_data.json()[i]['subject']
										barcode = requests_data.json()[i]['barcode']
										price = requests_data.json()[i]['totalPrice']
										discount = requests_data.json()[i]['discountPercent']
										warhouse = requests_data.json()[i]['warehouseName']
										discount_price = round((float(price)-(float(price)/100*float(discount))), 2)
												
										oblast = requests_data.json()[i]['oblast']
										last_change_datet = parse(requests_data.json()[i]['lastChangeDate']).strftime('%d.%m.%Y %H:%M')
										nmId = requests_data.json()[i]['nmId']

										order_num = NewOrdersDBFunc.get_orders_count(chat_id, day) + 1
										all_sum_orders = round(float(NewOrdersDBFunc.get_all_sum_orders(chat_id, day)) + discount_price, 2)
										parce_data = get_data(f'https://www.wildberries.ru/catalog/{nmId}/detail.aspx?targetUrl=SN')
										try:
											msg_text = create_message(order_num, date_order, brand, acticle, category, name, techSize, quality, barcode, oblast, discount_price, warhouse, last_change_datet, nmId, all_sum_orders, parce_data, key)
											
											bot.send_message(chat_id, msg_text, parse_mode='markdown', disable_web_page_preview=False)
											
										except:
											UsersDBFunc.update_bloked(chat_id, True)
										NewOrdersDBFunc.create(day, chat_id, order_number, discount_price, is_num_type_numeric)
						else:
							count_error += 1	
							if count_error >= len(proxies): count_error = 0			
		except Exception as e:
			count_error += 1
			if count_error >= len(proxies): count_error = 0
			print('Ошибка:\n', format_exc())

def create_message(order_num, date_order, brand, acticle, category, name, techSize, quality, barcode, oblast, discount_price, warhouse, last_change_datet, nmId, all_sum_orders, parce_data, key):
	try:
		today = datetime.now()
		start = today.replace(day = 1)
		orders = requests.get(f"https://suppliers-stats.wildberries.ru/api/v1/supplier/orders?dateFrom={datetime.strftime(start, '%Y-%m-%d')}&key={key}", proxies={"all": proxies[count_error]}).json()
		sales = requests.get(f"https://suppliers-stats.wildberries.ru/api/v1/supplier/sales?dateFrom={datetime.strftime(start, '%Y-%m-%d')}&key={key}", proxies={"all": proxies[count_error]}).json()
		info = requests.get(f"https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks?dateFrom={datetime.strftime(start, '%Y-%m-%d')}&key={key}", proxies={"all": proxies[count_error]}).json()
		all_orders = len([order for order in orders if not order['isCancel'] and order['supplierArticle'] == acticle])
		all_sales = len([sale for sale in sales if sale['saleID'].startswith("S") and sale['supplierArticle'] == acticle])
		info = [sale for sale in info if sale['supplierArticle'] == acticle]
		allToClient = 0
		allFromClient = 0
		allQuantity = 0
		for sale in info:
			allToClient += sale['inWayToClient']
			allFromClient += sale['inWayFromClient']
			allQuantity += sale['quantityFull']
		msg = 'У вас новый заказ!'
		msg += f'\n🛒 Заказ *№{order_num}*'
		msg += f'\n📅 Дата: *{date_order}*'
		msg += f'\n🏷 Бренд: *{brand}*'
		msg += f'\n🆔 Артикул: *{acticle}*'
		msg += f'\n🗂 Категория: *{category}*'
		msg += f'\n📦 Предмет: *{name}*'
		msg += f'\n🔢 Кол-во: *{quality}* шт.'
		if techSize != False:
			msg += f'\n📏 Размер: *{techSize}*'
		msg += f'\nℹ️ Штрих-код: *{barcode}*'
		msg += f'\n🚚 Регион: *{oblast}*'
		msg += f'\n💵 Цена продажи: *{discount_price}* руб.'
		if parce_data != None:
			if 'commission_percentage' in parce_data.keys():
				commission_percentage = parce_data['commission_percentage']
				msg += f'\n💼 Комиссия (базовая): *{commission_percentage}%*'
		msg += f'\n🏪 Склад отгрузки: *{warhouse}*'
		msg += f'\n🕘 Время обновления информации: *{last_change_datet}*'
		msg += f'\n💰 Сегодня (всех артикулов): *{order_num}* на *{all_sum_orders}* руб.'
		if all_orders > 0 and all_sales > 0:
			msg += f'\n💎 Выкупов за месяц: **{int(all_sales / all_orders * 100)}% ({all_sales}/{all_orders})**'
		msg += f'\n⏩ В пути к клиенту: **{allToClient}**'
		msg += f'\n⏪ В пути от клиента: **{allFromClient}**'
		msg += f'\n🕳 Остаток: **{allQuantity}**'
		""" if parce_data != None:
			if 'commission_percentage' in parce_data.keys():
				commission_percentage = parce_data['commission_percentage']
				msg += f'\n💼 Комиссия: *{commission_percentage}%*'

			if 'cost_mono_and_mix_logistics' in parce_data.keys():
				cost_mono_and_mix_logistics = parce_data['cost_mono_and_mix_logistics']
				msg += f'\n💳 Стоимость логистики Моно и Микс: *{cost_mono_and_mix_logistics}* руб.'

			if 'cost_storing_mono_and_mixed' in parce_data.keys():
				cost_storing_mono_and_mixed = parce_data['cost_storing_mono_and_mixed']
				msg += f'\n📝 Стоимость хранения Моно и Микс: *{cost_storing_mono_and_mixed}* руб./день'
			
			if 'cost_monopallet_logistics' in parce_data.keys():
				cost_monopallet_logistics = parce_data['cost_monopallet_logistics']
				msg += f'\n💳 Стоимость логистики Монопаллеты: *{cost_monopallet_logistics}* руб.'
			
			if 'storage_cost_monopallets' in parce_data.keys():
				storage_cost_monopallets = parce_data['storage_cost_monopallets']
				msg += f'\n📝 Стоимость хранения Монопаллеты: *{storage_cost_monopallets}* руб./день'
			
			if 'calculation_according_actual_dimensions_goods' in parce_data.keys():
				calculation_according_actual_dimensions_goods = parce_data['calculation_according_actual_dimensions_goods']
				msg += f'\n⚖️ Расчет по фактическим габаритам товара: *{calculation_according_actual_dimensions_goods}*' """

		msg += f'\n🔗 [Ссылка на товар](https://www.wildberries.ru/catalog/{nmId}/detail.aspx?targetUrl=SN)'

		return msg
	except Exception as e:
		print('Ошибка:\n', format_exc())

checker()



