from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.urls import reverse
from django.db.models import Q


class Counterparty(models.Model):
    code = models.CharField('Код контрагента', max_length=20, unique=True)
    name = models.CharField('Наименование', max_length=200)
    short_name = models.CharField('Краткое наименование', max_length=100, blank=True)

    inn = models.CharField(
        'ИНН', max_length=12,
        validators=[RegexValidator(r'^\d{10}$|^\d{12}$', '10 или 12 цифр')],
        help_text='10 или 12 цифр'
    )

    kpp = models.CharField('КПП', max_length=9, blank=True)
    ogrn = models.CharField('ОГРН', max_length=13, blank=True)
    legal_address = models.TextField('Юридический адрес', blank=True)
    actual_address = models.TextField('Фактический адрес', blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)

    is_active = models.BooleanField('Активен', default=True)
    is_marked_for_deletion = models.BooleanField('Помечен на удаление', default=False)
    comment = models.TextField('Комментарий', blank=True)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        if not self.inn or not self.inn.strip():
            raise ValidationError({'inn': 'ИНН не может быть пустым!'})
        self.inn = self.inn.strip()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('counterparties:counterparty_detail', args=[str(self.id)])

    def comprehensive_inn_check(self):
        exact = Counterparty.objects.filter(
            Q(inn=self.inn) & ~Q(id=self.id) & ~Q(is_marked_for_deletion=True)
        )
        contains = Counterparty.objects.filter(
            Q(inn__contains=self.inn) & ~Q(id=self.id) & ~Q(is_marked_for_deletion=True)
        )
        part_of = Counterparty.objects.filter(
            Q(inn__icontains=self.inn) & ~Q(id=self.id) & ~Q(is_marked_for_deletion=True)
        )
        return {
            'exact_duplicates': exact,
            'contains_other': contains,
            'part_of_other': part_of,
            'has_issues': exact.exists() or contains.exists() or part_of.exists()
        }