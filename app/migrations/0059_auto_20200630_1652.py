# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2020-06-30 16:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0058_tprestationsdossier_duree_prest_doss'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tordreservice',
            name='d_emiss_os',
            field=models.DateField(verbose_name="Date d'effet"),
        ),
    ]