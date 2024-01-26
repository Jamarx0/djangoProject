from django.shortcuts import render
from django.views.generic import View
from .forms import RegistrationForm
from django.contrib.auth import login
from django.shortcuts import redirect
from .models import Kosik, Kategorie, Produkt, Novinka


def zobraz_kosik(request):
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

    return render(request, 'shop/kosik.html', {'obsah_kosiku': obsah_kosiku})


def uvodni_stranka(request):
    produkty = Produkt.objects.all()
    return render(request, 'shop/uvodni_stranka.html', {'produkty': produkty})


def pokusovec(request):
    kategorie = Kategorie.objects.all()
    produkty = Produkt.objects.all()[:10]  # Získat prvních 10 produktů
    novinky = Novinka.objects.all()[:5]  # Získat prvních 5 novinek

    return render(request, 'shop/index.html', {'produkty': produkty, 'novinky': novinky, 'kategorie': kategorie})


def category_detail(request, pk):
    kategorie = Kategorie.objects.get(pk=pk)
    # Zde můžete přidat kód pro zobrazení detailu kategorie
    return render(request, 'shop/category_detail.html', {'kategorie': kategorie})


class RegistrationView(View):
    template_name = 'registration.html'  # Vytvořte šablonu pro registraci

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('uvodni_stranka')  # Přesměrujte kamkoliv po registraci
        return render(request, self.template_name, {'form': form})
