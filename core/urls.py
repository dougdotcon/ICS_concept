from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Views de interface web
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # API endpoints
    path('api/health/', views.health_check, name='health_check'),
    path('api/calculate/', views.ICSCalculationAPIView.as_view(), name='calculate_ics'),
    path('api/dashboard/stats/', views.dashboard_stats_api, name='dashboard_stats'),
    path('api/profiles/', views.profile_list_api, name='profile_list'),
    path('api/profiles/<int:profile_id>/', views.profile_detail_api, name='profile_detail'),
] 