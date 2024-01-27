from django.contrib.auth.views import LoginView
from django.urls import path
from . import views
from .views import pokusovec, RegistrationView, products_in_category

urlpatterns = [
    path('kosik/', views.zobraz_kosik, name='zobraz_kosik'),
    path("", pokusovec, name="pokusovec"),
    path('category/<int:category_id>/', views.products_in_category, name='products_in_category'),
    path('product/<int:pk>/', views.produkt_detail, name='product_detail'),
    path('login/', LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('register/', RegistrationView.as_view(), name='registration'),
]
