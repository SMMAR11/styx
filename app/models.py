#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.functions import *
from django.contrib.auth.models import User
from django.db import models

# Je créé les tables de la base de données.
class TFamille(models.Model):

    # Je définis les champs de la table.
    id_fam = models.AutoField(primary_key = True)

    class Meta :
        db_table = 't_famille'
        verbose_name = 'Famille'

class TNatureDossier(models.Model):

    # Je définis les champs de la table.
    id_nat_doss = models.AutoField(primary_key = True)
    int_nat_doss = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_nature_dossier'
        verbose_name = 'Nature de dossier'
        verbose_name_plural = 'Natures de dossiers'

    def __str__(self) :
        return self.int_nat_doss

class TTechnicien(models.Model):

    # Je définis les champs de la table.
    id_techn = models.AutoField(primary_key = True)
    n_techn = models.CharField(max_length = 255, verbose_name = 'Nom')
    pren_techn = models.CharField(max_length = 255, verbose_name = 'Prénom')
    en_act = models.BooleanField(default = True, verbose_name = 'En activité')

    class Meta :
        db_table = 't_technicien'
        verbose_name = 'Technicien'

    def __str__(self) :
        return '{0} {1}'.format(self.n_techn, self.pren_techn)

class TAvisCp(models.Model):

    # Je définis les champs de la table.
    id_av_cp = models.AutoField(primary_key=True)
    int_av_cp = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_avis_cp'
        verbose_name = 'Avis du CP'
        verbose_name_plural = 'Avis du CP'

    def __str__(self) :
        return self.int_av_cp

class TAvancement(models.Model):

    # Je définis les champs de la table.
    id_av = models.AutoField(primary_key = True)
    int_av = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_avancement'
        verbose_name = 'Avancement'

    def __str__(self) :
        return self.int_av

class TProgramme(models.Model):

    # Je définis les champs de la table.
    id_progr = models.AutoField(primary_key = True)
    dim_progr = models.CharField(max_length = 255, verbose_name = 'Diminutif')
    int_progr = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    seq_progr = models.IntegerField(default = 1, verbose_name = 'Séquentiel')

    class Meta :
        db_table = 't_programme'
        verbose_name = 'Programme'

    def __str__(self) :
        return self.int_progr

class TAxe(models.Model):

    # Je définis les champs de la table.
    id_axe = models.CharField(primary_key = True, max_length = 255)
    int_axe = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    num_axe = models.IntegerField(verbose_name = 'Numéro')
    id_progr = models.ForeignKey(TProgramme, db_column = 'id_progr', verbose_name = 'Programme')

    class Meta :
        db_table = 't_axe'
        unique_together = (('num_axe', 'id_progr'))
        verbose_name = 'Axe'

    def __str__(self) :
        return '[{0}] {1} - {2}'.format(self.id_progr.int_progr, self.num_axe, self.int_axe)

    def save(self, *args, **kwargs) :
        self.id_axe = '{0}_{1}'.format(self.id_progr.id_progr, self.num_axe)
        super(TAxe, self).save(*args, **kwargs)

class TSousAxe(models.Model):

    # Je définis les champs de la table.
    id_ss_axe = models.CharField(primary_key = True, max_length = 255)
    ech_ss_axe = models.IntegerField(null = True, blank = True, verbose_name = 'Échéancier')
    int_ss_axe = models.CharField(max_length = 255, null = True, blank = True, verbose_name = 'Intitulé')
    mont_ht_ss_axe = models.FloatField(null = True, blank = True, verbose_name = 'Montant HT')
    mont_ttc_ss_axe = models.FloatField(null = True, blank = True, verbose_name = 'Montant TTC')
    num_ss_axe = models.IntegerField(verbose_name = 'Numéro')
    id_axe = models.ForeignKey(TAxe, db_column = 'id_axe', verbose_name = 'Axe')

    class Meta :
        db_table = 't_sous_axe'
        unique_together = (('num_ss_axe', 'id_axe'))
        verbose_name = 'Sous-axe'

    def __str__(self) :
        return '[{0}] {1}.{2} - {3}'.format(
            self.id_axe.id_progr.int_progr, self.id_axe.num_axe, self.num_ss_axe, self.int_ss_axe
        )

    def save(self, *args, **kwargs) :
        self.id_ss_axe = '{0}_{1}'.format(self.id_axe.id_axe, self.num_ss_axe)
        super(TSousAxe, self).save(*args, **kwargs)

class TAction(models.Model):

    # Je définis les champs de la table.
    id_act = models.CharField(primary_key = True, max_length = 255)
    ech_act = models.IntegerField(null = True, blank = True, verbose_name = 'Échéancier')
    int_act = models.CharField(max_length = 255, null = True, blank = True, verbose_name = 'Intitulé')
    mont_ht_act = models.FloatField(null = True, blank = True, verbose_name = 'Montant HT')
    mont_ttc_act = models.FloatField(null = True, blank = True, verbose_name = 'Montant TTC')
    num_act = models.IntegerField(
        verbose_name = 'Numéro',
        help_text = 'Veuillez renseigner l\'index de la lettre de l\'alphabet. Exemple : 1 -> a, 2 -> b, 3 -> c...'
    )
    id_ss_axe = models.ForeignKey(TSousAxe, db_column = 'id_ss_axe', verbose_name = 'Sous-axe')

    class Meta :
        db_table = 't_action'
        unique_together = (('num_act', 'id_ss_axe'))
        verbose_name = 'Action'

    def __str__(self) :
        return '[{0}] {1}.{2}.{3} - {4}'.format(
            self.id_ss_axe.id_axe.id_progr.int_progr, 
            self.id_ss_axe.id_axe.num_axe, 
            self.id_ss_axe.num_ss_axe, 
            index_alpha(self.num_act), 
            self.int_act
        )

    def save(self, *args, **kwargs) :
        self.id_act = '{0}_{1}'.format(self.id_ss_axe.id_ss_axe, self.num_act)
        super(TAction, self).save(*args, **kwargs)

class TTypeDossier(models.Model):

    # Je définis les champs de la table.
    id_type_doss = models.AutoField(primary_key = True)
    int_type_doss = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    id_progr = models.ForeignKey(TProgramme, db_column = 'id_progr', verbose_name = 'Programme')

    class Meta :
        db_table = 't_type_dossier'
        verbose_name = 'Type de dossier'
        verbose_name_plural = 'Types de dossiers'

    def __str__(self) :
        return self.int_type_doss

class TCommune(models.Model):

    # Je définis les champs de la table.
    num_comm = models.CharField(primary_key = True, max_length = 5, verbose_name = 'Code INSEE')
    cp_comm = models.TextField(verbose_name = 'Code postal')
    n_comm = models.CharField(max_length = 255, verbose_name = 'Nom')

    class Meta :
        db_table = 't_commune'
        verbose_name = 'Commune'

    def __str__(self) :
        return '{0} ({1})'.format(self.n_comm, self.num_comm)

class TOrganisme(models.Model):

    # Je définis les champs de la table.
    id_org = models.AutoField(primary_key = True)
    adr_org = models.CharField(max_length = 255, verbose_name = 'Adresse (ligne 1)')
    bp_org = models.CharField(max_length = 255, null = True, blank = True)
    comm_org = models.CharField(max_length = 255, null = True, blank = True, verbose_name = 'Commentaire')
    compl_adr_org = models.CharField(max_length = 255, null = True, blank = True, verbose_name = 'Adresse (ligne 2)')
    cont_org = models.CharField(max_length = 255, null = True, blank = True)
    courr_org = models.CharField(max_length = 255, null = True, blank = True, verbose_name = 'Adresse électronique')
    cp_org = models.CharField(max_length = 5, verbose_name = 'Code postal')
    n_org = models.CharField(max_length = 255, verbose_name = 'Nom')
    port_org = models.CharField(
        max_length = 10, null = True, blank = True, verbose_name = 'Numéro de téléphone portable'
    )
    site_web_org = models.CharField(max_length = 255, null = True, blank = True, verbose_name = 'Site web')
    tel_org = models.CharField(max_length = 10, null = True, blank = True, verbose_name = 'Numéro de téléphone')
    num_comm = models.ForeignKey(TCommune, db_column = 'num_comm', verbose_name = 'Commune')

    class Meta :
        db_table = 't_organisme'
        verbose_name = 'Organisme'

    def __str__(self) :
        return self.n_org

class TUtilisateur(User):

    # Je définis les champs de la table.
    id_util = models.OneToOneField(User, db_column = 'id_util')
    port_util = models.CharField(
        max_length = 10, null = True, blank = True, verbose_name = 'Numéro de téléphone portable'
    )
    tel_util = models.CharField(max_length = 10, null = True, blank = True, verbose_name = 'Numéro de téléphone')
    id_org = models.ForeignKey(TOrganisme, db_column = 'id_org', verbose_name = 'Organisme')

    class Meta :
        db_table = 't_utilisateur'
        verbose_name = 'Utilisateur'

    def __str__(self) :
        return self.id_util.username

class TMoa(TOrganisme):

    # Je définis les champs de la table.
    id_org_moa = models.OneToOneField(TOrganisme, db_column = 'id_org_moa')
    dim_org_moa = models.CharField(max_length = 255, verbose_name = 'Diminutif')
    en_act = models.BooleanField(default = True, verbose_name = 'En activité')

    class Meta:
        db_table = 't_moa'
        verbose_name = 'Maître d\'ouvrage'
        verbose_name_plural = 'Maîtres d\'ouvrages'

    def __str__(self) :
        return self.id_org_moa.n_org

class TRegroupementMoa(models.Model):

    # Je définis les champs de la table.
    id_org_moa_anc = models.ForeignKey(
        TMoa, 
        db_column = 'id_org_moa_anc',
        related_name = 'id_org_moa_anc',
        verbose_name = 'Maître d\'ouvrage ancien'
    )
    id_org_moa_fil = models.ForeignKey(
        TMoa,
        db_column = 'id_org_moa_fil',
        related_name = 'id_org_moa_fil',
        verbose_name = 'Maître d\'ouvrage par filiation'
    )

    class Meta:
        db_table = 't_regroupement_moa'
        unique_together = (('id_org_moa_anc', 'id_org_moa_fil'))
        verbose_name = 'Regroupement MOA'
        verbose_name_plural = 'Regroupement MOA'

    def __str__(self) :
        return '{0} - {1}'.format(self.id_org_moa_fil.id_org_moa.n_org, self.id_org_moa_anc.id_org_moa.n_org)

class TDroit(models.Model):

    # Je définis les champs de la table.
    id_org_moa = models.ForeignKey(TMoa, db_column = 'id_org_moa')
    id_progr = models.ForeignKey(TProgramme, db_column = 'id_progr')
    id_util = models.ForeignKey(TUtilisateur, db_column = 'id_util')
    en_ecr = models.BooleanField()
    en_lect = models.BooleanField()

    class Meta:
        db_table = 't_droit'
        verbose_name = 'Droit'
        unique_together = (('id_org_moa', 'id_progr', 'id_util'))

    def __str__(self) :
        return '{0} - {1} - {2}'.format(
            self.id_util.id_util.username, self.id_progr.int_progr, self.id_org_moa.id_org_moa.n_org
        )

class TDossier(models.Model):

    # Je définis les champs de la table.
    id_doss = models.AutoField(primary_key = True)
    chem_dds_doss = models.CharField(max_length = 255, null = True, blank = True)
    comm_doss = models.CharField(max_length = 255, null = True, blank = True)
    comm_regl_doss = models.CharField(max_length = 255, null = True, blank = True)
    descr_doss = models.CharField(max_length = 255, null = True, blank = True)
    dt_av_cp_doss = models.DateField(null = True, blank = True)
    dt_delib_moa_doss = models.DateField(null = True, blank = True)
    dt_int_doss = models.DateField()
    geom_doss = models.TextField(null = True, blank = True)
    int_doss = models.CharField(max_length = 255)
    mont_ht_doss = models.FloatField()
    mont_ttc_doss = models.FloatField()  
    num_act = models.IntegerField(null = True, blank = True)
    num_axe = models.IntegerField(null = True, blank = True)
    num_doss = models.CharField(max_length = 255, unique = True)
    num_ss_axe = models.IntegerField(null = True, blank = True)
    id_progr = models.ForeignKey(TProgramme, db_column = 'id_progr')
    id_av = models.ForeignKey(TAvancement, db_column = 'id_av')
    id_av_cp = models.ForeignKey(TAvisCp, db_column = 'id_av_cp')
    id_doss_ass = models.ForeignKey('self', db_column = 'id_doss_ass', null = True, blank = True)
    id_fam = models.ForeignKey(TFamille, db_column = 'id_fam')
    id_nat_doss = models.ForeignKey(TNatureDossier, db_column = 'id_nat_doss')
    id_org_moa = models.ForeignKey(TMoa, db_column = 'id_org_moa')
    id_techn = models.ForeignKey(TTechnicien, db_column = 'id_techn')
    id_type_doss = models.ForeignKey(TTypeDossier, db_column = 'id_type_doss', null = True, blank = True)

    class Meta:
        db_table = 't_dossier'
        verbose_name = 'Dossier'

    def __str__(self) :
        return self.num_doss

class TRiviere(models.Model):

    # Je définis les champs de la table.
    id_riv = models.AutoField(primary_key = True)
    n_riv = models.CharField(max_length = 255, verbose_name = 'Nom')

    class Meta:
        db_table = 't_riviere'
        verbose_name = 'Rivière'

    def __str__(self) :
        return self.n_riv

class TUnite(models.Model):

    # Je définis les champs de la table.
    id_unit = models.AutoField(primary_key = True)
    int_unit = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta:
        db_table = 't_unite'
        verbose_name = 'Unité'

    def __str__(self) :
        return self.int_unit

class TPortee(models.Model):

    # Je définis les champs de la table.
    id_port = models.AutoField(primary_key = True)
    int_port = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta:
        db_table = 't_portee'
        verbose_name = 'Portée de dossier'
        verbose_name_plural = 'Portées de dossiers'

    def __str__(self) :
        return self.int_port

class TPgre(TDossier):

    # Je définis les champs de la table.
    id_pgre = models.OneToOneField(TDossier, db_column = 'id_pgre')
    quant_objs_pgre = models.FloatField(null = True, blank = True)
    quant_real_pgre = models.FloatField(null = True, blank = True)
    id_port = models.ForeignKey(TPortee, db_column = 'id_port', null = True, blank = True)
    id_unit = models.ForeignKey(TUnite, db_column = 'id_unit', null = True, blank = True)

    class Meta:
        db_table = 't_pgre'
        verbose_name = 'Dossier PGRE'
        verbose_name_plural = 'Dossiers PGRE'

    def __str__(self) :
        return self.id_pgre.num_doss

class TRivieresDossier(models.Model):

    # Je définis les champs de la table.
    id_pgre = models.ForeignKey(TPgre, db_column = 'id_pgre')
    id_riv = models.ForeignKey(TRiviere, db_column = 'id_riv')

    class Meta:
        db_table = 't_rivieres_dossier'
        unique_together = (('id_pgre', 'id_riv'))
        verbose_name = 'Rivière impactée'
        verbose_name_plural = 'Rivières impactées'

    def __str__(self) :
        return '{0} - {1}'.format(self.id_pgre.id_pgre.num_doss, self.id_riv.n_riv)

class TPeriodePriseVuePhoto(models.Model):

    # Je définis les champs de la table.
    id_ppv_ph = models.AutoField(primary_key = True)
    int_ppv_ph = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta:
        db_table = 't_periode_prise_vue_photo'
        verbose_name = 'Période de prise de vue'
        verbose_name_plural = 'Périodes de prise de vue'

    def __str__(self) :
        return self.int_ppv_ph

class TPhoto(models.Model):

    # Je définis les champs de la table.
    id_ph = models.AutoField(primary_key = True)
    chem_ph = models.CharField(max_length = 255)
    descr_ph = models.CharField(max_length = 255, null = True, blank = True)
    dt_pv_ph = models.DateField(null = True, blank = True)
    geom_ph = models.TextField(null = True, blank = True)
    int_ph = models.CharField(max_length = 255)
    id_doss = models.ForeignKey(TDossier, db_column = 'id_doss')
    id_ppv_ph = models.ForeignKey(TPeriodePriseVuePhoto, db_column = 'id_ppv_ph')

    class Meta:
        db_table = 't_photo'
        verbose_name = 'Photo'

    def __str__(self) :
        return self.int_ph

class TTypeDeclaration(models.Model):

    # Je définis les champs de la table.
    id_type_decl = models.AutoField(primary_key = True)
    int_type_decl = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta:
        db_table = 't_type_declaration'
        verbose_name = 'Type de déclaration'
        verbose_name_plural = 'Types de déclarations'

    def __str__(self) :
        return self.int_type_decl

class TTypeAvancementArrete(models.Model):

    # Je définis les champs de la table.
    id_type_av_arr = models.AutoField(primary_key = True)
    int_type_av_arr = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta:
        db_table = 't_type_avancement_arrete'
        verbose_name = 'Avancement d\'un arrêté'
        verbose_name_plural = 'Avancements d\'un arrêté'

    def __str__(self) :
        return self.int_type_av_arr

class TArretesDossier(models.Model):

    # Je définis les champs de la table.
    id_doss = models.ForeignKey(TDossier, db_column = 'id_doss')
    id_type_av_arr = models.ForeignKey(TTypeAvancementArrete, db_column = 'id_type_av_arr')
    id_type_decl = models.ForeignKey(TTypeDeclaration, db_column = 'id_type_decl')
    chem_pj_arr = models.CharField(max_length = 255, null = True, blank = True)
    dt_lim_encl_trav_arr = models.DateField(null = True, blank = True)
    dt_sign_arr = models.DateField(null = True, blank = True)
    num_arr = models.CharField(max_length = 255, null = True, blank = True)

    class Meta:
        db_table = 't_arretes_dossier'
        unique_together = (('id_doss', 'id_type_decl'))
        verbose_name = 'Arrêtés d\'un dossier',
        verbose_name_plural = 'Arrêtés d\'un dossier'

    def __str__(self) :
        return '{0} - {1}'.format(self.id_doss.num_doss, self.id_type_decl.int_type_decl)

class TDepartement(models.Model):

    # Je définis les champs de la table.
    num_dep = models.CharField(primary_key = True, max_length = 3, verbose_name = 'Numéro')
    n_dep = models.CharField(max_length = 255, verbose_name = 'Nom')

    class Meta:
        db_table = 't_departement'
        verbose_name = 'Département'

    def __str__(self) :
        return '{0} ({1})'.format(self.n_dep, self.num_dep)

class TPrestataire(TOrganisme):

    # Je définis les champs de la table.
    id_org_prest = models.OneToOneField(TOrganisme, db_column = 'id_org_prest')
    siret_org_prest = models.CharField(max_length = 14, unique = True, verbose_name = 'Numéro SIRET')
    num_dep = models.ForeignKey(TDepartement, db_column = 'num_dep', verbose_name = 'Département')

    class Meta:
        db_table = 't_prestataire'
        verbose_name = 'Prestataire'

    def __str__(self) :
        return self.id_org_prest.n_org

class TFinanceur(TOrganisme):

    # Je définis les champs de la table.
    id_org_fin = models.OneToOneField(TOrganisme, db_column = 'id_org_fin')

    class Meta:
        db_table = 't_financeur'
        verbose_name = 'Financeur'

    def __str__(self) :
        return self.id_org_fin.n_org

class TNaturePrestation(models.Model):

    # Je définis les champs de la table.
    id_nat_prest = models.AutoField(primary_key = True)
    int_nat_prest = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta:
        db_table = 't_nature_prestation'
        verbose_name = 'Nature de prestation'
        verbose_name_plural = 'Natures de prestations'

    def __str__(self) :
        return self.int_nat_prest

class TPrestation(models.Model):

    # Je définis les champs de la table.
    id_prest = models.AutoField(primary_key = True)
    chem_pj_prest = models.CharField(max_length = 255, null = True, blank = True)
    comm_prest = models.CharField(max_length = 255, null = True, blank = True)
    dt_fin_prest = models.DateField(null = True, blank = True)
    dt_notif_prest = models.DateField(null = True, blank = True)
    int_prest = models.CharField(max_length = 255)
    mont_ht_tot_prest = models.FloatField()
    mont_ttc_tot_prest = models.FloatField()
    id_nat_prest = models.ForeignKey(TNaturePrestation, db_column = 'id_nat_prest')
    id_org_prest = models.ForeignKey(TPrestataire, db_column = 'id_org_prest')

    class Meta:
        db_table = 't_prestation'
        verbose_name = 'Prestation'

    def __str__(self) :
        return self.int_prest

class TPrestationsDossier(models.Model):

    # Je définis les champs de la table.
    id_doss = models.ForeignKey(TDossier, db_column = 'id_doss')
    id_prest = models.ForeignKey(TPrestation, db_column = 'id_prest')
    mont_ht_prest = models.FloatField()
    mont_ttc_prest = models.FloatField()

    class Meta:
        db_table = 't_prestations_dossier'
        unique_together = (('id_doss', 'id_prest'))
        verbose_name = 'Prestations d\'un dossier'
        verbose_name_plural = 'Prestations d\'un dossier'

    def __str__(self) :
        return '{0} - {1}'.format(self.id_prest.int_prest, self.id_doss.num_doss)

class TAvenant(models.Model):

    # Je définis les champs de la table.
    id_aven = models.AutoField(primary_key = True)
    dt_aven = models.DateField(null = True, blank = True)
    int_aven = models.CharField(max_length = 255)
    mont_ht_aven = models.FloatField()
    mont_ttc_aven = models.FloatField()
    id_prest = models.ForeignKey(TPrestation, db_column = 'id_prest')

    class Meta:
        db_table = 't_avenant'
        verbose_name = 'Avenant'

    def __str__(self) :
        return self.int_aven

class TFacture(models.Model):

    # Je définis les champs de la table.
    id_fact = models.AutoField(primary_key = True)
    chem_pj_fact = models.CharField(max_length = 255, null = True, blank = True)
    comm_fact = models.CharField(max_length = 255, null = True, blank = True)
    dt_mep_fact = models.DateField(null = True, blank = True)
    dt_rec_fact = models.DateField(null = True, blank = True)
    int_fact = models.CharField(max_length = 255)
    mont_ht_fact = models.FloatField()
    mont_ttc_fact = models.FloatField()
    num_bord = models.CharField(max_length = 255, null = True, blank = True)
    num_mandat = models.CharField(max_length = 255, null = True, blank = True)
    id_doss = models.ForeignKey(TDossier, db_column = 'id_doss')
    id_prest = models.ForeignKey(TPrestation, db_column = 'id_prest')

    class Meta:
        db_table = 't_facture'
        verbose_name = 'Facture'

    def __str__(self) :
        return self.int_fact

class TPaiementPremierAcompte(models.Model):

    # Je définis les champs de la table.
    id_paiem_prem_ac = models.AutoField(primary_key = True)
    int_paiem_prem_ac = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta:
        db_table = 't_paiement_premier_acompte'
        verbose_name = 'Paiement du 1er acompte'
        verbose_name_plural = 'Paiements du 1er acompte'

    def __str__(self) :
        return self.int_paiem_prem_ac

class TFinancement(models.Model):

    # Je définis les champs de la table.
    id_fin = models.AutoField(primary_key = True)
    chem_pj_fin = models.CharField(max_length = 255, null = True, blank = True)
    comm_fin = models.CharField(max_length = 255, null = True, blank = True)
    dt_deb_elig_fin = models.DateField(null = True, blank = True)
    dt_lim_deb_oper_fin = models.DateField(null = True, blank = True)
    dt_lim_prem_ac_fin = models.DateField(null = True, blank = True)
    duree_pror_fin = models.IntegerField(default = 0)
    duree_valid_fin = models.IntegerField()
    int_fin = models.CharField(max_length = 255)
    mont_ht_elig_fin = models.FloatField()
    mont_ht_tot_subv_fin = models.FloatField()
    mont_ttc_elig_fin = models.FloatField()
    mont_ttc_tot_subv_fin = models.FloatField()
    pourc_elig_fin = models.FloatField()
    pourc_real_fin = models.FloatField(null = True, blank = True)
    id_doss = models.ForeignKey(TDossier, db_column = 'id_doss')
    id_org_fin = models.ForeignKey(TFinanceur, db_column = 'id_org_fin')
    id_paiem_prem_ac = models.ForeignKey(TPaiementPremierAcompte, db_column = 'id_paiem_prem_ac')

    class Meta:
        db_table = 't_financement'
        verbose_name = 'Financement'

    def __str__(self) :
        return self.int_fin

class TTypeVersement(models.Model):

    # Je définis les champs de la table.
    id_type_vers = models.AutoField(primary_key = True)
    int_type_vers = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta:
        db_table = 't_type_versement'
        verbose_name = 'Type de versement'
        verbose_name_plural = 'Types de versements'

    def __str__(self) :
        return self.int_type_vers

class TPaiement(models.Model):

    # Je définis les champs de la table.
    id_fact = models.ForeignKey(TFacture, db_column = 'id_fact')
    id_fin = models.ForeignKey(TFinancement, db_column = 'id_fin')
    id_type_vers = models.ForeignKey(TTypeVersement, db_column = 'id_type_vers')
    chem_pj_paiem = models.CharField(max_length = 255, null = True, blank = True)
    comm_dem_vers = models.CharField(max_length = 255, null = True, blank = True)
    dt_dem_vers = models.DateField(null = True, blank = True)
    dt_vers_paiem = models.DateField(null = True, blank = True)
    int_dem_vers = models.CharField(max_length = 255)
    mont_ht_dem_vers = models.FloatField()
    mont_ht_verse = models.FloatField()
    mont_ttc_dem_vers = models.FloatField()
    mont_ttc_verse = models.FloatField()

    class Meta:
        db_table = 't_paiement'
        unique_together = (('id_fact', 'id_fin'))
        verbose_name = 'Demande de versement'
        verbose_name_plural = 'Demandes de versements'

    def __str__(self) :
        return self.int_dem_vers