from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    patronymic = models.CharField("Отчество", max_length=30, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    phone = models.CharField("Номер телефона", max_length=20, blank=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль: {self.user.username}"

    @property
    def full_name(self):
        """ФИО полностью"""
        parts = [self.user.last_name, self.user.first_name, self.patronymic]
        return ' '.join(p for p in parts if p)