from config import *
import psycopg2
from db import MainDB

# def test():
#     try:
#         connection = psycopg2.connect(
#             host=db_host,
#             user=db_user,
#             password=db_password,
#             database='wb_main_db'
#             )
#
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "SELECT version();"
#                 )
#             print(f"Server version: {cursor.fetchone()}")
#
#     except Exception as _ex:
#         print('[INFO] Error while working with PostgreSQL', _ex)
#     finally:
#         if connection:
#             connection.close()
#             print('[INFO] PostgreSQL connection closed')
#
# def createdb():
#     pass

def create(chat_id, username, wb_key, sub_activate):
    conn, cursor = MainDB.connect()
    key = wb_key#encrypt_xor(wb_key, str(chat_id))
    sub_end = ''#datetime.now() + timedelta(weeks=1)
    reg_time = ''#time_unix()
    cursor.execute(f"INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (chat_id, username, key, 0, sub_activate, str(sub_end), True, False, False, reg_time))
    conn.commit()


def get_all_data():
    conn, cursor = MainDB.connect()
    cursor.execute(f"SELECT * FROM users")
    result = cursor.fetchall()
    return result

# create(
#     chat_id='',
#     username='',
#     wb_key='',
#     sub_activate=''
#     )

r = get_all_data()
with open('test.txt', 'w', encoding='utf-8') as f:
    for i in r:
        print(i)
        f.writelines(str(i))
print(len(r))
print(type(r))

