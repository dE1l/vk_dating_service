# -*- coding: utf-8 -*-
import shelve

import vk_api

from credentials import User


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def auth_handler():
    """ При возникновении двухфакторной аутентификации вызывается эта функция.
    """

    # Код двухфакторной аутентификации
    key = input("Enter authentication code: ")
    # Если 1 то сохранить, 0 не сохранять.
    remember_device = 1

    # Отправляет запрос
    return key, remember_device

def main():
    """ Пример получения последнего сообщения со стены """

    storage = shelve.open("shelve.txt")
    black_list = storage['black_list']
    valid = storage['valid']
    # storage.valid = []

    login, password = User.login, User.password

    vk_session = vk_api.VkApi(
        login, password,
        auth_handler=auth_handler  # функция для обработки двухфакторной аутентификации
    )
    # vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk = vk_session.get_api()

    """ VkApi.method позволяет выполнять запросы к API. В этом примере
        используется метод wall.get (https://vk.com/dev/wall.get) с параметром
        count = 1, т.е. мы получаем один последний пост со стены текущего
        пользователя.
    """
    response = vk.users.search(fields='photo_max,screen_name, last_seen, can_write_private_message',
                               sort=0, count=100, country=1, city=103, sex=1, status=1,
                               age_from=23, age_to=25, online=1, has_photo=1)

    l = len(response['items'])
    printProgressBar(0, l, prefix='Progress:', suffix='Complete', length=50)
    for i, user in enumerate(response['items']):
        printProgressBar(i, l, prefix='Progress:', suffix='Complete', length=50)
        if user['id'] not in storage['black_list']:
            if user['can_write_private_message'] == 1:
                friends_data = vk.friends.get(user_id=user['id'])
                if friends_data['count'] < 200:
                    messages = vk.messages.getHistory(user_id=user['id'], count=0)
                    if messages["count"] == 0:
                        valid.append(user)
                        black_list.append(user['id'])
                        print(user['first_name'], user['last_name'], 'http://vk.com/id%s' % user['id'])
    printProgressBar(l, l, prefix='Progress:', suffix='Complete', length=50)
    storage['valid'] = valid
    storage['black_list'] = black_list
    # response = vk.wall.get(count=1)  # Используем метод wall.get

    storage.close()

if __name__ == '__main__':
    main()