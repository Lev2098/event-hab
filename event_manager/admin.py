from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (User,
                     Event,
                     Participant,
                     Feedback)


@admin.action(description='Make selected users organizers')
def make_organizer(modeladmin, request, queryset):
    queryset.update(is_organizer=True)


@admin.action(description='Remove organizer status from selected users')
def remove_organizer(modeladmin, request, queryset):
    queryset.update(is_organizer=False)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_organizer', 'is_staff', )
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("is_organizer",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "is_organizer",
                    )
                },
            ),
        )
    )
    list_filter = ('is_organizer', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    actions = [make_organizer, remove_organizer]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'description',
                    'date',
                    'created_at',
                    'location',
                    'max_participants',
                    'organizer')
    list_filter = ('date', 'created_at', 'location')
    search_fields = ('title', 'description', 'location')
    ordering = ('-date',)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'is_confirmed')
    list_filter = ('is_confirmed', 'event')
    search_fields = ('user__username', 'event__title')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'rating', 'comment')
    list_filter = ('rating', 'event')
    search_fields = ('user__username', 'event__title', 'comment')
