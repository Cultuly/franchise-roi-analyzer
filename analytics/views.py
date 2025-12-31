from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
import json
from regions.models import Region
from .services import ProfitabilityCalculator


class CalculatorView(TemplateView):
    template_name = 'analytics/calculator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        return context


class CalculateAPIView(TemplateView):
    """API для расчета рентабельности"""

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            # Валидация данных
            required_fields = ['region_id', 'establishment_type', 'premises_area',
                               'staff_count', 'initial_fee', 'royalty_percent', 'avg_check']
            for field in required_fields:
                if field not in data or data[field] is None:
                    return JsonResponse({'error': f'Отсутствует обязательное поле: {field}'}, status=400)

            # Получение региона
            try:
                region = Region.objects.get(id=data['region_id'])
            except Region.DoesNotExist:
                return JsonResponse({'error': 'Регион не найден'}, status=404)

            # Расчёт данных
            result = ProfitabilityCalculator.calculate_custom(
                region=region,
                establishment_type=data['establishment_type'],
                premises_area=float(data['premises_area']),
                staff_count=int(data['staff_count']),
                initial_fee=float(data['initial_fee']),
                royalty_percent=float(data['royalty_percent']),
                avg_check=float(data['avg_check'])
            )

            # Генерация данных для графика
            chart_data = ProfitabilityCalculator.generate_payback_chart_data(
                startup_costs=result['startup_costs'],
                monthly_profit=result['monthly_profit']
            )

            return JsonResponse({
                'success': True,
                'results': {
                    'monthly_revenue': round(result['monthly_revenue'], 2),
                    'monthly_expenses': round(result['monthly_expenses'], 2),
                    'monthly_profit': round(result['monthly_profit'], 2),
                    'startup_costs': round(result['startup_costs'], 2),
                    'payback_period': round(result['payback_period'], 1),
                    'roi_annual': round(result['roi_annual'], 1),
                    'is_profitable': result['is_profitable'],
                    'daily_customers': round(result['daily_customers'], 1)
                },
                'chart_data': chart_data
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректный формат JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Ошибка расчета: {str(e)}'}, status=500)
