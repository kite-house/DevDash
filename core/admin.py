import openpyxl
from django.http import HttpResponse
from django.contrib import admin
from django.utils import timezone

from .models import Event, Case, Team, CheckPoint, TeamCheckPointStatus, ChatMessage


# ==================== INLINES ====================

class CaseInline(admin.TabularInline):
    model = Case
    extra = 0


class CheckPointInline(admin.TabularInline):
    model = CheckPoint
    extra = 0


class TeamCheckPointStatusInline(admin.TabularInline):
    model = TeamCheckPointStatus
    extra = 0


# ==================== ADMINS ====================

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location', 'registration_open', 'cases_visible_date']
    list_filter = ['registration_open']
    search_fields = ['name', 'location']
    inlines = [CaseInline, CheckPointInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'date', 'location', 'prize_fund')
        }),
        ('Настройки', {
            'fields': ('registration_open', 'cases_visible_date')
        }),
    )


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'event']
    list_filter = ['event']
    search_fields = ['title', 'description']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'captain', 'captain_name', 'event', 'selected_case', 'is_active', 'created_at']
    list_filter = ['event', 'is_active', 'selected_case']
    search_fields = ['name', 'captain__username', 'captain_name']
    filter_horizontal = ['members']
    inlines = [TeamCheckPointStatusInline]

    actions = ['export_to_excel']

    @admin.action(description="📥 Выгрузить выбранные команды в Excel")
    def export_to_excel(self, request, queryset):
        """Экспорт списка команд в Excel"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Команды"

        headers = [
            "Название команды",
            "Капитан (логин)",
            "ФИО капитана",
            "Мероприятие",
            "Кейс",
            "Статус",
            "Дата регистрации",
        ]
        ws.append(headers)

        for col in range(1, len(headers) + 1):
            ws.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)

        for team in queryset:
            ws.append([
                team.name,
                team.captain.username,
                team.captain_name,
                team.event.name if team.event else '',
                team.selected_case.title if team.selected_case else 'Не выбран',
                'В игре' if team.is_active else 'Выбыла',
                team.created_at.strftime('%d.%m.%Y %H:%M'),
            ])

        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = min(max_length + 2, 50)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"teams_export_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response


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

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['team', 'sender', 'text_preview', 'is_admin', 'created_at']
    list_filter = ['is_admin', 'team', 'created_at']
    search_fields = ['text', 'team__name', 'sender__username']
    readonly_fields = ['team', 'sender', 'text', 'is_admin', 'created_at']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Сообщение"

    def has_add_permission(self, request):
        return False  # Только через сайт