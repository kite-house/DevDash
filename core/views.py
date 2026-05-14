from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from .models import Event, Case, Team, CheckPoint, TeamCheckPointStatus, ChatMessage, User
from .forms import TeamRegistrationForm, ChatMessageForm, AddMemberForm


def home(request):
    """Главная страница с кешированием"""
    cache_key = "home_page"
    context = cache.get(cache_key)

    if context is None:
        event = Event.objects.first()
        now = timezone.now()
        can_view = (event and now >= event.cases_visible_date)
        context = {
            'event': event,
            'can_view_cases': can_view,
        }
        cache.set(cache_key, context, timeout=settings.CACHE_TTL["home"])

    return render(request, 'core/home.html', context)


def case_list(request):
    """Список кейсов с кешированием"""
    event = Event.objects.first()
    now = timezone.now()

    if not event or now < event.cases_visible_date:
        messages.warning(request, 'Кейсы будут доступны за 2 дня до мероприятия!')
        return redirect('home')

    cache_key = f"case_list_{event.id}"
    cases = cache.get(cache_key)

    if cases is None:
        cases = list(Case.objects.filter(event=event))
        cache.set(cache_key, cases, timeout=settings.CACHE_TTL["case_list"])

    return render(request, 'core/case_list.html', {'cases': cases, 'event': event})


@login_required
def register_team(request):
    """Регистрация команды"""
    event = Event.objects.first()

    if not event or not event.registration_open:
        messages.error(request, 'Регистрация на мероприятие закрыта.')
        return redirect('home')

    now = timezone.now()
    can_view = (event and now >= event.cases_visible_date)

    existing_team = Team.objects.filter(captain=request.user, event=event).first()
    if existing_team:
        messages.info(request, f'Вы уже зарегистрированы как капитан команды «{existing_team.name}».')
        return redirect('team_detail', team_id=existing_team.id)

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

            cache.delete(f"statistics_{event.id}")

            messages.success(request, f'Команда «{team.name}» успешно зарегистрирована!')
            return redirect('team_detail', team_id=team.id)
    else:
        form = TeamRegistrationForm(event=event, can_view_cases=can_view)

    return render(request, 'core/register_team.html', {
        'form': form,
        'event': event,
        'can_view_cases': can_view,
    })


@login_required
def team_detail(request, team_id):
    """Страница команды"""
    team = get_object_or_404(Team, id=team_id)

    if request.user != team.captain and request.user not in team.members.all():
        messages.error(request, 'У вас нет доступа к этой команде.')
        return redirect('home')

    return render(request, 'core/team_detail.html', {'team': team})


def statistics(request):
    """Статистика с кешированием"""
    event = Event.objects.first()

    if not event:
        return render(request, 'core/statistics.html', {
            'stats': [],
            'checkpoints': [],
            'event': None,
        })

    cache_key = f"statistics_{event.id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        stats = cached_data['stats']
        checkpoints = cached_data['checkpoints']
    else:
        teams = Team.objects.filter(event=event)
        checkpoints = list(CheckPoint.objects.filter(event=event).order_by('order'))

        stats = []
        for team in teams:
            passed_count = TeamCheckPointStatus.objects.filter(
                team=team, is_passed=True
            ).count()
            total_count = len(checkpoints)
            stats.append({
                'team': team,
                'passed': passed_count,
                'total': total_count,
                'is_active': team.is_active,
            })

        cache.set(
            cache_key,
            {'stats': stats, 'checkpoints': checkpoints},
            timeout=settings.CACHE_TTL["statistics"]
        )

    return render(request, 'core/statistics.html', {
        'stats': stats,
        'checkpoints': checkpoints,
        'event': event,
    })


@login_required
def team_chat(request, team_id):
    """Чат поддержки"""
    team = get_object_or_404(Team, id=team_id)

    if request.user != team.captain and request.user not in team.members.all() and not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этому чату.')
        return redirect('home')

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
            return redirect('team_chat', team_id=team.id)
    else:
        form = ChatMessageForm()

    messages_qs = team.chat_messages.all().order_by('created_at')

    return render(request, 'core/team_chat.html', {
        'team': team,
        'chat_messages': messages_qs,
        'form': form,
    })


@login_required
def manage_team(request, team_id):
    """Управление командой: добавление/удаление участников"""
    team = get_object_or_404(Team, id=team_id)

    if request.user != team.captain:
        messages.error(request, 'Только капитан может управлять составом команды.')
        return redirect('team_detail', team_id=team.id)

    if request.method == 'POST':
        form = AddMemberForm(request.POST, team=team)
        if form.is_valid():
            username = form.cleaned_data['username']
            new_member = User.objects.get(username=username)
            team.members.add(new_member)
            messages.success(request, f'Участник {username} добавлен в команду!')
            return redirect('manage_team', team_id=team.id)
    else:
        form = AddMemberForm(team=team)

    members = team.members.all()

    return render(request, 'core/manage_team.html', {
        'team': team,
        'members': members,
        'form': form,
    })


@login_required
def remove_member(request, team_id, user_id):
    """Удаление участника из команды"""
    team = get_object_or_404(Team, id=team_id)

    if request.user != team.captain:
        messages.error(request, 'Только капитан может удалять участников.')
        return redirect('team_detail', team_id=team.id)

    member = get_object_or_404(User, id=user_id)

    if member in team.members.all():
        team.members.remove(member)
        messages.success(request, f'Участник {member.username} удалён из команды.')
    else:
        messages.error(request, 'Этот пользователь не состоит в команде.')

    return redirect('manage_team', team_id=team.id)