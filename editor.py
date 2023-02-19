import csv


def addfile(filename, datafile):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['number', 'date', 'supplierArticle', 'techSize', 'barcode', 'quantity', 'totalPrice', 'discountPercent', 'warehouseName',
                                                     'oblast', 'incomeID', 'odid', 'nmid', 'subject', 'category', 'brand', 'is_cancel', 'cancel_dt'])
        writer.writerow({
        'number': 'Номер заказа',
        'date': 'Дата заказа',
        'supplierArticle': 'Артикул',
        'techSize': 'Размер',
        'barcode': 'Штрих-код',
        'quantity': 'Кол-во',
        'totalPrice': 'Цена до согласованной скидки/промо/спп',
        'discountPercent': 'Согласованный итоговый дисконт',
        'warehouseName': 'Склад отгрузки',
        'oblast': 'Область',
        'incomeID': 'Номер поставки',
        'odid': 'Уникальный идентификатор позиции заказа',
        'subject': 'Предмет',
        'category': 'Категория',
        'brand': 'Бренд',
        'is_cancel': 'Признак отмены заказа',
        'cancel_dt': 'Дата отмены заказа'
        })
        for data in datafile:
            writer.writerow(data)
    return filename

def adminile(filename, datafile):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['user_id', 'username', 'balance', 'statussub', 'endsub', 'notify', 'bloked', 'last_pay', 'date_last_pay', 'reg_time'])
        writer.writerow({
            'user_id': 'User ID',
            'username': 'User nickname',
            'balance': 'Balance',
            'statussub': 'Is the subscription active',
            'endsub': 'Subscription end date',
            'notify': 'Notifications',
            'bloked': 'Blocking the bot',
            'reg_time': 'Registration Time',
            'last_pay': 'Last payment',
            'date_last_pay': 'Last payment date'
        })
        for data in datafile:
            writer.writerow(data)
    return filename