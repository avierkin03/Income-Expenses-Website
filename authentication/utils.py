from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type 

# генератор токенів
class AppTokenGenerator(PasswordResetTokenGenerator):
    # перевизначаємо ключовий метод, який Django викликає під час генерації токена
    # повертаємо рядок, з якого буде згенерований hash
    #       - user.is_active	Якщо користувач активувався → токен стане невалідним
    #       - user.pk	        Прив’язка токена до конкретного користувача
    #       - timestamp	        Обмежує час життя токена
    # Результат: якщо хоч один параметр зміниться — старий токен більше не працює.
    def _make_hash_value(self, user, timestamp):
        return (text_type(user.is_active)+text_type(user.pk)+text_type(timestamp))
    
# екземпляр генератора
token_generator = AppTokenGenerator()