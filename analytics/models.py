from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class ProfitabilityAnalysis(models.Model):
    """Расчёт рентабельности для конкретной локации"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        null=True,
        blank=True
    )
    franchise = models.ForeignKey(
        'franchises.Franchise',
        on_delete=models.CASCADE,
        verbose_name="Франшиза"
    )
    region = models.ForeignKey(
        'regions.Region',
        on_delete=models.CASCADE,
        verbose_name="Регион"
    )
    premises_area = models.PositiveIntegerField(
        "Площадь помещения (м²)",
        default=50,
        validators=[MinValueValidator(30)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    startup_costs = models.DecimalField(
        "Стартовые затраты (руб.)",
        max_digits=15,
        decimal_places=2,
        editable=False,
        default=0.00
    )
    monthly_expenses = models.DecimalField(
        "Ежемесячные расходы (руб.)",
        max_digits=15,
        decimal_places=2,
        editable=False,
        default=0.00
    )
    forecasted_revenue = models.DecimalField(
        "Прогноз выручки (руб.)",
        max_digits=15,
        decimal_places=2,
        editable=False,
        default=0.00
    )
    payback_period = models.FloatField(
        "Срок окупаемости (мес)",
        editable=False,
        help_text="Время для возврата инвестиций",
        default=0.00
    )
    is_profitable = models.BooleanField(
        "Рентабельность > 15%",
        default=False,
        editable=False,
        help_text="Соответствует ли проект минимальному порогу"
    )

    class Meta:
        verbose_name = "Анализ рентабельности"
        verbose_name_plural = "Аналитика рентабельности"
        ordering = ['-created_at']

    def __str__(self):
        return f"Анализ {self.franchise} в {self.region} ({self.created_at.strftime('%d.%m.%Y')})"