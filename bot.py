from vkinder import *


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        if request == 'привет':
            write_msg(user_id, f'Привет, {get_name(user_id)} \n Для начала поиска напишите "Начать поиск"')

        elif request == 'начать поиск':
            creating_database()
            search(user_id)
            start_searching(user_id, offset)
            write_msg(event.user_id, f'Нашёл для тебя пару, пиши "Вперед" для перехода к следующей паре')

        elif request == 'вперед':
            for i in line:
                offset += 1
                start_searching(user_id, offset)
                break

        else:
            write_msg(event.user_id, 'Твоё сообщение непонятно')