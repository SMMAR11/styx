# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-02-25 10:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0089_auto_20210211_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='tprogramme',
            name='bilan_detaille_progr',
            field=models.BooleanField(default=False),
        ),
    ]
