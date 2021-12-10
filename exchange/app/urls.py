from django.urls import path
from . import views

app_name = "app"   


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register", views.register_request, name="register"),
    path("console",views.console_test,name="console"),
]