from time import sleep
from traceback import format_exc

from datetime import datetime

from database import NewOrdersDBFunc

def check_day():
	while True:
		try:
			sleep(1000)
			day = datetime.strptime(datetime.now().strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp()
			NewOrdersDBFunc.delete(day)
		except Exception as e:
			print('Ошибка:\n', format_exc())

check_day()