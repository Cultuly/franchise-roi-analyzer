from django.contrib import admin
from .models import Franchise


@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'initial_fee', 'royalty_percent', 'avg_roi_months')
    search_fields = ('name', 'type')
    list_filter = ('type',)