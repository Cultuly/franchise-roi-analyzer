from django.db import models


class Region(models.Model):
    """Регион с демографическими данными (загружается из CSV Росстата)"""
    name = models.CharField("Название региона", max_length=100, unique=True)
    population = models.PositiveIntegerField("Население")
    avg_income = models.DecimalField(
        "Средний доход (руб.)",
        max_digits=10,
        decimal_places=2,
        help_text="Среднедушевой доход в месяц"
    )
    rent_cost_per_sqm = models.DecimalField(
        "Стоимость аренды за м² (руб.)",
        max_digits=8,
        decimal_places=2,
        help_text="Средняя стоимость коммерческой аренды"
    )
    foot_traffic_index = models.FloatField(
        "Индекс пешеходного трафика",
        default=1.0,
        help_text="От 0.5 (низкий) до 2.0 (высокий)"
    )

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"
        ordering = ['name']

    def __str__(self):
        return self.name