from django.contrib import admin
from .models import ProfitabilityAnalysis


@admin.register(ProfitabilityAnalysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('franchise', 'region', 'payback_period', 'is_profitable', 'created_at')
    search_fields = ('franchise__name', 'region__name')
    list_filter = ('is_profitable', 'region')
    readonly_fields = ('startup_costs', 'monthly_expenses', 'forecasted_revenue', 'payback_period', 'is_profitable')