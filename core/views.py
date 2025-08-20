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



# ------------------- Static Pages -------------------
@login_required
def home(request):
    return render(request, "core/home.html")

def landing(request):
    return render(request, "core/landing.html")

@login_required
def profile(request):
    return render(request, "core/profile.html")


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


def thank_you(request):
    entry = None
    entry_id = request.GET.get("entry_id")
    if entry_id:
        entry = get_object_or_404(MoodEntry, pk=entry_id)

    mood_labels = {1: "Very bad", 2: "Bad", 3: "Okay", 4: "Good", 5: "Great"}
    mood_colors = {1: "#ffb3b3", 2: "#ffcc99", 3: "#ffe6b3", 4: "#c8f7dc", 5: "#a8e6cf"}

    context = {
        "entry": entry,
        "mood_label": mood_labels.get(entry.mood) if entry else None,
        "bg_color": mood_colors.get(entry.mood) if entry else "#fff5d1",
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
