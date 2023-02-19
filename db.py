import psycopg2
from tokens import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

connection.autocommit = True

def create_table_seen_users():  # references users(vk_id)
    """СОЗДАНИЕ ТАБЛИЦЫ SEEN_USERS (ПРОСМОТРЕННЫЕ ПОЛЬЗОВАТЕЛИ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
            id serial,
            vk_id varchar(50) PRIMARY KEY);"""
        )
    print("Таблица SEEN_USERS создана")

def insert_data_seen_users(vk_id):
    """ВСТАВКА ДАННЫХ В ТАБЛИЦУ SEEN_USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_users (vk_id) 
            VALUES ('{vk_id}');"""
        )

def select():
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT vk_id FROM seen_users;"""
        )
        select_user = cursor.fetchall()
        list_db=[]
        for i in select_user:
            for z in i:
                list_db.append(z)
        return list_db


def drop_seen_users():
    """УДАЛЕНИЕ ТАБЛИЦЫ SEEN_USERS КАСКАДОМ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS seen_users CASCADE;"""
        )
        print('Таблица SEEN_USERS удалена')


def creating_database():
    drop_seen_users()
    create_table_seen_users()
