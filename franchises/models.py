from django.db import models


class Franchise(models.Model):
    """Франшиза общепита с финансовыми параметрами"""
    TYPE_CHOICES = [
        ('cafe', 'Кофейня'),
        ('burger', 'Бургерная'),
        ('pizza', 'Пиццерия'),
        ('sushi-bar', 'Суши-бар'),
    ]

    name = models.CharField("Название франшизы", max_length=100)
    type = models.CharField("Тип заведения", max_length=20, choices=TYPE_CHOICES)
    initial_fee = models.DecimalField(
        "Вступительный взнос (руб.)",
        max_digits=12,
        decimal_places=2,
        help_text="Оплата за право использования франшизы"
    )
    royalty_percent = models.FloatField(
        "Роялти (%)",
        default=5.0,
        help_text="Процент от выручки ежемесячно"
    )
    min_area = models.PositiveIntegerField(
        "Минимальная площадь (м²)",
        default=40
    )
    avg_roi_months = models.PositiveIntegerField(
        "Средний срок окупаемости (мес)",
        help_text="По данным франчайзера"
    )

    class Meta:
        verbose_name = "Франшиза"
        verbose_name_plural = "Франшизы"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"