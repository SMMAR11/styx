# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-01-22 08:59
from __future__ import unicode_literals

import app.classes.MFEuroField
import app.classes.MFPercentField
import app.models.tables
import app.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0040_auto_20190122_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tfinancement',
            name='chem_pj_fin',
            field=models.FileField(blank=True, default='', upload_to=app.models.tables.TFinancement.set_chem_pj_fin_upload_to, validators=[app.validators.val_fich_pdf], verbose_name='Insérer l\'arrêté de subvention <span class="field-complement">(fichier PDF)</span>'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tfinancement',
            name='comm_fin',
            field=models.TextField(blank=True, default='', verbose_name='Commentaire'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tfinancement',
            name='id_doss',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.TDossier'),
        ),
        migrations.AlterField(
            model_name='tfinancement',
            name='id_org_fin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.TFinanceur', verbose_name='Organisme financeur'),
        ),
        migrations.AlterField(
            model_name='tfinancement',
            name='id_paiem_prem_ac',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.TPaiementPremierAcompte', verbose_name='Premier acompte payé en fonction de'),
        ),
        migrations.AlterField(
            model_name='tfinancement',
            name='mont_elig_fin',
            field=app.classes.MFEuroField.Class(blank=True, decimal_places=2, max_digits=26, null=True, verbose_name="Montant [ht_ou_ttc] de l'assiette éligible de la subvention"),
        ),
        migrations.AlterField(
            model_name='tfinancement',
            name='mont_part_fin',
            field=app.classes.MFEuroField.Class(decimal_places=2, max_digits=26, verbose_name='Montant [ht_ou_ttc] total de la participation'),
        ),
        migrations.AlterField(
            model_name='tfinancement',
            name='num_arr_fin',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name="Numéro de l'arrêté ou convention"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tfinancement',
            name='pourc_elig_fin',
            field=app.classes.MFPercentField.Class(blank=True, decimal_places=3, max_digits=6, null=True, verbose_name="Pourcentage de l'assiette éligible"),
        ),
        migrations.AlterField(
            model_name='tfinancement',
            name='pourc_real_fin',
            field=app.classes.MFPercentField.Class(blank=True, decimal_places=3, max_digits=6, null=True, verbose_name='Pourcentage de réalisation des travaux'),
        ),
    ]
