from django.views.generic import View
from .models import Kosik, Kategorie, Produkt, Novinka, Doprava, Platba, Objednavka, ProduktObjednavka
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm, SearchForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


class KosikView(LoginRequiredMixin, View):
    template_name = 'shop/kosik.html'

    def get(self, request, *args, **kwargs):
        kosik, created = Kosik.objects.get_or_create(user=request.user)
        obsah_kosiku = kosik.polozky_kosiku.all()

        # Aktualizace informací o ceně a obrázku do položek košíku
        for polozka in obsah_kosiku:
            polozka.produkt = polozka.id_produkt
            polozka.cena = polozka.celkova_cena()
            polozka.obrazek = polozka.id_produkt.nazev_obrazku  # Aktualizováno

        celkova_cena_kosiku = kosik.celkova_cena_kosiku()

        return render(request, self.template_name,
                      {'kosik': kosik, 'obsah_kosiku': obsah_kosiku, 'celkova_cena_kosiku': celkova_cena_kosiku})


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
    return render(request, 'shop/product_detail.html', {'produkt': produkt})


def products_in_category(request, category_id):
    kategorie = get_object_or_404(Kategorie, id_kategorie=category_id)
    produkty = Produkt.objects.filter(id_kategorie=kategorie)
    return render(request, 'shop/products_in_category.html',
                  {'aktualni_kategorie': kategorie, 'produkty': produkty})


@login_required
def pridat_do_kosiku(request, produkt_id):
    produkt = get_object_or_404(Produkt, id_produktu=produkt_id)
    kosik, created = Kosik.objects.get_or_create(user=request.user)
    kosik.add_to_cart(produkt)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def pokusovec(request):
    kategorie = Kategorie.objects.all()
    produkty = Produkt.objects.all()[:10]
    novinky = Novinka.objects.all()[:5]
    return render(request, 'shop/index.html', {'produkty': produkty, 'novinky': novinky, 'kategorie': kategorie})


def profile(request):
    user = request.user
    return render(request, 'shop/profile.html', {'user': user, 'other_data': 'Další informace o uživateli'})


def search(request):
    form = SearchForm(request.GET)
    results = []

    if form.is_valid():
        query = form.cleaned_data['query']
        results = Produkt.objects.filter(nazev__icontains=query)

    return render(request, 'shop/search_results.html', {'form': form, 'results': results})


def vyber_dopravy_a_platby(request):
    moznosti_dopravy = Doprava.objects.all()
    moznosti_platby = Platba.objects.all()
    return render(request, 'shop/vyber_dopravy_a_platby.html',
                  {'moznosti_dopravy': moznosti_dopravy, 'moznosti_platby': moznosti_platby})


def shrnuti_objednavky(request):
    # Získání obsahu košíku
    kosik, _ = Kosik.objects.get_or_create(user=request.user)
    obsah_kosiku = kosik.polozky_kosiku.all()

    # Získání vybrané dopravy a platby z session
    vybrana_doprava_id = request.session.get('vybrana_doprava')
    vybrana_platba_id = request.session.get('vybrana_platba')
    vybrana_doprava = Doprava.objects.get(id_dopravy=vybrana_doprava_id)
    vybrana_platba = Platba.objects.get(id_platby=vybrana_platba_id)

    celkova_cena_kosiku = kosik.celkova_cena_kosiku()

    return render(request, 'shop/shrnuti_objednavky.html',
                  {'obsah_kosiku': obsah_kosiku, 'vybrana_doprava': vybrana_doprava, 'vybrana_platba': vybrana_platba,
                   'celkova_cena_kosiku': celkova_cena_kosiku})


def potvrzeni_objednavky(request):
    if request.method == 'POST':
        # Zde zpracujte potvrzení objednávky
        vybrana_doprava_id = request.session.get('vybrana_doprava')
        vybrana_doprava = Doprava.objects.get(id_dopravy=vybrana_doprava_id)

        vybrana_platba_id = request.POST.get('platba')
        # Přidání kódu pro potvrzení objednávky, např. vytvoření instance Objednavka
        vybrana_platba = Platba.objects.get(id_platby=vybrana_platba_id)

        # Vytvoření instance Objednavka
        objednavka = Objednavka.objects.create(
            user=request.user,
            stav="Vytvorena",
            vybrana_doprava=vybrana_doprava,
            vybrana_platba=vybrana_platba
        )

        # Přiřazení položek z košíku k objednávce
        for polozka in Kosik.objects.get(user=request.user).polozky_kosiku.all():
            ProduktObjednavka.objects.create(
                id_produktu=polozka.id_produkt,
                id_objednavky=objednavka,
                mnozstvi=polozka.mnozstvi
            )

            # Snížení skladových zásob
            produkt = polozka.id_produkt
            produkt.skladove_zasoby -= polozka.mnozstvi
            produkt.save()

        # Odstranění obsahu košíku uživatele
        kosik = Kosik.objects.get(user=request.user)
        kosik.delete()

        # Přesměrování na stránku potvrzení objednávky nebo kamkoliv jinam
        return redirect('pokusovec')
