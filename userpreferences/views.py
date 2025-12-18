from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from .models import UserPreference
from django.contrib.auth.decorators import login_required
import os
import json


@login_required(login_url='/authentication/login')
def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open (file_path, 'r') as json_file:
        data = json.load(json_file)
        for key, value in data.items():
            currency_data.append({'name': key, 'value': value})

    user_preferences_exists = UserPreference.objects.filter(user = request.user).exists()
    user_preferences = None

    if user_preferences_exists:
        user_preferences = UserPreference.objects.get(user = request.user)

    if request.method == "GET":
        return render(request, "preferences/index.html", {"currencies": currency_data, "user_preferences": user_preferences})
    else:
        currency = request.POST.get("currency")
        
        if user_preferences_exists:
            user_preferences.currency = currency
            user_preferences.save()
        else:   
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, "Changes saved")

        return render(request, "preferences/index.html", {"currencies": currency_data, "user_preferences": user_preferences})
