# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-01-22 08:41
from __future__ import unicode_literals

import app.classes.MFEuroField
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0038_auto_20190122_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tprestationsdossier',
            name='mont_prest_doss',
            field=app.classes.MFEuroField.Class(decimal_places=2, max_digits=26),
        ),
    ]