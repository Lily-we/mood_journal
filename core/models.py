from django.contrib.auth.models import User
from django.db import models

class MoodEntry(models.Model):
    MOODS = [
        (1, "Very bad / Depressed"),
        (2, "Bad / Frustrated"),
        (3, "Okay / Neutral"),
        (4, "Good / Energetic"),
        (5, "Great / Happy")
    ]
    mood = models.IntegerField(choices=MOODS)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    generated_tip = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"Mood {self.mood} on {self.created_at.date()}"



class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.ImageField(upload_to="covers/")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
    

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    mood = models.IntegerField(choices=[(1,'Sad'),(2,'Neutral'),(3,'Happy')])



