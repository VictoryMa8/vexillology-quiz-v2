from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.db.models import F
from django.core.cache import cache
# Named django_settings to avoid conflict with settings.py (my view)
from django.conf import settings as django_settings

from allauth.account.models import EmailAddress

from .forms import LoginForm, VexillologistCreationForm, VexillologistChangeForm
from .models import Country, Vexillologist
import random
import time
import requests

# Create your views here.
# Users who are not logged in can only access index, signup, and login

"""
The key used to store the country list in the cache

The :v1 suffix is a versioning trick; if we ever change the shape of the
dictionaries below (add a key, rename one), we bump this to :v2 and all
old cached values simply age out on their own
"""
COUNTRIES_CACHE_KEY = 'countries:v1'

"""
How long (in seconds) to keep the cached list before Django discards it and
re-queries the database

The post_save/post_delete signals in models.py will also clear the cache immediately 
whenever an admin edits a Country record
"""
COUNTRIES_CACHE_TTL = 60 * 60  # 1 hour

def get_countries():
    """
    1. Try the cache first
    
    cache.get() returns None on a cache miss
    
    On a hit it returns the previously stored list from RAM, no database round-trip
    """
    cached = cache.get(COUNTRIES_CACHE_KEY)
    if cached is not None:
        return cached

    """
    2. Cache miss: query the database and build the list of dicts
    
    Original code path, now only reached on the very first
    request (or after the cache expires / is invalidated by a signal)
    """
    result = [
        {
            'Country': c.name,
            'Flag': c.flag_emoji,
            'flag_image_url': c.flag_image_url,
            'Capital': c.capital,
            'Population_2024': c.population,
            'Area_km2': c.area_km2,
            'Official_Language': c.official_language,
            'Region': c.region,
            'Type': c.entry_type,
            'Fact': c.fact,
        }
        for c in Country.objects.all().order_by('name')
    ]

    """
    3. Store the result in the cache so every subsequent call within the
    TTL window returns the in-memory copy instead of hitting the DB
    """
    cache.set(COUNTRIES_CACHE_KEY, result, COUNTRIES_CACHE_TTL)
    return result

def index(request):
    countries = get_countries()
    return render(request, 'index.html', context={'countries': countries })

def signup(request):
    # On the sign up page, get the form with post
    if request.method == 'POST':
        token = request.POST.get('g-recaptcha-response', '')
        # Verify with Google
        # Use requests library to send a POST request to the Google Recaptcha API
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': django_settings.RECAPTCHA_SECRET_KEY,
            'response': token,
        })
        # If the CAPTCHA is not successful, show an error message and render the signup page again
        if not resp.json().get('success'):
            messages.error(request, 'Please complete the CAPTCHA.')
            return render(request, 'signup.html', {
                'form': VexillologistCreationForm(),
                'recaptcha_site_key': django_settings.RECAPTCHA_SITE_KEY,
            })

        # If the CAPTCHA is successful, process the form
        form = VexillologistCreationForm(request.POST)
        # If the form is valid, save the user and login the user
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # EmailAddress is from allauth.account.models for storing email addresses for users
            # create() creates a new email address record in the database
            email_address = EmailAddress.objects.create(
                user=user, email=user.email, primary=True, verified=False
            )
            # send_confirmation() generates the confirmation token and fires the email
            # signup=True tells allauth to use the signup-specific email template
            email_address.send_confirmation(request, signup=True)
            return redirect('index')
    else:
        form = VexillologistCreationForm()

    return render(request, 'signup.html', {
        'form': form,
        'recaptcha_site_key': django_settings.RECAPTCHA_SITE_KEY,
    })

def login_view(request):
    if request.method == 'POST':
        # request.META contains all the metadata of the HTTP request (the HTTP headers) that is coming to our Django server, it can contain the user agent, ip address, content type, and so on.
        
        # REMOTE_ADDR is the key for the connecting IP address, we use it to identify who is making the request
        # Otherwise unknown
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f'login_attempts_{ip}'
        attempts = cache.get(cache_key, 0)

        if attempts >= 5:
            messages.error(request, 'Too many login attempts. Please wait a minute and try again.')
            return render(request, 'login.html', {'form': LoginForm()})

        form = LoginForm(request.POST)
        # If the form is valid, delete the cache key and login the user
        if form.is_valid():
            cache.delete(cache_key)
            auth_login(request, form.user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('index')
        else:
            # Set the cache key to the number of attempts + 1, and the timeout to 60 seconds
            cache.set(cache_key, attempts + 1, 60)
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

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
    """
    Reworked to use session data instead of hidden form fields
    
    Hidden form fields are vulnerable to tampering (a player could edit the streak value in DevTools)
    
    Session data is stored server-side so only the server can modify it

    request.session is a dictionary-like object. We set keys on it just like a regular dict. 
    
    Django automatically saves it and associates it with this user's session ID cookie
    """
    if request.method == "GET":
        """
        After a POST guess, the POST handler redirects here and leaves a 'quiz_result' key in the session with the outcome of that guess
        
        pop() reads it and immediately removes it so a second refresh won't re-display it 
        (it's consumed exactly once, like a flash message)
        """
        result = request.session.pop('quiz_result', None)

        if result:
            # Continuing an in-progress game after a guess redirect.
            # The POST already chose the next country and wrote it to the session,
            # so we don't need to touch get_countries() at all here.
            random_country = request.session.get('quiz_country')
            streak = request.session.get('quiz_streak', 0)
            collected_flags = request.session.get('quiz_collected_flags', [])
            return render(request, 'quiz.html', context={
                'random_country': random_country,
                'streak': streak,
                'collected_flags': collected_flags,
                'game_over': result['game_over'],
                'final_streak': result['final_streak'],
                'final_collected_flags': result['final_collected_flags'],
                'truth_name': result['truth_name'],
                'truth_flag': result['truth_flag'],
            })

        # Fresh page load — reset all game state.
        countries = get_countries()
        random_country = random.choice(countries) if countries else None
        request.session['quiz_country'] = random_country
        request.session['quiz_streak'] = 0
        request.session['quiz_collected_flags'] = []
        request.session['quiz_collected_names'] = [] # Make sure user doesn't get the same country twice
        return render(request, 'quiz.html', context={
            'random_country': random_country,
            'streak': 0,
            'collected_flags': [],
        })

    elif request.method == "POST":
        """
        Read game state from the server-side session, not from POST data
        
        request.session.get(key, default) reads the value back from the
        server-side session that was stored on the previous GET/POST
        """
        truth = request.session.get('quiz_country')
        streak = request.session.get('quiz_streak', 0)
        collected_flags = request.session.get('quiz_collected_flags', [])
        collected_names = request.session.get('quiz_collected_names', [])

        if not truth:
            return redirect('quiz')

        guess = request.POST.get('guess', '').strip()
        truth_name = truth['Country']
        truth_flag = truth.get('flag_image_url') or truth['Flag']

        user = request.user
        
        update_fields = []

        game_over = False
        final_streak = 0
        final_collected_flags = []

        if truth_name.lower() == guess.lower():
            streak += 1
            collected_flags = collected_flags + [truth_flag]
            collected_names = collected_names + [truth_name]

            if streak > user.high_score:
                user.high_score = streak
                update_fields.append('high_score')

            messages.success(request, f"Correct 🥳 It was {truth_name}!")

        else:
            game_over = True
            final_streak = streak
            final_collected_flags = collected_flags[:]
            """
            # Permanently record every flag the player collected this game
            """
            if collected_names:
                mastered = Country.objects.filter(name__in=collected_names)
                # *mastered is a list unpacking operation, it unpacks the list mastered into 
                # the user.mastered_flags.add() method
                user.mastered_flags.add(*mastered)
            streak = 0
            collected_flags = []
            collected_names = []
            user.games_played = F('games_played') + 1
            update_fields.append('games_played')
            messages.error(request, f"Noooo 😢 it was {truth_name}")

        # Only hit the database if there is actually something to update
        if update_fields:
            user.save(update_fields=update_fields)

        """
        Pick the next country and write all game state back to the session
        
        Filter out countries already collected this game so the same flag never appears twice in a single streak
        
        If the player has somehow collected every country, fall back to the full list rather than crash
        """
        countries = get_countries()
        available = [c for c in countries if c['Country'] not in collected_names]
        if not available:
            available = countries
        random_country = random.choice(available)
        request.session['quiz_country'] = random_country
        request.session['quiz_streak'] = streak
        request.session['quiz_collected_flags'] = collected_flags
        request.session['quiz_collected_names'] = collected_names

        """
        Store the result context in the session and redirect to GET so a browser refresh doesnt resubmit the form
        
        Without this, hitting refresh after a wrong guess would reprocess the same POST and double count games_played
        """
        request.session['quiz_result'] = {
            'game_over': game_over,
            'final_streak': final_streak,
            'final_collected_flags': final_collected_flags,
            'truth_name': truth_name,
            'truth_flag': truth_flag,
        }
        return redirect('quiz')

    else:
        return redirect('quiz')
    
def leaderboard(request):
    top_players = Vexillologist.objects.order_by('-high_score')[:10]
    return render(request, 'leaderboard.html', {'top_players': top_players, 'current_user': request.user})

@login_required
def mastery(request):
    countries = get_countries()
    # Fetch just the names of countries this user has already mastered
    # A flat list query is cheaper than loading full Country objects
    mastered_names = set(request.user.mastered_flags.values_list('name', flat=True))
    entries = [
        # **c is a dictionary unpacking operation, it unpacks the dictionary c into the dictionary entries
        {**c, 'mastered': c['Country'] in mastered_names}
        for c in countries
    ]
    return render(request, 'mastery.html', {
        'entries': entries,
        'mastered_count': len(mastered_names),
        'total_count': len(countries),
    })

def about(request):
    return render(request, 'about.html')

def privacy(request):
    return render(request, 'privacy.html')

def contact(request):
    return render(request, 'contact.html')

def release_notes(request):
    return render(request, 'release_notes.html')

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

    email_record = EmailAddress.objects.filter(user=request.user, primary=True).first()
    email_verified = email_record.verified if email_record else False
    return render(request, 'settings.html', {'form': form, 'email_verified': email_verified})


@login_required
def resend_confirmation(request):
    # If the user clicks the "Resend Confirmation Email" button, this view is called
    if request.method == 'POST':
        '''
        get_or_create() creates a new email address record in the database if it doesn't exist
        
        get_or_create always returns a 2-tuple (instance, created_bool)
        
        The object we want and a boolean for whether it was just created. Without unpacking it, email_record was holding the whole tuple, hence the error. 
        
        The , _ discards the boolean since we don't need it.
        '''
        email_record, _ = EmailAddress.objects.get_or_create(
            user=request.user,
            defaults={'email': request.user.email, 'primary': True, 'verified': False},
        )
        if email_record.verified:
            messages.info(request, 'Your email is already confirmed.')
        else:
            email_record.send_confirmation(request)
            messages.success(request, 'Confirmation email sent! Check your inbox.')
    return redirect('settings')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('index')
    return redirect('settings')