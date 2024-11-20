from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import DateTimeInput
from django.contrib.auth import get_user_model
from event_manager.models import User, Event, Feedback, Participant


class EventSearchForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by title event..."}
        )
    )


class UserSearchForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by username..."}
        )
    )


class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title',
                  'description',
                  'date',
                  'location',
                  'max_participants']
        widgets = {
            'date': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 10, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = []

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title',
                  'description',
                  'date',
                  'location',
                  'max_participants']
        widgets = {
            'date': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organizer'] = forms.ModelChoiceField(
            queryset=User.objects.none(),
            required=False,
            widget=forms.HiddenInput()
        )



class CustomUserCreationForm(UserCreationForm):
    User = get_user_model()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']