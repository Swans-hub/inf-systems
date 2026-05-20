import json
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DataPoint


def index(request):
    """Главная страница АРМ"""
    latest_data = DataPoint.objects.all()[:5]
    values = [dp.value for dp in latest_data]
    timestamps = [dp.timestamp.strftime('%H:%M:%S') for dp in latest_data]

    context = {
        'current_value': values[0] if values else 0,
        'previous_values': values[1:] if len(values) > 1 else [],
        'timestamps': timestamps,
        'n1': 5,
        'n2': 20,
    }
    return render(request, 'monitoring/index.html', context)


@csrf_exempt
def add_data(request):
    """Добавление новой точки данных"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            value = float(data.get('value', 0))

            new_point = DataPoint.objects.create(value=value)

            previous = DataPoint.objects.filter(id__lt=new_point.id).first()

            warning = False
            if previous and previous.value != 0:
                change_percent = abs((value - previous.value) / previous.value * 100)
                warning = change_percent > 20

            all_data = DataPoint.objects.all()[:10]
            values = [dp.value for dp in all_data]
            timestamps = [dp.timestamp.strftime('%H:%M:%S') for dp in all_data]

            return JsonResponse({
                'status': 'success',
                'current_value': value,
                'all_values': values,
                'timestamps': timestamps,
                'warning': warning
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@csrf_exempt
def generate_plots(request):
    """Генерация графиков"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            values = data.get('values', [])
            selection_type = data.get('selection_type', 'all')
            threshold = data.get('threshold', 0)
            multiple = data.get('multiple', 1)

            # Фильтрация данных
            if selection_type == 'greater':
                filtered_values = [v for v in values if v > threshold]
            elif selection_type == 'less':
                filtered_values = [v for v in values if v < threshold]
            elif selection_type == 'multiple':
                filtered_values = [v for v in values if v % multiple == 0]
            else:
                filtered_values = values

            # Создаем линейный график
            plt.figure(figsize=(10, 5))
            x = range(len(values))
            plt.plot(x, values, 'b-', label='Все значения', linewidth=2)

            # Отмечаем выбранные значения
            filtered_indices = [i for i, v in enumerate(values) if v in filtered_values]
            filtered_vals = [values[i] for i in filtered_indices]
            plt.scatter(filtered_indices, filtered_vals, color='green', s=50, label='Выбранные значения')

            # Среднее значение
            avg = np.mean(filtered_values) if filtered_values else 0
            plt.axhline(y=avg, color='red', linestyle='--', linewidth=2, label=f'Среднее: {avg:.2f}')

            plt.xlabel('Номер измерения')
            plt.ylabel('Значение')
            plt.title('График значений параметра')
            plt.legend()
            plt.grid(True, alpha=0.3)

            # Сохраняем график в base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            plot_url = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            # Создаем гистограмму
            plt.figure(figsize=(10, 5))
            if filtered_values:
                plt.bar(range(len(filtered_values)), filtered_values, color='skyblue')
                plt.axhline(y=avg, color='red', linestyle='--', linewidth=2, label=f'Среднее: {avg:.2f}')
            else:
                plt.text(0.5, 0.5, 'Нет данных для отображения', ha='center', va='center',
                         transform=plt.gca().transAxes)

            plt.xlabel('Номер записи')
            plt.ylabel('Значение')
            plt.title('Диаграмма выборочных значений')
            plt.legend()
            plt.grid(True, alpha=0.3)

            buffer2 = BytesIO()
            plt.savefig(buffer2, format='png', dpi=100)
            buffer2.seek(0)
            chart_url = base64.b64encode(buffer2.getvalue()).decode()
            plt.close()

            return JsonResponse({
                'status': 'success',
                'plot_url': plot_url,
                'chart_url': chart_url,
                'average': avg,
                'filtered_values': filtered_values
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
