# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-05-26 11:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0098_auto_20210526_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tprospectiveannuelleppipap',
            name='ppi_id',
            field=models.ForeignKey(db_column='ppi_id', on_delete=django.db.models.deletion.CASCADE, to='app.TPlanPluriannuelInvestissementPpi'),
        ),
    ]
