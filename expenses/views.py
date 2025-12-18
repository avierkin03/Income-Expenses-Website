from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from django.contrib import messages
from django.core.paginator import Paginator

@login_required(login_url='/authentication/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 1)  # Show 5 expenses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "expenses": expenses,
        "page_obj": page_obj
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