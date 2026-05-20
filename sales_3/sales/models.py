from django.db import models


class FieldDefinition(models.Model):
    """Хранит структуру данных (как поля таблицы)"""
    FIELD_TYPES = [
        ('string', 'Строка'),
        ('number', 'Число'),
        ('date', 'Дата'),
    ]

    name = models.CharField(max_length=50, verbose_name="Имя поля")
    label = models.CharField(max_length=100, verbose_name="Отображаемое имя")
    field_type = models.CharField(max_length=10, choices=FIELD_TYPES, verbose_name="Тип")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Передавать")
    precision = models.IntegerField(default=2, verbose_name="Точность (для чисел)", blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label} ({self.get_field_type_display()})"


class DynamicRecord(models.Model):
    """Хранит одну запись данных в JSON формате"""
    data = models.JSONField(verbose_name="Данные")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Запись #{self.id}"

    def get_profit(self):
        """Вычисление прибыли (если есть поля продажи)"""
        try:
            quantity = float(self.data.get('quantity', 0))
            sale_price = float(self.data.get('sale_price', 0))
            purchase_price = float(self.data.get('purchase_price', 0))
            discount = float(self.data.get('discount', 0))
            return (sale_price - discount) * quantity - purchase_price * quantity
        except (ValueError, TypeError):
            return 0