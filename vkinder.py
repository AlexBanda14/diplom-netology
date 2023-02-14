from random import randrange
from tokens import *
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
from pprint import pprint
from db import *


vk = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk)
vk_user = vk_api.VkApi(token=token_user)



def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7) })

def get_name(user_id):
    """Имя пользователя кто написал боту"""
    name = vk.method('users.get', {'user_ids': user_id})
    return name[0]['first_name']

def age(user_id):
    """Определение возраста пользователя"""
    age_user = vk.method('users.get', {'user_ids': user_id, 'fields': 'bdate'})
    if 'bdate' in age_user[0]:
        year_user = int(age_user[0]['bdate'][-4:])
        year_now = int(datetime.date.today().year)
        return  int(year_now-year_user)
    elif 'bdate' not in age_user[0]:
        write_msg(user_id, 'Введите свой возраст: ')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                ages = event.text
                return int(ages)

def city(user_id):
    """Определение города пользователя"""
    city_user = vk.method('users.get', {'user_ids': user_id, 'fields': 'city'})
    if 'city' in city_user[0]:
        return print(city_user[0]['city']['title'])
    elif 'city' not in city_user[0]:
        write_msg(user_id, 'Введите свой город: ')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                town = event.text.lower()
                return print(town)

def sex(user_id):
    """Определение пола пользователя"""
    sex_user = vk.method('users.get', {'user_ids': user_id, 'fields': 'sex'})
    if sex_user[0]['sex'] == 2:
        return 1
    elif sex_user[0]['sex'] == 1:
        return 2


def search(user_id):
    """Поиск людей по параметрам"""
    age_search = age(user_id)
    age_from = age_search - 3
    age_to = age_search + 3
    search_user = vk_user.method('users.search', {'count': 100, 'city': city(user_id), 'sex': sex(user_id),
                               'status': 1 or 6,'age_from': age_from,
                               'age_to': age_to, 'has_photo': '1', 'fields': 'is_closed' })
    for persons in search_user['items']:
        if persons['is_closed'] == False:
            first_name = persons['first_name']
            last_name = persons['last_name']
            vk_id = str(persons['id'])
            vk_link = 'vk.com/id' + vk_id
            insert_data_users(first_name, last_name, vk_id, vk_link)
        else:
            continue
    return print('Поиск завершен')


def found_users_info(offset):
    """Вывод инфы о найденном пользователе"""
    tuple_users = select(offset)
    list_users = []
    for users in tuple_users:
        list_users.append(users)
    return (f' {list_users[0]} {list_users[1]}, ссылка {list_users[3]}')



def photo_of_found_person(user_id):
        """ПОЛУЧЕНИЕ ID ФОТОГРАФИЙ С СОРТИРОВКОЙ"""
        result = vk_user.method('photos.get', {'owner_id': user_id, 'album_id': 'profile', 'extended': 1, 'count':30 })
        photos_dict = {}
        for photo in result['items']:
            photo_id = str(photo['id'])
            photo_like = photo['likes']
            photo_comments = photo['comments']
            if photo_like['count']:
                like = int(photo_like['count'])
                photos_dict[like] = photo_id
            if photo_comments['count']:
                comment = int(photo_comments['count'])
                photos_dict[comment] = photo_id
        list_of_ids: list = sorted(photos_dict.items(), reverse=True)
        return [photoid[1] for photoid in list_of_ids[0:3]]



def get_photo_list(offset):
    """Получение списка фото"""
    list_id = photo_of_found_person(person_id(offset))
    photo_list  = []
    for num_id in range(len(list_id)):
        photo_list.append(f"photo{person_id(offset)}_{list_id[num_id]}")
    return photo_list


def send_photo(user_id, offset):
    """Отправка фотографий"""
    for num_photo in range(len(get_photo_list(offset))):
        message = f'Фото №{num_photo + 1}'
        vk.method('messages.send', {'user_id': user_id,
                                    'access_token': token_user,
                                    'message': message,
                                    'attachment': get_photo_list(offset)[num_photo],
                                    'random_id': 0})


def person_id(offset):
    """Вывод ID пользователя"""
    user_info = select(offset)
    list_person = []
    for info_item in user_info:
        list_person.append(info_item)
    return int(list_person[2])

def start_searching(user_id, offset):
    """ЗАПУСК ВСЕХ МЕТОДОВ """
    write_msg(user_id, found_users_info(offset))
    person_id(offset)
    photo_of_found_person(person_id(offset))
    send_photo(user_id,offset)
    insert_data_seen_users(person_id(offset))
