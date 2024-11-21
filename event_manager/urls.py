from django.urls import path

from .views import (index,
                    EventListView,
                    EventDetailView,
                    EventCreateView,
                    EventUpdateView,
                    EventDeleteView,
                    UserListView,
                    registration,
                    UserDetailView,
                    UserUpdateView,
                    add_feedback,
                    participate_in_event,
                    )


urlpatterns = [
    path("", index, name="index"),

    path("users/", UserListView.as_view(), name="user-list"),
    path("user/<int:pk>/detail/", UserDetailView.as_view(), name="user-detail"),
    path('user/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),

    path('event/<int:pk>/feedback/', add_feedback, name='add-feedback'),
    path('event/<int:pk>/participate/', participate_in_event, name='participate-in-event'),
    path("events/", EventListView.as_view(), name="event-list"),
    path("event/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path(
        "event/create/",
        EventCreateView.as_view(),
        name="event-create"
    ),
    path(
        "event/<int:pk>/update/",
        EventUpdateView.as_view(),
        name="event-update"
    ),
    path(
        "event/<int:pk>/delete/",
        EventDeleteView.as_view(),
        name="event-delete"
    ),

    path("registration/", registration, name="registration"),
]

app_name = "event-manager"
