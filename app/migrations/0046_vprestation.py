# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-01-22 11:44
from __future__ import unicode_literals

import app.classes.MFEuroField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0045_vfinancement_vsuividossier_vsuiviprestationsdossier'),
    ]

    operations = [
        migrations.CreateModel(
            name='VPrestation',
            fields=[
                ('id_prest', models.IntegerField(primary_key=True, serialize=False)),
                ('mont_prest', app.classes.MFEuroField.Class(decimal_places=2, max_digits=26)),
            ],
            options={
                'db_table': 'v_prestation',
                'managed': False,
            },
        ),
    ]