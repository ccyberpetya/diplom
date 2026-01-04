# backend/social_auth_pipeline.py
def set_user_type(backend, user, response, *args, **kwargs):
    """
    Устанавливаем тип пользователя при социальной авторизации
    """
    if backend.name in ['vk-oauth2', 'github']:
        # Сохраняем информацию о социальной сети
        user.social_id = response.get('id')
        user.social_provider = backend.name

        # По умолчанию создаем покупателя
        if not user.type:
            user.type = 'buyer'

        # Заполняем данные из социальной сети если их нет
        if not user.first_name and response.get('first_name'):
            user.first_name = response.get('first_name')
        if not user.last_name and response.get('last_name'):
            user.last_name = response.get('last_name')
        if not user.email and response.get('email'):
            user.email = response.get('email')

        # Автоматически активируем пользователя при социальной авторизации
        user.is_active = True

        user.save()

    return {'user': user}


def save_avatar(backend, user, response, *args, **kwargs):
    """
    Сохраняем аватар из социальной сети
    """
    if backend.name == 'vk-oauth2' and response.get('photo_200'):
        # Для VK: photo_200 - URL аватара 200x200px
        import requests
        from io import BytesIO
        from django.core.files import File

        try:
            photo_url = response.get('photo_200')
            if photo_url:
                response_img = requests.get(photo_url)
                if response_img.status_code == 200:
                    img_name = f"vk_avatar_{user.social_id}.jpg"
                    user.avatar.save(img_name, File(BytesIO(response_img.content)), save=True)
        except Exception as e:
            print(f"Ошибка загрузки аватара: {e}")

    elif backend.name == 'github' and response.get('avatar_url'):
        # Для GitHub
        import requests
        from io import BytesIO
        from django.core.files import File

        try:
            photo_url = response.get('avatar_url')
            if photo_url:
                response_img = requests.get(photo_url)
                if response_img.status_code == 200:
                    img_name = f"github_avatar_{user.social_id}.jpg"
                    user.avatar.save(img_name, File(BytesIO(response_img.content)), save=True)
        except Exception as e:
            print(f"Ошибка загрузки аватара: {e}")