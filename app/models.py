# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class TAction(models.Model):
    id_act = models.IntegerField(primary_key=True)
    ech_act = models.IntegerField(blank=True, null=True)
    int_act = models.CharField(max_length=255, blank=True, null=True)
    mont_ht_act = models.FloatField(blank=True, null=True)
    mont_ttc_act = models.FloatField(blank=True, null=True)
    id_progr = models.ForeignKey('TProgramme', models.DO_NOTHING, db_column='id_progr', primary_key=True)
    id_axe = models.ForeignKey('TAxe', models.DO_NOTHING, db_column='id_axe', primary_key=True)
    id_ss_axe = models.ForeignKey('TSousAxe', models.DO_NOTHING, db_column='id_ss_axe')

    class Meta:
        managed = False
        db_table = 't_action'
        unique_together = (('id_act', 'id_ss_axe', 'id_axe', 'id_progr'),)


class TArretesDossier(models.Model):
    id_doss = models.ForeignKey('TDossier', models.DO_NOTHING, db_column='id_doss', primary_key=True)
    id_type_av_arr = models.ForeignKey('TTypeAvancementArrete', models.DO_NOTHING, db_column='id_type_av_arr', primary_key=True)
    id_type_decl = models.ForeignKey('TTypeDeclaration', models.DO_NOTHING, db_column='id_type_decl', primary_key=True)
    chem_pj_arr = models.CharField(max_length=255, blank=True, null=True)
    dt_lim_encl_trav_arr = models.DateField(blank=True, null=True)
    dt_sign_arr = models.DateField(blank=True, null=True)
    num_arr = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_arretes_dossier'
        unique_together = (('id_doss', 'id_type_av_arr', 'id_type_decl'),)


class TAvancement(models.Model):
    id_av = models.AutoField(primary_key=True)
    int_av = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_avancement'


class TAvenant(models.Model):
    id_aven = models.AutoField(primary_key=True)
    dt_aven = models.DateField(blank=True, null=True)
    int_aven = models.CharField(max_length=255)
    mont_ht_aven = models.FloatField()
    mont_ttc_aven = models.FloatField()
    id_prest = models.ForeignKey('TPrestation', models.DO_NOTHING, db_column='id_prest')

    class Meta:
        managed = False
        db_table = 't_avenant'


class TAvisCp(models.Model):
    id_av_cp = models.AutoField(primary_key=True)
    int_av_cp = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_avis_cp'


class TAxe(models.Model):
    id_axe = models.IntegerField(primary_key=True)
    int_axe = models.CharField(max_length=255, blank=True, null=True)
    id_progr = models.ForeignKey('TProgramme', models.DO_NOTHING, db_column='id_progr', primary_key=True)

    class Meta:
        managed = False
        db_table = 't_axe'
        unique_together = (('id_axe', 'id_progr'),)


class TCommune(models.Model):
    num_comm = models.CharField(primary_key=True, max_length=5)
    cp_comm = models.TextField()
    n_comm = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_commune'


class TDepartement(models.Model):
    num_dep = models.CharField(primary_key=True, max_length=3)
    n_dep = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_departement'


class TDossier(models.Model):
    id_doss = models.AutoField(primary_key=True)
    chem_dds_doss = models.CharField(max_length=255, blank=True, null=True)
    comm_doss = models.CharField(max_length=255, blank=True, null=True)
    comm_regl_doss = models.CharField(max_length=255, blank=True, null=True)
    descr_doss = models.CharField(max_length=255, blank=True, null=True)
    dt_av_cp_doss = models.DateField(blank=True, null=True)
    dt_delib_moa_doss = models.DateField(blank=True, null=True)
    dt_int_doss = models.DateField()
    geom_doss = models.TextField(blank=True, null=True)
    int_doss = models.CharField(max_length=255)
    mont_ht_doss = models.FloatField()
    mont_ttc_doss = models.FloatField()
    num_doss = models.CharField(max_length=255)
    id_act = models.IntegerField(blank=True, null=True)
    id_ss_axe = models.IntegerField(blank=True, null=True)
    id_axe = models.IntegerField(blank=True, null=True)
    id_progr = models.ForeignKey('TProgramme', models.DO_NOTHING, db_column='id_progr')
    id_av = models.ForeignKey(TAvancement, models.DO_NOTHING, db_column='id_av')
    id_av_cp = models.ForeignKey(TAvisCp, models.DO_NOTHING, db_column='id_av_cp')
    id_doss_ass = models.ForeignKey('self', models.DO_NOTHING, db_column='id_doss_ass', blank=True, null=True)
    id_fam = models.ForeignKey('TFamille', models.DO_NOTHING, db_column='id_fam')
    id_nat_doss = models.ForeignKey('TNatureDossier', models.DO_NOTHING, db_column='id_nat_doss')
    id_org_moa = models.ForeignKey('TMoa', models.DO_NOTHING, db_column='id_org_moa')
    id_techn = models.ForeignKey('TTechnicien', models.DO_NOTHING, db_column='id_techn')
    id_type_doss = models.ForeignKey('TTypeDossier', models.DO_NOTHING, db_column='id_type_doss', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_dossier'


class TDroit(models.Model):
    id_org_moa = models.ForeignKey('TMoa', models.DO_NOTHING, db_column='id_org_moa', primary_key=True)
    id_progr = models.ForeignKey('TProgramme', models.DO_NOTHING, db_column='id_progr', primary_key=True)
    id_util = models.ForeignKey('TUtilisateur', models.DO_NOTHING, db_column='id_util', primary_key=True)
    en_ecr = models.IntegerField()
    en_lect = models.IntegerField()

    class Meta:
        managed = False
        db_table = 't_droit'
        unique_together = (('id_org_moa', 'id_progr', 'id_util'),)


class TFacture(models.Model):
    id_fact = models.AutoField(primary_key=True)
    chem_pj_fact = models.CharField(max_length=255, blank=True, null=True)
    comm_fact = models.CharField(max_length=255, blank=True, null=True)
    dt_mep_fact = models.DateField(blank=True, null=True)
    dt_rec_fact = models.DateField(blank=True, null=True)
    int_fact = models.CharField(max_length=255)
    mont_ht_fact = models.FloatField()
    mont_ttc_fact = models.FloatField()
    num_bord = models.CharField(max_length=255, blank=True, null=True)
    num_mandat = models.CharField(max_length=255, blank=True, null=True)
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING, db_column='id_doss')
    id_prest = models.ForeignKey('TPrestation', models.DO_NOTHING, db_column='id_prest')

    class Meta:
        managed = False
        db_table = 't_facture'


class TFamille(models.Model):
    id_fam = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 't_famille'


class TFinancement(models.Model):
    id_fin = models.AutoField(primary_key=True)
    chem_pj_fin = models.CharField(max_length=255, blank=True, null=True)
    comm_fin = models.CharField(max_length=255, blank=True, null=True)
    dt_deb_elig_fin = models.DateField(blank=True, null=True)
    dt_lim_deb_oper_fin = models.DateField(blank=True, null=True)
    dt_lim_prem_ac_fin = models.DateField(blank=True, null=True)
    duree_pror_fin = models.IntegerField(blank=True, null=True)
    duree_valid_fin = models.IntegerField()
    int_fin = models.CharField(max_length=255)
    mont_ht_elig_fin = models.FloatField()
    mont_ht_tot_subv_fin = models.FloatField()
    mont_ttc_elig_fin = models.FloatField()
    mont_ttc_tot_subv_fin = models.FloatField()
    pourc_elig_fin = models.FloatField()
    pourc_real_fin = models.FloatField(blank=True, null=True)
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING, db_column='id_doss')
    id_org_fin = models.ForeignKey('TFinanceur', models.DO_NOTHING, db_column='id_org_fin')
    id_paiem_prem_ac = models.ForeignKey('TPaiementPremierAcompte', models.DO_NOTHING, db_column='id_paiem_prem_ac')

    class Meta:
        managed = False
        db_table = 't_financement'


class TFinanceur(models.Model):
    id_org_fin = models.ForeignKey('TOrganisme', models.DO_NOTHING, db_column='id_org_fin', primary_key=True)

    class Meta:
        managed = False
        db_table = 't_financeur'


class TMoa(models.Model):
    id_org_moa = models.ForeignKey('TOrganisme', models.DO_NOTHING, db_column='id_org_moa', primary_key=True)
    dim_org_moa = models.CharField(max_length=255)
    en_act = models.IntegerField()

    class Meta:
        managed = False
        db_table = 't_moa'


class TNatureDossier(models.Model):
    id_nat_doss = models.AutoField(primary_key=True)
    int_nat_doss = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_nature_dossier'


class TNaturePrestation(models.Model):
    id_nat_prest = models.AutoField(primary_key=True)
    int_nat_prest = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_nature_prestation'


class TOrganisme(models.Model):
    id_org = models.AutoField(primary_key=True)
    adr_org = models.CharField(max_length=255)
    bp_org = models.CharField(max_length=255, blank=True, null=True)
    comm_org = models.CharField(max_length=255, blank=True, null=True)
    compl_adr_org = models.CharField(max_length=255, blank=True, null=True)
    cont_org = models.CharField(max_length=255, blank=True, null=True)
    courr_org = models.CharField(max_length=255, blank=True, null=True)
    cp_org = models.CharField(max_length=5)
    n_org = models.CharField(max_length=255)
    port_org = models.CharField(max_length=10, blank=True, null=True)
    siret_org = models.CharField(max_length=14, blank=True, null=True)
    site_web_org = models.CharField(max_length=255, blank=True, null=True)
    tel_org = models.CharField(max_length=10, blank=True, null=True)
    num_comm = models.ForeignKey(TCommune, models.DO_NOTHING, db_column='num_comm')

    class Meta:
        managed = False
        db_table = 't_organisme'


class TPaiement(models.Model):
    id_fact = models.ForeignKey(TFacture, models.DO_NOTHING, db_column='id_fact', primary_key=True)
    id_fin = models.ForeignKey(TFinancement, models.DO_NOTHING, db_column='id_fin', primary_key=True)
    id_type_vers = models.ForeignKey('TTypeVersement', models.DO_NOTHING, db_column='id_type_vers', primary_key=True)
    chem_pj_paiem = models.CharField(max_length=255, blank=True, null=True)
    comm_dem_vers = models.CharField(max_length=255, blank=True, null=True)
    dt_dem_vers = models.DateField(blank=True, null=True)
    dt_vers_paiem = models.DateField(blank=True, null=True)
    int_dem_vers = models.CharField(max_length=255)
    mont_ht_dem_vers = models.FloatField()
    mont_ht_verse = models.FloatField()
    mont_ttc_dem_vers = models.FloatField()
    mont_ttc_verse = models.FloatField()

    class Meta:
        managed = False
        db_table = 't_paiement'
        unique_together = (('id_fact', 'id_fin', 'id_type_vers'),)


class TPaiementPremierAcompte(models.Model):
    id_paiem_prem_ac = models.AutoField(primary_key=True)
    int_paiem_prem_ac = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_paiement_premier_acompte'


class TPeriodePriseVuePhoto(models.Model):
    id_ppv_ph = models.AutoField(primary_key=True)
    int_ppv_ph = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_periode_prise_vue_photo'


class TPgre(models.Model):
    id_pgre = models.ForeignKey(TDossier, models.DO_NOTHING, db_column='id_pgre', primary_key=True)
    quant_objs_pgre = models.FloatField(blank=True, null=True)
    quant_real_pgre = models.FloatField(blank=True, null=True)
    id_port = models.ForeignKey('TPortee', models.DO_NOTHING, db_column='id_port', blank=True, null=True)
    id_unit = models.ForeignKey('TUnite', models.DO_NOTHING, db_column='id_unit', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_pgre'


class TPhoto(models.Model):
    id_ph = models.AutoField(primary_key=True)
    chem_ph = models.CharField(max_length=255)
    descr_ph = models.CharField(max_length=255, blank=True, null=True)
    dt_pv_ph = models.DateField(blank=True, null=True)
    geom_ph = models.TextField(blank=True, null=True)
    int_ph = models.CharField(max_length=255)
    num_ph = models.CharField(max_length=255, null=True)
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING, db_column='id_doss')
    id_ppv_ph = models.ForeignKey(TPeriodePriseVuePhoto, models.DO_NOTHING, db_column='id_ppv_ph')

    class Meta:
        managed = False
        db_table = 't_photo'


class TPortee(models.Model):
    id_port = models.AutoField(primary_key=True)
    int_port = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_portee'


class TPrestataire(models.Model):
    id_org_prest = models.ForeignKey(TOrganisme, models.DO_NOTHING, db_column='id_org_prest', primary_key=True)
    num_dep = models.ForeignKey(TDepartement, models.DO_NOTHING, db_column='num_dep')

    class Meta:
        managed = False
        db_table = 't_prestataire'


class TPrestation(models.Model):
    id_prest = models.AutoField(primary_key=True)
    chem_pj_prest = models.CharField(max_length=255, blank=True, null=True)
    comm_prest = models.CharField(max_length=255, blank=True, null=True)
    dt_fin_prest = models.DateField(blank=True, null=True)
    dt_notif_prest = models.DateField(blank=True, null=True)
    int_prest = models.CharField(max_length=255)
    mont_ht_tot_prest = models.FloatField()
    mont_ttc_tot_prest = models.FloatField()
    id_nat_prest = models.ForeignKey(TNaturePrestation, models.DO_NOTHING, db_column='id_nat_prest')
    id_org_prest = models.ForeignKey(TPrestataire, models.DO_NOTHING, db_column='id_org_prest')

    class Meta:
        managed = False
        db_table = 't_prestation'


class TPrestationsDossier(models.Model):
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING, db_column='id_doss', primary_key=True)
    id_prest = models.ForeignKey(TPrestation, models.DO_NOTHING, db_column='id_prest', primary_key=True)
    mont_ht_prest = models.FloatField()
    mont_ttc_prest = models.FloatField()

    class Meta:
        managed = False
        db_table = 't_prestations_dossier'
        unique_together = (('id_doss', 'id_prest'),)


class TProgramme(models.Model):
    id_progr = models.AutoField(primary_key=True)
    dim_progr = models.CharField(max_length=255)
    int_progr = models.CharField(max_length=255)
    seq_progr = models.IntegerField()

    class Meta:
        managed = False
        db_table = 't_programme'


class TRegroupementMoa(models.Model):
    id_org_moa_anc = models.ForeignKey(TMoa, models.DO_NOTHING, db_column='id_org_moa_anc', primary_key=True, related_name='id_org_moa_anc')
    id_org_moa_fil = models.ForeignKey(TMoa, models.DO_NOTHING, db_column='id_org_moa_fil', primary_key=True, related_name='id_org_moa_fil')

    class Meta:
        managed = False
        db_table = 't_regroupement_moa'
        unique_together = (('id_org_moa_anc', 'id_org_moa_fil'),)


class TRiviere(models.Model):
    id_riv = models.AutoField(primary_key=True)
    n_riv = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_riviere'


class TRivieresDossier(models.Model):
    id_pgre = models.ForeignKey(TPgre, models.DO_NOTHING, db_column='id_pgre', primary_key=True)
    id_riv = models.ForeignKey(TRiviere, models.DO_NOTHING, db_column='id_riv', primary_key=True)

    class Meta:
        managed = False
        db_table = 't_rivieres_dossier'
        unique_together = (('id_pgre', 'id_riv'),)


class TSousAxe(models.Model):
    id_ss_axe = models.IntegerField(primary_key=True)
    ech_ss_axe = models.IntegerField(blank=True, null=True)
    int_ss_axe = models.CharField(max_length=255, blank=True, null=True)
    mont_ht_ss_axe = models.FloatField(blank=True, null=True)
    mont_ttc_ss_axe = models.FloatField(blank=True, null=True)
    id_progr = models.ForeignKey(TProgramme, models.DO_NOTHING, db_column='id_progr', primary_key=True)
    id_axe = models.ForeignKey(TAxe, models.DO_NOTHING, db_column='id_axe', primary_key=True)

    class Meta:
        managed = False
        db_table = 't_sous_axe'
        unique_together = (('id_ss_axe', 'id_axe', 'id_progr'),)


class TTechnicien(models.Model):
    id_techn = models.AutoField(primary_key=True)
    en_act = models.IntegerField()
    n_techn = models.CharField(max_length=255)
    pren_techn = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_technicien'


class TTypeAvancementArrete(models.Model):
    id_type_av_arr = models.AutoField(primary_key=True)
    int_type_av_arr = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_type_avancement_arrete'


class TTypeDeclaration(models.Model):
    id_type_decl = models.AutoField(primary_key=True)
    int_type_decl = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_type_declaration'


class TTypeDossier(models.Model):
    id_type_doss = models.AutoField(primary_key=True)
    int_type_doss = models.CharField(max_length=255)
    id_progr = models.ForeignKey(TProgramme, models.DO_NOTHING, db_column='id_progr')

    class Meta:
        managed = False
        db_table = 't_type_dossier'


class TTypeVersement(models.Model):
    id_type_vers = models.AutoField(primary_key=True)
    int_type_vers = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_type_versement'


class TUnite(models.Model):
    id_unit = models.AutoField(primary_key=True)
    int_unit = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 't_unite'


class TUtilisateur(models.Model):
    id_util = models.AutoField(primary_key=True)
    courr_util = models.CharField(max_length=255)
    jet_util = models.CharField(max_length=40, blank=True, null=True)
    mdp_util = models.CharField(max_length=40)
    n_util = models.CharField(max_length=255)
    port_util = models.CharField(max_length=10, blank=True, null=True)
    pren_util = models.CharField(max_length=255)
    pseudo_util = models.CharField(max_length=255)
    tel_util = models.CharField(max_length=10, blank=True, null=True)
    id_org = models.ForeignKey(TOrganisme, models.DO_NOTHING, db_column='id_org')

    class Meta:
        managed = False
        db_table = 't_utilisateur'
