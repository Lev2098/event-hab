from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.urls import reverse


class User(AbstractUser):
    """
    Ви можете розширити вбудовану Django модель користувачів
    """
    email = models.EmailField(unique=True)
    is_organizer = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["username"]


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    max_participants = models.IntegerField()
    organizer = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name="organized_events")

    def get_rating(self):
        result = self.feedbacks.aggregate(average_rating=Avg('rating'))
        return result['average_rating'] or 0

    def get_absolute_url(self):
        return reverse("event_manager:event-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["date"]


class Participant(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="participations"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="participants"
    )
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class Feedback(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(10)]
    )
    comment = models.TextField()

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.event.title}"
