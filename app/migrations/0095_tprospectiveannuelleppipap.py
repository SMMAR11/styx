# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2021-05-20 11:10
from __future__ import unicode_literals

import app.classes.MFEuroField
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0094_auto_20210520_0835'),
    ]

    operations = [
        migrations.CreateModel(
            name='TProspectiveAnnuellePpiPap',
            fields=[
                ('pap_id', models.AutoField(primary_key=True, serialize=False)),
                ('pap_an', models.IntegerField(verbose_name='Année')),
                ('pap_dps_eli_fctva', app.classes.MFEuroField.Class(decimal_places=2, max_digits=26, verbose_name='Dépenses éligibles FCTVA (en €)')),
                ('pap_dps_ttc_rp', app.classes.MFEuroField.Class(decimal_places=2, max_digits=26, verbose_name='Dépenses TTC réelles projetées (en €)')),
                ('pap_vsm_previ_rp', app.classes.MFEuroField.Class(decimal_places=2, max_digits=26, verbose_name='Versements prévisionnels réels projetés (en €)')),
                ('ppi_id', models.ForeignKey(db_column='ppi_id', on_delete=django.db.models.deletion.CASCADE, to='app.TPlanPluriannuelInvestissementPpi')),
            ],
            options={
                'db_table': 't_prospective_annuelle_ppi_pap',
                'ordering': ['pap_an'],
            },
        ),
    ]
