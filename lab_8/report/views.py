from django.shortcuts import render
from .models import SalaryAccrual


def salary_report(request):
    # Получаем все начисления
    accruals = SalaryAccrual.objects.select_related('employee').all()

    # Общая сумма
    total_sum = sum(a.amount for a in accruals)

    # Пороги и кратность (по заданию)
    LOW_THRESHOLD = 8000  # нижний порог
    HIGH_THRESHOLD = 12000  # верхний порог
    MULTIPLE_OF = 100  # кратность

    # Присваиваем класс для подсветки
    for accrual in accruals:
        amount = accrual.amount

        if amount > HIGH_THRESHOLD:
            accrual.color_class = 'high'  # выше верхнего порога → красный
        elif amount < LOW_THRESHOLD:
            accrual.color_class = 'low'  # ниже нижнего порога → зеленый
        elif int(amount) % MULTIPLE_OF == 0:
            accrual.color_class = 'multiple'  # кратно 100 → синий
        else:
            accrual.color_class = 'normal'  # между порогами → белый

    return render(request, 'report/salary_report.html', {
        'accruals': accruals,
        'total_sum': total_sum,
    })