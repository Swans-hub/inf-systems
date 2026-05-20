from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Employee
from .forms import EmployeeForm


def is_director(user):
    return user.groups.filter(name='Директор').exists()


def is_deputy(user):
    return user.groups.filter(name='Заместитель директора').exists()


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('employee_list')
        messages.error(request, 'Неверные данные')
    return render(request, 'employees/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def employee_list(request):
    user = request.user
    employees = Employee.objects.all()

    # Для гостя показываем не все поля
    is_guest = user.groups.filter(name='Гость').exists()

    can_add = is_director(user)
    can_edit = is_director(user) or is_deputy(user)
    can_delete = is_director(user)

    context = {
        'employees': employees,
        'is_guest': is_guest,
        'can_add': can_add,
        'can_edit': can_edit,
        'can_delete': can_delete,
        'user_group': user.groups.first().name if user.groups.exists() else 'Гость'
    }
    return render(request, 'employees/list.html', context)


@login_required
@user_passes_test(is_director)
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сотрудник добавлен')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/form.html', {'form': form, 'title': 'Добавление'})


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['Директор', 'Заместитель директора']).exists())
def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=emp)
    return render(request, 'employees/form.html', {'form': form, 'title': 'Редактирование'})


@login_required
@user_passes_test(is_director)
def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    emp.delete()
    messages.success(request, 'Сотрудник удалён')
    return redirect('employee_list')