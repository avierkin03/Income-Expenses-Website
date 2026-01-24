from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from userpreferences.models import UserPreference
from .models import Source, Income
import json
import csv
import xlwt
import datetime
from decimal import Decimal

from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Sum


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
    

def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="income_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Amount", "Description", "Source", "Date"])

    incomes = Income.objects.filter(owner=request.user)
    for income in incomes:
        writer.writerow([income.amount, income.description, income.source, income.date])

    return response


def export_excel(request):
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        f'attachment; filename="income_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xls"'
    )

    work_book = xlwt.Workbook(encoding="utf-8")
    work_book_sheet = work_book.add_sheet('Income')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ["Amount", "Description", "Source", "Date"]
    for col_num in range(len(columns)):
        work_book_sheet.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Income.objects.filter(owner=request.user).values_list("amount", "description", "source", "date")
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            work_book_sheet.write(row_num, col_num, str(row[col_num]), font_style)

    work_book.save(response)

    return response


def export_pdf(request):
    income = Income.objects.filter(owner=request.user)
    sum = income.aggregate(Sum("amount"))

    html_string = render_to_string("incomes/pdf-output.html", {"incomes": income, "total": sum["amount__sum"]})

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; attachment; filename="income_'
        f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf"'
    )

    return response


@login_required(login_url='/authentication/login')
def stats_view(request):
    return render(request, "incomes/stats.html") 


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
def income_category_summary(request):
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
    incomes = Income.objects.filter(owner=request.user)
    if start_date:
        incomes = incomes.filter(date__gte=start_date)
    incomes = incomes.filter(date__lte=end_date)

    # Підрахунок по категоріях (все в Decimal)
    final_rep = {}
    source_list = incomes.values_list('source', flat=True).distinct()

    for source in source_list:
        amount = incomes.filter(source=source).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        final_rep[source] = amount   # залишаємо Decimal

    # Ключові метрики
    total = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    transaction_count = incomes.count()

    # Кількість днів у періоді
    if start_date:
        days_in_period = (end_date - start_date).days + 1
    else:
        oldest = incomes.order_by('date').first()
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
        "top_source": top_source_name,
        "top_percent": round(top_percent, 1),
    }

    return JsonResponse({
        "income_source_data": {k: float(v) for k, v in final_rep.items()},  # для фронтенду — float
        "stats": stats,
        "currency": currency,
        "period": {
            "start": str(start_date) if start_date else None,
            "end": str(end_date)
        }
    }, safe=False)