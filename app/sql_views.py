#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.models import *
from django.db import models

class VSuiviDossier(models.Model) :

    id_doss = models.IntegerField(primary_key = True)
    mont_doss = models.FloatField()
    est_ttc_doss = models.BooleanField()
    mont_part_fin_sum = models.FloatField()
    mont_prest_doss_sum = models.FloatField()
    mont_aven_sum = models.FloatField()
    mont_tot_prest_doss = models.FloatField()
    mont_raf = models.FloatField()
    mont_rae = models.FloatField()

    class Meta :
        db_table = 'v_suivi_dossier'
        managed = False

class VFinancement(models.Model) :

    id_fin = models.IntegerField(primary_key = True)
    chem_pj_fin = models.CharField(max_length = 255)
    comm_fin = models.TextField()
    dt_deb_elig_fin = models.DateField()
    dt_fin_elig_fin = models.DateField()
    dt_lim_deb_oper_fin = models.DateField()
    dt_lim_prem_ac_fin = models.DateField()
    duree_pror_fin = models.IntegerField()
    duree_valid_fin = models.IntegerField()
    mont_ddv_sum = models.FloatField()
    mont_elig_fin = models.FloatField()
    mont_part_fin = models.FloatField()
    mont_rad = models.FloatField()
    num_arr_fin = models.CharField(max_length = 255)
    pourc_elig_fin = models.FloatField()
    pourc_glob_fin = models.FloatField()
    pourc_real_fin = models.FloatField()
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING, db_column = 'id_doss_id')
    id_org_fin = models.ForeignKey(TFinanceur, models.DO_NOTHING, db_column = 'id_org_fin_id')
    id_paiem_prem_ac = models.ForeignKey(TPaiementPremierAcompte, models.DO_NOTHING, db_column = 'id_paiem_prem_ac_id')

    class Meta :
        db_table = 'v_financement'
        managed = False

class VSuiviPrestationsDossier(models.Model) :

    id_prest_doss = models.IntegerField(db_column = 'id', primary_key = True)
    id_prest = models.ForeignKey(TPrestation, models.DO_NOTHING, db_column = 'id_prest_id')
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING, db_column = 'id_doss_id')
    mont_prest_doss = models.FloatField()
    nb_aven = models.IntegerField()
    mont_aven_sum = models.FloatField()  
    nb_fact = models.IntegerField()
    mont_ht_fact_sum = models.FloatField()
    mont_ttc_fact_sum = models.FloatField()
    mont_tot_prest_doss = models.FloatField()
    mont_raf = models.FloatField()

    class Meta :
        db_table = 'v_suivi_prestations_dossier'
        managed = False

class VDemandeVersement(models.Model) :

    # Je définis les champs de la table.
    id_ddv = models.IntegerField(primary_key = True)
    chem_pj_ddv = models.CharField(max_length = 255)
    comm_ddv = models.TextField()
    dt_ddv = models.DateField()
    dt_vers_ddv = models.DateField()
    int_ddv = models.CharField(max_length = 255)
    map_ht_ddv = models.FloatField()
    map_ttc_ddv = models.FloatField()
    mont_ht_ddv = models.FloatField()
    mont_ht_verse_ddv = models.FloatField()
    mont_ttc_ddv = models.FloatField()
    mont_ttc_verse_ddv = models.FloatField()
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING, db_column = 'id_doss_id')
    id_fin = models.ForeignKey(TFinancement, models.DO_NOTHING, db_column = 'id_fin_id')
    id_org_fin = models.ForeignKey(TFinanceur, models.DO_NOTHING, db_column = 'id_org_fin_id')
    id_type_vers = models.ForeignKey(TTypeVersement, models.DO_NOTHING, db_column = 'id_type_vers_id')

    class Meta :
        db_table = 'v_demande_versement'
        managed = False