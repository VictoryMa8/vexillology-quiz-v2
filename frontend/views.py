from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.text import slugify
import csv
import random
import time
import os

# Create your views here.

with open(os.path.join(settings.BASE_DIR, 'frontend', 'static', 'assets', 'countries.csv'), 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    countries = list(reader)

def index(request):
    return render(request, 'index.html', context={'countries': countries })

def search_countries(request):
    query = request.GET.get("search_countries", "")
    print(query)
    if query:
        # List of countries where the country name starts with the stripped and lowercased query
        filtered_countries = [country for country in countries if country['Country'].lower().startswith(query.strip().lower())]
    else:
        filtered_countries = countries
    time.sleep(0.1)
    return render(request, "list.html", context={'countries': filtered_countries })

def search_guesses(request):
    query = request.GET.get("guess", "")
    print(query)
    if query:
        # List of countries where the country name starts with the stripped and lowercased query
        filtered_countries = [country for country in countries if country['Country'].lower().startswith(query.strip().lower())]
    else:
        filtered_countries = countries
    time.sleep(0.1)
    return render(request, "guesses.html", context={'countries': filtered_countries })

def country(request, country_name):
    # Slugify makes it a cleaner string
    chosen_country = [country for country in countries if slugify(country['Country']) == country_name]
    if chosen_country:
        print(chosen_country[0])
        return render(request, 'country.html', context={'chosen_country': chosen_country[0]})
    else:
        return redirect("/")

def quiz(request):
    if request.method == "GET":
        random_country = random.choice(countries)
        print(f"New random country: {random_country['Country']}")
        streak = 0
        return render(request, 'quiz.html', context={'countries': countries, 'random_country': random_country, 'streak': streak })

    elif request.method == "POST":
        truth = request.POST.get('truth')
        guess = request.POST.get('guess')
        streak = int(request.POST.get('streak'))

        print(f"Seeing if {guess} is the same as {truth}...")
        print(f"Streak: {streak}")

        if truth.lower() == guess.strip().lower():
            streak += 1
            message = f"Correct 🥳 It was {truth}!"
            print(f"User is correct! Streak is now {streak}")
        
        else:
            streak = 0
            message = f"Noooo 😢 it was {truth}"

        random_country = random.choice(countries)
        print(f"New random country: {random_country['Country']}")

        return render(request, 'quiz.html', context={'countries': countries, 'random_country': random_country, 'streak': streak, 'message': message })
    
    else:
        streak = 0
        return render(request, 'quiz.html', context={'countries': countries, 'random_country': random_country, 'streak': streak, 'message': message })


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def settings(request):
    return render(request, 'settings.html')