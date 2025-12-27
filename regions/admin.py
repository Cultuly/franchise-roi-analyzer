from django.contrib import admin
from .models import Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'population', 'avg_income', 'rent_cost_per_sqm')
    search_fields = ('name',)
    list_filter = ('name',)