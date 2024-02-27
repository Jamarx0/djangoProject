from django.views.generic import View
from .models import Kosik, Kategorie, Produkt, Novinka, Doprava, Platba, Objednavka, ProduktObjednavka
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm, SearchForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib.auth import logout


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
        # Assuming 'image' is the attribute containing the image URL
        results = Produkt.objects.filter(nazev__icontains=query).values('id_produktu', 'nazev', 'cena', 'nazev_obrazku')

    return render(request, 'shop/search_results.html', {'form': form, 'results': results})


def vyber_dopravy_a_platby(request):
    if request.method == 'POST':
        vybrana_doprava_id = request.POST.get('doprava')
        vybrana_platba_id = request.POST.get('platba')

        print("Vybraná doprava:", vybrana_doprava_id)
        print("Vybraná platba:", vybrana_platba_id)

        # Uložení vybrané dopravy a platby do session
        request.session['vybrana_doprava'] = vybrana_doprava_id
        request.session['vybrana_platba'] = vybrana_platba_id

        # Uložení vybrané dopravy a platby do modelu Kosik
        kosik, _ = Kosik.objects.get_or_create(user=request.user)
        kosik.vybrana_doprava_id = vybrana_doprava_id
        kosik.vybrana_platba_id = vybrana_platba_id
        kosik.save()

        return redirect('shrnuti_objednavky')
    else:
        moznosti_dopravy = Doprava.objects.all()
        moznosti_platby = Platba.objects.all()
        return render(request, 'shop/vyber_dopravy_a_platby.html',
                      {'moznosti_dopravy': moznosti_dopravy, 'moznosti_platby': moznosti_platby})


def shrnuti_objednavky(request):
    kosik, _ = Kosik.objects.get_or_create(user=request.user)
    obsah_kosiku = kosik.polozky_kosiku.all()

    # Načtení vybrané dopravy a platby z modelu Kosik
    vybrana_doprava = kosik.vybrana_doprava
    vybrana_platba = kosik.vybrana_platba

    # Načtení cen dopravy a platby, pokud jsou dostupné
    cena_dopravy = vybrana_doprava.cena if vybrana_doprava else 0
    cena_platby = vybrana_platba.cena if vybrana_platba else 0

    celkova_cena_kosiku = kosik.celkova_cena_kosiku()

    # Přičtení cen dopravy a platby k celkové ceně košíku
    celkova_cena_kosiku += cena_dopravy + cena_platby

    return render(request, 'shop/shrnuti_objednavky.html',
                  {'obsah_kosiku': obsah_kosiku, 'vybrana_doprava': vybrana_doprava, 'vybrana_platba': vybrana_platba,
                   'celkova_cena_kosiku': celkova_cena_kosiku, 'cena_dopravy': cena_dopravy,
                   'cena_platby': cena_platby})


@transaction.atomic
def potvrzeni_objednavky(request):
    if request.method == 'POST':
        # Získání košíku uživatele
        kosik, _ = Kosik.objects.get_or_create(user=request.user)
        vybrana_doprava = kosik.vybrana_doprava
        vybrana_platba = kosik.vybrana_platba

        # Vytvoření nové objednávky
        nova_objednavka = Objednavka.objects.create(
            user=request.user,
            stav="Vytvorena",
            vybrana_doprava=vybrana_doprava,
            vybrana_platba=vybrana_platba
        )

        # Přiřazení položek z košíku k objednávce a snížení skladových zásob
        for polozka in kosik.polozky_kosiku.all():
            ProduktObjednavka.objects.create(
                id_produktu=polozka.id_produkt,
                id_objednavky=nova_objednavka,
                mnozstvi=polozka.mnozstvi
            )

            # Snížení skladových zásob
            produkt = polozka.id_produkt
            produkt.skladove_zasoby -= polozka.mnozstvi
            produkt.save()

        # Odstranění obsahu košíku
        kosik.delete()

        return redirect('pokusovec')
    else:
        # Zde zobrazte formulář pro potvrzení objednávky
        pass


@login_required
def historie_objednavek(request):
    objednavky = Objednavka.objects.filter(user=request.user).order_by('-datum_objednavky')
    for objednavka in objednavky:
        cena_dopravy = objednavka.vybrana_doprava.cena if objednavka.vybrana_doprava else 0
        cena_platby = objednavka.vybrana_platba.cena if objednavka.vybrana_platba else 0
        objednavka.celkova_cena = objednavka.celkova_cena() + cena_dopravy + cena_platby
    return render(request, 'shop/historie_objednavek.html', {'objednavky': objednavky})


@login_required
def logout_user(request):
    logout(request)
    return redirect('pokusovec')  # Přesměrování na domovskou stránku nebo jinou vhodnou stránku po odhlášení
