# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2022-05-23 09:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0116_auto_20220523_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfinanceur',
            name='abre_org_fin',
            field=models.CharField(blank=True, max_length=63, verbose_name='Abréviation'),
        ),
        migrations.AlterField(
            model_name='tfinanceur',
            name='est_princi',
            field=models.BooleanField(default=True, help_text='\n        Si non, alors désaffichage du financeur dans le bilan "Décisions du comité de programmation - CD GEMAPI".\n        ', verbose_name='Est-ce un financeur principal ?'),
        ),
        migrations.AlterField(
            model_name='tprospectiveannuelleppipap',
            name='ppi_id',
            field=models.ForeignKey(db_column='ppi_id', on_delete=django.db.models.deletion.CASCADE, to='app.TPlanPluriannuelInvestissementPpi'),
        ),
    ]
