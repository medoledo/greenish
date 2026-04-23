from django.contrib import admin
from django.utils.html import format_html
from .models import Session, Slide, Participant, Badge, ActivityResult, AnonymousPost


class SlideInline(admin.TabularInline):
    model = Slide
    extra = 1
    fields = ['order', 'slide_type', 'title', 'activity_type', 'is_active']
    ordering = ['order']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'facilitator_name', 'status', 'current_slide_index', 'created_at']
    list_filter = ['status']
    search_fields = ['code', 'title']
    readonly_fields = ['code', 'created_at']
    inlines = [SlideInline]


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slide_type', 'activity_type', 'is_active', 'order']
    list_filter = ['slide_type', 'activity_type']
    list_editable = ['order']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'trigger_type', 'trigger_value']
    list_filter = ['trigger_type']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['name', 'avatar', 'session', 'total_points', 'streak', 'joined_at']
    list_filter = ['session']


@admin.register(ActivityResult)
class ActivityResultAdmin(admin.ModelAdmin):
    list_display = ['participant', 'activity_type', 'is_correct', 'points_earned', 'submitted_at']
    list_filter = ['activity_type', 'is_correct']


@admin.register(AnonymousPost)
class AnonymousPostAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'session', 'is_public', 'created_at']
    list_filter = ['is_public']