# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-02-02 13:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0067_auto_20210202_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='TFinDds',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('app.tdossier',),
        ),
    ]