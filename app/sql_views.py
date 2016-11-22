#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.models import *
from django.db import models

# Je créé le modèle de chaque vue utile de la base de données.
class VFinancement(models.Model):

    # Je définis les champs de la vue.
    id_fin = models.IntegerField(primary_key = True)
    chem_pj_fin = models.CharField(max_length = 255)
    comm_fin = models.CharField(max_length = 255)
    dt_deb_elig_fin = models.DateField()
    dt_fin_elig_fin = models.DateField()
    dt_lim_deb_oper_fin = models.DateField()
    dt_lim_prem_ac_fin = models.DateField()
    duree_pror_fin = models.IntegerField()
    duree_valid_fin = models.IntegerField()
    int_fin = models.CharField(max_length = 255)
    mont_ht_elig_fin = models.FloatField()
    mont_ht_tot_subv_fin = models.FloatField()
    mont_ttc_elig_fin = models.FloatField()
    mont_ttc_tot_subv_fin = models.FloatField()
    pourc_elig_fin = models.FloatField()
    pourc_fact_fin = models.FloatField()
    pourc_real_fin = models.FloatField()
    id_doss = models.ForeignKey(TDossier, db_column = 'id_doss')
    id_org_fin = models.ForeignKey(TFinanceur, db_column = 'id_org_fin')
    id_paiem_prem_ac = models.ForeignKey(TPaiementPremierAcompte, db_column = 'id_paiem_prem_ac')

    class Meta:
        db_table = 'v_financement'
        managed = False

class VPrestation(models.Model):

    # Je définis les champs de la vue.
    id_prest = models.IntegerField(primary_key = True)
    chem_pj_prest = models.CharField(max_length = 255)
    comm_prest = models.CharField(max_length = 255)
    dt_fin_prest = models.DateField()
    dt_notif_prest = models.DateField()
    int_prest = models.CharField(max_length = 255)
    mont_ht_tot_prest = models.FloatField()
    mont_ttc_tot_prest = models.FloatField()
    id_nat_prest = models.ForeignKey(TNaturePrestation, db_column = 'id_nat_prest')
    id_org_prest = models.ForeignKey(TPrestataire, db_column = 'id_org_prest')
    mont_ht_aven_sum = models.FloatField()
    mont_ttc_aven_sum = models.FloatField()
    mont_ht_tot_prest_aven = models.FloatField()
    mont_ttc_tot_prest_aven = models.FloatField()

    class Meta:
        db_table = 'v_prestation'
        managed = False

class VSuiviDossier(models.Model):

    # Je définis les champs de la vue.
    id_doss = models.IntegerField(primary_key = True)
    mont_ht_doss = models.FloatField()
    mont_ttc_doss = models.FloatField()
    mont_ht_elig_fin_sum = models.FloatField()
    mont_ttc_elig_fin_sum = models.FloatField()
    mont_ht_prest_sum = models.FloatField()
    mont_ttc_prest_sum = models.FloatField()
    mont_ht_raf = models.FloatField()
    mont_ttc_raf = models.FloatField()
    mont_ht_rau = models.FloatField()
    mont_ttc_rau = models.FloatField()
    en_proj = models.IntegerField()

    class Meta:
        db_table = 'v_suivi_dossier'
        managed = False

class VSuiviPrestationsDossier(models.Model):

    # Je définis les champs de la vue.
    id_doss = models.IntegerField(primary_key = True)
    id_prest = models.IntegerField(primary_key = True)
    mont_ht_prest = models.FloatField()
    mont_ttc_prest = models.FloatField()
    mont_ht_fact_sum = models.FloatField()
    mont_ttc_fact_sum = models.FloatField()
    mont_ht_rap = models.FloatField()
    mont_ttc_rap = models.FloatField()

    class Meta:
        db_table = 'v_suivi_prestations_dossier'
        managed = False