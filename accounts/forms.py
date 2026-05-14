from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re
from datetime import date


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Имя"
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Фамилия"
    )
    patronymic = forms.CharField(
        max_length=30,
        required=False,
        label="Отчество (при наличии)"
    )
    birth_date = forms.DateField(
        required=True,
        label="Дата рождения",
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Формат: ДД.ММ.ГГГГ"
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        label="Номер телефона",
        widget=forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'})
    )

    class Meta:
        model = User
        fields = (
            'username', 'last_name', 'first_name', 'patronymic',
            'birth_date', 'email', 'phone', 'password1', 'password2'
        )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        phone_clean = re.sub(r'[^\d+]', '', phone)
        if not re.match(r'^\+?[78]\d{10}$', phone_clean):
            raise forms.ValidationError('Введите корректный номер телефона (11 цифр, начиная с 7 или 8)')
        return phone_clean

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            age = (date.today() - birth_date).days // 365
            if age < 14:
                raise forms.ValidationError('Участник должен быть старше 14 лет')
            if age > 100:
                raise forms.ValidationError('Проверьте дату рождения')
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
        return user