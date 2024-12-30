# backends.py
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class CustomUserAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to authenticate using either email or username
            if '@' in username:
                user = CustomUser.objects.get(email=username)
            else:
                user = CustomUser.objects.get(username=username)

            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except CustomUser.DoesNotExist:
            return None

# backends.py
# from django.contrib.auth.backends import ModelBackend
# from .models import CustomUser
# from django.core.exceptions import ValidationError

# class CustomUserAuthenticationBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             # Try to authenticate using either email or username
#             if '@' in username:
#                 user = CustomUser.objects.get(email=username)
#             else:
#                 user = CustomUser.objects.get(username=username)

#             # Check password and authentication
#             if user.check_password(password) and self.user_can_authenticate(user):
#                 return user
#             else:
#                 raise ValidationError("Invalid password.")

#         except CustomUser.DoesNotExist:
#             raise ValidationError("User not found.")
#         except ValidationError as e:
#             # Raise validation errors with custom messages
#             raise e

