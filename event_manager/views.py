from datetime import timedelta
from xmlrpc.client import ResponseError

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Avg
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import generic
from django.contrib import messages
from django.contrib.auth import login
from event_manager.forms import (EventForm,
                                 EventCreateForm,
                                 EventSearchForm,
                                 UserSearchForm,
                                 CustomUserCreationForm,
                                 FeedbackForm,
                                 ParticipantForm,
                                 )
from event_manager.models import Event, User, Participant


@login_required
def index(request: HttpRequest) -> HttpResponse:
    num_events = Event.objects.count()
    num_organizers = Event.objects.count()
    num_users = User.objects.count()
    context = {
        "num_events": num_events,
        "num_organizers": num_organizers,
        "num_users": num_users,
    }
    return render(request, "event_manager/index.html", context=context)

@login_required
def add_feedback(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Перевірка, чи дозволено залишати фідбек
    if now() < event.date + timedelta(hours=24):
        messages.error(request, "Feedback can only be submitted 24 hours after the event starts.")
        return redirect('event_manager:event-detail', pk=event.pk)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.event = event
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Your feedback has been submitted.")
        else:
            messages.error(request, "There was an error submitting your feedback.")
    return redirect('event_manager:event-detail', pk=event.pk)

@login_required
def participate_in_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # Перевірка, чи досягнута максимальна кількість учасників
    if event.participants.count() >= event.max_participants:
        messages.error(request, "This event has reached its maximum number of participants.")
        return redirect('event_manager:event-detail', pk=event.pk)

    # Додаємо учасника до події
    if request.method == 'POST':
        Participant.objects.get_or_create(user=request.user, event=event)
        messages.success(request, "You have successfully joined the event.")
    return redirect('event_manager:event-detail', pk=event.pk)

def registration(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect("event_manager:event-list")
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


class UserListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "event_manager/user_list.html"
    context_object_name = "users"
    paginate_by = 2

    def get_queryset(self):
        queryset = User.objects.annotate(
            event_count=Count("organized_events"),
            average_rating=Avg("organized_events__feedbacks__rating")
        ).order_by("-event_count")

        search_query = self.request.GET.get("username", "")
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = UserSearchForm(self.request.GET)
        for user in context[self.context_object_name]:
            user.rating = user.average_rating if user.average_rating else 0
        return context


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    context_object_name = "user"


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    fields = ["first_name", "last_name", ]
    success_url = reverse_lazy("user-profile")

    def get_object(self, queryset=None):
        obj = super(UserUpdateView, self).get_object(queryset)
        if obj != self.request.user:
            raise PermissionDenied("Cannot edit another user's information.")
        return obj

    def get_success_url(self):
        return f'/user/{self.request.user.pk}/detail/'  # Redirect to user detail page after successful update


class EventListView(LoginRequiredMixin, generic.ListView):
    model = Event
    template_name = "event_manager/event_list.html"
    context_object_name = "event_list"
    paginate_by = 1

    def get_queryset(self):
        queryset = (super().get_queryset().
                    select_related("organizer").
                    prefetch_related("feedbacks"))
        form = EventSearchForm(self.request.GET)
        if form.is_valid():
            title = form.cleaned_data.get("title")
            if title:
                queryset = queryset.filter(title__icontains=title)
        return queryset

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context["search_form"] = EventSearchForm(self.request.GET)
        for event in context[self.context_object_name]:
            event.rating = event.get_rating()
        return context


class EventDetailView(LoginRequiredMixin, generic.DetailView):
    model = Event
    context_object_name = "event"

    def get_queryset(self):
        return super().get_queryset().select_related("organizer")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedback_form'] = FeedbackForm()
        context['participant_form'] = ParticipantForm()
        context['participants'] = self.object.participants.all()
        return context


class EventCreateView(LoginRequiredMixin, generic.CreateView):
    model = Event
    form_class = EventCreateForm
    success_url = reverse_lazy("event_manager:event-list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_organizer:
            raise PermissionDenied("Only organizers can create events.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Event
    form_class = EventForm

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if event.organizer != self.request.user:
            raise PermissionDenied("You are not allowed to edit this event.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Event
    success_url = reverse_lazy("event_manager:event-list")

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if (event.organizer != self.request.user
                and not self.request.user.is_staff):
            raise PermissionDenied("You are not allowed to delete this event.")
        return super().dispatch(request, *args, **kwargs)
