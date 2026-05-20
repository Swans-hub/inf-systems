from django.shortcuts import render
from django.http import JsonResponse
from .models import Client, Product, Order, OrderItem
from django.db import transaction
from decimal import Decimal
import json
from django.views.decorators.csrf import csrf_exempt
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from collections import defaultdict


def index(request):
    clients = Client.objects.all()
    products = Product.objects.all()
    return render(request, 'main/index.html', {
        'clients': clients,
        'products': products
    })


def search_clients(request):
    query = request.GET.get('q', '')
    clients = Client.objects.filter(name__icontains=query).values('id', 'name')[:10]
    return JsonResponse(list(clients), safe=False)


def get_client(request, client_id):
    client = Client.objects.get(id=client_id)
    data = {
        'id': client.id,
        'name': client.name,
        'total_purchases': float(client.total_purchases),
        'current_account': float(client.current_account),
        'credit_limit': float(client.credit_limit),
        'current_debt': float(client.current_debt),
        'credit_remaining': float(client.credit_remaining),
        'comment': client.comment,
    }
    return JsonResponse(data)


def get_products(request):
    products = Product.objects.all().values('id', 'name', 'price', 'quantity')
    return JsonResponse(list(products), safe=False)


def check_products_warning(request):
    """Проверка товаров на незаполненные поля"""
    empty_names = Product.objects.filter(name__isnull=True) | Product.objects.filter(name='')
    zero_price = Product.objects.filter(price=0)
    zero_quantity = Product.objects.filter(quantity=0)

    warnings = []

    if empty_names.exists():
        warnings.append(f"❌ {empty_names.count()} товаров с пустым названием")

    if zero_price.exists():
        products = zero_price.values_list('name', flat=True)
        warnings.append(
            f"⚠️ {zero_price.count()} товаров с нулевой ценой: {', '.join(products[:3])}{'...' if zero_price.count() > 3 else ''}")

    if zero_quantity.exists():
        products = zero_quantity.values_list('name', flat=True)
        warnings.append(
            f"📦 {zero_quantity.count()} товаров с нулевым остатком: {', '.join(products[:3])}{'...' if zero_quantity.count() > 3 else ''}")

    return JsonResponse({
        'has_warnings': len(warnings) > 0,
        'warnings': warnings,
        'count': {
            'empty_names': empty_names.count(),
            'zero_price': zero_price.count(),
            'zero_quantity': zero_quantity.count()
        }
    })


@csrf_exempt
def complete_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            payment_type = data.get('payment_type')
            items = data.get('items', [])
            total = Decimal(str(data.get('total', 0)))
            confirmed = data.get('confirmed', False)
            barter_exchange = data.get('barter_exchange', [])  # для бартера: список товаров которые отдаем и получаем

            # Получаем клиента
            client = Client.objects.get(id=client_id)

            # Проверка для кредита
            if payment_type == 'credit':
                available = client.credit_remaining + client.current_account
                if total > available:
                    return JsonResponse({
                        'success': False,
                        'error': f'❌ Превышен кредитный лимит!\n\nСумма заказа: {total} ₽\nДоступно: {available} ₽\n'
                                 f'Текущий долг: {client.current_debt} ₽\nПотолок кредита: {client.credit_limit} ₽'
                    })

                # Предупреждение если используем >80% доступного
                if not confirmed and total > available * 0.8:
                    return JsonResponse({
                        'success': False,
                        'warning': True,
                        'message': f'⚠️ Внимание! Вы используете {total / available * 100:.1f}% доступного кредита.\n\n'
                                   f'Продолжить?'
                    })

            # Создаём заказ в транзакции
            with transaction.atomic():
                order = Order.objects.create(
                    client=client,
                    payment_type=payment_type,
                    total_amount=total
                )

                # Для бартера нужно отдельно обработать обмен
                if payment_type == 'barter':
                    # Группируем товары: что отдаем (-), что получаем (+)
                    stock_changes = defaultdict(int)
                    total_in = Decimal('0')
                    total_out = Decimal('0')

                    for item in items:
                        product = Product.objects.get(id=item['product_id'])
                        quantity = item['quantity']

                        # Проверяем остаток для отдаваемых товаров (quantity < 0)
                        if quantity < 0 and abs(quantity) > product.quantity:
                            raise Exception(f'Недостаточно товара для бартера: {product.name}')

                        # Создаём позицию заказа (для истории)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=item['price'],
                            sum=abs(Decimal(str(item['price'])) * Decimal(str(abs(quantity))))
                        )

                        # Запоминаем изменения на складе
                        stock_changes[product.id] = quantity

                        if quantity > 0:
                            total_in += Decimal(str(item['price'])) * Decimal(str(quantity))
                        else:
                            total_out += Decimal(str(item['price'])) * Decimal(str(abs(quantity)))

                    # Проверяем равенство сумм (погрешность 1 рубль)
                    if abs(total_in - total_out) > Decimal('1'):
                        raise Exception(f'Стоимость товаров при бартере должна быть равна!\n'
                                        f'Получаем: {total_in} ₽\nОтдаем: {total_out} ₽\n'
                                        f'Разница: {abs(total_in - total_out)} ₽')

                    # Применяем изменения на складе
                    for product_id, change in stock_changes.items():
                        product = Product.objects.get(id=product_id)
                        product.quantity += change  # change может быть + или -
                        product.save()

                else:
                    # Обычная обработка для остальных типов оплаты
                    for item in items:
                        product = Product.objects.get(id=item['product_id'])

                        # Проверка остатка
                        if item['quantity'] > product.quantity:
                            raise Exception(f'Недостаточно товара: {product.name}')

                        # Создаём позицию заказа
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item['quantity'],
                            price=item['price'],
                            sum=item['sum']
                        )

                        # Уменьшаем остаток (кроме взаимозачета - там товары приходят)
                        if payment_type != 'mutual':
                            product.quantity -= item['quantity']
                            product.save()
                        else:
                            # При взаимозачете товары возвращаются на склад
                            product.quantity += item['quantity']
                            product.save()

                # Обновляем счета клиента в зависимости от типа оплаты
                if payment_type == 'cash':
                    client.total_purchases += total

                elif payment_type == 'cashless':
                    client.total_purchases += total
                    client.current_account -= total

                elif payment_type == 'credit':
                    client.total_purchases += total

                    # Сначала используем текущий счёт
                    if client.current_account > 0:
                        from_account = min(client.current_account, total)
                        client.current_account -= from_account
                        client.current_debt += (total - from_account)
                    else:
                        client.current_debt += total

                elif payment_type == 'mutual':
                    # Взаимозачет: уменьшаем долг, товары приходят на склад
                    if client.current_debt > 0:
                        client.current_debt -= min(client.current_debt, total)

                # Для бартера счета не меняются
                # Для взаимозачета общий счет покупок не увеличивается

                client.save()

            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'message': f'Заказ №{order.id} оформлен!'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def order_report(request):
    # Получаем все заказы с клиентами и товарами
    orders = Order.objects.all().prefetch_related('items__product', 'client')

    report_data = []
    client_totals = {}

    for order in orders:
        for item in order.items.all():
            report_data.append({
                'order_id': order.id,
                'date': order.created_at.strftime('%d.%m.%Y %H:%M'),
                'client': order.client.name,
                'product': item.product.name,
                'quantity': item.quantity,
                'price': float(item.price),
                'sum': float(item.sum),
                'payment_type': order.get_payment_type_display(),
            })

            # Суммируем по клиентам для графика (только покупки, не возвраты)
            if item.quantity > 0:  # положительные quantity - покупка
                client = order.client.name
                if client in client_totals:
                    client_totals[client] += float(item.sum)
                else:
                    client_totals[client] = float(item.sum)

    # Создаём график
    if client_totals:
        plt.figure(figsize=(10, 6))
        clients = list(client_totals.keys())
        totals = list(client_totals.values())

        # Столбцы
        bars = plt.bar(clients, totals, color='skyblue', edgecolor='navy')

        # Красная линия среднего
        avg = sum(totals) / len(totals)
        plt.axhline(y=avg, color='red', linestyle='--', linewidth=2, label=f'Среднее: {avg:,.0f} ₽')

        plt.title('Общая сумма покупок по клиентам', fontsize=16, fontweight='bold')
        plt.xlabel('Клиенты')
        plt.ylabel('Сумма, ₽')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)

        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:,.0f}', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()

        # Сохраняем в base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()

        graphic = base64.b64encode(image_png).decode('utf-8')
    else:
        graphic = None

    return JsonResponse({
        'data': report_data,
        'graphic': graphic,
        'total_orders': orders.count(),
        'total_sales': sum(item['sum'] for item in report_data if item['quantity'] > 0)
    })