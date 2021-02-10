# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-02-04 08:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0080_tavenant_duree_aven'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfacture',
            name='dt_emiss_fact',
            field=models.DateField(blank=True, null=True, verbose_name='\n        Date d\'émission de la facture\n        <span class="field-complement">(JJ/MM/AAAA)</span>\n        '),
        ),
    ]
