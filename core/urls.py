from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cases/', views.case_list, name='case_list'),
    path('team/register/', views.register_team, name='register_team'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('team/<int:team_id>/manage/', views.manage_team, name='manage_team'),
    path('team/<int:team_id>/remove/<int:user_id>/', views.remove_member, name='remove_member'),
    path('team/<int:team_id>/chat/', views.team_chat, name='team_chat'),
    path('statistics/', views.statistics, name='statistics'),
]