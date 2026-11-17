from database import (
    add_user, get_user, add_favorite, get_favorites,
    add_viewed, get_viewed)
from vkapi import get_photos, search_users, vk_session, vk, user_vk
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

longpoll = VkBotLongPoll(vk_session, 241832744)
users_state = {}
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        print(event.obj.message['from_id'], event.obj.message['text'])
        user_id = int(event.obj.message['from_id'])
        text = event.obj.message['text']
        if user_id not in users_state:
            user_info = get_user(user_id)
            if user_info:
                users_state[user_id] = {
                    'step': 'done',
                    'age': user_info[2],
                    'gender': user_info[3],
                    'city': user_info[4]
                }
                poisk = search_users(users_state[user_id]['age'], users_state[user_id]['gender'],
                                     users_state[user_id]['city'])
                viewed = get_viewed(user_id)
                poisk = [candidate for candidate in poisk if candidate['id'] not in viewed]
                users_state[user_id]['candidates'] = poisk
                users_state[user_id]['candidate_index'] = 0
                if poisk:
                    candidate = poisk[users_state[user_id]['candidate_index']]
                    photos = get_photos(candidate['id'])
                    if photos:
                        vk.messages.send(
                            user_id=user_id,
                            message=f"{candidate['first_name']} {candidate['last_name']}\n\nСсылка на профиль: https://vk.com/id{candidate['id']}\n\nЕсли хотите добавить в избранное, напишите: +\n\nЕсли хотите увидеть следующую анкету, напишите: -\n\nЕсли хотите просмотреть избранное, напишите: *",
                            attachment=','.join(f'photo{candidate["id"]}_{photo_id}' for photo_id in photos),
                            random_id=0
                        )
                    else:
                        vk.messages.send(
                            user_id=user_id,
                            message=f"{candidate['first_name']} {candidate['last_name']}\n\nСсылка на профиль: https://vk.com/id{candidate['id']}\n\nЕсли хотите добавить в избранное, напишите: +\n\nЕсли хотите увидеть следующую анкету, напишите: -\n\nЕсли хотите просмотреть избранное, напишите: *",
                            random_id=0
                        )
                    add_viewed(user_id, candidate['id'])
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message="Анкеты не найдены. Попробуйте позже",
                        random_id=0
                    )
            else:
                users_state[user_id] = {'step': 'age'}
                vk.messages.send(
                    user_id=user_id,
                    message='Введите ваш возраст',
                    random_id=0
                )
        elif users_state[user_id]['step'] == 'age':
            users_state[user_id]['age'] = int(text)
            users_state[user_id]['step'] = 'gender'
            vk.messages.send(
                user_id=user_id,
                message='Введите ваш пол: 1 - женский, 2 - мужской',
                random_id=0
            )
        elif users_state[user_id]['step'] == 'gender':
            users_state[user_id]['gender'] = int(text)
            users_state[user_id]['step'] = 'city'
            vk.messages.send(
                user_id=user_id,
                message='Введите ID вашего города',
                random_id=0
            )
        elif users_state[user_id]['step'] == 'city':
            users_state[user_id]['step'] = 'done'
            users_state[user_id]['city'] = int(text)
            add_user(user_id, users_state[user_id]['age'],
                     users_state[user_id]['gender'],
                     users_state[user_id]['city'])
            vk.messages.send(
                user_id=user_id,
                message='Данные сохранены! Начинается поиск.',
                random_id=0
            )
            poisk = search_users(users_state[user_id]['age'], users_state[user_id]['gender'],
                                 users_state[user_id]['city'])
            viewed = get_viewed(user_id)
            poisk = [candidate for candidate in poisk if candidate['id'] not in viewed]
            users_state[user_id]['candidates'] = poisk
            users_state[user_id]['candidate_index'] = 0
            if poisk:
                candidate = poisk[users_state[user_id]['candidate_index']]
                photos = get_photos(candidate['id'])
                if photos:
                    vk.messages.send(
                        user_id=user_id,
                        message=f"{candidate['first_name']} {candidate['last_name']}\n\nСсылка на профиль: https://vk.com/id{candidate['id']}\n\nЕсли хотите добавить в избранное, напишите: +\n\nЕсли хотите увидеть следующую анкету, напишите: -\n\nЕсли хотите просмотреть избранное, напишите: *",
                        attachment=','.join(f'photo{candidate["id"]}_{photo_id}' for photo_id in photos),
                        random_id=0
                    )
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message=f"{candidate['first_name']} {candidate['last_name']}\n\nСсылка на профиль: https://vk.com/id{candidate['id']}\n\nЕсли хотите добавить в избранное, напишите: +\n\nЕсли хотите увидеть следующую анкету, напишите: -\n\nЕсли хотите просмотреть избранное, напишите: *",
                        random_id=0
                    )
                add_viewed(user_id, candidate['id'])
            else:
                vk.messages.send(
                    user_id=user_id,
                    message="Анкеты не найдены. Попробуйте позже.",
                    random_id=0
                )
        elif text == '-' and users_state[user_id]['step'] == 'done':
            users_state[user_id]['candidate_index'] += 1
            if users_state[user_id]['candidate_index'] < len(users_state[user_id]['candidates']):
                candidate = users_state[user_id]['candidates'][users_state[user_id]['candidate_index']]
                photos = get_photos(candidate['id'])
                if photos:
                    vk.messages.send(
                        user_id=user_id,
                        message=f"{candidate['first_name']} {candidate['last_name']}\n\nСсылка на профиль: https://vk.com/id{candidate['id']}\n\nЕсли хотите добавить в избранное, напишите: +\n\nЕсли хотите увидеть следующую анкету, напишите: -\n\nЕсли хотите просмотреть избранное, напишите: *",
                        attachment=','.join(f'photo{candidate["id"]}_{photo_id}' for photo_id in photos),
                        random_id=0
                    )
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message=f"{candidate['first_name']} {candidate['last_name']}\n\nСсылка на профиль: https://vk.com/id{candidate['id']}\n\nЕсли хотите добавить в избранное, напишите: +\n\nЕсли хотите увидеть следующую анкету, напишите: -\n\nЕсли хотите просмотреть избранное, напишите: *",
                        random_id=0
                    )
                add_viewed(user_id, candidate['id'])
            else:
                vk.messages.send(
                    user_id=user_id,
                    message='Анкеты закончились!\n\nЕсли хотите просмотреть избранное, напишите: *',
                    random_id=0
                )

        elif text == '+' and users_state[user_id]['step'] == 'done':
            if users_state[user_id]['candidate_index'] < len(users_state[user_id]['candidates']):
                candidate = users_state[user_id]['candidates'][
                    users_state[user_id]['candidate_index']
                ]
                add_favorite(user_id, candidate['id'])
                vk.messages.send(
                    user_id=user_id,
                    message='Анкета добавлена в избранное!\n\nЕсли хотите увидеть следующую анкету, напишите: -\n\nЕсли хотите просмотреть избранное, напишите: *',
                    random_id=0
                )
            else:
                vk.messages.send(
                    user_id=user_id,
                    message='Анкеты закончились. Добавить в избранное нечего.',
                    random_id=0
                )
        elif text == "*" and users_state[user_id]['step'] == 'done':
            favorites = get_favorites(user_id)
            if not favorites:
                vk.messages.send(
                    user_id=user_id,
                    message='У вас пока нет избранных анкет\n\nЕсли хотите увидеть следующую анкету, напишите: -\n\n',
                    random_id=0
                )
            else:
                for i in favorites:
                    favorite_user = user_vk.users.get(user_id=i)
                    favorite_user = favorite_user[0]
                    photos = get_photos(favorite_user['id'])
                    if photos:
                        vk.messages.send(
                            user_id=user_id,
                            message=f"{favorite_user['first_name']} {favorite_user['last_name']}\n\nСсылка на профиль: https://vk.com/id{favorite_user['id']}",
                            attachment=','.join(f'photo{favorite_user["id"]}_{photo_id}' for photo_id in photos),
                            random_id=0
                        )
                    else:
                        vk.messages.send(
                            user_id=user_id,
                            message=f"{favorite_user['first_name']} {favorite_user['last_name']}\n\nСсылка на профиль: https://vk.com/id{favorite_user['id']}",
                            random_id=0
                        )
                vk.messages.send(
                    user_id=user_id,
                    message="Чтобы продолжить, напишите: -",
                    random_id=0
                )
