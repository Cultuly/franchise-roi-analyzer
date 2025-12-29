from decimal import Decimal, ROUND_HALF_UP


class ProfitabilityCalculator:
    @staticmethod
    def calculate_custom(region, establishment_type, premises_area, staff_count,
                         initial_fee, royalty_percent, avg_check):
        """Расчет рентабельности с пользовательскими параметрами"""

        # Базовые коэффициенты для типов заведения
        ESTABLISHMENT_COEFFS = {
            'cafe': {'traffic_factor': 1.2, 'seating_factor': 0.85},
            'burger': {'traffic_factor': 1.0, 'seating_factor': 0.75},
            'pizza': {'traffic_factor': 0.9, 'seating_factor': 0.70},
            'sushi': {'traffic_factor': 0.85, 'seating_factor': 0.65},
            'fastfood': {'traffic_factor': 1.3, 'seating_factor': 0.60},
        }

        coeffs = ESTABLISHMENT_COEFFS.get(establishment_type, ESTABLISHMENT_COEFFS['cafe'])

        # 1. Прогноз выручки
        daily_customers = premises_area * coeffs['seating_factor'] * region.foot_traffic_index * coeffs[
            'traffic_factor']
        monthly_revenue = daily_customers * avg_check * 30 * 0.85

        # 2. Ежемесячные расходы
        monthly_rent = region.rent_cost_per_sqm * premises_area
        base_salary = Decimal('45000')
        staff_cost = base_salary * staff_count * Decimal(str(region.avg_salary_coeff))

        utilities = monthly_rent * (region.utility_percent / 100)
        food_costs = monthly_revenue * (region.food_cost_percent / 100)
        marketing_costs = monthly_revenue * (region.marketing_percent / 100)
        royalty = monthly_revenue * (royalty_percent / 100)

        monthly_expenses = monthly_rent + staff_cost + utilities + food_costs + marketing_costs + royalty

        # 3. Стартовые затраты (пока mock данные)
        equipment_cost = premises_area * 15000
        renovation_cost = premises_area * 10000
        training_cost = 150000

        startup_costs = initial_fee + equipment_cost + renovation_cost + training_cost

        # 4. Финансовые показатели
        monthly_profit = monthly_revenue - monthly_expenses
        payback_period = startup_costs / monthly_profit if monthly_profit > 0 else float('inf')
        roi_annual = (monthly_profit * 12) / startup_costs * 100 if startup_costs > 0 else 0
        is_profitable = roi_annual >= 15 and payback_period <= 24

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
    def generate_payback_chart_data(startup_costs, monthly_profit, months=24):
        """Генерация данных для графика окупаемости"""
        data = []
        for month in range(1, months + 1):
            cumulative_profit = monthly_profit * month - startup_costs
            data.append({
                'month': month,
                'cumulative_profit': cumulative_profit
            })

        # Поиск точки безубыточности
        break_even = next((item for item in data if item['cumulative_profit'] >= 0), None)

        return {
            'data': data,
            'break_even_month': break_even['month'] if break_even else None
        }