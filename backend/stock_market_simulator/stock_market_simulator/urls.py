"""
URL configuration for stock_market_simulator project.

The `urlpatterns` list routes URLs to views. For more information please see:
  https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
  1. Add an import:  from my_app import views
  2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
  1. Add an import:  from other_app.views import Home
  2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
  1. Import the include() function: from django.urls import include, path
  2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import signup, login_view, dashboard
from .views import run_daily_stock_data, run_realtime_data_collector, run_historical_data_fetcher
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/signup/', signup, name='signup'),  # Capturing requests under '/api/signup/'
    path('api/login/', login_view, name='login'),  # Capturing requests under '/api/login/'
    path('dashboard/', dashboard, name='dashboard'),  # Capturing requests under '/dashboard/'
    # ... other URL patterns (if any)
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
