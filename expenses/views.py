from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from userpreferences.models import UserPreference
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
import json
import csv
import xlwt
import datetime
from django.conf import settings
from pathlib import Path
from decimal import Decimal

from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Sum

def search_expenses(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchText")
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)  # Show 5 expenses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency = UserPreference.objects.get(user = request.user).currency
    context = {
        "expenses": expenses,
        "page_obj": page_obj,
        "currency": currency
    }
    return render(request, "expenses/index.html", context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        "categories": categories,
        "values": request.POST
    }
    
    if request.method == "GET":
        return render(request, "expenses/add_expense.html", context)

    if request.method == "POST":
        amount = request.POST.get("amount")
        description = request.POST.get("description")
        category = request.POST.get("category")
        expense_date = request.POST.get("expense_date")

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "expenses/add_expense.html", context)
        if not description:
            messages.error(request, "Description is required")
            return render(request, "expenses/add_expense.html", context)
        if not category:
            messages.error(request, "Category is required")
            return render(request, "expenses/add_expense.html", context)
        if not expense_date:    
            messages.error(request, "Date is required")
            return render(request, "expenses/add_expense.html", context)    

        Expense.objects.create(
            amount=amount,
            description=description,
            category=category,
            date=expense_date,
            owner=request.user
        )
        messages.success(request, "Expense added successfully")

        return redirect("expenses")


@login_required(login_url='/authentication/login')
def edit_expense(request, id):
    expense = Expense.objects.get(id=id)
    categories = Category.objects.all()
    context = {
        "expense": expense,
        "values": expense,
        "categories": categories
    }
    
    if request.method == "GET":
        return render(request, "expenses/edit_expense.html", context)
    if request.method == "POST":
        amount = request.POST.get("amount")
        description = request.POST.get("description")
        category = request.POST.get("category")
        expense_date = request.POST.get("expense_date")

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "expenses/edit_expense.html", context)
        if not description:
            messages.error(request, "Description is required")
            return render(request, "expenses/edit_expense.html", context)
        if not category:
            messages.error(request, "Category is required")
            return render(request, "expenses/edit_expense.html", context)
        if not expense_date:
            messages.error(request, "Date is required")
            return render(request, "expenses/edit_expense.html", context)

        expense.amount = amount
        expense.description = description
        expense.category = category
        expense.date = expense_date
        expense.save()

        messages.success(request, "Expense updated successfully")

        return redirect("expenses")


@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(id=id)
    expense.delete()
    messages.success(request, "Expense deleted successfully")
    return redirect("expenses")


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="expenses_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Amount", "Description", "Category", "Date"])

    expenses = Expense.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response


def export_excel(request):
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        f'attachment; filename="expenses_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xls"'
    )

    work_book = xlwt.Workbook(encoding="utf-8")
    work_book_sheet = work_book.add_sheet('Expenses')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ["Amount", "Description", "Category", "Date"]
    for col_num in range(len(columns)):
        work_book_sheet.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list("amount", "description", "category", "date")
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            work_book_sheet.write(row_num, col_num, str(row[col_num]), font_style)

    work_book.save(response)

    return response


def export_pdf(request):
    expenses = Expense.objects.filter(owner=request.user)
    sum = expenses.aggregate(Sum("amount"))

    html_string = render_to_string("expenses/pdf-output.html", {"expenses": expenses, "total": sum["amount__sum"]})

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; attachment; filename="expenses_'
        f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf"'
    )

    return response


@login_required(login_url='/authentication/login')
def stats_view(request):
    return render(request, "expenses/stats.html")    


def get_currency_symbol(currency_str):
    """
    Витягує короткий символ або код валюти з рядка типу "UAH - Ukrainian Hryvnia"
    """
    if not currency_str:
        return '₴'
    
    if len(currency_str) <= 3:
        return currency_str.upper()
    
    if ' - ' in currency_str:
        code = currency_str.split(' - ')[0].strip().upper()
        return code
    
    return currency_str.upper() 


@login_required(login_url='/authentication/login')
def expense_category_summary(request):
    today = datetime.date.today()
    period = request.GET.get('period', '6m')
    from_date_str = request.GET.get('from')
    to_date_str = request.GET.get('to')

    # Визначаємо дати початку та кінця періоду
    if period == '30d':
        start_date = today - datetime.timedelta(days=30)
        end_date = today
    elif period == '3m':
        start_date = today - datetime.timedelta(days=90)
        end_date = today
    elif period == '6m':
        start_date = today - datetime.timedelta(days=180)
        end_date = today
    elif period == '12m':
        start_date = today - datetime.timedelta(days=365)
        end_date = today
    elif period == 'all':
        start_date = None
        end_date = today
    elif period == 'custom' and from_date_str and to_date_str:
        try:
            start_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today - datetime.timedelta(days=180)
            end_date = today
    else:
        start_date = today - datetime.timedelta(days=180)
        end_date = today

    # Запит витрат
    expenses = Expense.objects.filter(owner=request.user)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    expenses = expenses.filter(date__lte=end_date)

    # Підрахунок по категоріях (все в Decimal)
    final_rep = {}
    category_list = expenses.values_list('category', flat=True).distinct()

    for category in category_list:
        amount = expenses.filter(category=category).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        final_rep[category] = amount   # залишаємо Decimal

    # Ключові метрики
    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    transaction_count = expenses.count()

    # Кількість днів у періоді
    if start_date:
        days_in_period = (end_date - start_date).days + 1
    else:
        oldest = expenses.order_by('date').first()
        days_in_period = (today - oldest.date).days + 1 if oldest else 1

    days_in_period = Decimal(days_in_period)  # для точних обчислень

    avg_per_day = total / days_in_period if days_in_period > 0 else Decimal('0')
    avg_per_month = total / Decimal('30.4375') if days_in_period > 0 else Decimal('0')

    # Найбільша категорія та відсоток
    if final_rep:
        top_source = max(final_rep.items(), key=lambda x: x[1])
        top_source_name = top_source[0]
        top_source_amount = top_source[1]
        top_percent = float((top_source_amount / total) * 100) if total > 0 else 0.0
    else:
        top_source_name = "—"
        top_percent = 0.0
    
    # Отримуємо валюту користувача
    try:
        user_pref = UserPreference.objects.get(user=request.user)
        raw_currency = user_pref.currency or 'UAH - Ukrainian Hryvnia'
        currency = get_currency_symbol(raw_currency)
    except UserPreference.DoesNotExist:
        currency = '₴'

    stats = {
        "total": round(float(total), 2),
        "transaction_count": transaction_count,
        "avg_per_day": round(float(avg_per_day), 2),
        "avg_per_month": round(float(avg_per_month), 2),
        "top_category": top_source_name,
        "top_percent": round(top_percent, 1),
    }

    return JsonResponse({
        "expenses_source_data": {k: float(v) for k, v in final_rep.items()}, 
        "stats": stats,
        "currency": currency,
        "period": {
            "start": str(start_date) if start_date else None,
            "end": str(end_date)
        }
    }, safe=False)





