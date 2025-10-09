from django.urls import path
from monitoring import views
from monitoring import views_auth

urlpatterns = [
    path('', views.landing_auth, name='landing_auth'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/', views.export_csv, name='export_csv'),
    path('api/sensor/', views.update_sensor),
    path('api/status/', views.get_status),
    path('api/history/', views.get_history),
    path('api/register_token/', views.register_token, name='register_token'),
    path('api/ajax_register/', views_auth.ajax_register, name='ajax_register'),
    path('api/ajax_login/', views_auth.ajax_login, name='ajax_login'),
    path('api/ajax_logout/', views_auth.ajax_logout, name='ajax_logout'),
]
