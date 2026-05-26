from django.shortcuts import render
from .models import MoneyGiven

def subordinate_report(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    qs = MoneyGiven.objects.select_related('employee')
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    # Собираем данные по сотрудникам
    report_dict = {}
    for item in qs:
        name = item.employee.name
        if name not in report_dict:
            report_dict[name] = {
                'total': 0,
                'details': []
            }
        report_dict[name]['total'] += item.amount
        report_dict[name]['details'].append({
            'date': item.date,
            'amount': item.amount,
            'purpose': item.purpose,
        })

    # Превращаем в список для шаблона
    report_list = []
    for name, data in report_dict.items():
        report_list.append({
            'name': name,
            'total': data['total'],
            'details': data['details'],
        })
    report_list.sort(key=lambda x: x['total'], reverse=True)

    grand_total = sum(item['total'] for item in report_list)

    return render(request, 'accounting/report.html', {
        'report_list': report_list,
        'grand_total': grand_total,
        'date_from': date_from,
        'date_to': date_to,
    })