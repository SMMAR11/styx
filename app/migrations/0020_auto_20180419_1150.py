# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-04-19 09:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20180417_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tavancementpgretraces',
            name='id_doss_pgre',
            field=models.ForeignKey(db_column='id_doss_pgre', on_delete=django.db.models.deletion.CASCADE, to='app.TDossierPgre'),
        ),
        migrations.AlterField(
            model_name='tdossier',
            name='dt_int_doss',
            field=models.DateField(default=datetime.datetime(2018, 4, 19, 9, 50, 13, 43079, tzinfo=utc)),
        ),
    ]