from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from userpreferences.models import UserPreference
from .models import Source, Income
import json


@login_required(login_url='/authentication/login')
def index(request):
    incomes = Income.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 5)  # Show 5 expenses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency = UserPreference.objects.get(user = request.user).currency
    context = {
        "incomes": incomes,
        "page_obj": page_obj,
        "currency": currency
    }
    return render(request, "incomes/index.html", context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        "sources": sources,
        "values": request.POST
    }
    
    if request.method == "GET":
        return render(request, "incomes/add_income.html", context)

    if request.method == "POST":
        amount = request.POST.get("amount")
        description = request.POST.get("description")
        source = request.POST.get("source")
        income_date = request.POST.get("income_date")

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "incomes/add_income.html", context)
        if not description:
            messages.error(request, "Description is required")
            return render(request, "incomes/add_income.html", context)
        if not source:
            messages.error(request, "Source is required")
            return render(request, "incomes/add_income.html", context)
        if not income_date:    
            messages.error(request, "Date is required")
            return render(request, "incomes/add_income.html", context)    

        Income.objects.create(
            amount=amount,
            description=description,
            source=source,
            date=income_date,
            owner=request.user
        )
        messages.success(request, "Income added successfully")

        return redirect("incomes")
    

@login_required(login_url='/authentication/login')
def edit_income(request, id):
    income = Income.objects.get(id=id)
    sources = Source.objects.all()
    context = {
        "income": income,
        "values": income,
        "sources": sources
    }
    
    if request.method == "GET":
        return render(request, "incomes/edit_income.html", context)
    if request.method == "POST":
        amount = request.POST.get("amount")
        description = request.POST.get("description")
        source = request.POST.get("source")
        income_date = request.POST.get("income_date")

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "incomes/edit_income.html", context)
        if not description:
            messages.error(request, "Description is required")
            return render(request, "incomes/edit_income.html", context)
        if not source:
            messages.error(request, "Source is required")
            return render(request, "incomes/edit_income.html", context)
        if not income_date:
            messages.error(request, "Date is required")
            return render(request, "incomes/edit_income.html", context)

        income.amount = amount
        income.description = description
        income.source = source
        income.date = income_date
        income.save()

        messages.success(request, "Income updated successfully")

        return redirect("incomes")


@login_required(login_url='/authentication/login')
def delete_income(request, id):
    income = Income.objects.get(id=id)
    income.delete()
    messages.success(request, "Income deleted successfully")
    return redirect("incomes")


def search_income(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchText")
        incomes = Income.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Income.objects.filter(
            date__istartswith=search_str, owner=request.user) | Income.objects.filter(
            description__icontains=search_str, owner=request.user) | Income.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = incomes.values()
        return JsonResponse(list(data), safe=False)