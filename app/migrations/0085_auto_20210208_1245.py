# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-02-08 12:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0084_auto_20210208_1244'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tdossier',
            old_name='est_autofin',
            new_name='est_autofin_doss',
        ),
        migrations.RenameField(
            model_name='tdossier',
            old_name='est_pec_ds_bilan',
            new_name='est_pec_ds_bilan_doss',
        ),
    ]
