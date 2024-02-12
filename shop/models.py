from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Platba(models.Model):
    id_platby = models.AutoField(primary_key=True)
    metoda_platby = models.CharField(max_length=255, null=False)
    cena = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    def __str__(self):
        return f"{self.metoda_platby} - {self.cena} Kč"


class Doprava(models.Model):
    id_dopravy = models.AutoField(primary_key=True)
    metoda_dopravy = models.CharField(max_length=255, null=False)
    cena = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    def __str__(self):
        return f"{self.metoda_dopravy} - {self.cena} Kč"


class Kosik(models.Model):
    id_kosiku = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    obsah_kosiku = models.ManyToManyField('Produkt', through='PolozkaKosiku')
    vybrana_doprava = models.ForeignKey(Doprava, on_delete=models.SET_NULL, null=True)
    vybrana_platba = models.ForeignKey(Platba, on_delete=models.SET_NULL, null=True)
    cena_dopravy = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cena_platby = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cena = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    # Metody a další atributy zůstávají nezměněny

    def vytvor_objednavku(self):
        if self.vybrana_doprava is None or self.vybrana_platba is None:
            raise ValueError("Vybraná doprava a platba musí být nastaveny.")

        nova_objednavka = Objednavka.objects.create(
            user=self.user,
            datum_objednavky=timezone.now(),
            stav="Vytvorena",
            vybrana_doprava=self.vybrana_doprava,
            vybrana_platba=self.vybrana_platba
        )

        celkova_cena = 0
        for polozka in self.obsah_kosiku.all():
            ProduktObjednavka.objects.create(
                id_produktu=polozka.id_produkt,
                id_objednavky=nova_objednavka,
                mnozstvi=polozka.mnozstvi
            )

            # Snížení skladových zásob
            polozka.id_produkt.skladove_zasoby -= polozka.mnozstvi
            polozka.id_produkt.save()

            # Přičtení ceny položky k celkové ceně
            celkova_cena += polozka.celkova_cena()

        # Přičtení ceny dopravy a platby k celkové ceně
        celkova_cena += self.cena_dopravy + self.cena_platby

        nova_objednavka.celkova_cena = celkova_cena
        nova_objednavka.save()

        self.delete()

    def add_to_cart(self, produkt):
        # Metoda pro přidání produktu do košíku
        polozka, created = PolozkaKosiku.objects.get_or_create(id_kosik=self, id_produkt=produkt)
        if not created:
            polozka.mnozstvi += 1
            polozka.save()

    def __str__(self):
        return f"Kosik {self.id_kosiku} od zákazníka {self.user}"

    def celkova_cena_kosiku(self):
        celkova_cena = 0
        for polozka in self.obsah_kosiku.all():
            celkova_cena += polozka.celkova_cena()  # Předpokládáme, že metoda celkova_cena() vrací správnou cenu za
            # položku
        return celkova_cena


class Produkt(models.Model):
    id_produktu = models.AutoField(primary_key=True)
    nazev = models.CharField(max_length=255, null=False)
    popis = models.TextField(null=True)
    cena = models.DecimalField(max_digits=100, decimal_places=2, null=False)
    id_kategorie = models.ForeignKey('Kategorie', on_delete=models.SET_NULL, null=True)
    skladove_zasoby = models.IntegerField(null=True)
    nazev_obrazku = models.CharField(max_length=255, null=False)
    datum_vytvoreni = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-datum_vytvoreni']

    def __str__(self):
        return f"{self.nazev} - {self.cena} Kč"

    def celkova_cena(self):
        # Spočítejte celkovou cenu na základě atributů produktu
        celkova_cena = 0
        polozky_kosiku = PolozkaKosiku.objects.filter(id_produkt=self)
        for polozka in polozky_kosiku:
            celkova_cena += polozka.celkova_cena()
        return celkova_cena


class PolozkaKosiku(models.Model):
    id_kosik = models.ForeignKey(Kosik, related_name='polozky_kosiku', on_delete=models.CASCADE)
    id_produkt = models.ForeignKey(Produkt, related_name='polozky_kosiku', on_delete=models.CASCADE)
    mnozstvi = models.PositiveIntegerField(default=1)

    def celkova_cena(self):
        return self.id_produkt.cena * self.mnozstvi

    class Meta:
        verbose_name_plural = "položky košíku"


class Kategorie(models.Model):
    id_kategorie = models.AutoField(primary_key=True)
    nazev = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.nazev


class Objednavka(models.Model):
    id_objednavky = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    datum_objednavky = models.DateTimeField(auto_now_add=True)
    stav = models.CharField(max_length=255, null=False)
    vybrana_doprava = models.ForeignKey(Doprava, on_delete=models.SET_NULL, null=True)
    vybrana_platba = models.ForeignKey(Platba, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Objednávka #{self.id_objednavky} od zákazníka {self.user} - Stav: {self.stav}"

    def celkova_cena(self):
        # Spočítejte celkovou cenu objednávky na základě jejích položek
        celkova_cena = 0
        polozky_objednavky = ProduktObjednavka.objects.filter(id_objednavky=self)
        for polozka in polozky_objednavky:
            celkova_cena += polozka.id_produktu.cena * polozka.mnozstvi
        return celkova_cena

class Novinka(models.Model):
    id_novinky = models.AutoField(primary_key=True)
    nazev = models.CharField(max_length=255, null=False)
    obsah = models.TextField(null=True)
    produkty = models.ManyToManyField(Produkt)

    def __str__(self):
        return self.nazev


class ProduktObjednavka(models.Model):
    id_produktu = models.ForeignKey(Produkt, on_delete=models.CASCADE)
    id_objednavky = models.ForeignKey(Objednavka, on_delete=models.CASCADE)
    mnozstvi = models.IntegerField(null=False)

    def __str__(self):
        return f"Produkt {self.id_produktu} v objednávce {self.id_objednavky} - Množství: {self.mnozstvi}"


class Registrace(models.Model):
    id_registrace = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    heslo = models.CharField(max_length=255, null=False)

    class Meta:
        indexes = [
            models.Index(fields=['user'])
        ]

    def __str__(self):
        return f"Registrace #{self.id_registrace} pro zákazníka {self.user}"


class Recenze(models.Model):
    id_recenze = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    id_produktu = models.ForeignKey(Produkt, on_delete=models.CASCADE)
    text = models.TextField(null=True)
    datum_recenze = models.DateTimeField(null=False)

    class Meta:
        indexes = [
            models.Index(fields=['id_produktu']),
            models.Index(fields=['user'])
        ]

    def __str__(self):
        return f"Recenze #{self.id_recenze} pro produkt {self.id_produktu} od zákazníka {self.user}"


class HistorieObjednavek(models.Model):
    id_historie = models.AutoField(primary_key=True)
    id_objednavky = models.ForeignKey(Objednavka, on_delete=models.CASCADE)
    stav = models.CharField(max_length=255, null=False)
    datum_zmeny = models.DateTimeField(null=False)

    class Meta:
        indexes = [
            models.Index(fields=['id_objednavky'])
        ]

    def __str__(self):
        return f"Historie objednávky #{self.id_objednavky} - Stav: {self.stav}"
