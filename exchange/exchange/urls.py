"""exchange URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("register", views.register_request, name="register"),
    path("", views.api, name="api"),
    path('accounts/', include('django.contrib.auth.urls')),
    path("console", views.console, name="console"),
    path("API/orders/<int:id>", views.order_id, name="single"),
    path("API/balance", views.balance, name="balance"),
    path("API/overview", views.exchangeOverview, name="overview"),
    path("API/traders", views.tradersOverview, name="traders"),
]
