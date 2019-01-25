# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-01-22 08:46
from __future__ import unicode_literals

import app.classes.MFEuroField
import app.models.tables
import app.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_auto_20190122_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tfacture',
            name='chem_pj_fact',
            field=models.FileField(blank=True, default='', upload_to=app.models.tables.TFacture.set_chem_pj_fact_upload_to, validators=[app.validators.val_fich_pdf], verbose_name='Insérer le fichier scanné de la facture <span class="field-complement">(fichier PDF)</span>'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tfacture',
            name='comm_fact',
            field=models.TextField(blank=True, default='', verbose_name='Commentaire'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tfacture',
            name='id_doss',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.TDossier'),
        ),
        migrations.AlterField(
            model_name='tfacture',
            name='id_prest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.TPrestation'),
        ),
        migrations.AlterField(
            model_name='tfacture',
            name='mont_ht_fact',
            field=app.classes.MFEuroField.Class(blank=True, decimal_places=2, max_digits=26, null=True, verbose_name='Montant HT de la facture'),
        ),
        migrations.AlterField(
            model_name='tfacture',
            name='mont_ttc_fact',
            field=app.classes.MFEuroField.Class(blank=True, decimal_places=2, max_digits=26, null=True, verbose_name='Montant TTC de la facture'),
        ),
        migrations.AlterField(
            model_name='tfacture',
            name='num_bord_fact',
            field=models.CharField(max_length=255, verbose_name='Numéro de bordereau'),
        ),
        migrations.AlterField(
            model_name='tfacture',
            name='num_fact',
            field=models.CharField(max_length=255, verbose_name='Numéro de facture'),
        ),
        migrations.AlterField(
            model_name='tfacture',
            name='num_mandat_fact',
            field=models.CharField(max_length=255, verbose_name='Numéro de mandat'),
        ),
    ]