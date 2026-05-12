from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Event(models.Model):
    """Мероприятие (ИТ-кубок)"""
    name = models.CharField("Название", max_length=200)
    date = models.DateTimeField("Дата проведения")
    location = models.CharField("Место проведения", max_length=300)
    prize_fund = models.CharField("Призовой фонд", max_length=100, blank=True, null=True)
    cases_visible_date = models.DateTimeField("Дата открытия кейсов")
    registration_open = models.BooleanField("Регистрация открыта", default=True)

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return self.name


class Case(models.Model):
    """Кейс (задача) для хакатона"""
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание")
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='cases',
        verbose_name="Мероприятие"
    )

    class Meta:
        verbose_name = "Кейс"
        verbose_name_plural = "Кейсы"

    def __str__(self):
        return f"{self.title} ({self.event.name})"


class Team(models.Model):
    """Команда участников"""
    name = models.CharField("Название команды", max_length=100)
    captain_name = models.CharField("ФИО капитана", max_length=200, default='')
    captain = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='captained_teams',
        verbose_name="Капитан"
    )
    members = models.ManyToManyField(
        User,
        related_name='teams',
        blank=True,
        verbose_name="Участники"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='teams',
        verbose_name="Мероприятие"
    )
    selected_case = models.ForeignKey(
        Case,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Выбранный кейс"
    )
    is_active = models.BooleanField("В игре", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"
        unique_together = ['name', 'event']

    def __str__(self):
        return f"{self.name} — {self.event.name}"


class CheckPoint(models.Model):
    """Контрольная точка турнира"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='checkpoints',
        verbose_name="Мероприятие"
    )
    name = models.CharField("Название", max_length=100)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Контрольная точка"
        verbose_name_plural = "Контрольные точки"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} — {self.event.name}"


class TeamCheckPointStatus(models.Model):
    """Статус прохождения командой контрольной точки"""
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='checkpoint_statuses',
        verbose_name="Команда"
    )
    checkpoint = models.ForeignKey(
        CheckPoint,
        on_delete=models.CASCADE,
        verbose_name="Контрольная точка"
    )
    is_passed = models.BooleanField("Пройдена", default=False)
    passed_at = models.DateTimeField("Время прохождения", null=True, blank=True)

    class Meta:
        verbose_name = "Статус прохождения КП"
        verbose_name_plural = "Статусы прохождения КП"
        unique_together = ['team', 'checkpoint']

    def __str__(self):
        status = "✅" if self.is_passed else "❌"
        return f"{self.team.name} — {self.checkpoint.name} {status}"