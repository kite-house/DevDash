from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('cases/', views.case_list, name='case_list'),
    path('team/register/', views.register_team, name='register_team'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('statistics/', views.statistics, name='statistics'),
]