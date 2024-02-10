from django.contrib.auth.views import LoginView
from django.urls import path
from . import views
from .views import pokusovec, RegistrationView, KosikView, search, vyber_dopravy_a_platby, shrnuti_objednavky, potvrzeni_objednavky

urlpatterns = [
    path('search/', search, name='search'),
    path('pridat_do_kosiku/<int:produkt_id>/', views.pridat_do_kosiku, name='pridat_do_kosiku'),
    path("", pokusovec, name="pokusovec"),
    path('category/<int:category_id>/', views.products_in_category, name='products_in_category'),
    path('product/<int:pk>/', views.produkt_detail, name='product_detail'),
    path('login/', LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('register/', RegistrationView.as_view(), name='registration'),
    path('accounts/profile/', views.profile, name='profile'),
    path('kosik/', KosikView.as_view(), name='kosik'),
    path("vyber_dopravy_a_platby", vyber_dopravy_a_platby, name="vyber_dopravy_a_platby"),
    path("shrnuti_objednavky", shrnuti_objednavky, name="shrnuti_objednavky"),
    path('potvrzeni_objednavky/', potvrzeni_objednavky, name='potvrzeni_objednavky'),
]
