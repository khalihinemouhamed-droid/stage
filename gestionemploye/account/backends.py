from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password


class LegacyPasswordBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        user_model = get_user_model()
        try:
            user = user_model._default_manager.get_by_natural_key(username)
        except user_model.DoesNotExist:
            return None

        if not getattr(user, "is_active", True):
            return None

        if user.password and user.password.startswith("pbkdf2_sha256$"):
            return super().authenticate(request, username=username, password=password, **kwargs)

        if user.password == password:
            user.set_password(password)
            user.save(update_fields=["password"])
            return user

        if check_password(password, user.password):
            return user

        return None
