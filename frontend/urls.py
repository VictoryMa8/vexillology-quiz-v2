from django.urls import path, include
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("search_countries/", views.search_countries, name="search_countries"),
    path("search_guesses/", views.search_guesses, name="search_guesses"),
    path("country/<slug:country_name>/", views.country, name="country"),
    path("quiz/", views.quiz, name="quiz"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("settings/", views.settings, name="settings")
]