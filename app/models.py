#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gismodels
from django.db import models
import uuid

class TFamille(models.Model) :

    id_fam = models.AutoField(primary_key = True)

    class Meta :
    	db_table = 't_famille'
    	verbose_name = 'T_FAMILLE'
    	verbose_name_plural = 'T_FAMILLE'

    def __str__(self) :
    	return self.id_fam

class TNatureDossier(models.Model) :

    id_nat_doss = models.AutoField(primary_key = True)
    int_nat_doss = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    peu_doss = models.BooleanField(
        verbose_name = 'Autorisée (gestion des dossiers)'
    )
    peu_doss_pgre = models.BooleanField(
        verbose_name = 'Autorisée (gestion des actions PGRE)'
    )

    class Meta :
        db_table = 't_nature_dossier'
        ordering = ['int_nat_doss']
        verbose_name = 'T_NATURE_DOSSIER'
        verbose_name_plural = 'T_NATURE_DOSSIER'

    def __str__(self) :
        return self.int_nat_doss

class TTechnicien(models.Model) :

    id_techn = models.AutoField(primary_key = True)
    en_act = models.BooleanField(default = True, verbose_name = 'En activité')
    n_techn = models.CharField(max_length = 255, verbose_name = 'Nom de famille')
    pren_techn = models.CharField(max_length = 255, verbose_name = 'Prénom')

    class Meta :
        db_table = 't_technicien'
        ordering = ['n_techn', 'pren_techn']
        verbose_name = 'T_TECHNICIEN'
        verbose_name_plural = 'T_TECHNICIEN'

    def __str__(self) :
        return '{0} {1}'.format(self.n_techn, self.pren_techn)

class TAvisCp(models.Model) :

    id_av_cp = models.AutoField(primary_key = True)
    int_av_cp = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_avis_cp'
        ordering = ['int_av_cp']
        verbose_name = 'T_AVIS_CP'
        verbose_name_plural = 'T_AVIS_CP'

    def __str__(self) :
        return self.int_av_cp

class TAvancement(models.Model) :

    id_av = models.AutoField(primary_key = True)
    int_av = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    ordre_av = models.IntegerField(verbose_name = 'Ordre dans la liste déroulante')
    id_av_pere = models.ForeignKey(
        'self', models.DO_NOTHING, blank = True, null = True, verbose_name = 'État d\'avancement père'
    )

    class Meta :
        db_table = 't_avancement'
        ordering = ['ordre_av', 'int_av']
        verbose_name = 'T_AVANCEMENT'
        verbose_name_plural = 'T_AVANCEMENT'

    def __str__(self) :
        return self.int_av

class TTypeProgramme(models.Model) :

    id_type_progr = models.AutoField(primary_key = True)
    int_type_progr = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_type_programme'
        ordering = ['int_type_progr']
        verbose_name = 'T_TYPE_PROGRAMME'
        verbose_name_plural = 'T_TYPE_PROGRAMME'

    def __str__(self) :
        return self.int_type_progr

class TTypeGeom(models.Model) :

    id_type_geom = models.AutoField(primary_key = True)
    int_type_geom = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_type_geom'
        ordering = ['int_type_geom']
        verbose_name = 'T_TYPE_GEOM'
        verbose_name_plural = 'T_TYPE_GEOM'

    def __str__(self) :
        return self.int_type_geom

class TTypeDossier(models.Model) :

    id_type_doss = models.AutoField(primary_key = True)
    int_type_doss = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    type_progr = models.ManyToManyField(TTypeProgramme, through = 'TTypesProgrammesTypeDossier')
    type_geom = models.ManyToManyField(TTypeGeom, through = 'TTypesGeomTypeDossier')

    class Meta :
        db_table = 't_type_dossier'
        ordering = ['int_type_doss']
        verbose_name = 'T_TYPE_DOSSIER'
        verbose_name_plural = 'T_TYPE_DOSSIER'

    def __str__(self) :
        return self.int_type_doss

class TTypesGeomTypeDossier(models.Model) :

    id_type_doss = models.ForeignKey(TTypeDossier, models.DO_NOTHING)
    id_type_geom = models.ForeignKey(TTypeGeom, models.DO_NOTHING, verbose_name = 'Type de géométrie')

    class Meta :
        db_table = 't_types_geom_type_dossier'
        verbose_name = 'T_TYPES_GEOM_TYPE_DOSSIER'
        verbose_name_plural = 'T_TYPES_GEOM_TYPE_DOSSIER'

    def __str__(self) :
        return '{0} -> {1}'.format(self.id_type_doss, self.id_type_geom)

class TTypesProgrammesTypeDossier(models.Model) :

    id_type_progr = models.ForeignKey(TTypeProgramme, models.DO_NOTHING, verbose_name = 'Type de programme')
    id_type_doss = models.ForeignKey(TTypeDossier, models.DO_NOTHING)

    class Meta :
        db_table = 't_types_programmes_type_dossier'
        verbose_name = 'T_TYPES_PROGRAMMES_TYPE_DOSSIER'
        verbose_name_plural = 'T_TYPES_PROGRAMMES_TYPE_DOSSIER'

    def __str__(self) :
        return '{0} -> {1}'.format(self.id_type_progr, self.id_type_doss)

class TProgramme(models.Model) :

    id_progr = models.AutoField(primary_key = True)
    dim_progr = models.CharField(max_length = 255, unique = True, verbose_name = 'Diminutif')
    en_act = models.BooleanField(default = True, verbose_name = 'En activité')
    int_progr = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    seq_progr = models.IntegerField(default = 1, verbose_name = 'Séquentiel')
    id_type_progr = models.ForeignKey(TTypeProgramme, models.DO_NOTHING, verbose_name = 'Type de programme')

    class Meta :
        db_table = 't_programme'
        ordering = ['int_progr']
        verbose_name = 'T_PROGRAMME'
        verbose_name_plural = 'T_PROGRAMME'

    def __str__(self) :
        return self.int_progr

class TAxe(models.Model) :

    id_axe = models.CharField(max_length = 255, primary_key = True)
    int_axe = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    num_axe = models.IntegerField(verbose_name = 'Numéro')
    id_progr = models.ForeignKey(TProgramme, models.DO_NOTHING, verbose_name = 'Programme')

    class Meta :
        db_table = 't_axe'
        ordering = ['id_progr__int_progr', 'num_axe']
        unique_together = (('num_axe', 'id_progr'))
        verbose_name = 'T_AXE'
        verbose_name_plural = 'T_AXE'

    def __str__(self) :
        return '{0} - {1}'.format(self.num_axe, self.int_axe)

    def save(self, *args, **kwargs) :
        self.pk = '{0}_{1}'.format(self.id_progr.id_progr, self.num_axe)
        super(TAxe, self).save(*args, **kwargs)

class TSousAxe(models.Model) :

    id_ss_axe = models.CharField(max_length = 255, primary_key = True)
    ech_ss_axe = models.IntegerField(blank = True, null = True, verbose_name = 'Échéancier')
    int_ss_axe = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    mont_ht_ss_axe = models.FloatField(blank = True, null = True, verbose_name = 'Montant HT')
    mont_ttc_ss_axe = models.FloatField(blank = True, null = True, verbose_name = 'Montant TTC')
    num_ss_axe = models.IntegerField(verbose_name = 'Numéro')
    id_axe = models.ForeignKey(TAxe, models.DO_NOTHING, verbose_name = 'Axe')

    class Meta :
        db_table = 't_sous_axe'
        ordering = ['id_axe__id_progr__int_progr', 'id_axe__num_axe', 'num_ss_axe']
        unique_together = (('num_ss_axe', 'id_axe'))
        verbose_name = 'T_SOUS_AXE'
        verbose_name_plural = 'T_SOUS_AXE'

    def __str__(self) :
        return '{0}.{1} - {2}'.format(self.id_axe.num_axe, self.num_ss_axe, self.int_ss_axe)

    def save(self, *args, **kwargs) :
        self.pk = '{0}_{1}'.format(self.id_axe.id_axe, self.num_ss_axe)
        super(TSousAxe, self).save(*args, **kwargs)

class TAction(models.Model) :

    id_act = models.CharField(primary_key = True, max_length = 255)
    ech_act = models.IntegerField(blank = True, null = True, verbose_name = 'Échéancier')
    int_act = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Intitulé')
    mont_ht_act = models.FloatField(blank = True, null = True, verbose_name = 'Montant HT')
    mont_ttc_act = models.FloatField(blank = True, null = True, verbose_name = 'Montant TTC')
    num_act = models.CharField(max_length = 1, verbose_name = 'Numéro')
    id_ss_axe = models.ForeignKey(TSousAxe, models.DO_NOTHING, verbose_name = 'Sous-axe')

    class Meta :
        db_table = 't_action'
        ordering = [
            'id_ss_axe__id_axe__id_progr__int_progr', 'id_ss_axe__id_axe__num_axe', 'id_ss_axe__num_ss_axe', 'num_act'
        ]
        unique_together = (('num_act', 'id_ss_axe'))
        verbose_name = 'T_ACTION'
        verbose_name_plural = 'T_ACTION'

    def __str__(self) :
        return '{0}.{1}.{2} - {3}'.format(
            self.id_ss_axe.id_axe.num_axe,
            self.id_ss_axe.num_ss_axe,
            self.num_act,
            self.int_act
        )

    def save(self, *args, **kwargs) :
        self.pk = '{0}_{1}'.format(self.id_ss_axe.id_ss_axe, self.num_act)
        super(TAction, self).save(*args, **kwargs)

class TCommune(models.Model):

    num_comm = models.CharField(max_length = 5, primary_key = True)
    n_comm = models.CharField(max_length = 255)

    class Meta :
        db_table = 't_commune'
        ordering = ['n_comm', 'num_comm']
        verbose_name = 'T_COMMUNE'
        verbose_name_plural = 'T_COMMUNE'

    def __str__(self) :
        return '{0} ({1})'.format(self.n_comm, self.num_comm)

class TCp(models.Model) :

    cp_comm = models.CharField(primary_key = True, max_length = 5)
    code_comm = models.ManyToManyField(TCommune, through = 'TCommunesCp')

    class Meta :
        db_table = 't_cp'
        ordering = ['cp_comm']
        verbose_name = 'T_CP'
        verbose_name_plural = 'T_CP'

    def __str__(self) :
        return self.cp_comm

class TCommunesCp(models.Model) :

    cp_comm = models.ForeignKey(TCp, models.DO_NOTHING)
    num_comm = models.ForeignKey(TCommune, models.DO_NOTHING)

    class Meta :
        db_table = 't_communes_cp'
        verbose_name = 'T_COMMUNES_CP'
        verbose_name_plural = 'T_COMMUNES_CP'

    def __str__(self) :
    	return str(self.pk)

class TOrganisme(models.Model):

    # Imports
    from app.validators import val_tel

    id_org = models.AutoField(primary_key = True)
    adr_org = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Adresse (ligne 1)')
    bp_org = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Boîte postale')
    cedex_org = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Cedex')
    comm_org = models.TextField(blank = True, null = True, verbose_name = 'Commentaire')
    compl_adr_org = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Adresse (ligne 2)')
    cont_org = models.CharField(blank = True, max_length = 255, null = True)
    courr_org = models.EmailField(blank = True, null = True, verbose_name = 'Adresse électronique')
    cp_org = models.CharField(blank = True, max_length = 5, null = True, verbose_name = 'Code postal')
    n_org = models.CharField(max_length = 255, verbose_name = 'Nom')
    port_org = models.CharField(
        blank = True,
        max_length = 10,
        null = True,
        validators = [val_tel],
        verbose_name = 'Numéro de téléphone portable'
    )
    site_web_org = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Site web')
    tel_org = models.CharField(
        blank = True, max_length = 10, null = True, validators = [val_tel], verbose_name = 'Numéro de téléphone'
    )
    num_comm = models.ForeignKey(TCommune, models.DO_NOTHING, blank = True, null = True, verbose_name = 'Commune')

    class Meta :
        db_table = 't_organisme'
        ordering = ['n_org']
        verbose_name = 'T_ORGANISME'
        verbose_name_plural = 'T_ORGANISME'

    def __str__(self) :
        return self.n_org

class TMoa(TOrganisme) :

    # Imports
    from app.validators import val_fich_img

    def set_logo_org_moa_upload_to(_i, _fn) :
        new_fn = '{0}.{1}'.format(_i.dim_org_moa.lower(), _fn.split('.')[-1])
        return 'logos/{0}'.format(new_fn)

    id_org_moa = models.OneToOneField(TOrganisme)
    dim_org_moa = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Diminutif')
    en_act_doss = models.BooleanField(verbose_name = 'En activité (gestion des dossiers)')
    logo_org_moa = models.FileField(
        blank = True,
        null = True,
        upload_to = set_logo_org_moa_upload_to,
        validators = [val_fich_img],
        verbose_name = 'Logo'
    )
    moa = models.ManyToManyField('self', related_name = '+', symmetrical = False, through = 'TRegroupementsMoa')
    en_act_doss_pgre = models.BooleanField(verbose_name = 'En activité (gestion des actions PGRE)')
    peu_doss = models.BooleanField(verbose_name = 'Utilisé (gestion des dossiers)')
    peu_doss_pgre = models.BooleanField(verbose_name = 'Utilisé (gestion des actions PGRE)')

    class Meta :
        db_table = 't_moa'
        verbose_name = 'T_MOA'
        verbose_name_plural = 'T_MOA'

    def clean(self) :

        # Imports
        from app.models import TMoa
        from django.core.exceptions import ValidationError

        if self.dim_org_moa :
            qs_moa = TMoa.objects.filter(dim_org_moa = self.dim_org_moa)
            if self.pk :
                qs_moa = qs_moa.exclude(pk = self.pk)
            if len(qs_moa) > 0 :
                raise ValidationError({ 'dim_org_moa' : 'Le diminutif {0} existe déjà.'.format(self.dim_org_moa) })

class TRegroupementsMoa(models.Model) :

    id_org_moa_anc = models.ForeignKey(
        TMoa, models.DO_NOTHING, related_name = 'id_org_moa_anc', verbose_name = 'Maître d\'ouvrage ancien'
    )
    id_org_moa_fil = models.ForeignKey(TMoa, models.DO_NOTHING, related_name = 'id_org_moa_fil')

    class Meta :
        db_table = 't_regroupements_moa'
        verbose_name = 'T_REGROUPEMENTS_MOA'
        verbose_name_plural = 'T_REGROUPEMENTS_MOA'

    def __str__(self) :
        return '{0} ({1})'.format(self.id_org_moa_anc, self.id_org_moa_fil)

class TUtilisateur(User) :

    # Imports
    from app.validators import val_tel

    id_util = models.OneToOneField(User)
    port_util = models.CharField(
        blank = True,
        max_length = 10,
        null = True,
        validators = [val_tel],
        verbose_name = 'Numéro de téléphone portable'
    )
    tel_util = models.CharField(
        blank = True, max_length = 10, null = True, validators = [val_tel], verbose_name = 'Numéro de téléphone'
    )
    id_org = models.ForeignKey(TOrganisme, models.DO_NOTHING, verbose_name = 'Organisme')
    moa = models.ManyToManyField(TMoa, related_name = '+', through = 'TDroit')

    class Meta :
        db_table = 't_utilisateur'
        ordering = ['username']
        verbose_name = 'T_UTILISATEUR'
        verbose_name_plural = 'T_UTILISATEUR'

    def __str__(self) :
        return self.id_util.username

class TDroit(models.Model) :

    id_org_moa = models.ForeignKey(
        TMoa, models.DO_NOTHING, blank = True, null = True, verbose_name = 'Maître d\'ouvrage'
    )
    id_type_progr = models.ForeignKey(
        TTypeProgramme, models.DO_NOTHING, blank = True, null = True, verbose_name = 'Type de programme'
    )
    id_util = models.ForeignKey(TUtilisateur, models.DO_NOTHING, verbose_name = 'Utilisateur')
    en_ecr = models.BooleanField(verbose_name = 'Écriture')
    en_lect = models.BooleanField(verbose_name = 'Lecture')

    class Meta :
        db_table = 't_droit'
        unique_together = ('id_org_moa', 'id_type_progr', 'id_util')
        verbose_name = 'T_DROIT'
        verbose_name_plural = 'T_DROIT'

    def __str__(self) :
        return ''

class TSage(models.Model) :

    id_sage = models.AutoField(primary_key = True)
    n_sage = models.CharField(max_length = 255, verbose_name = 'Nom')

    class Meta :
        db_table = 't_sage'
        ordering = ['n_sage']
        verbose_name = 'T_SAGE'
        verbose_name_plural = 'T_SAGE'

    def __str__(self) :
        return self.n_sage

class TTypeDeclaration(models.Model) :

    id_type_decl = models.AutoField(primary_key = True)
    int_type_decl = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_type_declaration'
        ordering = ['int_type_decl']
        verbose_name = 'T_TYPE_DECLARATION'
        verbose_name_plural = 'T_TYPE_DECLARATION'

    def __str__(self) :
        return self.int_type_decl

class TTypeAvancementArrete(models.Model) :

    id_type_av_arr = models.AutoField(primary_key = True)
    int_type_av_arr = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    ordre_type_av_arr = models.IntegerField(blank = True, null = True, verbose_name = 'Ordre dans la liste déroulante')

    class Meta :
        db_table = 't_type_avancement_arrete'
        ordering = ['ordre_type_av_arr']
        verbose_name = 'T_TYPE_AVANCEMENT_ARRETE'
        verbose_name_plural = 'T_TYPE_AVANCEMENT_ARRETE'

    def __str__(self) :
        return self.int_type_av_arr

class TDossier(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_pdf
    from app.validators import val_mont_nul
    from django.utils import timezone

    def set_chem_pj_doss_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/caracteristiques/{0}'.format(new_fn)

    def set_id_av_cp_default() :

        # Imports
        from app.models import TAvisCp
        from styx.settings import T_DONN_BDD_STR

        # Je vérifie l'existence d'un objet TAvisCp dont son intitulé est "En attente".
        try :
            v_av_cp = TAvisCp.objects.get(int_av_cp = T_DONN_BDD_STR['AV_CP_EA']).pk
        except :
            v_av_cp = None

        return v_av_cp

    id_doss = models.AutoField(primary_key = True)
    chem_pj_doss = models.FileField(
        blank = True,
        null = True,
        upload_to = set_chem_pj_doss_upload_to,
        validators = [val_fich_pdf],
        verbose_name = '''
        Insérer le fichier scanné du mémoire technique <span class="field-complement">(fichier PDF)</span>
        '''
    )
    comm_doss = models.TextField(blank = True, null = True, validators = [val_cdc], verbose_name = 'Commentaire')
    comm_regl_doss = models.TextField(blank = True, null = True, validators = [val_cdc], verbose_name = 'Commentaire')
    dt_av_cp_doss = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de l\'avis du comité de programmation <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_delib_moa_doss = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de délibération au maître d\'ouvrage <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_int_doss = models.DateField(default = timezone.now())
    est_ttc_doss = models.BooleanField()
    lib_1_doss = models.CharField(
        max_length = 255, validators = [val_cdc], verbose_name = 'Territoire ou caractéristique'
    )
    lib_2_doss = models.CharField(
        max_length = 255, validators = [val_cdc], verbose_name = 'Territoire ou lieu-dit précis'
    )
    mont_doss = models.FloatField(
        validators = [val_mont_nul], verbose_name = 'Montant du dossier présenté au CD GEMAPI'
    )
    mont_suppl_doss = models.FloatField(
        default = 0, verbose_name = 'Dépassement du dossier', validators = [val_mont_nul]
    )
    num_act = models.CharField(blank = True, max_length = 1, null = True)
    num_axe = models.IntegerField(blank = True, null = True)
    num_doss = models.CharField(max_length = 255, unique = True)
    num_ss_axe = models.IntegerField(blank = True, null = True)
    id_progr = models.ForeignKey(TProgramme, models.DO_NOTHING, verbose_name = 'Programme')
    id_av = models.ForeignKey(TAvancement, models.DO_NOTHING, verbose_name = 'État d\'avancement')
    id_av_cp = models.ForeignKey(
        TAvisCp,
        models.DO_NOTHING,
        default = set_id_av_cp_default,
        verbose_name = 'Avis du comité de programmation - CD GEMAPI'
    )
    id_doss_ass = models.ForeignKey('self', models.DO_NOTHING, blank = True, null = True)
    id_fam = models.ForeignKey(TFamille, models.DO_NOTHING)
    id_nat_doss = models.ForeignKey(TNatureDossier, models.DO_NOTHING, verbose_name = 'Nature du dossier')
    id_org_moa = models.ForeignKey(TMoa, models.DO_NOTHING)
    id_sage = models.ForeignKey(TSage, models.DO_NOTHING, blank = True, null = True, verbose_name = 'SAGE')
    id_techn = models.ForeignKey(TTechnicien, models.DO_NOTHING, verbose_name = 'Agent responsable')
    id_type_doss = models.ForeignKey(TTypeDossier, models.DO_NOTHING, verbose_name = 'Type de dossier')
    type_decl = models.ManyToManyField(TTypeDeclaration, through = 'TArretesDossier')
    annee_prev_doss = models.IntegerField(blank = True, null = True, verbose_name = 'Année prévisionnelle du dossier')

    class Meta :
        db_table = 't_dossier'
        ordering = ['num_doss']
        verbose_name = 'T_DOSSIER'
        verbose_name_plural = 'T_DOSSIER'

    def get_int_doss(self) :
        return '{0} - {1} - {2} - {3}'.format(self.id_nat_doss, self.id_type_doss, self.lib_1_doss, self.lib_2_doss)

    def __str__(self) :
        return self.num_doss

class TDossierGeom(gismodels.Model) :

    gid = models.UUIDField(default = uuid.uuid4, editable = False, primary_key = True)
    geom_lin = gismodels.LineStringField(blank = True, null = True, srid = 2154)
    geom_pct = gismodels.PointField(blank = True, null = True, srid = 2154)
    geom_pol = gismodels.PolygonField(blank = True, null = True, srid = 2154)
    objects = gismodels.GeoManager()
    id_doss = models.ForeignKey(TDossier, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_dossier_geom'
        verbose_name = 'T_DOSSIER_GEOM'
        verbose_name_plural = 'T_DOSSIER_GEOM'

    def __str__(self) :
        return self.gid

class TPeriodePriseVuePhoto(models.Model) :

    id_ppv_ph = models.AutoField(primary_key = True)
    int_ppv_ph = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    ordre_ppv_ph = models.IntegerField(blank = True, null = True, verbose_name = 'Ordre dans la liste déroulante')

    class Meta :
        db_table = 't_periode_prise_vue_photo'
        ordering = ['ordre_ppv_ph']
        verbose_name = 'T_PERIODE_PRISE_VUE_PHOTO'
        verbose_name_plural = 'T_PERIODE_PRISE_VUE_PHOTO'

    def __str__(self) :
        return self.int_ppv_ph

class TPhoto(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_img

    def set_chem_ph_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/photos/{0}'.format(new_fn)

    id_ph = models.AutoField(primary_key = True)
    chem_ph = models.FileField(
        upload_to = set_chem_ph_upload_to,
        validators = [val_fich_img],
        verbose_name = 'Insérer une photo <span class="field-complement">(taille limitée à 3 Mo)</span>'
    )
    descr_ph = models.CharField(
        blank = True, max_length = 255, null = True, validators = [val_cdc], verbose_name = 'Description'
    )
    dt_pv_ph = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de prise de vue <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_ph = models.CharField(max_length = 255, validators = [val_cdc], verbose_name = 'Intitulé de la photo')
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING)
    id_ppv_ph = models.ForeignKey(TPeriodePriseVuePhoto, models.DO_NOTHING, verbose_name = 'Période de prise de vue')

    class Meta :
        db_table = 't_photo'
        verbose_name = 'T_PHOTO'
        verbose_name_plural = 'T_PHOTO'

    def __str__(self) :
        return self.int_ph

class TArretesDossier(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_pdf

    def set_chem_pj_arr_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/reglementations/{0}'.format(new_fn)

    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING)
    id_type_av_arr = models.ForeignKey(TTypeAvancementArrete, models.DO_NOTHING, verbose_name = 'Avancement')
    id_type_decl = models.ForeignKey(TTypeDeclaration, models.DO_NOTHING)
    chem_pj_arr = models.FileField(
        blank = True,
        null = True,
        upload_to = set_chem_pj_arr_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer le fichier scanné de l\'arrêté <span class="field-complement">(fichier PDF)</span>'
    )
    comm_arr = models.TextField(blank = True, null = True, validators = [val_cdc], verbose_name = 'Commentaire')
    dt_lim_encl_trav_arr = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date limite d\'enclenchement des travaux <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_sign_arr = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de signature de l\'arrêté <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    num_arr = models.CharField(
        blank = True, max_length = 255, null = True, validators = [val_cdc], verbose_name = 'Numéro de l\'arrêté'
    )

    class Meta :
        db_table = 't_arretes_dossier'
        verbose_name = 'T_ARRETES_DOSSIER'
        verbose_name_plural = 'T_ARRETES_DOSSIER'

    def __str__(self) :
        return str(self.pk)

class TDepartement(models.Model) :

    num_dep = models.CharField(max_length = 3, primary_key = True, verbose_name = 'Numéro')
    n_dep = models.CharField(max_length = 255, verbose_name = 'Nom')

    class Meta :
        db_table = 't_departement'
        ordering = ['num_dep']
        verbose_name = 'T_DEPARTEMENT'
        verbose_name_plural = 'T_DEPARTEMENT'

    def __str__(self) :
        return '{0} ({1})'.format(self.n_dep, self.num_dep)

class TPrestataire(TOrganisme) :

    # Imports
    from app.validators import val_siret

    id_org_prest = models.OneToOneField(TOrganisme)
    siret_org_prest = models.CharField(
        max_length = 14, unique = True, validators = [val_siret], verbose_name = 'Numéro SIRET'
    )
    num_dep = models.ForeignKey(TDepartement, models.DO_NOTHING, verbose_name = 'Département')

    class Meta :
        db_table = 't_prestataire'
        verbose_name = 'T_PRESTATAIRE'
        verbose_name_plural = 'T_PRESTATAIRE'

class TFinanceur(TOrganisme) :

    id_org_fin = models.OneToOneField(TOrganisme)

    class Meta :
        db_table = 't_financeur'
        verbose_name = 'T_FINANCEUR'
        verbose_name_plural = 'T_FINANCEUR'

class TNaturePrestation(models.Model):

    id_nat_prest = models.AutoField(primary_key = True)
    int_nat_prest = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_nature_prestation'
        ordering = ['int_nat_prest']
        verbose_name = 'T_NATURE_PRESTATION'
        verbose_name_plural = 'T_NATURE_PRESTATION'

    def __str__(self) :
        return self.int_nat_prest

class TPrestation(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_pdf

    def set_chem_pj_prest_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/prestations/{0}'.format(new_fn)

    id_prest = models.AutoField(primary_key = True)
    chem_pj_prest = models.FileField(
        blank = True,
        null = True,
        upload_to = set_chem_pj_prest_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer le contrat de prestation <span class="field-complement">(fichier PDF)</span>'
    )
    comm_prest = models.TextField(blank = True, null = True, validators = [val_cdc], verbose_name = 'Commentaire')
    dt_fin_prest = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de fin de la prestation <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_notif_prest = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de notification de la prestation <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_prest = models.CharField(max_length = 255, validators = [val_cdc], verbose_name = 'Intitulé de la prestation')
    ref_prest = models.CharField(
        blank = True, max_length = 255, null = True, validators = [val_cdc], verbose_name = 'Référence de la prestation'
    )
    id_nat_prest = models.ForeignKey(TNaturePrestation, models.DO_NOTHING, verbose_name = 'Nature de la prestation')
    id_org_prest = models.ForeignKey(TPrestataire, models.DO_NOTHING)
    doss = models.ManyToManyField(TDossier, through = 'TPrestationsDossier')

    class Meta :
        db_table = 't_prestation'
        ordering = ['id_org_prest', 'int_prest', 'dt_notif_prest']
        verbose_name = 'T_PRESTATION'
        verbose_name_plural = 'T_PRESTATION'

    def __str__(self) :

        # Imports
        from app.functions import dt_fr

        return '{0} - {1} - {2}'.format(self.id_org_prest, dt_fr(self.dt_notif_prest) or 'NC', self.int_prest)

class TPrestationsDossier(models.Model) :

    # Imports
    from app.validators import val_mont_pos

    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING)
    id_prest = models.ForeignKey(TPrestation, models.DO_NOTHING)
    mont_prest_doss = models.FloatField(validators = [val_mont_pos])
    seq_aven_prest_doss = models.IntegerField(default = 1)

    class Meta :
        db_table = 't_prestations_dossier'
        verbose_name = 'T_PRESTATIONS_DOSSIER'
        verbose_name_plural = 'T_PRESTATIONS_DOSSIER'

    def __str__(self) :
        return str(self.pk)

class TAvenant(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_pdf
    from app.validators import val_mont_nul

    def set_chem_pj_aven_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/avenants/{0}'.format(new_fn)

    id_aven = models.AutoField(primary_key = True)
    chem_pj_aven = models.FileField(
        blank = True,
        null = True,
        upload_to = set_chem_pj_aven_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer le fichier scanné de l\'avenant <span class="field-complement">(fichier PDF)</span>'
    )
    comm_aven = models.TextField(blank = True, null = True, validators = [val_cdc], verbose_name = 'Commentaire')
    dt_aven = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de fin de l\'avenant <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_aven = models.CharField(max_length = 255, validators = [val_cdc], verbose_name = 'Intitulé de l\'avenant')
    mont_aven = models.FloatField(
        blank = True,
        null = True,
        validators = [val_mont_nul],
        verbose_name = 'Montant [ht_ou_ttc] de l\'avenant'
    )
    num_aven = models.IntegerField()
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING)
    id_prest = models.ForeignKey(TPrestation, models.DO_NOTHING)

    class Meta :
        db_table = 't_avenant'
        ordering = ['num_aven']
        verbose_name = 'T_AVENANT'
        verbose_name_plural = 'T_AVENANT'

    def __str__(self) :
        return self.int_aven

class TFacture(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_pdf
    from app.validators import val_mont_pos

    def set_chem_pj_fact_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/factures/{0}'.format(new_fn)

    id_fact = models.AutoField(primary_key = True)
    chem_pj_fact = models.FileField(
        blank = True,
        null = True,
        upload_to = set_chem_pj_fact_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer le fichier scanné de la facture <span class="field-complement">(fichier PDF)</span>'
    )
    comm_fact = models.TextField(blank = True, null = True, validators = [val_cdc], verbose_name = 'Commentaire')
    dt_mand_moa_fact = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de mandatement par le maître d\'ouvrage <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_rec_fact = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de réception de la facture <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    mont_ht_fact = models.FloatField(
        blank = True, null = True, validators = [val_mont_pos], verbose_name = 'Montant HT de la facture'
    )
    mont_ttc_fact = models.FloatField(
        blank = True, null = True, validators = [val_mont_pos], verbose_name = 'Montant TTC de la facture'
    )
    num_bord_fact = models.CharField(max_length = 255, validators = [val_cdc], verbose_name = 'Numéro de bordereau')
    num_fact = models.CharField(max_length = 255, validators = [val_cdc], verbose_name = 'Numéro de facture')
    num_mandat_fact = models.CharField(max_length = 255, validators = [val_cdc], verbose_name = 'Numéro de mandat')
    suivi_fact = models.CharField(max_length = 255)
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING)
    id_prest = models.ForeignKey(TPrestation, models.DO_NOTHING)

    class Meta :
        db_table = 't_facture'
        ordering = ['-dt_mand_moa_fact', 'id_prest']
        verbose_name = 'T_FACTURE'
        verbose_name_plural = 'T_FACTURE'

    def __str__(self) :
        return self.num_fact

class TPaiementPremierAcompte(models.Model) :

    id_paiem_prem_ac = models.AutoField(primary_key = True)
    int_paiem_prem_ac = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_paiement_premier_acompte'
        ordering = ['int_paiem_prem_ac']
        verbose_name = 'T_PAIEMENT_PREMIER_ACOMPTE'
        verbose_name_plural = 'T_PAIEMENT_PREMIER_ACOMPTE'

    def __str__(self) :
        return self.int_paiem_prem_ac

class TFinancement(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_pdf
    from app.validators import val_mont_pos
    from app.validators import val_pourc

    def set_chem_pj_fin_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/financements/{0}'.format(new_fn)

    id_fin = models.AutoField(primary_key = True)
    chem_pj_fin = models.FileField(
        blank = True,
        null = True,
        upload_to = set_chem_pj_fin_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer l\'arrêté de subvention <span class="field-complement">(fichier PDF)</span>'
    )
    comm_fin = models.TextField(blank = True, null = True, validators = [val_cdc], verbose_name = 'Commentaire')
    dt_deb_elig_fin = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de début d\'éligibilité <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_lim_deb_oper_fin = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date limite du début de l\'opération <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_lim_prem_ac_fin = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date limite du premier acompte <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    duree_pror_fin = models.IntegerField(blank = True, null = True, verbose_name = 'Durée de la prorogation (en mois)')
    duree_valid_fin = models.IntegerField(
        blank = True, null = True, verbose_name = 'Durée de validité de l\'aide (en mois)'
    )
    mont_elig_fin = models.FloatField(
        blank = True,
        null = True,
        validators = [val_mont_pos],
        verbose_name = 'Montant [ht_ou_ttc] de l\'assiette éligible de la subvention'
    )
    mont_part_fin = models.FloatField(
        validators = [val_mont_pos], verbose_name = 'Montant [ht_ou_ttc] total de la participation'
    )
    num_arr_fin = models.CharField(
        blank = True,
        max_length = 255,
        null = True,
        validators = [val_cdc],
        verbose_name = 'Numéro de l\'arrêté ou convention'
    )
    pourc_elig_fin = models.FloatField(
        blank = True, null = True, validators = [val_pourc], verbose_name = 'Pourcentage de l\'assiette éligible'
    )
    pourc_real_fin = models.FloatField(
        blank = True, null = True, validators = [val_pourc], verbose_name = 'Pourcentage de réalisation des travaux'
    )
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING)
    id_org_fin = models.ForeignKey(TFinanceur, models.DO_NOTHING, verbose_name = 'Organisme financeur')
    id_paiem_prem_ac = models.ForeignKey(
        TPaiementPremierAcompte,
        models.DO_NOTHING,
        blank = True,
        null = True,
        verbose_name = 'Premier acompte payé en fonction de'
    )
    a_inf_fin = models.CharField(
        choices = [('Oui', 'Oui'), ('Non', 'Non'), ('Sans objet', 'Sans objet')],
        default = 'Sans objet',
        max_length = 255,
        verbose_name = 'Avez-vous informé le partenaire financier du début de l\'opération ?'
    )

    class Meta :
        db_table = 't_financement'
        verbose_name = 'T_FINANCEMENT'
        verbose_name_plural = 'T_FINANCEMENT'

    def __str__(self) :
        return str(self.id_fin)

class TTypeVersement(models.Model) :

    id_type_vers = models.AutoField(primary_key = True)
    int_type_vers = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_type_versement'
        ordering = ['int_type_vers']
        verbose_name = 'T_TYPE_VERSEMENT'
        verbose_name_plural = 'T_TYPE_VERSEMENT'

    def __str__(self) :
        return self.int_type_vers

class TDemandeVersement(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_pdf
    from app.validators import val_mont_nul
    from app.validators import val_mont_pos

    def set_chem_pj_ddv_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/demandes_de_versements/{0}'.format(new_fn)

    id_ddv = models.AutoField(primary_key = True)
    chem_pj_ddv = models.FileField(
        blank = True,
        null = True,
        upload_to = set_chem_pj_ddv_upload_to,
        validators = [val_fich_pdf],
        verbose_name = '''
        Insérer le courrier scanné de la demande de versement <span class="field-complement">(fichier PDF)</span>
        '''
    )
    comm_ddv = models.TextField(blank = True, null = True, validators = [val_cdc], verbose_name = 'Commentaire')
    dt_ddv = models.DateField(
        verbose_name = 'Date de la demande de versement <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_vers_ddv = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de versement <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_ddv = models.CharField(
        max_length = 255, validators = [val_cdc], verbose_name = 'Intitulé de la demande de versement'
    )
    mont_ht_ddv = models.FloatField(
        blank = True,
        null = True,
        validators = [val_mont_pos],
        verbose_name = 'Montant HT de la demande de versement'
    )
    mont_ht_verse_ddv = models.FloatField(
        blank = True,
        null = True,
        validators = [val_mont_nul],
        verbose_name = 'Montant HT versé'
    )
    mont_ttc_ddv = models.FloatField(
        blank = True,
        null = True,
        validators = [val_mont_pos],
        verbose_name = 'Montant TTC de la demande de versement'
    )
    mont_ttc_verse_ddv = models.FloatField(
        blank = True,
        null = True,
        validators = [val_mont_nul],
        verbose_name = 'Montant TTC versé'
    )
    id_fin = models.ForeignKey(TFinancement, models.DO_NOTHING)
    id_type_vers = models.ForeignKey(TTypeVersement, models.DO_NOTHING, verbose_name = 'Type de demande de versement')
    fact = models.ManyToManyField(TFacture, through = 'TFacturesDemandeVersement')
    num_bord_ddv = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Numéro de bordereau')
    num_titre_rec_ddv = models.CharField(
        blank = True, max_length = 255, null = True, verbose_name = 'Numéro de titre de recette'
    )

    class Meta :
        db_table = 't_demande_versement'
        ordering = ['-dt_ddv']
        verbose_name = 'T_DEMANDE_VERSEMENT'
        verbose_name_plural = 'T_DEMANDE_VERSEMENT'

    def __str__(self) :
        return self.int_ddv

class TFacturesDemandeVersement(models.Model) :

    id_ddv = models.ForeignKey(TDemandeVersement, models.DO_NOTHING)
    id_fact = models.ForeignKey(TFacture, models.DO_NOTHING)

    class Meta :
        db_table = 't_factures_demande_versement'
        verbose_name = 'T_FACTURES_DEMANDE_VERSEMENT'
        verbose_name_plural = 'T_FACTURES_DEMANDE_VERSEMENT'

    def __str__(self) :
        return str(self.pk)

class TAvancementPgre(models.Model) :

    id_av_pgre = models.AutoField(primary_key = True)
    int_av_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    ordre_av_pgre = models.IntegerField(verbose_name = 'Ordre dans la liste déroulante')

    class Meta :
        db_table = 't_avancement_pgre'
        ordering = ['ordre_av_pgre']
        verbose_name = 'T_AVANCEMENT_PGRE'
        verbose_name_plural = 'T_AVANCEMENT_PGRE'

    def __str__(self) :
        return self.int_av_pgre

class TPrioritePgre(models.Model) :

    id_pr_pgre = models.AutoField(primary_key = True)
    int_pr_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_priorite_pgre'
        ordering = ['int_pr_pgre']
        verbose_name = 'T_PRIORITE_PGRE'
        verbose_name_plural = 'T_PRIORITE_PGRE'

    def __str__(self) :
        return self.int_pr_pgre

class TInstanceConcertationPgre(models.Model) :

    id_ic_pgre = models.AutoField(primary_key = True)
    int_ic_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_instance_concertation_pgre'
        ordering = ['int_ic_pgre']
        verbose_name = 'T_INSTANCE_CONCERTATION_PGRE'
        verbose_name_plural = 'T_INSTANCE_CONCERTATION_PGRE'

    def __str__(self) :
        return self.int_ic_pgre

class TAtelierPgre(models.Model) :

    id_atel_pgre = models.AutoField(primary_key = True)
    int_atel_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    ic_pgre = models.ManyToManyField(TInstanceConcertationPgre, through = 'TInstancesConcertationPgreAtelierPgre')

    class Meta :
        db_table = 't_atelier_pgre'
        ordering = ['int_atel_pgre']
        verbose_name = 'T_ATELIER_PGRE'
        verbose_name_plural = 'T_ATELIER_PGRE'

    def __str__(self) :
        return self.int_atel_pgre

class TInstancesConcertationPgreAtelierPgre(models.Model) :

    id_atel_pgre = models.ForeignKey(TAtelierPgre, models.DO_NOTHING)
    id_ic_pgre = models.ForeignKey(TInstanceConcertationPgre, models.DO_NOTHING)

    class Meta :
        db_table = 't_instances_concertation_pgre_atelier_pgre'
        verbose_name = 'T_INSTANCES_CONCERTATION_PGRE_ATELIER_PGRE'
        verbose_name_plural = 'T_INSTANCES_CONCERTATION_PGRE_ATELIER_PGRE'

    def __str__(self) :
        return '{0} ({1})'.format(self.id_atel_pgre, self.id_ic_pgre)

class TDossierPgre(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_pdf
    from app.validators import val_mont_nul

    def set_chem_pj_doss_pgre_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'actions_pgre/caracteristiques/{0}'.format(new_fn)

    id_doss_pgre = models.AutoField(primary_key = True)
    ann_prev_deb_doss_pgre = models.IntegerField(verbose_name = 'Année prévisionnelle du début de l\'action PGRE')
    chem_pj_doss_pgre = models.FileField(
        blank = True,
        null = True,
        upload_to = set_chem_pj_doss_pgre_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer la fiche action <span class="field-complement">(fichier PDF)</span>'
    )
    comm_doss_pgre = models.TextField(blank = True, null = True, validators = [val_cdc], verbose_name = 'Commentaire')
    dt_deb_doss_pgre = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de début de l\'action PGRE <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_fin_doss_pgre = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de fin de l\'action PGRE <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_doss_pgre = models.CharField(
        max_length = 255, validators = [val_cdc], verbose_name = 'Intitulé de l\'action PGRE'
    )
    num_doss_pgre = models.CharField(
        max_length = 255, unique = True, validators = [val_cdc], verbose_name = 'Numéro de l\'action PGRE'
    )
    obj_econ_ress_doss_pgre = models.FloatField(
        verbose_name = 'Objectifs d\'économie de la ressource en eau (en m<sup>3</sup>)'
    )
    id_doss = models.ForeignKey(TDossier, models.DO_NOTHING, blank = True, null = True)
    id_ic_pgre = models.ForeignKey(
        TInstanceConcertationPgre, models.DO_NOTHING, verbose_name = 'Instance de concertation'
    )
    id_pr_pgre = models.ForeignKey(TPrioritePgre, models.DO_NOTHING, verbose_name = 'Priorité')
    id_av_pgre = models.ForeignKey(TAvancementPgre, models.DO_NOTHING, verbose_name = 'État d\'avancement')
    id_nat_doss = models.ForeignKey(TNatureDossier, models.DO_NOTHING, verbose_name = 'Nature de l\'action PGRE')
    atel_pgre = models.ManyToManyField(TAtelierPgre, through = 'TAteliersPgreDossierPgre')
    moa = models.ManyToManyField(TMoa, through = 'TMoaDossierPgre')
    mont_doss_pgre = models.FloatField(
        verbose_name='Montant dossier PGRE',
        default=0.0,
        validators = [val_mont_nul],
    )

    class Meta :
        db_table = 't_dossier_pgre'
        ordering = ['num_doss_pgre']
        verbose_name = 'T_DOSSIER_PGRE'
        verbose_name_plural = 'T_DOSSIER_PGRE'

    def __str__(self) :
        return self.num_doss_pgre

    # def save(self, *args, **kwargs) :
    #
    #     TAvancementPgreTraces = apps.get_model('app', model_name='TAvancementPgreTraces')
    #     # Si création d'un dossier je garde une trace de l'avancement originale
    #     if not self.id_doss_pgre:
    #         instance_buff = super().save(*args, **kwargs)
    #         TAvancementPgreTraces.objects.create(
    #             id_doss_pgre=instance_buff,
    #             id_av_pgre=instance_buff.id_av_pgre)
    #         return instance_buff
    #
    #     # Sinon je garde une trace si le champ id_av_pgre a été modifié par l'opération en cours
    #     instance_old = TDossierPgre.objects.get(id_doss_pgre=self.id_doss_pgre)
    #     if self.id_av_pgre != instance_old.id_av_pgre:
    #         instance_buff = super().save(*args, **kwargs)
    #         TAvancementPgreTraces.objects.create(
    #             id_doss_pgre=instance_buff,
    #             id_av_pgre=self.id_av_pgre)
    #         return instance_buff


class TAteliersPgreDossierPgre(models.Model) :

    id_atel_pgre = models.ForeignKey(TAtelierPgre, models.DO_NOTHING)
    id_doss_pgre = models.ForeignKey(TDossierPgre, models.DO_NOTHING)

    class Meta :
        db_table = 't_ateliers_pgre_dossier_pgre'
        ordering = ['id_atel_pgre']
        verbose_name = 'T_ATELIERS_PGRE_DOSSIER_PGRE'
        verbose_name_plural = 'T_ATELIERS_PGRE_DOSSIER_PGRE'

    def __str__(self) :
        return str(self.pk)

class TMoaDossierPgre(models.Model) :

    id_doss_pgre = models.ForeignKey(TDossierPgre, models.DO_NOTHING)
    id_org_moa = models.ForeignKey(TMoa, models.DO_NOTHING)

    class Meta :
        db_table = 't_moa_dossier_pgre'
        ordering = ['id_org_moa']
        verbose_name = 'T_MOA_DOSSIER_PGRE'
        verbose_name_plural = 'T_MOA_DOSSIER_PGRE'

    def __str__(self) :
        return str(self.pk)

class TControleDossierPgre(models.Model) :

    id_contr_doss_pgre = models.AutoField(primary_key = True)
    dt_contr_doss_pgre = models.DateField(
        verbose_name = 'Date du contrôle <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    obj_real_contr_doss_pgre = models.FloatField(
        verbose_name = 'Objectif réalisé en terme d\'économie de la ressource en eau (en m<sup>3</sup>)'
    )
    id_doss_pgre = models.ForeignKey(TDossierPgre, models.DO_NOTHING)

    class Meta :
        db_table = 't_controle_dossier_pgre'
        ordering = ['dt_contr_doss_pgre']
        verbose_name = 'T_CONTROLE_DOSSIER_PGRE'
        verbose_name_plural = 'T_CONTROLE_DOSSIER_PGRE'

    def __str__(self) :
        return str(self.pk)

class TDossierPgreGeom(gismodels.Model) :

    gid = models.UUIDField(default = uuid.uuid4, editable = False, primary_key = True)
    geom_lin = gismodels.LineStringField(blank = True, null = True, srid = 2154)
    geom_pct = gismodels.PointField(blank = True, null = True, srid = 2154)
    geom_pol = gismodels.PolygonField(blank = True, null = True, srid = 2154)
    objects = gismodels.GeoManager()
    id_doss_pgre = models.ForeignKey(TDossierPgre, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_dossier_pgre_geom'
        verbose_name = 'T_DOSSIER_PGRE_GEOM'
        verbose_name_plural = 'T_DOSSIER_PGRE_GEOM'

    def __str__(self) :
        return self.gid

class TPhotoPgre(models.Model) :

    # Imports
    from app.validators import val_cdc
    from app.validators import val_fich_img

    def set_chem_ph_pgre_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'actions_pgre/photos/{0}'.format(new_fn)

    id_ph_pgre = models.AutoField(primary_key = True)
    chem_ph_pgre = models.FileField(
        upload_to = set_chem_ph_pgre_upload_to,
        validators = [val_fich_img],
        verbose_name = 'Insérer une photo <span class="field-complement">(taille limitée à 3 Mo)</span>'
    )
    descr_ph_pgre = models.CharField(
        blank = True, max_length = 255, null = True, validators = [val_cdc], verbose_name = 'Description'
    )
    dt_pv_ph_pgre = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de prise de vue <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_ph_pgre = models.CharField(max_length = 255, validators = [val_cdc], verbose_name = 'Intitulé de la photo')
    id_doss_pgre = models.ForeignKey(TDossierPgre, models.DO_NOTHING)
    id_ppv_ph = models.ForeignKey(TPeriodePriseVuePhoto, models.DO_NOTHING, verbose_name = 'Période de prise de vue')

    class Meta :
        db_table = 't_photo_pgre'
        verbose_name = 'T_PHOTO_PGRE'
        verbose_name_plural = 'T_PHOTO_PGRE'

    def __str__(self) :
        return self.int_ph_pgre

class TAvancementPgreTraces(models.Model):

    id_trace = models.AutoField(primary_key = True)
    id_doss_pgre = models.ForeignKey('TDossierPgre', on_delete = models.CASCADE, db_column = 'id_doss_pgre')
    id_av_pgre = models.ForeignKey('TAvancementPgre', on_delete = models.CASCADE, db_column = 'id_av_pgre')
    date_modif_av = models.DateTimeField("Horodatage du changement d'état d'avancement", auto_now_add=True)

    class Meta :
        db_table = 't_avancement_pgre_traces'
        ordering = ('id_trace', )

class TDossierSsAction(models.Model):

    id_ss_act = models.AutoField(primary_key = True)
    lib_ss_act = models.CharField(max_length = 255, verbose_name = 'Libellé')
    desc_ss_act = models.TextField(blank = True, null = True, verbose_name = 'Descriptif')
    comm_ss_act = models.TextField(blank = True, null = True, verbose_name = 'Commentaire')
    dt_prevision_ss_action_pgre =  models.DateTimeField(verbose_name = 'Prévisionnel')
    dt_deb_ss_action_pgre =  models.DateTimeField(blank = True, null = True, verbose_name = 'Début')
    dt_fin_ss_action_pgre =  models.DateTimeField(blank = True, null = True, verbose_name = 'Fin')
    mont_ss_action_pgre = models.FloatField(verbose_name = 'Montant')
    obj_econ_ress_ss_action_pgre = models.FloatField(verbose_name = "Objectif d'économie de ressource")
    t_nature_dossier = models.ForeignKey('TNatureDossier', on_delete = models.CASCADE, db_column = 'id_nat_doss')
    id_av_pgre = models.ForeignKey('TAvancementPgre', on_delete = models.CASCADE, db_column = 'id_av_pgre')
    moa = models.ManyToManyField(TMoa)

    class Meta :
        db_table = 't_dossier_pgre_ss_action'
