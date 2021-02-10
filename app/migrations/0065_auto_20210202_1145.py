# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-02-02 11:45
from __future__ import unicode_literals

import app.models.tables
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0064_auto_20210202_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tacpfinddscdg',
            name='acp_id',
            field=models.ForeignKey(db_column='acp_id', default=app.models.tables.TAcpFinDdsCdg.acp_id_default, on_delete=django.db.models.deletion.CASCADE, to='app.TAvisCp', verbose_name='Avis'),
        ),
        migrations.AlterField(
            model_name='tfinanceur',
            name='init_acpfinddscdg',
            field=models.BooleanField(default=False, verbose_name="\n        Doit-il faire l'objet par défaut d'une instance TAcpFinDdsCdg ?\n        "),
        ),
    ]
