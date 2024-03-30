from django.http import JsonResponse
from django.core.management import call_command
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Remove for production
import json
from django.contrib.auth import authenticate, login

# ... other imports (if needed)

@csrf_exempt  # Remove for production
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Perform validation and create a new user
        if email and password:
            user = User.objects.create_user(username=email, email=email, password=password)
            return JsonResponse({'message': 'Signup successful!'})
        else:
            return JsonResponse({'error': 'Email and password are required.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt  # Remove for production
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Authenticate user credentials
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)  # Create a session
            return JsonResponse({'success': True, 'message': 'Login successful!'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def dashboard(request):
    # Access user data if needed (optional)
    # user = request.user  # You can access the logged-in user object here
 
    # Your dashboard logic (prepare data for template context)
    context = {}  # Empty context dictionary for now
 
    # Example: Pass user data to the template (if applicable)
    # context['user'] = user
 
    return render(request, 'dashboard.html', context)


def run_daily_stock_data(request):
    # Call the management command to execute the daily_stock_data script
    call_command('daily_stock_data')
    return JsonResponse({'message': 'Daily stock data updated successfully'})


def run_realtime_data_collector(request):
    # Call the management command to execute the realtime_data_collector script
    call_command('realtime_data_collector')
    return JsonResponse({'message': 'Realtime data collection completed successfully'})


def run_historical_data_fetcher(request):
    # Call the management command to execute the historical_data script
    call_command('historical_data_storage')
    return JsonResponse({'message': 'Historical data fetched successfully'})




