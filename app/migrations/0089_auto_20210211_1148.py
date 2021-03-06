# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-02-11 11:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0088_remove_tfinanceur_init_acpfinddscdg'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='findds',
            options={'verbose_name': 'Plan de financement', 'verbose_name_plural': 'Plans de financement'},
        ),
        migrations.AlterModelOptions(
            name='tcdgemapicdg',
            options={'ordering': ['-cdg_date'], 'verbose_name': 'CD GEMAPI', 'verbose_name_plural': 'CD GEMAPI'},
        ),
        migrations.AlterModelOptions(
            name='tddscdg',
            options={'ordering': ['-cdg_id', 'dds_id'], 'verbose_name': 'Dossier présente à un CD GEMAPI', 'verbose_name_plural': 'Dossiers présentés à un CD GEMAPI'},
        ),
    ]
