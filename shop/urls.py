from django.contrib.auth.views import LoginView
from django.urls import path

from . import views
from .views import uvodni_stranka, pokusovec, category_detail, RegistrationView

urlpatterns = [
    path('kosik/', views.zobraz_kosik, name='zobraz_kosik'),
    path('uvod/', uvodni_stranka, name='uvodni_stranka'),
    path("", pokusovec, name="pokusovec"),
    path('category/<int:pk>/', category_detail, name='category_detail'),  # Přidejte tento řádek
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegistrationView.as_view(), name='registration'),

]

