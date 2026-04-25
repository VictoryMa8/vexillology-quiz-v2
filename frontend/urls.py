from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path("search_countries/", views.search_countries, name="search_countries"),
    path("search_guesses/", views.search_guesses, name="search_guesses"),
    path("country/<slug:country_name>/", views.country, name="country"),
    path("quiz/", views.quiz, name="quiz"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy, name="privacy"),
    path("contact/", views.contact, name="contact"),
    path("settings/", views.settings, name="settings"),
    path("settings/delete_account/", views.delete_account, name="delete_account"),
    path("settings/resend_confirmation/", views.resend_confirmation, name="resend_confirmation"),
]