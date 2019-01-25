# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-01-21 13:34
from __future__ import unicode_literals

import datetime
import django.contrib.gis.db.models.fields
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20180426_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tdossier',
            name='dt_int_doss',
            field=models.DateField(default=datetime.datetime(2019, 1, 21, 13, 34, 13, 826114, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='tdossiergeom',
            name='geom_lin',
            field=django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='tdossiergeom',
            name='geom_pct',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='tdossiergeom',
            name='geom_pol',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='tdossierpgregeom',
            name='geom_lin',
            field=django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='tdossierpgregeom',
            name='geom_pct',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='tdossierpgregeom',
            name='geom_pol',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326),
        ),
    ]