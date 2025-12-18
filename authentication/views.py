from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from validate_email import validate_email
import json
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import auth

from .utils import token_generator


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({"email_error": "Email is invalid"}, status=400)
        
        if User.objects.filter(email = email).exists():
            return JsonResponse({"email_error": "Sorry, this email already in use, choose another one"}, status=409)
        
        return JsonResponse({"email_valid": True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({"username_error": "Username should only contain alphanumeric characters"}, status=400)
        
        if User.objects.filter(username = username).exists():
            return JsonResponse({"username_error": "Sorry, this username already in use, choose another one"}, status=409)
        
        return JsonResponse({"username_valid": True})


class RegistrationView(View):
    def get(self, request):
        return render(request, "authentication/register.html")
    
    def post(self, request):
        username = request.POST.get("username")
        user_email = request.POST.get("email")
        password = request.POST.get("password")

        context = {
            "fieldValues": request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=user_email).exists():

                if len(password) < 6:
                    messages.error(request, "Password is too short")
                    return render(request, "authentication/register.html", context)
                
                user = User.objects.create_user(username=username, email=user_email)
                user.set_password(password)
                user.is_active = False
                user.save()

                # Кодуємо id користувача (pk) у формат base64, щоб безпечно передавати його в URL
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                # Отримуємо домен поточного сайту (наприклад: example.com або localhost:8000)
                domain = get_current_site(request).domain
                # Генеруємо відносний URL для активації акаунта
                link = reverse('activate', kwargs={"uidb64": uidb64, "token": token_generator.make_token(user)})
                # Формуємо повне посилання для активації акаунта. Наприклад: http://example.com/activate/Ng/token123/
                activate_url = 'http://'+domain+link
                
                email_subject = 'Activate your account'
                email_body = 'Hi ' + user.username + '! Please use this link to verify your account\n' + activate_url

                email_message = EmailMessage(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    to=[user_email],
                )
                email_message.send(fail_silently=False)
                messages.success(request, "Account was succesfully created")
                return render(request, "authentication/register.html")
        return render(request, "authentication/register.html")


class VerificationView(View):
    """
    View для активації акаунта користувача через email.
    Користувач переходить за посиланням виду:
    /activate/<uidb64>/<token>/
    """
    def get(self, request, uidb64, token):
        """
        Обробляє GET-запит при переході за посиланням з email
        """
        try:
            # Розкодовуємо uid з base64 у звичайний рядок (id користувача) та отримуємо користувача з бд
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            # Перевіряємо, чи токен дійсний для цього користувача
            # Якщо токен НЕ валідний - значить акаунт вже активований або посилання прострочене
            if not token_generator.check_token(user, token):
                return redirect("login"+"?message="+"User already activated")

            # Додаткова перевірка: якщо користувач вже активний - просто редіректимо на логін
            if user.is_active:
                return redirect("login")
            
            # Активуємо акаунт
            user.is_active = True
            user.save()

            # Повідомлення про успішну активацію та перенаправляємо на сторінку логіну
            messages.success(request, "Account was activated successfully")
            return redirect("login")

        except Exception as ex:
            # Якщо виникла будь-яка помилка:
            # - неправильний uid
            # - користувача не існує
            # - помилка декодування
            # просто перенаправляємо на сторінку логіну
            pass
        
        # Резервний редірект у разі помилки
        return redirect("login")
    

class LoginView(View):
    def get(self, request):
        return render(request, "authentication/login.html")
    
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username and password:
            user = auth.authenticate(username = username, password = password)

            if user:
                if user.is_active:
                    auth.login(request=request, user=user)
                    messages.success(request, "Welcome, "+user.username+" you are now logged in")
                    return redirect("expenses")
                
                messages.error(request, "Account is not active, please check your email")
                return render(request, "authentication/login.html")
            
            messages.error(request, "Invalid username or password")
            return render(request, "authentication/login.html")
        messages.error(request, "Please fill all fields")
        return render(request, "authentication/login.html")


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, "You have been logged out")
        return redirect("login")