from time import sleep
import requests
import json
from datetime import datetime

from traceback import format_exc
from database import AdminsDBFunc
from times_func import get_date, get_days_vievs, dynamic_delay
from check_errors import check_api_error
from config import proxies as proxies_list

api_urls = {
    'sales':'https://suppliers-stats.wildberries.ru/api/v1/supplier/sales',
    'orders':'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders',
    'remains':'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks',
    'brief':'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders',
    'cancelled_orders':'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders'
}
api_words = {
    'sales':'Выкупы',
    'orders':'Заказы'
}

count_error = 0

def get_data(api_method, date_methhod_or_date, key, choice_remain):
    try:

        dateFrom = get_date(date_methhod_or_date)
        date_for_views = get_days_vievs(date_methhod_or_date)

        if api_method in ('sales', 'orders'):
            msg = ''
            word = api_words[api_method]
            msg = msg + f'{word} за {date_for_views[0]}:\n'
            msg = msg + send_req(api_method, dateFrom, key, choice_remain, False, False, False)
                
        elif api_method == 'remains':
            msg = ''
            msg = msg + send_req(api_method, dateFrom, key, choice_remain, False, False, False)
        
        elif api_method == 'brief':
            msg = ''
            msg += f'Дата:{date_for_views}\n'
            
            brief_data = send_req(api_method, dateFrom, key, choice_remain, False, True, False)
            if isinstance(brief_data, list):
                total_orders, total_price = brief_data
                msg += (
                    f"Всего заказов: {total_orders}\n" + \
                    f"Заказано на сумму: {round(total_price, 2)} руб.\n"
                )
            else:
                msg += (
                    f"Всего заказов: {brief_data}\n" + \
                    f"Заказано на сумму: {brief_data}\n"
                )
                

            sales_data = send_req('sales', dateFrom, key, choice_remain, False, True, True)
            if isinstance(sales_data, list):
                sales_count, sales_price = sales_data
                msg += (
                    f"Всего выкупов: {sales_count}\n" + \
                    f"Выкуплено на сумму: {round(sales_price, 2)} руб.\n"
                )
            else:
                msg += (
                    f"Всего выкупов: {sales_data}\n" + \
                    f"Выкуплено на сумму: {sales_data}\n"
                )

            cancelled_orders_data = send_req('cancelled_orders', dateFrom, key, choice_remain, False, True, True)
            if isinstance(cancelled_orders_data, list):
                cancelled_count, cancelled_price = cancelled_orders_data
                msg += (
                    f"Всего возвращенных заказов: {cancelled_count}\n" + \
                    f"Возвращено на сумму: {round(cancelled_price, 2)} руб.\n"
                )
            else:
                msg += (
                    f"Всего возвращенных заказов: {cancelled_orders_data}\n" + \
                    f"Возвращено на сумму: {cancelled_orders_data}\n"
                )

        return msg

    except Exception as e:
        print('Ошибка:\n', format_exc())

def send_req(api_method, dateFrom, key, choice_remain, get_json, specifed_timer, get_count):
    global count_error
    try:
        proxies = ["http://iseau8725:b7ea0c@193.23.50.223:10027"]#proxies_list#AdminsDBFunc.get_proxies()
        #if api_method == 'orders' or 'cancelled_orders':
        #    sleep(dynamic_delay(specifed_timer, True))
        #else:
        #    sleep(dynamic_delay(specifed_timer, False))
        url = api_urls[api_method]
        data = requests.get(
                f'{url}',
                params={
                    'dateFrom':dateFrom,
                    'flag':1,
                    'key':key
                })
            #, proxies={"all": proxies[count_error]})
        print(data)
        error = None
        error_count = 0
        while error == None:
            
            if check_api_error(data.status_code) is False:
                error = False
                msg = ''
                json_format = json.loads(data.text)
                if len(json_format) != 0:

                    if api_method == 'sales':
                        count = 0
                        sales_price = 0
                        if get_count is True:
                            for elem in json_format:
                                count += 1
                                for_pay = elem['forPay']
                                sales_price += for_pay
                            return [count, sales_price]
                        else:
                            for elem in json_format:
                                count += 1
                                brand = elem['brand']
                                quality = elem['quantity']
                                acticle = elem['supplierArticle']
                                category = elem['category']
                                try:
                                    techSize = elem['techSize']
                                    if techSize == 0 or techSize== '0':
                                        size = 0
                                    else:
                                        size = 1
                                        techSize = elem['techSize']
                                except:
                                    size = 0
                                name = elem['subject']
                                barcode = elem['barcode']
                                warhouse = elem['warehouseName']
                                for_pay = elem['forPay']

                                if size == 0:
                                    msg = msg + (
                                        f'\n{count}.' + \
                                        f'\nБренд: {brand}' + \
                                        f'\nКол-во: {quality} шт' + \
                                        f'\nАртикул: {acticle}' + \
                                        f'\nКатегория: {category}' + \
                                        f'\nПредмет: {name}' + \
                                        f'\nШтрих-код: {barcode}' + \
                                        f'\nСклад отгрузки: {warhouse}' + \
                                        f"\nК перечислению поставщику: {for_pay} руб.\n"
                                    )
                                else:
                                    msg = msg + (
                                        f'\n{count}.' + \
                                        f'\nБренд: {brand}' + \
                                        f'\nКол-во: {quality} шт' + \
                                        f'\nАртикул: {acticle}' + \
                                        f'\nКатегория: {category}' + \
                                        f'\nПредмет: {name}' + \
                                        f'\nРазмер: {techSize}' + \
                                        f'\nШтрих-код: {barcode}' + \
                                        f'\nСклад отгрузки: {warhouse}' + \
                                        f"\nК перечислению поставщику: {for_pay} руб.\n"
                                    )

                    elif api_method == 'orders':
                        count = 0
                        for elem in json_format:
                            print(elem)
                            count += 1
                            brand = elem['brand']
                            quality = elem['quantity']
                            acticle = elem['supplierArticle']
                            category = elem['category']
                            try:
                                techSize = elem['techSize']
                                if techSize == 0 or techSize== '0':
                                    size = 0
                                else:
                                    size = 1
                                    techSize = elem['techSize']
                            except:
                                size = 0 
                            name = elem['subject']
                            barcode = elem['barcode']
                            price = elem['totalPrice']
                            discount = elem['discountPercent']
                            warhouse = elem['warehouseName']
                            discount_price = round((float(price)-(float(price)/100*float(discount))), 2)
                            oblast = elem['oblast']

                            if size == 0:
                                msg = msg + (
                                    f'\n{count}.' + \
                                    f'\nБренд: {brand}' + \
                                    f'\nКол-во: {quality} шт' + \
                                    f'\nАртикул: {acticle}' + \
                                    f'\nКатегория: {category}' + \
                                    f'\nПредмет: {name}' + \
                                    f'\nШтрих-код: {barcode}' + \
                                    f'\nРегион: {oblast}' + \
                                    f'\nСклад отгрузки: {warhouse}' + \
                                    f'\nЦена продажи: {discount_price} руб\n'
                                )
                            else:
                                msg = msg + (
                                    f'\n{count}.' + \
                                    f'\nБренд: {brand}' + \
                                    f'\nКол-во: {quality} шт' + \
                                    f'\nАртикул: {acticle}' + \
                                    f'\nКатегория: {category}' + \
                                    f'\nПредмет: {name}' + \
                                    f'\nРазмер: {techSize}' + \
                                    f'\nШтрих-код: {barcode}' + \
                                    f'\nРегион: {oblast}' + \
                                    f'\nСклад отгрузки: {warhouse}' + \
                                    f'\nЦена продажи: {discount_price} руб\n'
                                )
    
                    elif api_method == 'brief':
                        total_orders = 0
                        total_price = 0
                        for elem in json_format:
                            total_orders += 1
                            price = elem['totalPrice']
                            discount = elem['discountPercent']
                            total_price += float(price)-(float(price)/100*float(discount))
                        
                        return [total_orders, total_price]

                    elif api_method == 'remains':
                        if choice_remain == None:
                            remains_data = []
                            for elem in json_format:
                                warehouse_name = elem['warehouseName']
                                if warehouse_name not in remains_data:
                                    remains_data.append(warehouse_name)

                            for remain in remains_data:
                                msg = msg + f'\n\n*{remain}*:'
                                count = 0
                                for elem in json_format:
                                    warehouse_name = elem['warehouseName']
                                    if remain == warehouse_name:
                                        count += 1
                                        category = elem['category']
                                        brand = elem['brand']
                                        supplier_article = elem['supplierArticle']
                                        try:
                                            techSize = elem['techSize']
                                            if techSize == 0 or techSize== '0':
                                                size = 0
                                            else:
                                                size = 1
                                                techSize = elem['techSize']
                                        except:
                                            size = 0                                    
                                        subject = elem['subject']
                                        quantity_full = elem['quantityFull']
                                        if size == 0:
                                            msg = msg +  f'\n{count}. {category} {brand} {supplier_article} {subject} - {quantity_full} шт.\n'
                                        elif size == 1:
                                            msg = msg +  f'\n{count}. {category} {brand} {supplier_article} {subject} {techSize} - {quantity_full} шт.\n'
                        else:
                            count = 0
                            for elem in json_format:
                                warehouse_name = elem['warehouseName']
                                if choice_remain == warehouse_name:
                                    count += 1
                                    category = elem['category']
                                    brand = elem['brand']
                                    supplier_article = elem['supplierArticle']
                                    try:
                                        techSize = elem['techSize']
                                        if techSize == 0 or techSize== '0':
                                            size = 0
                                        else:
                                            size = 1
                                            techSize = elem['techSize']
                                    except:
                                        size = 0                                 
                                    subject = elem['subject']
                                    quantity_full = elem['quantityFull']
                                    if size == 0:
                                        msg = msg +  f'\n\n{count}. {category} {brand} {supplier_article} {subject} - {quantity_full} шт.'
                                    elif size == 1:
                                        msg = msg +  f'\n\n{count}. {category} {brand} {supplier_article} {subject} {techSize} - {quantity_full} шт.'

                    elif api_method == 'cancelled_orders':
                        count = 0
                        cancelled_price = 0
                        if get_count is True:
                            for elem in json_format:
                                is_cancel = elem['isCancel']
                                if is_cancel == True:
                                    count += 1
                                    price = elem['totalPrice']
                                    discount = elem['discountPercent']
                                    cancelled_price += float(price)-(float(price)/100*float(discount))
                                    

                            return [count, cancelled_price]
                        else:
                            for elem in json_format:
                                count += 1
                                is_cancel = elem['isCancel']
                                if is_cancel == True:
                                    brand = elem['brand']
                                    quality = elem['quantity']
                                    acticle = elem['supplierArticle']
                                    category = elem['category']
                                    try:
                                        techSize = elem['techSize']
                                        if techSize == 0 or techSize== '0':
                                            size = 0
                                        else:
                                            size = 1
                                            techSize = elem['techSize']
                                    except:
                                        size = 0 
                                    name = elem['subject']
                                    barcode = elem['barcode']
                                    price = elem['totalPrice']
                                    discount = elem['discountPercent']
                                    warhouse = elem['warehouseName']
                                    discount_price = round((float(price)-(float(price)/100*float(discount))), 2)
                                    oblast = elem['oblast']
                                    cancel_dt = elem['cancel_dt']
                                    if size == 0:
                                        msg = msg + (
                                            f'\n{count}.' + \
                                            f'\nБренд: {brand}' + \
                                            f'\nКол-во: {quality} шт' + \
                                            f'\nАртикул: {acticle}' + \
                                            f'\nКатегория: {category}' + \
                                            f'\nПредмет: {name}' + \
                                            f'\nШтрих-код: {barcode}' + \
                                            f'\nРегион: {oblast}' + \
                                            f'\nСклад отгрузки: {warhouse}' + \
                                            f'\nЦена продажи: {discount_price} руб' + \
                                            f'\nДата отмены заказа: {cancel_dt}\n'
                                        )
                                    else:
                                        msg = msg + (
                                            f'\n{count}.' + \
                                            f'\nБренд: {brand}' + \
                                            f'\nКол-во: {quality} шт' + \
                                            f'\nАртикул: {acticle}' + \
                                            f'\nКатегория: {category}' + \
                                            f'\nПредмет: {name}' + \
                                            f'\nРазмер: {techSize}' + \
                                            f'\nШтрих-код: {barcode}' + \
                                            f'\nРегион: {oblast}' + \
                                            f'\nСклад отгрузки: {warhouse}' + \
                                            f'\nЦена продажи: {discount_price} руб' + \
                                            f'\nДата отмены заказа: {cancel_dt}\n'
                                        )

                else:
                    msg = msg + 'Нет данных за этот период времени'
                if get_json is True:
                    return msg, json_format
                else:
                    return msg
            else:
                count_error += 1
                if count_error >= len(proxies): count_error = 0
                if data.status_code == 429:
                    if error_count != 10:
                        error_count += 1
                        #if api_method == 'orders' or 'cancelled_orders':
                        #    sleep(dynamic_delay(specifed_timer, True))
                        #else:
                        #    sleep(dynamic_delay(specifed_timer, False))
                    else:
                        return 'Подождите пару минут и попробуйте снова'
                else:
                    return check_api_error(data.status_code)

    except Exception as e:
        count_error += 1
        if count_error >= len(proxies): count_error = 0
        print('Ошибка:\n', format_exc())

def check_remains_warehouse_count(key):
    try:
        sleep(dynamic_delay(False, False))
        error = None
        while error == None:
            dateFrom = datetime.now().strftime('%Y-%m-%dT00:00:00')
            data = requests.get(
                'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks',
                params={
                    'dateFrom':dateFrom,
                    'key':key
                })

            if check_api_error(data.status_code) is False:
                json_format = json.loads(data.text)
                warehouse_data = []
                for warehouse in json_format:
                    if warehouse['warehouseName'] not in warehouse_data:
                        warehouse_data.append(warehouse['warehouseName'])
                error = False
                
            else:
                sleep(dynamic_delay(False, False))

        return len(warehouse_data)

    except Exception as e:
        print('Ошибка:\n', format_exc())

def get_all_warehouse_name(key):
    global count_error
    """ Получение всех складов """
    try:
        sleep(dynamic_delay(False, False))
        error = None
        warehouse_data = []
        while error == None:
            dateFrom = datetime.now().strftime('%Y-%m-%dT00:00:00')
            data = requests.get(
                'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks',
                params={
                    'dateFrom':dateFrom,
                    'key':key
                })

        
            if check_api_error(data.status_code) is False:
                json_format = json.loads(data.text)
                for warehouse in json_format:
                    if warehouse['warehouseName'] not in warehouse_data:
                        warehouse_data.append(warehouse['warehouseName'])
                error = False
            else:
                if data.status_code == 429:
                    sleep(dynamic_delay(False, False))
                    
        return warehouse_data

    except Exception as e:
        print('Ошибка:\n', format_exc())