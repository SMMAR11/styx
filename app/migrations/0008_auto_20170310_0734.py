# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-10 07:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20170227_1241'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tprestation',
            options={'ordering': ['id_org_prest', 'int_prest', 'dt_notif_prest'], 'verbose_name': 'T_PRESTATION', 'verbose_name_plural': 'T_PRESTATION'},
        ),
        migrations.AlterField(
            model_name='tdossier',
            name='dt_int_doss',
            field=models.DateField(default=datetime.datetime(2017, 3, 10, 7, 34, 8, 93237, tzinfo=utc)),
        ),
    ]