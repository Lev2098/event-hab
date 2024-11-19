from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone  # додано імпорт
from django.contrib.admin.sites import site
from event_manager.models import Event, Participant, Feedback

User = get_user_model()


class UserAdminTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='password123',
            email='admin@example.com',
        )
        self.client.force_login(self.admin_user)

        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com',
            is_organizer=False,
        )

    def test_make_organizer_action(self):
        url = reverse('admin:event_manager_user_changelist')  # виправлено
        data = {
            'action': 'make_organizer',
            '_selected_action': [self.user.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_organizer)

    def test_remove_organizer_action(self):
        self.user.is_organizer = True
        self.user.save()
        url = reverse('admin:event_manager_user_changelist')  # виправлено
        data = {
            'action': 'remove_organizer',
            '_selected_action': [self.user.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_organizer)


class EventAdminTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='password123',
            email='admin@example.com',
        )
        self.client.force_login(self.admin_user)

        self.event = Event.objects.create(
            title="Test Event",
            description="This is a test event.",
            date=timezone.now().replace(tzinfo=timezone.utc),  # виправлено
            created_at=timezone.now().replace(tzinfo=timezone.utc),  # виправлено
            location="Test Location",
            max_participants=100,
            organizer=self.admin_user,
        )

    def test_event_list_display(self):
        url = reverse('admin:event_manager_event_changelist')  # виправлено
        response = self.client.get(url)
        self.assertContains(response, self.event.title)
        self.assertContains(response, self.event.description)
        self.assertContains(response, self.event.location)


class ParticipantAdminTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='password123',
            email='admin@example.com',
        )
        self.client.force_login(self.admin_user)

        self.event = Event.objects.create(
            title="Test Event",
            description="This is a test event.",
            date=timezone.now().replace(tzinfo=timezone.utc),  # виправлено
            created_at=timezone.now().replace(tzinfo=timezone.utc),  # виправлено
            location="Test Location",
            max_participants=100,
            organizer=self.admin_user,
        )

        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com',
        )

        self.participant = Participant.objects.create(
            user=self.user,
            event=self.event,
            is_confirmed=False,
        )

    def test_participant_list_display(self):
        url = reverse('admin:event_manager_participant_changelist')  # виправлено
        response = self.client.get(url)
        self.assertContains(response, self.participant.user.username)
        self.assertContains(response, self.participant.event.title)


class FeedbackAdminTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='password123',
            email='admin@example.com',
        )
        self.client.force_login(self.admin_user)

        self.event = Event.objects.create(
            title="Test Event",
            description="This is a test event.",
            date=timezone.now().replace(tzinfo=timezone.utc),  # виправлено
            created_at=timezone.now().replace(tzinfo=timezone.utc),  # виправлено
            location="Test Location",
            max_participants=100,
            organizer=self.admin_user,
        )

        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com',
        )

        self.feedback = Feedback.objects.create(
            user=self.user,
            event=self.event,
            rating=5,
            comment="Great event!",
        )

    def test_feedback_list_display(self):
        url = reverse('admin:event_manager_feedback_changelist')  # виправлено
        response = self.client.get(url)
        self.assertContains(response, self.feedback.user.username)
        self.assertContains(response, self.feedback.event.title)
        self.assertContains(response, self.feedback.comment)
