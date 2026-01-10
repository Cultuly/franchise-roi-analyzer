from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import JsonResponse
import json
import logging
from regions.models import Region
from .services import ProfitabilityCalculator


logger = logging.getLogger(__name__)

class CalculatorView(TemplateView):
    template_name = 'analytics/calculator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        return context


class CalculateAPIView(View):
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

            try:
                region = Region.objects.get(id=data['region_id'])
            except Region.DoesNotExist:
                return JsonResponse({'error': 'Регион не найден'}, status=404)

            try:
                result = ProfitabilityCalculator.calculate_custom(
                    region=region,
                    establishment_type=data['establishment_type'],
                    premises_area=data['premises_area'],
                    staff_count=data['staff_count'],
                    initial_fee=data['initial_fee'],
                    royalty_percent=data['royalty_percent'],
                    avg_check=data['avg_check']
                )
            except Exception as e:
                logger.exception("Ошибка при расчете")
                return JsonResponse({'error': f'Ошибка данных региона: {str(e)}'}, status=400)

            chart_data = ProfitabilityCalculator.generate_payback_chart_data(
                startup_costs=result['startup_costs'],
                monthly_profit=result['monthly_profit'],
                monthly_revenue=result['monthly_revenue'],
                monthly_expenses=result['monthly_expenses']
            )

            formatted_results = {
                'monthly_revenue': float(result['monthly_revenue']),
                'monthly_expenses': float(result['monthly_expenses']),
                'monthly_profit': float(result['monthly_profit']),
                'startup_costs': float(result['startup_costs']),
                'is_profitable': result['is_profitable'],
                'daily_customers': float(result['daily_customers'])
            }

            if result['payback_period'] == float('inf'):
                formatted_results['payback_period'] = None
                formatted_results['roi_annual'] = 0.0
            else:
                formatted_results['payback_period'] = float(result['payback_period'])
                formatted_results['roi_annual'] = float(result['roi_annual'])

            return JsonResponse({
                'success': True,
                'results': formatted_results,
                'chart_data': chart_data
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректный формат JSON'}, status=400)
        except Exception as e:
            logger.exception("Неожиданная ошибка")
            return JsonResponse({'error': f'Неожиданная ошибка: {str(e)}'}, status=500)