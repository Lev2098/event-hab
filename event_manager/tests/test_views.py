from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from event_manager.models import Event


class EventManagerViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username='testuser', password='testpass123', email='testmailuser1@gmail.com')
        self.organizer = self.user_model.objects.create_user(username='organizer', password='testpass123', email='testmailuser2@gmail.com',
                                                             is_organizer=True)
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            date="2023-12-31 23:59:59",
            location="Test Location",
            max_participants=100,
            organizer=self.organizer
        )

    def test_index_view(self):
        print(self.user)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('event_manager:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_manager/index.html')

    def test_event_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('event_manager:event-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_manager/event_list.html')

    def test_event_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('event_manager:event-detail', args=(self.event.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_manager/event_detail.html')

    def test_create_event_view(self):
        self.client.login(username='organizer', password='testpass123')
        response = self.client.get(reverse('event_manager:event-create'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('event_manager:event-create'), {
            'title': 'New Event',
            'description': 'Description for New Event',
            'date': '2023-12-31 23:59:59',
            'location': 'New Location',
            'max_participants': 150,
            'organizer': self.organizer.id,
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_update_event_view(self):
        self.client.login(username='organizer', password='testpass123')
        url = reverse('event_manager:event-update', args=(self.event.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'title': 'Updated Event',
            'description': 'Updated Description for Event',
            'date': '2023-12-31 23:59:59',
            'location': 'Updated Location',
            'max_participants': 200,
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_user_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('event_manager:user-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_manager/user_list.html')
