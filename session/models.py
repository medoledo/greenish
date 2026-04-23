import string
import random
from django.db import models
from django.utils import timezone


def generate_session_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Session.objects.filter(code=code).exists():
            return code


class Session(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('active', 'Active'),
        ('ended', 'Ended'),
    ]
    code = models.CharField(max_length=6, unique=True, default=generate_session_code)
    title = models.CharField(max_length=255)
    facilitator_name = models.CharField(max_length=100, blank=True, default='')
    facilitator_password = models.CharField(max_length=128, blank=True, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    current_slide_index = models.PositiveIntegerField(default=0)
    activity_active = models.BooleanField(default=False)
    show_answers_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Slide(models.Model):
    SLIDE_TYPE_CHOICES = [
        ('info', 'Information'),
        ('activity', 'Activity'),
    ]
    ACTIVITY_TYPE_CHOICES = [
        ('sprint', '♻️ Waste Sorting Sprint'),
        ('decompose', '⏳ Decomposition Race'),
        ('quiz', '🌍 Plastic vs Planet Quiz'),
        ('commitment', '💚 Green Commitment'),
        ('sort_stats', '📊 Sort the Stats'),
    ]
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='slides')
    order = models.PositiveIntegerField(default=0)
    slide_type = models.CharField(max_length=10, choices=SLIDE_TYPE_CHOICES, default='info')
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='slides/', blank=True, null=True)
    activity_type = models.CharField(max_length=15, choices=ACTIVITY_TYPE_CHOICES, blank=True, null=True)
    activity_config = models.JSONField(blank=True, null=True)
    shocking_fact = models.BooleanField(default=False)
    time_hint = models.PositiveIntegerField(blank=True, null=True, help_text='Seconds to display')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Slide {self.order}: {self.title or self.slide_type}"


class Badge(models.Model):
    TRIGGER_TYPE_CHOICES = [
        ('points', 'Points Threshold'),
        ('streak', 'Streak Threshold'),
        ('activity', 'Activity Completion'),
        ('count', 'Answer Count'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10)
    trigger_type = models.CharField(max_length=10, choices=TRIGGER_TYPE_CHOICES)
    trigger_value = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['name', 'trigger_type', 'trigger_value']

    def __str__(self):
        return f"{self.icon} {self.name}"


class Participant(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True, default='')
    avatar = models.CharField(max_length=10, default='🌱')
    total_points = models.PositiveIntegerField(default=0)
    streak = models.PositiveIntegerField(default=0)
    max_streak = models.PositiveIntegerField(default=0)
    badges = models.ManyToManyField(Badge, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'name']
        indexes = [
            models.Index(fields=['session', '-total_points']),
        ]

    def __str__(self):
        return f"{self.avatar} {self.name} ({self.total_points}pts)"


class ActivityResult(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='results')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='results')
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE, related_name='results')
    activity_type = models.CharField(max_length=15)
    answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['session', 'slide']),
            models.Index(fields=['session', '-submitted_at']),
        ]

    def __str__(self):
        return f"{self.participant.name}: {self.activity_type} ({self.points_earned}pts)"


class AnonymousPost(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='posts')
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', 'slide', 'is_public', '-created_at']),
        ]

    def __str__(self):
        return f"Post: {self.content[:50]}"