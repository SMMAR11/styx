# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2022-08-05 10:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0120_auto_20220805_0906'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='v_demandeversement_synthesedossierfinanceur',
            options={'managed': False, 'ordering': ['FNC_ID__n_org']},
        ),
        migrations.AlterField(
            model_name='tprospectiveannuelleppipap',
            name='ppi_id',
            field=models.ForeignKey(db_column='ppi_id', on_delete=django.db.models.deletion.CASCADE, to='app.TPlanPluriannuelInvestissementPpi'),
        ),
    ]
