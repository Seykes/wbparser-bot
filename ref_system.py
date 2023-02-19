import secrets
import string

from traceback import format_exc

from config import length_referral_link
from database import ReferalSystemDBFunc


def generate_alphanum_crypt_string(length):
	try:
		letters_and_digits = string.ascii_letters + string.digits
		crypt_rand_string = ''.join(secrets.choice(
			letters_and_digits) for i in range(length))

		return crypt_rand_string
		
	except Exception as e:
		print('Ошибка:\n', format_exc())

def generate_referral_link():
	""" Генерация реферральной ссылки для пользователя """
	try:
		link = generate_alphanum_crypt_string(length_referral_link)
		link_unique = True 
		if ReferalSystemDBFunc.check_unique_code(link):
			return link
		else:
			link_unique = False
			while link_unique == False:
				link = generate_alphanum_crypt_string(length_referral_link)
				if ReferalSystemDBFunc.check_unique_code:
					link_unique = True
					return link
				else:
					link_unique = False

	except Exception as e:
		print('Ошибка:\n', format_exc())

