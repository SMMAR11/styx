# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-02-05 17:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0082_vfacture'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tprestationsdossier',
            options={'ordering': ['id_doss'], 'verbose_name': 'T_PRESTATIONS_DOSSIER', 'verbose_name_plural': 'T_PRESTATIONS_DOSSIER'},
        ),
    ]
