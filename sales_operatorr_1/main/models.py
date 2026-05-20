from django.db import models

class Client(models.Model):
    """Клиент"""
    name = models.CharField(max_length=200, verbose_name="Название")
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Всего покупок")
    current_account = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Текущий счет")
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=100000, verbose_name="Кредитный лимит")
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Текущий долг")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    def __str__(self):
        return self.name

    @property
    def credit_remaining(self):
        return self.credit_limit - self.current_debt


class Product(models.Model):
    """Товар"""
    name = models.CharField(max_length=200, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.IntegerField(default=0, verbose_name="Остаток")

    def __str__(self):
        return f"{self.name} - {self.price} руб."


class Order(models.Model):
    """Заказ"""
    PAYMENT_TYPES = [
        ('cash', 'Наличные'),
        ('cashless', 'Безнал'),
        ('credit', 'Кредит'),
        ('barter', 'Бартер'),
        ('mutual', 'Взаимозачет'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name="Тип оплаты")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Сумма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return f"Заказ №{self.id} - {self.client.name}"


class OrderItem(models.Model):
    """Товар в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    sum = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")