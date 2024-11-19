from django.urls import path

from .views import (index,
                    EventListView,
                    EventDetailView,
                    EventCreateView,
                    EventUpdateView,
                    EventDeleteView, UserListView,

                    )


urlpatterns = [
    path("", index, name="index"),
    path("users/", UserListView.as_view(), name="user-list"),
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
    )
]

app_name = "event-manager"
