from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.landing, name="landing"),   
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path("home/", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("analytics/", views.analytics, name="analytics"),
    path("submit/", views.submit_mood, name="submit_mood"),
    path("thank-you/", views.thank_you, name="thank_you"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
