# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-02-02 12:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0066_auto_20210202_1145'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tacpfinddscdg',
            unique_together=set([('ddscdg_id', 'fin_id')]),
        ),
    ]
