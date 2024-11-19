
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Avg
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from event_manager.forms import EventForm, EventCreateForm, EventSearchForm, UserSearchForm
from event_manager.models import Event, User


@login_required
def index(request: HttpRequest) -> HttpResponse:
    num_events = Event.objects.count()
    num_organizers = Event.objects.filter(organizer=request.user).count()
    num_users = User.objects.count()
    context = {
        "num_events": num_events,
        "num_organizers": num_organizers,
        "num_users": num_users,
    }
    return render(request, "event_manager/index.html", context=context)


class UserListView(LoginRequiredMixin ,generic.ListView):
    model = User
    template_name = "event_manager/user_list.html"
    context_object_name = "users"
    paginate_by = 2

    def get_queryset(self):
        queryset = User.objects.annotate(
            event_count=Count('organized_events'),
            average_rating=Avg('organized_events__feedbacks__rating')
        ).order_by('-event_count')

        search_query = self.request.GET.get('username', '')
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = UserSearchForm(self.request.GET)
        for user in context[self.context_object_name]:
            user.rating = user.average_rating if user.average_rating else 0
        return context

class EventListView(LoginRequiredMixin, generic.ListView):
    model = Event
    template_name = "event_manager/event_list.html"
    context_object_name = "event_list"
    paginate_by = 1
    def get_queryset(self):
        queryset = super().get_queryset().select_related("organizer").prefetch_related('feedbacks')
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
        return super().get_queryset().select_related('organizer')


class EventCreateView(LoginRequiredMixin, generic.CreateView):
    model = Event
    form_class = EventCreateForm
    success_url = reverse_lazy("event_manager:event-list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_organizer:
            raise PermissionDenied("Only organizers can create events.")  # Використовуйте raise замість return
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
        form.instance.organizer = self.request.user  # Переконаємося, що організатор не зміниться
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Event
    success_url = reverse_lazy("event_manager:event-list")

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if event.organizer != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You are not allowed to delete this event.")
        return super().dispatch(request, *args, **kwargs)