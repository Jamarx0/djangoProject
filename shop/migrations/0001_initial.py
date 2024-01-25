# Generated by Django 5.0.1 on 2024-01-18 18:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Kategorie',
            fields=[
                ('id_kategorie', models.AutoField(primary_key=True, serialize=False)),
                ('nazev', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Zakaznik',
            fields=[
                ('id_zakaznika', models.AutoField(primary_key=True, serialize=False)),
                ('jmeno', models.CharField(max_length=255)),
                ('prijmeni', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('telefonni_cislo', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Produkt',
            fields=[
                ('id_produktu', models.AutoField(primary_key=True, serialize=False)),
                ('nazev', models.CharField(max_length=255)),
                ('popis', models.TextField(null=True)),
                ('cena', models.DecimalField(decimal_places=2, max_digits=10)),
                ('skladove_zasoby', models.IntegerField(null=True)),
                ('id_kategorie', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.kategorie')),
            ],
        ),
        migrations.CreateModel(
            name='Objednavka',
            fields=[
                ('id_objednavky', models.AutoField(primary_key=True, serialize=False)),
                ('datum_objednavky', models.DateTimeField(auto_now_add=True)),
                ('stav', models.CharField(max_length=255)),
                ('id_zakaznika', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.zakaznik')),
            ],
        ),
        migrations.CreateModel(
            name='HistorieObjednavek',
            fields=[
                ('id_historie', models.AutoField(primary_key=True, serialize=False)),
                ('stav', models.CharField(max_length=255)),
                ('datum_zmeny', models.DateTimeField()),
                ('id_objednavky', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.objednavka')),
            ],
            options={
                'indexes': [models.Index(fields=['id_objednavky'], name='shop_histor_id_obje_e26167_idx')],
            },
        ),
        migrations.CreateModel(
            name='Doprava',
            fields=[
                ('id_dopravy', models.AutoField(primary_key=True, serialize=False)),
                ('cena', models.DecimalField(decimal_places=2, max_digits=10)),
                ('metoda_dopravy', models.CharField(max_length=255)),
                ('datum_dopravy', models.DateTimeField()),
                ('id_objednavky', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.objednavka')),
            ],
            options={
                'indexes': [models.Index(fields=['id_objednavky'], name='shop_doprav_id_obje_c0e051_idx')],
            },
        ),
        migrations.CreateModel(
            name='Platba',
            fields=[
                ('id_platby', models.AutoField(primary_key=True, serialize=False)),
                ('suma', models.DecimalField(decimal_places=2, max_digits=10)),
                ('metoda_platby', models.CharField(max_length=255)),
                ('datum_platby', models.DateTimeField()),
                ('id_objednavky', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.objednavka')),
            ],
            options={
                'indexes': [models.Index(fields=['id_objednavky'], name='shop_platba_id_obje_434e64_idx')],
            },
        ),
        migrations.CreateModel(
            name='ObrazekProduktu',
            fields=[
                ('id_obrazku', models.AutoField(primary_key=True, serialize=False)),
                ('nazev_obrazku', models.CharField(max_length=255)),
                ('id_produktu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.produkt')),
            ],
            options={
                'indexes': [models.Index(fields=['id_produktu'], name='shop_obraze_id_prod_901c33_idx')],
            },
        ),
        migrations.CreateModel(
            name='ProduktObjednavka',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mnozstvi', models.IntegerField()),
                ('id_objednavky', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.objednavka')),
                ('id_produktu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.produkt')),
            ],
            options={
                'unique_together': {('id_produktu', 'id_objednavky')},
            },
        ),
        migrations.CreateModel(
            name='Registrace',
            fields=[
                ('id_registrace', models.AutoField(primary_key=True, serialize=False)),
                ('heslo', models.CharField(max_length=255)),
                ('id_zakaznika', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.zakaznik')),
            ],
            options={
                'indexes': [models.Index(fields=['id_zakaznika'], name='shop_regist_id_zaka_1b2b77_idx')],
            },
        ),
        migrations.CreateModel(
            name='Recenze',
            fields=[
                ('id_recenze', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=255)),
                ('datum_recenze', models.DateTimeField()),
                ('id_produktu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.produkt')),
                ('id_zakaznika', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.zakaznik')),
            ],
            options={
                'indexes': [models.Index(fields=['id_produktu'], name='shop_recenz_id_prod_4c25a6_idx'), models.Index(fields=['id_zakaznika'], name='shop_recenz_id_zaka_b19386_idx')],
            },
        ),
    ]
