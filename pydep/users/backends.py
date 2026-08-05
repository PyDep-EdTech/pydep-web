from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class CaseInsensitiveModelBackend(ModelBackend):
    """
    Аутентификация по логину без учёта регистра: admin и Admin —
    один и тот же пользователь. Регистр в БД при этом сохраняется как есть.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        try:
            user = User._default_manager.get(
                **{User.USERNAME_FIELD + '__iexact': username}
            )
        except User.DoesNotExist:
            # Прогон set_password, чтобы время ответа не выдавало отсутствие юзера.
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # В БД уже есть варианты в разном регистре — берём точное совпадение.
            user = User._default_manager.filter(
                **{User.USERNAME_FIELD: username}
            ).order_by('id').first()
            if user is None:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
