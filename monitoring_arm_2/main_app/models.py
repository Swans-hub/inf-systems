from django.db import models


class DataPoint(models.Model):
    value = models.FloatField(verbose_name="Значение параметра")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время записи")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp}: {self.value}"
