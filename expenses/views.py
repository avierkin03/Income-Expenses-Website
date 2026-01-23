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


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    final_rep = {}

    def get_category(expense):
        return expense.category
    
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category = category)

        for item in filtered_by_category:
            amount += item.amount

        return amount

    for x in expenses:
        for category in category_list:
            final_rep[category] = get_expense_category_amount(category)

    return JsonResponse({"expense_category_data": final_rep}, safe=False)


def stats_view(request):
    return render(request, "expenses/stats.html")    


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
    logo_path = Path(settings.STATICFILES_DIRS[0]) / "img/company_logo.png"

    html_string = render_to_string("expenses/pdf-output.html", {"expenses": expenses, "total": sum["amount__sum"], "logo_path": logo_path})

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; attachment; filename="expenses_'
        f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf"'
    )

    return response
