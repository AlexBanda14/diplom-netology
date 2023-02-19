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

search_users =[]


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7) })

def question_city(user_id):
    write_msg(user_id, 'Введите свой город: ')
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            town = event.text.lower()
            return town

def question_ages(user_id):
    write_msg(user_id, 'Введите свой возраст: ')
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            age = int(event.text)
            return age


def user_info(user_id):
    user_info = vk.method('users.get', {'user_ids': user_id, 'fields': 'bdate,city,sex'})
    if 'error' not in user_info:
        user_info_dict = {'id':user_id}
        user_info_dict['first_name'] = user_info[0]['first_name']
        if user_info[0]['sex'] == 2:
            user_info_dict['sex'] = 1
        elif user_info[0]['sex'] == 1:
            user_info_dict['sex'] = 2
        if 'city' in user_info[0]:
            user_info_dict['city'] = user_info[0]['city']['title']
        else:
            user_info_dict['city'] = question_city(user_id)
        if 'bdate' in user_info[0]:
            year_user = int(user_info[0]['bdate'][-4:])
            year_now = int(datetime.date.today().year)
            age = int(year_now-year_user)
            age_from = age - 3
            age_to = age + 3
            user_info_dict['age_from'] = age_from
            user_info_dict['age_to'] = age_to
        else:
            age = question_ages(user_id)
            age_from = age - 3
            age_to = age + 3
            user_info_dict['age_from'] = age_from
            user_info_dict['age_to'] = age_to
        return user_info_dict
    else:
        print('Ошибка подключения к серверу')



def search(user_id):
    """Поиск людей по параметрам"""
    user = user_info(user_id)
    search_user = vk_user.method('users.search', {'count': 100,
                                                  'city': print(user['city']),
                                                  'sex': user['sex'],
                                                  'status': 1 or 6,
                                                  'age_from': user['age_from'],
                                                  'age_to': user['age_to'],
                                                  'has_photo': '1',
                                                  'fields': 'is_closed' })
    if 'error' not in search_user:
        for persons in search_user['items']:
            if persons['is_closed'] == False:
                person = [
                persons['first_name'],
                persons['last_name'],
                str(persons['id'])]
                search_users.append(person)
    else:
        print('Ошибка подключения к серверу')


def found_users_info(offset):
    """Вывод инфы о найденном пользователе"""
    found_user = search_users[offset]
    return f' {found_user[0]} {found_user[1]}, ссылка https://vk.com/id{found_user[2]}'


def photo_of_found_person(user_id):
        """ПОЛУЧЕНИЕ ID ФОТОГРАФИЙ С СОРТИРОВКОЙ"""
        result = vk_user.method('photos.get', {'owner_id': user_id, 'album_id': 'profile', 'extended': 1, 'count':30 })
        photos_dict = {}
        if 'error' not in result:
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
        else:
            print('Ошибка подключения к серверу')



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
    id_user = search_users[offset]
    return int(id_user[2])


def start_searching(user_id, offset):
    if person_id(offset) not in select():
        person_id(offset)
        write_msg(user_id, found_users_info(offset))
        photo_of_found_person(person_id(offset))
        send_photo(user_id, offset)
        insert_data_seen_users(person_id(offset))
    else:
        offset += 1
        person_id(offset)
        write_msg(user_id, found_users_info(offset))
        photo_of_found_person(person_id(offset))
        send_photo(user_id, offset)
        insert_data_seen_users(person_id(offset))
