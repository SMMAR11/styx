# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2020-09-04 10:58
from __future__ import unicode_literals

import app.models.tables
import app.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0059_auto_20200630_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tphoto',
            name='chem_ph',
            field=models.FileField(upload_to=app.models.tables.TPhoto.set_chem_ph_upload_to, validators=[app.validators.val_fich_img], verbose_name='Insérer une photo <span class="field-complement">(taille limitée à 5 Mo)</span>'),
        ),
        migrations.AlterField(
            model_name='tphotopgre',
            name='chem_ph_pgre',
            field=models.FileField(upload_to=app.models.tables.TPhotoPgre.set_chem_ph_pgre_upload_to, validators=[app.validators.val_fich_img], verbose_name='Insérer une photo <span class="field-complement">(taille limitée à 5 Mo)</span>'),
        ),
    ]