from django.contrib.auth.models import User
from django.db import models

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        (1, 'Very bad'),
        (2, 'Bad'),
        (3, 'Okay'),
        (4, 'Good'),
        (5, 'Great'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # add this
    mood = models.IntegerField(choices=MOOD_CHOICES)
    note = models.TextField(blank=True)
    generated_tip = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mood {self.mood} on {self.created_at.date()}"

    def __str__(self):
        return f"Mood {self.mood} on {self.created_at.date()}"

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.ImageField(upload_to="covers/")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


