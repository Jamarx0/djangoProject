from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models

class Kosik(models.Model):
    id_kosiku = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    obsah_kosiku = models.ManyToManyField('Produkt', through='PolozkaKosiku')

    def vytvor_objednavku(self):
        nova_objednavka = Objednavka.objects.create(
            user=self.user,
            datum_objednavky=timezone.now(),
            stav="Vytvorena"
        )

        for polozka in self.obsah_kosiku.all():
            ProduktObjednavka.objects.create(
                id_produktu=polozka.produkt,
                id_objednavky=nova_objednavka,
                mnozstvi=polozka.mnozstvi
            )

            # Snížení skladových zásob
            polozka.produkt.skladove_zasoby -= polozka.mnozstvi
            polozka.produkt.save()

        self.delete()

    def add_to_cart(self, produkt):
        # Metoda pro přidání produktu do košíku
        polozka, created = PolozkaKosiku.objects.get_or_create(kosik=self, produkt=produkt)
        if not created:
            polozka.mnozstvi += 1
            polozka.save()

    def __str__(self):
        return f"Kosik {self.id_kosiku} od zákazníka {self.user}"


class PolozkaKosiku(models.Model):
    kosik = models.ForeignKey(Kosik, on_delete=models.CASCADE)
    produkt = models.ForeignKey('Produkt', on_delete=models.CASCADE)
    mnozstvi = models.IntegerField(default=1)


class Produkt(models.Model):
    id_produktu = models.AutoField(primary_key=True)
    nazev = models.CharField(max_length=255, null=False)
    popis = models.TextField(null=True)
    cena = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    id_kategorie = models.ForeignKey('Kategorie', on_delete=models.SET_NULL, null=True)
    skladove_zasoby = models.IntegerField(null=True)
    datum_vytvoreni = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-datum_vytvoreni']

    def __str__(self):
        return f"{self.nazev} - {self.cena} Kč"


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

    def __str__(self):
        return f"Objednávka #{self.id_objednavky} od zákazníka {self.user} - Stav: {self.stav}"


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
    id_produktu = models.ForeignKey(Produkt, on_delete=models.CASCADE)  # Změňte podle skutečného modelu produktu
    text = models.TextField(null=True)
    datum_recenze = models.DateTimeField(null=False)

    class Meta:
        indexes = [
            models.Index(fields=['id_produktu']),
            models.Index(fields=['user'])
        ]

    def __str__(self):
        return f"Recenze #{self.id_recenze} pro produkt {self.id_produktu} od zákazníka {self.user}"


class Platba(models.Model):
    id_platby = models.AutoField(primary_key=True)
    id_objednavky = models.ForeignKey(Objednavka, on_delete=models.CASCADE)
    suma = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    metoda_platby = models.CharField(max_length=255, null=False)
    datum_platby = models.DateTimeField(null=False)

    class Meta:
        indexes = [
            models.Index(fields=['id_objednavky'])
        ]

    def __str__(self):
        return f"Platba #{self.id_platby} pro objednávku {self.id_objednavky} - {self.suma} Kč"


class ObrazekProduktu(models.Model):
    id_obrazku = models.AutoField(primary_key=True)
    id_produktu = models.ForeignKey(Produkt, on_delete=models.CASCADE)
    nazev_obrazku = models.CharField(max_length=255, null=False)

    class Meta:
        indexes = [
            models.Index(fields=['id_produktu'])
        ]

    def __str__(self):
        return f"Obrazek #{self.id_obrazku} pro produkt {self.id_produktu}"


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


class Doprava(models.Model):
    id_dopravy = models.AutoField(primary_key=True)
    id_objednavky = models.ForeignKey(Objednavka, on_delete=models.CASCADE)
    cena = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    metoda_dopravy = models.CharField(max_length=255, null=False)
    datum_dopravy = models.DateTimeField(null=False)

    class Meta:
        indexes = [
            models.Index(fields=['id_objednavky'])
        ]

    def __str__(self):
        return f"Doprava pro objednávku #{self.id_objednavky} - Cena: {self.cena} Kč"
