from traceback import format_exc

def check_api_error(status_code):
	try:
		if status_code == 200:
			return False
		elif status_code == 429:
			print('Ошибка Api ', status_code)
			return "Слишком много запросов к api! Пожалуйста повторите спустя некоторое время"
		elif status_code == 400:
			print('Ошибка Api ', status_code)
			return "Возникла неизвестная ошибка"
			
	except Exception as e:
		print('Ошибка:\n', format_exc())