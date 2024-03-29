# Generated by Django 5.0.1 on 2024-02-08 19:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_polozkakosiku_celkova_cena'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='polozkakosiku',
            name='celkova_cena',
        ),
        migrations.AlterField(
            model_name='polozkakosiku',
            name='kosik',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='polozky_kosiku', to='shop.kosik'),
        ),
        migrations.AlterField(
            model_name='polozkakosiku',
            name='mnozstvi',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='polozkakosiku',
            name='produkt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='polozky_kosiku', to='shop.produkt'),
        ),
    ]
