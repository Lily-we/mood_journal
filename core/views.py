from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from .models import MoodEntry, Book
from django.contrib.auth.decorators import login_required
from .forms import MoodEntryForm
from django.core.serializers import serialize
import json



# ------------------- Static Pages -------------------
@login_required
def home(request):
    return render(request, "core/home.html")

def landing(request):
    return render(request, "core/landing.html")


# ------------------- Profile -------------------
@login_required
def profile(request):
    mood_entries_qs = MoodEntry.objects.filter(user=request.user).order_by('created_at')

    # Prepare data for Chart.js
    mood_entries_chart = [
        {
            "date": entry.created_at.strftime("%Y-%m-%d"),
            "mood": entry.mood
        } for entry in mood_entries_qs
    ]

    context = {
        "mood_entries_qs": mood_entries_qs,
        "mood_entries": json.dumps(mood_entries_chart) 
    }
    return render(request, "core/profile.html", context)

# ------------------- Mood Recommend Help Line -------------------
from django.shortcuts import render

# Mood database
mood_db = {
    "happy": {
        "songs": ["Happy - Pharrell Williams", "Walking on Sunshine - Katrina & The Waves"],
        "stories": ["A Day at the Beach", "Finding Joy in Small Things"]
    },
    "sad": {
        "songs": ["Fix You - Coldplay", "Someone Like You - Adele"],
        "stories": ["Overcoming Loss", "A Rainy Day Adventure"]
    },
    "angry": {
        "songs": ["Weight of the World - Earth, Wind & Fire", "Let It Be - The Beatles"],
        "stories": ["Meditation Journey", "Calming the Storm Within"]
    },
    "anxious": {
        "songs": ["Weightless - Marconi Union", "Breathe Me - Sia"],
        "stories": ["Mindfulness Exercises", "A Peaceful Forest Walk"]
    }
}

def mood_recommendation(request):
    recommendation = None
    if request.method == "POST":
        mood = request.POST.get("mood", "").lower()
        if mood in mood_db:
            recommendation = mood_db[mood]
    return render(request, "core/mood.html", {"recommendation": recommendation})


# ------------------- Mood Tracker -------------------
@login_required
def submit_mood(request):
    if request.method == "POST":
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            mood_entry = form.save(commit=False)
            mood_entry.user = request.user
            mood_entry.save()
            return redirect('thank_you')  # now goes to the thank you page
    else:
        form = MoodEntryForm()
    return render(request, "core/submit_mood.html", {"form": form})


from django.shortcuts import render, redirect, get_object_or_404
from .models import MoodEntry

# Mood DB for recommendations (expanded)
mood_db = {
    "Very bad / Depressed": {
        "songs": ["Fix You - Coldplay", "Someone Like You - Adele"],
        "stories": ["Overcoming Loss", "A Rainy Day Adventure"]
    },
    "Bad / Frustrated": {
        "songs": ["Let It Be - The Beatles", "Weight of the World - Earth, Wind & Fire"],
        "stories": ["Meditation Journey", "Calming the Storm Within"]
    },
    "Okay / Neutral": {
        "songs": ["Here Comes the Sun - Beatles", "Count on Me - Bruno Mars"],
        "stories": ["A Small Triumph", "An Unexpected Friend"]
    },
    "Good / Energetic": {
        "songs": ["Walking on Sunshine - Katrina & The Waves", "Happy - Pharrell Williams"],
        "stories": ["A Day at the Park", "Finding Joy in Small Things"]
    },
    "Great / Happy": {
        "songs": ["Best Day of My Life - American Authors", "Uptown Funk - Bruno Mars"],
        "stories": ["Celebrating Success", "A Fun Adventure"]
    }
}

# Submit mood view
def submit_mood(request):
    if request.method == "POST":
        mood_value = int(request.POST.get("mood", 50))
        note = request.POST.get("note", "")

        # Map 0-100 slider to 1-5 mood scale
        if mood_value <= 20:
            mood = 1  # Very bad / Depressed
        elif mood_value <= 40:
            mood = 2  # Bad / Frustrated
        elif mood_value <= 60:
            mood = 3  # Okay / Neutral
        elif mood_value <= 80:
            mood = 4  # Good / Energetic
        else:
            mood = 5  # Great / Happy

        entry = MoodEntry.objects.create(mood=mood, note=note)

        # Save the entry id to redirect with it
        return redirect(f"/thank-you/?entry_id={entry.id}")

    return render(request, "core/submit_mood.html")

# Thank-you page (already expanded with recommendation)
def thank_you(request):
    entry = None
    entry_id = request.GET.get("entry_id")
    if entry_id:
        entry = get_object_or_404(MoodEntry, pk=entry_id)

    mood_labels = {
        1: "Very bad / Depressed",
        2: "Bad / Frustrated",
        3: "Okay / Neutral",
        4: "Good / Energetic",
        5: "Great / Happy"
    }
    mood_colors = {
        1: "#ffb3b3",
        2: "#ffcc99",
        3: "#ffe6b3",
        4: "#c8f7dc",
        5: "#a8e6cf"
    }

    recommendation = None
    if entry:
        label = mood_labels.get(entry.mood)
        recommendation = mood_db.get(label)

    context = {
        "entry": entry,
        "mood_label": mood_labels.get(entry.mood) if entry else None,
        "bg_color": mood_colors.get(entry.mood) if entry else "#fff5d1",
        "recommendation": recommendation
    }
    return render(request, "core/thank_you.html", context)


@login_required
def analytics(request):
    entries = MoodEntry.objects.filter(user=request.user)  # only current user
    total_entries = entries.count()
    mood_count = entries.values('mood').annotate(count=Count('mood')).order_by('mood')
    average_mood = entries.aggregate(avg_mood=Avg('mood'))['avg_mood']

    mood_stats = {item['mood']: item['count'] for item in mood_count}

    daily_data = entries.annotate(date=TruncDate('created_at')) \
                        .values('date', 'mood') \
                        .annotate(count=Count('id')) \
                        .order_by('date')

    context = {
        "total_entries": total_entries,
        "mood_stats": mood_stats,
        "average_mood": round(average_mood, 2) if average_mood else None,
        "daily_data": list(daily_data),
    }
    return render(request, "core/analytics.html", context)


# ------------------- Authentication -------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = None

        if username:
            user = authenticate(request, username=username, password=password)
            if user:
                auth_login(request, user)
                return redirect("home")

        messages.error(request, "Invalid email or password")

    return render(request, "core/login.html")

def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, "core/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "core/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "core/signup.html")

        user = User.objects.create_user(username=username, email=email, password=password1)
        auth_login(request, user)
        return redirect("home")

    return render(request, "core/signup.html")

def logout_view(request):
    logout(request)
    return redirect("landing")
