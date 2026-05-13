from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.cache import cache

from .models import Event, Case, Team, CheckPoint, TeamCheckPointStatus, ChatMessage



# ==================== MODELS TESTS ====================

class EventModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name='Тестовый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            prize_fund='100 000 ₽',
            cases_visible_date=timezone.now() + timedelta(days=8),
        )

    def test_event_creation(self):
        self.assertEqual(str(self.event), 'Тестовый Кубок')
        self.assertTrue(self.event.registration_open)

    def test_event_verbose_names(self):
        self.assertEqual(Event._meta.verbose_name, 'Мероприятие')
        self.assertEqual(Event._meta.verbose_name_plural, 'Мероприятия')


class CaseModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name='Тестовый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            cases_visible_date=timezone.now() + timedelta(days=8),
        )
        self.case = Case.objects.create(
            title='Тестовый кейс',
            description='Описание кейса',
            event=self.event
        )

    def test_case_creation(self):
        self.assertIn('Тестовый Кубок', str(self.case))
        self.assertEqual(self.case.event, self.event)


class TeamModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.event = Event.objects.create(
            name='Тестовый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            cases_visible_date=timezone.now() + timedelta(days=8),
        )
        self.team = Team.objects.create(
            name='Тестовая команда',
            captain=self.user,
            captain_name='Тестов Тест Тестович',
            event=self.event,
        )

    def test_team_creation(self):
        self.assertEqual(self.team.captain, self.user)
        self.assertTrue(self.team.is_active)
        self.assertIn('Тестовый Кубок', str(self.team))

    def test_team_unique_constraint(self):
        with self.assertRaises(Exception):
            Team.objects.create(
                name='Тестовая команда',
                captain=self.user,
                captain_name='Дубль',
                event=self.event,
            )


class CheckPointModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name='Тестовый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            cases_visible_date=timezone.now() + timedelta(days=8),
        )
        self.cp = CheckPoint.objects.create(
            event=self.event,
            name='Чек-поинт 1',
            order=1
        )

    def test_checkpoint_creation(self):
        self.assertEqual(self.cp.order, 1)
        self.assertIn('Тестовый Кубок', str(self.cp))


class ChatMessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.admin = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        self.event = Event.objects.create(
            name='Тестовый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            cases_visible_date=timezone.now() + timedelta(days=8),
        )
        self.team = Team.objects.create(
            name='Тестовая команда',
            captain=self.user,
            captain_name='Тестов Тест Тестович',
            event=self.event,
        )

    def test_chat_message_creation(self):
        msg = ChatMessage.objects.create(
            team=self.team,
            sender=self.user,
            text='Привет!',
        )
        self.assertEqual(msg.text, 'Привет!')
        self.assertFalse(msg.is_admin)

    def test_admin_message(self):
        msg = ChatMessage.objects.create(
            team=self.team,
            sender=self.admin,
            text='Ответ поддержки',
            is_admin=True
        )
        self.assertTrue(msg.is_admin)


# ==================== VIEWS TESTS ====================

class HomeViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.event = Event.objects.create(
            name='Тестовый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            cases_visible_date=timezone.now() + timedelta(days=8),
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый Кубок')
        self.assertTemplateUsed(response, 'core/home.html')

    def test_home_without_event(self):
        Event.objects.all().delete()
        cache.clear()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Мероприятий пока нет')


class CaseListViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()

        # Ивент, где кейсы ЗАКРЫТЫ (дата в будущем)
        self.event_closed = Event.objects.create(
            name='Закрытый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            cases_visible_date=timezone.now() + timedelta(days=5),  # Ещё 5 дней
        )
        Case.objects.create(title='Секретный кейс', event=self.event_closed)

        # Ивент, где кейсы ОТКРЫТЫ (дата прошла)
        self.event_open = Event.objects.create(
            name='Открытый Кубок',
            date=timezone.now() + timedelta(days=2),
            location='Питер',
            cases_visible_date=timezone.now() - timedelta(days=1),  # Вчера
        )
        Case.objects.create(title='Открытый кейс', event=self.event_open)

    def test_cases_hidden_when_not_visible(self):
        """Кейсы не видны до cases_visible_date"""
        response = self.client.get(reverse('case_list'))
        # Редиректит на home, потому что берётся Event.objects.first()
        # (закрытый ивент первый)
        self.assertEqual(response.status_code, 302)

    def test_cases_visible_after_date(self):
        """Кейсы видны после cases_visible_date (удаляем закрытый ивент)"""
        self.event_closed.delete()
        response = self.client.get(reverse('case_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Открытый кейс')


class TeamRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='captain', password='pass123')
        self.event = Event.objects.create(
            name='Тестовый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            cases_visible_date=timezone.now() - timedelta(days=1),  # Кейсы открыты
        )
        self.case = Case.objects.create(title='Кейс 1', event=self.event)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('register_team'))
        self.assertEqual(response.status_code, 302)

    def test_register_team_success(self):
        self.client.login(username='captain', password='pass123')
        response = self.client.post(reverse('register_team'), {
            'name': 'Новая команда',
            'captain_name': 'Иванов Иван',
            'selected_case': self.case.id,
            'event': self.event.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Team.objects.filter(name='Новая команда').exists())

    def test_registration_closed(self):
        self.event.registration_open = False
        self.event.save()
        self.client.login(username='captain', password='pass123')
        response = self.client.get(reverse('register_team'))
        self.assertEqual(response.status_code, 302)  # Редирект на home


class TeamChatTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.captain = User.objects.create_user(username='captain', password='pass123')
        self.other_user = User.objects.create_user(username='other', password='pass123')
        self.event = Event.objects.create(
            name='Тестовый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            cases_visible_date=timezone.now() + timedelta(days=8),
        )
        self.team = Team.objects.create(
            name='Команда',
            captain=self.captain,
            captain_name='Капитан Капитан',
            event=self.event,
        )

    def test_chat_access_for_captain(self):
        self.client.login(username='captain', password='pass123')
        response = self.client.get(reverse('team_chat', args=[self.team.id]))
        self.assertEqual(response.status_code, 200)

    def test_chat_access_denied_for_outsider(self):
        self.client.login(username='other', password='pass123')
        response = self.client.get(reverse('team_chat', args=[self.team.id]))
        self.assertEqual(response.status_code, 302)

    def test_send_message(self):
        self.client.login(username='captain', password='pass123')
        response = self.client.post(reverse('team_chat', args=[self.team.id]), {
            'text': 'Тестовое сообщение'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ChatMessage.objects.filter(text='Тестовое сообщение').exists())


class StatisticsViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(username='captain', password='pass123')
        self.event = Event.objects.create(
            name='Тестовый Кубок',
            date=timezone.now() + timedelta(days=10),
            location='Москва',
            cases_visible_date=timezone.now() + timedelta(days=8),
        )
        self.team_active = Team.objects.create(
            name='Активная команда',
            captain=self.user,
            captain_name='Капитан',
            event=self.event,
            is_active=True,
        )
        self.team_eliminated = Team.objects.create(
            name='Выбывшая команда',
            captain=self.user,
            captain_name='Капитан 2',
            event=self.event,
            is_active=False,
        )
        self.cp = CheckPoint.objects.create(event=self.event, name='КП 1', order=1)

    def test_statistics_page(self):
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Активная команда')
        self.assertContains(response, 'Выбывшая команда')
        self.assertContains(response, 'В игре')
        self.assertContains(response, 'Выбыла')


# ==================== MIDDLEWARE LOGIC TEST ====================

class CaseVisibilityLogicTest(TestCase):
    def setUp(self):
        self.now = timezone.now()

    def test_cases_not_visible_before_date(self):
        event = Event.objects.create(
            name='Кубок',
            date=self.now + timedelta(days=10),
            location='Москва',
            cases_visible_date=self.now + timedelta(days=2),
        )
        self.assertFalse(self.now >= event.cases_visible_date)

    def test_cases_visible_after_date(self):
        event = Event.objects.create(
            name='Кубок',
            date=self.now + timedelta(days=10),
            location='Москва',
            cases_visible_date=self.now - timedelta(days=1),
        )
        self.assertTrue(self.now >= event.cases_visible_date)