from django.views.generic import View
from .models import Kosik, Kategorie, Produkt, Novinka, ObrazekProduktu, PolozkaKosiku
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm


class KosikView(View):
    template_name = 'shop/kosik.html'

    def get(self, request, *args, **kwargs):
        kosik_id = request.session.get('kosik_id')

        if kosik_id:
            try:
                kosik = Kosik.objects.get(id_kosiku=kosik_id)
                obsah_kosiku = kosik.obsah_kosiku.all()
            except Kosik.DoesNotExist:
                kosik = Kosik.objects.create()
                request.session['kosik_id'] = kosik.id_kosiku
                obsah_kosiku = []
        else:
            kosik = Kosik.objects.create()
            request.session['kosik_id'] = kosik.id_kosiku
            obsah_kosiku = []

        return render(request, self.template_name, {'obsah_kosiku': obsah_kosiku})

    def post(self, request, *args, **kwargs):
        # Zde bychom měli získat identifikátor produktu z POST požadavku
        produkt_id = request.POST.get('produkt_id')

        # Získání nebo vytvoření instance Kosik
        kosik_id = request.session.get('kosik_id')
        if kosik_id:
            kosik = Kosik.objects.get(id_kosiku=kosik_id)
        else:
            kosik = Kosik.objects.create()
            request.session['kosik_id'] = kosik.id_kosiku

        # Získání instance produktu nebo 404, pokud neexistuje
        produkt = get_object_or_404(Produkt, pk=produkt_id)

        # Přidání produktu do košíku
        kosik.add_to_cart(produkt)

        # Přesměrování na stránku s obsahem košíku
        return redirect('kosik')

    def add_to_cart(self, produkt):
        # Metoda pro přidání produktu do košíku
        # Implementujte podle potřeby, může se lišit podle struktury vašeho modelu
        pass


def pokusovec(request):
    kategorie = Kategorie.objects.all()
    produkty = Produkt.objects.all()[:10]
    novinky = Novinka.objects.all()[:5]

    return render(request, 'shop/index.html', {'produkty': produkty, 'novinky': novinky, 'kategorie': kategorie})


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


# views.py
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

        # Přidáno: Pokud přihlášení selže, zobrazí se chyba
        return render(request, self.template_name, {'form': form, 'kategorie': kategorie, 'error_message': 'Invalid login credentials'})

def produkt_detail(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)
    obrazky_produktu = ObrazekProduktu.objects.filter(id_produktu=produkt)

    return render(request, 'shop/product_detail.html', {
        'produkt': produkt,
        'obrazky_produktu': obrazky_produktu,
    })

def products_in_category(request, category_id):
    kategorie = get_object_or_404(Kategorie, id_kategorie=category_id)
    produkty = Produkt.objects.filter(id_kategorie=kategorie)
    obrazky_produktu = {}

    for produkt in produkty:
        obrazky_produktu[produkt.id_produktu] = ObrazekProduktu.objects.filter(id_produktu=produkt.id_produktu)

    return render(request, 'shop/products_in_category.html', {'aktualni_kategorie': kategorie,'produkty': produkty,'obrazky_produktu': obrazky_produktu,})

def pridat_do_kosiku(request, produkt_id):
    # Získání produktu
    produkt = Produkt.objects.get(id_produktu=produkt_id)

    # Získání nebo vytvoření košíku pro přihlášeného uživatele
    kosik, created = Kosik.objects.get_or_create(id_zakaznika=request.user)

    # Přidání produktu do košíku nebo zvýšení množství, pokud již existuje
    polozka, created = PolozkaKosiku.objects.get_or_create(kosik=kosik, produkt=produkt)
    if not created:
        polozka.mnozstvi += 1
        polozka.save()

    return redirect('product_detail', pk=produkt_id)

def zobraz_kosik(request):
    # Získání aktuálního košíku pro přihlášeného uživatele
    kosik = Kosik.objects.get(id_zakaznika=request.user.id)

    # Získání obsahu košíku
    obsah_kosiku = kosik.obsah_kosiku.all()

    # Spočítání celkové ceny košíku
    celkova_cena = sum(polozka.produkt.cena * polozka.mnozstvi for polozka in obsah_kosiku)

    return render(request, 'kosik.html', {'kosik': kosik, 'obsah_kosiku': obsah_kosiku, 'celkova_cena': celkova_cena})

def profile(request):
    # Zde získáte informace o přihlášeném uživateli, například request.user
    user = request.user
    # Váš kód pro získání dalších informací o uživateli

    return render(request, 'shop/profile.html', {'user': user, 'other_data': 'Další informace o uživateli'})