from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login

from .forms import LoginForm, VexillologistCreationForm, VexillologistChangeForm
from .models import Country
import csv
import random
import time
import ast
import os

# Create your views here.
# Users who are not logged in can only access index, signup, and login

def get_countries():
    # Providing the exact dictionary structure as the original CSV (just a text list of countries) to minimize app changes
    return [
        {
            'Country': c.name,
            'Flag': c.flag_emoji,
            'flag_image_url': c.flag_image_url,
            'Capital': c.capital,
            'Population_2024': c.population,
            'GDP_USD_Billions': float(c.gdp_usd_billions) if c.gdp_usd_billions is not None else None,
            'Area_km2': c.area_km2,
            'Official_Language': c.official_language,
            'Region': c.region,
        }
        for c in Country.objects.all().order_by('name')
    ]

def index(request):
    countries = get_countries()
    return render(request, 'index.html', context={'countries': countries })

def signup(request):
    # On the sign up page, get the form with post
    if request.method == 'POST':
        form = VexillologistCreationForm(request.POST)
        if form.is_valid():
            # Put user info into database, login user, and redirect to index
            user = form.save()
            auth_login(request, user)
            return redirect('index')
    else:
        form = VexillologistCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            auth_login(request, form.user)
            return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def search_countries(request):
    countries = get_countries()
    query = request.GET.get("search_countries", "")
    print(query)
    if query:
        # List of countries where the country name starts with the stripped and lowercased query
        filtered_countries = [country for country in countries if country['Country'].lower().startswith(query.strip().lower())]
    else:
        filtered_countries = countries
    time.sleep(0.075)
    return render(request, "list.html", context={'countries': filtered_countries })

@login_required
def search_guesses(request):
    countries = get_countries()
    query = request.GET.get("guess", "")
    print(query)
    if query:
        # List of countries where the country name starts with the stripped and lowercased query
        filtered_countries = [country for country in countries if country['Country'].lower().startswith(query.strip().lower())]
    else:
        filtered_countries = countries
    return render(request, "guesses.html", context={'countries': filtered_countries })

@login_required
def country(request, country_name):
    countries = get_countries()
    # Slugify makes it a cleaner string
    chosen_country = [country for country in countries if slugify(country['Country']) == country_name]
    if chosen_country:
        print(chosen_country[0])
        return render(request, 'country.html', context={'chosen_country': chosen_country[0]})
    else:
        return redirect("/")

@login_required
def quiz(request):
    countries = get_countries()
    message = ""
    if request.method == "GET":
        random_country = random.choice(countries) if countries else None
        print(f"New random country: {random_country['Country'] if random_country else 'None'}")
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
        truth_flag = truth.get('flag_image_url') or truth['Flag']

        if truth_name.lower() == guess.strip().lower():
            streak += 1
            if collected_flags:
                collected_flags.append(truth_flag)
            else:
                collected_flags = [truth_flag]
            
            # Slight performance benefit with update_fields
            user = request.user
            if streak > user.high_score:
                user.high_score = streak
                user.save(update_fields=['high_score'])
                
            messages.success(request, f"Correct 🥳 It was {truth_name}!")
            message = f"Correct 🥳 It was {truth_name}!"
            print(f"User is correct! Streak is now {streak}")
        
        else:
            streak = 0
            collected_flags = []
            message = f"Noooo 😢 it was {truth_name}"

        random_country = random.choice(countries) if countries else None

        return render(request, 'quiz.html', context={'countries': countries, 'random_country': random_country, 'streak': streak, 'message': message, 'collected_flags': collected_flags })
    
    else:
        streak = 0
        random_country = random.choice(countries) if countries else None
        return render(request, 'quiz.html', context={'countries': countries, 'random_country': random_country, 'streak': streak, 'message': message })
    
def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

@login_required
def settings(request):
    if request.method == 'POST':
        # 'instance' parameter tells the Django form which record to update
        # Necessary since we are updating (current logged-in user) rather than creating
        form = VexillologistChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Using Django messages for success message
            messages.success(request, 'Your settings have been saved!')
            return redirect('settings')
    else:
        form = VexillologistChangeForm(instance=request.user)
    return render(request, 'settings.html', {'form': form})