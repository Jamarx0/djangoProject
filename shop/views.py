from django.shortcuts import render
from .models import Kosik, Kategorie, Produkt, Novinka



def zobraz_kosik(request):
    kosik_id = request.session.get('kosik_id')  # Získání ID košíku z relace

    if kosik_id:
        try:
            kosik = Kosik.objects.get(id_kosiku=kosik_id)  # Použijte správný název primárního klíče
            obsah_kosiku = kosik.obsah_kosiku.all()
        except Kosik.DoesNotExist:
            kosik = None
            obsah_kosiku = []
    else:
        kosik = Kosik.objects.create()
        request.session['kosik_id'] = kosik.id_kosiku  # Použijte správný název primárního klíče
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
