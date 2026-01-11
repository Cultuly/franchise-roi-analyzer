from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from .views import HomeView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('analytics/', include('analytics.urls', namespace='analytics')),
]
