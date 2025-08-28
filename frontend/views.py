from django.shortcuts import render, redirect
from django.conf import settings
import pandas as pd
import random

# Create your views here.

csv = pd.read_csv('./frontend/static/assets/countries.csv')
countries = csv.to_dict(orient='records')

def index(request):
    return render(request, 'index.html', context={'countries': countries })

def search_countries(request):
    query = request.GET.get("search_countries", "")
    print(query)
    if query:
        filtered_countries = [country for country in countries if country['Country'].lower().startswith(query.strip().lower())]
    else:
        filtered_countries = countries

    return render(request, "list.html", context={'countries': filtered_countries })

def quiz(request):
    if request.method == "GET":
        random_country = random.choice(countries)
        print(f"New random country: {random_country['Country']}")
        streak = 0
        return render(request, 'quiz.html', context={'random_country': random_country, 'streak': streak })

    elif request.method == "POST":
        truth = request.POST.get('truth')
        guess = request.POST.get('guess')
        streak = int(request.POST.get('streak'))

        print(f"Seeing if {guess} is the same as {truth}...")
        print(f"Streak: {streak}")

        if truth.lower() == guess.strip().lower():
            streak += 1
            message = f"You're correct! The answer was {truth}!"
            print(f"User is correct! Streak is now {streak}")
        
        else:
            streak = 0
            message = f"Sadly that is incorrect... 😢 the answer was {truth}"

        random_country = random.choice(countries)
        print(f"New random country: {random_country['Country']}")

        return render(request, 'quiz.html', context={'random_country': random_country, 'streak': streak, 'message': message })
    
    else:
        streak = 0
        return render(request, 'quiz.html', context={'random_country': random_country, 'streak': streak, 'message': message })


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def settings(request):
    return render(request, 'settings.html')