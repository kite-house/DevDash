from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, Case, Team, CheckPoint, TeamCheckPointStatus, ChatMessage
from .forms import TeamRegistrationForm, ChatMessageForm


def home(request):
    """Главная страница с информацией о ближайшем кубке"""
    event = Event.objects.first()
    now = timezone.now()
    can_view = (event and now >= event.cases_visible_date)

    context = {
        'event': event,
        'can_view_cases': can_view,
    }
    return render(request, 'core/home.html', context)


def case_list(request):
    """Список кейсов (доступен только когда откроют)"""
    event = Event.objects.first()
    now = timezone.now()

    if not event or now < event.cases_visible_date:
        messages.warning(request, 'Кейсы будут доступны за 2 дня до мероприятия!')
        return redirect('core:home')

    cases = Case.objects.filter(event=event)
    return render(request, 'core/case_list.html', {'cases': cases, 'event': event})


@login_required
def register_team(request):
    """Регистрация команды"""
    event = Event.objects.first()

    if not event or not event.registration_open:
        messages.error(request, 'Регистрация на мероприятие закрыта.')
        return redirect('core:home')

    now = timezone.now()
    can_view = (event and now >= event.cases_visible_date)

    existing_team = Team.objects.filter(captain=request.user, event=event).first()
    if existing_team:
        messages.info(request, f'Вы уже зарегистрированы как капитан команды «{existing_team.name}».')
        return redirect('core:team_detail', team_id=existing_team.id)

    if request.method == 'POST':
        form = TeamRegistrationForm(
            request.POST,
            event=event,
            can_view_cases=can_view
        )
        if form.is_valid():
            team = form.save(commit=False)
            team.captain = request.user
            team.event = event
            team.captain_name = form.cleaned_data['captain_name']
            team.save()
            form.save_m2m()
            messages.success(request, f'Команда «{team.name}» успешно зарегистрирована!')
            return redirect('core:team_detail', team_id=team.id)
    else:
        form = TeamRegistrationForm(event=event, can_view_cases=can_view)

    return render(request, 'core/register_team.html', {
        'form': form,
        'event': event,
        'can_view_cases': can_view,
    })


@login_required
def team_detail(request, team_id):
    """Страница команды (личный кабинет)"""
    team = get_object_or_404(Team, id=team_id)

    if request.user != team.captain and request.user not in team.members.all():
        messages.error(request, 'У вас нет доступа к этой команде.')
        return redirect('core:home')

    return render(request, 'core/team_detail.html', {'team': team})


def statistics(request):
    """Статистика турнира: выбывшие и активные команды"""
    event = Event.objects.first()
    teams = Team.objects.filter(event=event) if event else Team.objects.none()
    checkpoints = CheckPoint.objects.filter(event=event).order_by('order') if event else []

    stats = []
    for team in teams:
        passed_count = TeamCheckPointStatus.objects.filter(
            team=team, is_passed=True
        ).count()
        total_count = checkpoints.count()
        stats.append({
            'team': team,
            'passed': passed_count,
            'total': total_count,
            'is_active': team.is_active,
        })

    return render(request, 'core/statistics.html', {
        'stats': stats,
        'checkpoints': checkpoints,
        'event': event,
    })

@login_required
def team_chat(request, team_id):
    """Чат поддержки для команды"""
    team = get_object_or_404(Team, id=team_id)

    if request.user != team.captain and request.user not in team.members.all() and not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этому чату.')
        return redirect('core:home')

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            ChatMessage.objects.create(
                team=team,
                sender=request.user,
                text=form.cleaned_data['text'],
                is_admin=request.user.is_staff
            )
            messages.success(request, 'Сообщение отправлено')
            return redirect('core:team_chat', team_id=team.id)
    else:
        form = ChatMessageForm()

    messages_qs = team.chat_messages.all().order_by('created_at')

    return render(request, 'core/team_chat.html', {
        'team': team,
        'chat_messages': messages_qs,
        'form': form,
    })