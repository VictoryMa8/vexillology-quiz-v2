from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.text import slugify
import csv
import random
import time
import ast
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
        collected_flags = []
        return render(request, 'quiz.html', context={'countries': countries, 'random_country': random_country, 'streak': streak, 'collected_flags': collected_flags })

    elif request.method == "POST":
        # ast.literal_eval() allows us to turn the string into a dictionary (of the country)
        truth = ast.literal_eval(request.POST.get('truth'))
        collected_flags = ast.literal_eval(request.POST.get('collected_flags'))
        guess = request.POST.get('guess')
        streak = int(request.POST.get('streak'))

        truth_name = truth['Country']
        truth_flag = truth['Flag']

        if truth_name.lower() == guess.strip().lower():
            streak += 1
            if collected_flags:
                collected_flags.append(truth_flag)
            else:
                collected_flags = [truth_flag]
            message = f"Correct 🥳 It was {truth_name}!"
            print(f"User is correct! Streak is now {streak}")
        
        else:
            streak = 0
            collected_flags = []
            message = f"Noooo 😢 it was {truth_name}"

        random_country = random.choice(countries)
        print(f"New random country: {random_country['Country']}")

        return render(request, 'quiz.html', context={'countries': countries, 'random_country': random_country, 'streak': streak, 'message': message, 'collected_flags': collected_flags })
    
    else:
        streak = 0
        return render(request, 'quiz.html', context={'countries': countries, 'random_country': random_country, 'streak': streak, 'message': message })


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def settings(request):
    return render(request, 'settings.html')