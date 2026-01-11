from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)


class ProfitabilityCalculator:
    @staticmethod
    def clean_value(value):
        """Очищает значение от невидимых символов и преобразует в Decimal"""
        if value is None:
            return Decimal('0')
        if isinstance(value, Decimal):
            return value
        value_str = str(value)
        value_str = ''.join(c for c in value_str if c.isdigit() or c in ['.', ',', '-'])
        value_str = value_str.replace(',', '.')
        try:
            return Decimal(value_str)
        except (TypeError, ValueError):
            logger.error(f"Не удалось преобразовать значение в Decimal: {value}")
            return Decimal('0')

    @staticmethod
    def calculate_custom(region, establishment_type, premises_area, staff_count,
                         initial_fee, royalty_percent, avg_check):
        """Расчет рентабельности с пользовательскими параметрами"""
        premises_area = Decimal(str(premises_area))
        staff_count = Decimal(str(staff_count))
        initial_fee = Decimal(str(initial_fee))
        royalty_percent = Decimal(str(royalty_percent))
        avg_check = Decimal(str(avg_check))
        rent_cost_per_sqm = ProfitabilityCalculator.clean_value(region.rent_cost_per_sqm)
        avg_salary_coeff = ProfitabilityCalculator.clean_value(region.avg_salary_coeff)
        foot_traffic_index = ProfitabilityCalculator.clean_value(region.foot_traffic_index)
        utility_percent = ProfitabilityCalculator.clean_value(region.utility_percent)
        food_cost_percent = ProfitabilityCalculator.clean_value(region.food_cost_percent)
        marketing_percent = ProfitabilityCalculator.clean_value(region.marketing_percent)

        ESTABLISHMENT_COEFFS = {
            'cafe': {'traffic_factor': Decimal('1.2'), 'seating_factor': Decimal('0.85')},
            'burger': {'traffic_factor': Decimal('1.0'), 'seating_factor': Decimal('0.75')},
            'pizza': {'traffic_factor': Decimal('0.9'), 'seating_factor': Decimal('0.70')},
            'sushi': {'traffic_factor': Decimal('0.85'), 'seating_factor': Decimal('0.65')},
            'fastfood': {'traffic_factor': Decimal('1.3'), 'seating_factor': Decimal('0.60')},
        }

        if establishment_type not in ESTABLISHMENT_COEFFS:
            logger.warning(f"Неизвестный тип заведения: {establishment_type}. Используется кофейня по умолчанию.")
            establishment_type = 'cafe'

        coeffs = ESTABLISHMENT_COEFFS[establishment_type]
        daily_customers = premises_area * coeffs['seating_factor'] * foot_traffic_index * coeffs['traffic_factor']
        monthly_revenue = daily_customers * avg_check * Decimal('30') * Decimal('0.85')
        monthly_rent = rent_cost_per_sqm * premises_area
        base_salary = Decimal('45000')
        staff_cost = base_salary * staff_count * avg_salary_coeff
        utilities = monthly_rent * (utility_percent / Decimal('100'))
        food_costs = monthly_revenue * (food_cost_percent / Decimal('100'))
        marketing_costs = monthly_revenue * (marketing_percent / Decimal('100'))
        royalty = monthly_revenue * (royalty_percent / Decimal('100'))
        monthly_expenses = monthly_rent + staff_cost + utilities + food_costs + marketing_costs + royalty
        equipment_cost = premises_area * Decimal('15000')
        renovation_cost = premises_area * Decimal('10000')
        training_cost = Decimal('150000')
        startup_costs = initial_fee + equipment_cost + renovation_cost + training_cost
        monthly_profit = monthly_revenue - monthly_expenses

        if monthly_profit <= 0:
            return {
                'monthly_revenue': monthly_revenue,
                'monthly_expenses': monthly_expenses,
                'monthly_rent': monthly_rent,
                'staff_cost': staff_cost,
                'monthly_profit': monthly_profit,
                'startup_costs': startup_costs,
                'payback_period': float('inf'),
                'roi_annual': Decimal('0'),
                'is_profitable': False,
                'daily_customers': daily_customers
            }

        payback_period = startup_costs / monthly_profit
        roi_annual = (monthly_profit * Decimal('12')) / startup_costs * Decimal('100')
        is_profitable = float(roi_annual) >= 15 and float(payback_period) <= 24

        return {
            'monthly_revenue': monthly_revenue,
            'monthly_expenses': monthly_expenses,
            'monthly_rent': monthly_rent,
            'staff_cost': staff_cost,
            'monthly_profit': monthly_profit,
            'startup_costs': startup_costs,
            'payback_period': payback_period,
            'roi_annual': roi_annual,
            'is_profitable': is_profitable,
            'daily_customers': daily_customers
        }

    @staticmethod
    def generate_payback_chart_data(startup_costs, monthly_profit, monthly_revenue, monthly_expenses, months=24):
        """Генерация данных для графика окупаемости со всеми метриками"""
        data = []
        for month in range(1, months + 1):
            cumulative_profit = float(monthly_profit * month - startup_costs)
            cumulative_revenue = float(monthly_revenue * month)
            cumulative_expenses = float(startup_costs + monthly_expenses * month)
            data.append({
                'month': month,
                'cumulative_profit': cumulative_profit,
                'cumulative_revenue': cumulative_revenue,
                'cumulative_expenses': cumulative_expenses
            })
        break_even = next((item for item in data if item['cumulative_profit'] >= 0), None)
        return {
            'data': data,
            'break_even_month': break_even['month'] if break_even else None
        }

    @staticmethod
    def generate_monthly_chart_data(startup_costs, monthly_revenue, monthly_expenses, months=12):
        """Генерация данных для месячной столбчатой диаграммы с учетом одноразовых затрат"""
        revenue_data = []
        expenses_data = []
        profit_data = []
        months_list = []

        # Одноразовые затраты в первом месяце (часть стартовых затрат)
        one_time_expenses = float(startup_costs * Decimal('0.2'))  # 20% одноразовых затрат в первый месяц

        # Добавим небольшой рост выручки каждый месяц (2%)
        growth_rate = 1.02

        for month in range(1, months + 1):
            months_list.append(month)

            current_revenue = float(monthly_revenue) * (growth_rate ** (month - 1))

            if month == 1:
                current_expenses = float(monthly_expenses) + one_time_expenses
            else:
                current_expenses = float(monthly_expenses) * (1.01 ** (month - 1))

            current_profit = current_revenue - current_expenses

            revenue_data.append(current_revenue)
            expenses_data.append(current_expenses)
            profit_data.append(current_profit)

        return {
            'months': months_list,
            'revenue': revenue_data,
            'expenses': expenses_data,
            'profit': profit_data
        }