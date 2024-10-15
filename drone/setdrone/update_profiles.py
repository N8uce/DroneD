from django.contrib.auth.models import User
from setdrone.models import Profile

def update_profiles():
    for user in User.objects.all():
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
            print(f'Профиль создан для пользователя: {user.username}')

update_profiles()
