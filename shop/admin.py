from django.contrib import admin
from .models import Registrace, Recenze, Produkt, ProduktObjednavka, Platba, Objednavka, Kategorie, HistorieObjednavek, Doprava, Kosik

admin.site.register(Kosik)
admin.site.register(Registrace)
admin.site.register(Recenze)
admin.site.register(Produkt)
admin.site.register(ProduktObjednavka)
admin.site.register(Platba)
admin.site.register(Objednavka)
admin.site.register(Kategorie)
admin.site.register(HistorieObjednavek)
admin.site.register(Doprava)