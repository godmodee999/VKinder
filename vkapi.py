import os
from dotenv import load_dotenv
import vk_api

load_dotenv()


group_token = os.getenv("GROUP_TOKEN")
vk_session = vk_api.VkApi(token=group_token)
vk = vk_session.get_api()
user_token = os.getenv("USER_TOKEN")
user_session = vk_api.VkApi(token=user_token)
user_vk = user_session.get_api()


def search_users(age, gender, city, offset=0):
    result = user_vk.users.search(
        age_from=age,
        age_to=age,
        sex=1 if gender == 2 else 2,
        city=city,
        has_photo=1,
        count=100,
        fields="city, bdate",
        offset=offset,
    )

    candidates = []

    for user in result["items"]:
        if user["is_closed"] is False:
            candidates.append(
                {
                    "id": user["id"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                }
            )

    return candidates


def get_photos(user_id):
    result = []
    likes_list = []
    photos = user_vk.photos.get(
        owner_id=user_id, count=20, album_id="profile", extended=1
    )
    for a in photos["items"]:
        likes_list.append((a["likes"]["count"], a["id"]))
    sort = sorted(likes_list, key=lambda x: x[0], reverse=True)[:3]
    for i in sort:
        result.append(i[1])
    return result
