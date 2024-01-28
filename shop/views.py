from django.views.generic import View
from .models import Kosik, Kategorie, Produkt, Novinka, ObrazekProduktu, PolozkaKosiku
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from django.contrib.auth.mixins import LoginRequiredMixin

class KosikView(LoginRequiredMixin, View):
    template_name = 'shop/kosik.html'

    def get(self, request, *args, **kwargs):
        kosik, created = Kosik.objects.get_or_create(user=request.user)
        obsah_kosiku = kosik.obsah_kosiku.all()
        return render(request, self.template_name, {'obsah_kosiku': obsah_kosiku})

    def add_to_cart(self, produkt):
        polozka, created = PolozkaKosiku.objects.get_or_create(kosik=self, produkt=produkt)
        if not created:
            polozka.mnozstvi += 1
            polozka.save()


class RegistrationView(View):
    template_name = 'shop/registration.html'

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        kategorie = Kategorie.objects.all()
        return render(request, self.template_name, {'form': form, 'kategorie': kategorie})

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pokusovec')
        kategorie = Kategorie.objects.all()
        return render(request, self.template_name, {'form': form, 'kategorie': kategorie})

class LoginView(View):
    template_name = 'shop/login.html'

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        kategorie = Kategorie.objects.all()
        return render(request, self.template_name, {'form': form, 'kategorie': kategorie})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        kategorie = Kategorie.objects.all()

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('pokusovec')

        return render(request, self.template_name,
                      {'form': form, 'kategorie': kategorie, 'error_message': 'Invalid login credentials'})



def produkt_detail(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)
    obrazky_produktu = ObrazekProduktu.objects.filter(id_produktu=produkt)
    return render(request, 'shop/product_detail.html', {'produkt': produkt, 'obrazky_produktu': obrazky_produktu})


def products_in_category(request, category_id):
    kategorie = get_object_or_404(Kategorie, id_kategorie=category_id)
    produkty = Produkt.objects.filter(id_kategorie=kategorie)
    obrazky_produktu = {produkt.id_produktu: ObrazekProduktu.objects.filter(id_produktu=produkt.id_produktu) for produkt
                        in produkty}
    return render(request, 'shop/products_in_category.html',
                  {'aktualni_kategorie': kategorie, 'produkty': produkty, 'obrazky_produktu': obrazky_produktu})


def pridat_do_kosiku(request, produkt_id):
    produkt = get_object_or_404(Produkt, id_produktu=produkt_id)
    if request.user.is_authenticated:
        kosik, created = Kosik.objects.get_or_create(user=request.user)
    else:
        kosik, created = Kosik.objects.get_or_create(id_kosiku=request.session.get('kosik_id'))
        if not request.session.get('kosik_id'):
            request.session['kosik_id'] = kosik.id_kosiku
    kosik.add_to_cart(produkt)
    return redirect('zobraz_kosik')


def pokusovec(request):
    kategorie = Kategorie.objects.all()
    produkty = Produkt.objects.all()[:10]
    novinky = Novinka.objects.all()[:5]
    return render(request, 'shop/index.html', {'produkty': produkty, 'novinky': novinky, 'kategorie': kategorie})


def profile(request):
    user = request.user
    return render(request, 'shop/profile.html', {'user': user, 'other_data': 'Další informace o uživateli'})


class ZobrazKosikView(View):
    template_name = 'shop/kosik.html'

    def get(self, request, *args, **kwargs):
        kosik, created = Kosik.objects.get_or_create(user=request.user)
        obsah_kosiku = kosik.obsah_kosiku.all()
        return render(request, self.template_name, {'obsah_kosiku': obsah_kosiku})
