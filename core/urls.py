from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('clients/', views.clients, name='clients'),
    path('training/', views.federated_training, name='training'),
    path('detection/', views.intrusion_detection, name='detection'),
    path('logs/', views.attack_logs, name='logs'),
    path('performance/', views.performance, name='performance'),

    # API
    path('api/run-training/', views.api_run_training, name='api_run_training'),
    path('api/stats/', views.api_dashboard_stats, name='api_stats'),
    path('api/add-client/', views.api_add_client, name='api_add_client'),
    path('api/simulate-attack/', views.api_simulate_attack, name='api_simulate_attack'),
]
