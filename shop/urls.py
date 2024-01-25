from django.urls import path
from .views import uvodni_stranka
from .views import pokusovec
from . import views

urlpatterns = [
    path('kosik/', views.zobraz_kosik, name='zobraz_kosik'),
    path('uvod/', uvodni_stranka, name='uvodni_stranka'),
    path("pokus/", pokusovec, name="pokusovec")
]