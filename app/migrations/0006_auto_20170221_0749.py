# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-21 07:49
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20170217_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfinancement',
            name='a_inf_fin',
            field=models.CharField(choices=[('Oui', 'Oui'), ('Non', 'Non'), ('Sans objet', 'Sans objet')], default='Sans objet', max_length=255, verbose_name="Avez-vous informé le partenaire financier du début de l'opération ?"),
        ),
        migrations.AlterField(
            model_name='tdossier',
            name='dt_int_doss',
            field=models.DateField(default=datetime.datetime(2017, 2, 21, 7, 49, 49, 908434, tzinfo=utc)),
        ),
    ]
