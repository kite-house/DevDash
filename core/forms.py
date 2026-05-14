from django import forms
from .models import Team, Case, Event

class TeamRegistrationForm(forms.ModelForm):
    captain_name = forms.CharField(
        label="ФИО капитана",
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'})
    )

    class Meta:
        model = Team
        fields = ['name', 'selected_case', 'event']
        labels = {
            'name': 'Название команды',
            'selected_case': 'Выберите кейс',
            'event': 'Мероприятие',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Введите название команды'}),
            'event': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event', None)
        can_view_cases = kwargs.pop('can_view_cases', False)
        super().__init__(*args, **kwargs)

        if event:
            self.fields['event'].initial = event
            self.fields['selected_case'].queryset = Case.objects.filter(event=event)

        if not can_view_cases:
            self.fields['selected_case'].widget = forms.HiddenInput()
            self.fields['selected_case'].required = False
            self.fields['selected_case'].help_text = 'Кейсы будут доступны за 2 дня до мероприятия'
        else:
            self.fields['selected_case'].required = False
            self.fields['selected_case'].help_text = 'Можно выбрать позже'

class ChatMessageForm(forms.Form):
    """Форма отправки сообщения в чат"""
    text = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Введите сообщение...',
            'class': 'form-control'
        })
    )

class AddMemberForm(forms.Form):
    """Форма добавления участника в команду"""
    username = forms.CharField(
        label="Имя пользователя",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Введите username участника'})
    )

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        from django.contrib.auth.models import User
        username = self.cleaned_data['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('Пользователь с таким именем не найден. Попросите его зарегистрироваться.')

        if self.team and user in self.team.members.all():
            raise forms.ValidationError('Этот пользователь уже в команде.')

        if self.team and user == self.team.captain:
            raise forms.ValidationError('Капитан уже в команде.')

        return username