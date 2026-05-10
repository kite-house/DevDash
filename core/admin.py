from django.contrib import admin
from .models import Event, Case, Team, CheckPoint, TeamCheckPointStatus

# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location', 'registration_open']
    list_filter = ['registration_open']
    search_fields = ['name', 'location']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'event']
    list_filter = ['event']
    search_fields = ['title']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'captain', 'event', 'selected_case', 'is_active', 'created_at']
    list_filter = ['event', 'is_active']
    search_fields = ['name', 'captain__username']
    filter_horizontal = ['members']


@admin.register(CheckPoint)
class CheckPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'order']
    list_filter = ['event']
    ordering = ['event', 'order']


@admin.register(TeamCheckPointStatus)
class TeamCheckPointStatusAdmin(admin.ModelAdmin):
    list_display = ['team', 'checkpoint', 'is_passed', 'passed_at']
    list_filter = ['is_passed', 'checkpoint']
    search_fields = ['team__name']