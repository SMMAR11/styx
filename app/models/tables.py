# coding: utf-8

# Imports
from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gismodels
from django.db import models
from django.db.models import Sum
import uuid


class TFamille(models.Model) :

    '''Ensemble des familles de dossiers'''

    # Colonnes
    id_fam = models.AutoField(primary_key = True)

    class Meta :
        db_table = 't_famille'
        verbose_name = verbose_name_plural = 'T_FAMILLE'

class TNatureDossier(models.Model) :

    '''Ensemble des natures de dossier'''

    # Imports
    id_nat_doss = models.AutoField(primary_key = True)
    int_nat_doss = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    peu_doss = models.BooleanField(
        default = False, verbose_name = 'Est-elle autorisée (module Gestion des dossiers) ?'
    )
    peu_doss_pgre = models.BooleanField(default = False, verbose_name = 'Est-elle autorisée (module PGRE) ?')

    class Meta :
        db_table = 't_nature_dossier'
        ordering = ['int_nat_doss']
        verbose_name = verbose_name_plural = 'T_NATURE_DOSSIER'

    # Méthodes système

    def __str__(self) : return self.int_nat_doss

class TTechnicien(models.Model) :

    '''Ensemble des agents'''

    # Imports
    id_techn = models.AutoField(primary_key = True)
    en_act = models.BooleanField(default = True, verbose_name = 'Est-il en activité ?')
    n_techn = models.CharField(max_length = 255, verbose_name = 'Nom de famille')
    pren_techn = models.CharField(max_length = 255, verbose_name = 'Prénom')

    class Meta :
        db_table = 't_technicien'
        ordering = ['n_techn', 'pren_techn']
        verbose_name = verbose_name_plural = 'T_TECHNICIEN'

    # Méthodes système

    def __str__(self) : return ' '.join([i.strip() for i in [self.n_techn.upper(), self.pren_techn.title()]])

class TAvisCp(models.Model) :

    '''Ensemble des avis du comité de programmation'''

    # Colonnes
    id_av_cp = models.AutoField(primary_key = True)
    int_av_cp = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_avis_cp'
        ordering = ['int_av_cp']
        verbose_name = verbose_name_plural = 'T_AVIS_CP'

    # Méthodes système

    def __str__(self) : return self.int_av_cp

class TAvancement(models.Model) :

    '''Ensemble des états d'avancement'''

    # Colonnes
    id_av = models.AutoField(primary_key = True)
    int_av = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    ordre_av = models.IntegerField(verbose_name = 'Ordre (liste déroulante)')
    id_av_pere = models.ForeignKey(
        'self', blank = True, null = True, on_delete = models.SET_NULL, verbose_name = 'État d\'avancement père'
    )

    class Meta :
        db_table = 't_avancement'
        ordering = ['ordre_av', 'int_av']
        verbose_name = verbose_name_plural = 'T_AVANCEMENT'

    # Méthodes système

    def __str__(self) : return self.int_av

class TTypeProgramme(models.Model) :

    '''Ensemble des types de programme'''

    # Colonnes
    id_type_progr = models.AutoField(primary_key = True)
    int_type_progr = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_type_programme'
        ordering = ['int_type_progr']
        verbose_name = verbose_name_plural = 'T_TYPE_PROGRAMME'

    # Méthodes système

    def __str__(self) : return self.int_type_progr

class TTypeGeom(models.Model) :

    '''Ensemble des types de géométrie'''

    # Colonnes
    id_type_geom = models.AutoField(primary_key = True)
    int_type_geom = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_type_geom'
        ordering = ['int_type_geom']
        verbose_name = verbose_name_plural = 'T_TYPE_GEOM'

    # Méthodes système

    def __str__(self) : return self.int_type_geom

class TTypeDossier(models.Model) :

    '''Ensemble des types de dossier'''

    # Colonnes
    id_type_doss = models.AutoField(primary_key = True)
    int_type_doss = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    # Relations
    type_geom = models.ManyToManyField(TTypeGeom, through = 'TTypesGeomTypeDossier')
    type_progr = models.ManyToManyField(TTypeProgramme, through = 'TTypesProgrammesTypeDossier')

    class Meta :
        db_table = 't_type_dossier'
        ordering = ['int_type_doss']
        verbose_name = verbose_name_plural = 'T_TYPE_DOSSIER'

    # Méthodes système

    def __str__(self) : return self.int_type_doss

class TTypesGeomTypeDossier(models.Model) :

    '''Ensemble des types de géométrie par type de dossier'''

    # Colonnes
    id_type_doss = models.ForeignKey(TTypeDossier, on_delete = models.CASCADE, verbose_name = 'Type de dossier')
    id_type_geom = models.ForeignKey(TTypeGeom, on_delete = models.CASCADE, verbose_name = 'Type de géométrie')

    class Meta :
        db_table = 't_types_geom_type_dossier'
        verbose_name = verbose_name_plural = 'T_TYPES_GEOM_TYPE_DOSSIER'

class TTypesProgrammesTypeDossier(models.Model) :

    '''Ensemble des types de programme par type de dossier'''

    # Colonnes
    id_type_doss = models.ForeignKey(TTypeDossier, on_delete = models.DO_NOTHING, verbose_name = 'Type de dossier')
    id_type_progr = models.ForeignKey(TTypeProgramme, on_delete = models.CASCADE, verbose_name = 'Type de programme')

    class Meta :
        db_table = 't_types_programmes_type_dossier'
        verbose_name = verbose_name_plural = 'T_TYPES_PROGRAMMES_TYPE_DOSSIER'

class TProgramme(models.Model) :

    '''Ensemble des programmes'''

    # Colonnes
    id_progr = models.AutoField(primary_key = True)
    dim_progr = models.CharField(
        help_text = 'Utilisé pour la création d\'un numéro de dossier',
        max_length = 255,
        unique = True,
        verbose_name = 'Diminutif'
    )
    en_act = models.BooleanField(default = True, verbose_name = 'Est-il en activité ?')
    int_progr = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    seq_progr = models.PositiveIntegerField(
        default = 1, help_text = 'Utilisé pour la création d\'un numéro de dossier', verbose_name = 'Séquentiel'
    )
    id_type_progr = models.ForeignKey(TTypeProgramme, on_delete = models.CASCADE, verbose_name = 'Type de programme')

    class Meta :
        db_table = 't_programme'
        ordering = ['int_progr']
        verbose_name = verbose_name_plural = 'T_PROGRAMME'

    # Méthodes système

    def __str__(self) : return self.int_progr

class TAxe(models.Model) :

    '''Ensemble des axes'''

    # Colonnes
    id_axe = models.CharField(max_length = 255, primary_key = True)
    int_axe = models.CharField(blank = True, max_length = 255, verbose_name = 'Intitulé')
    num_axe = models.CharField(max_length = 255, verbose_name = 'Numéro')
    id_progr = models.ForeignKey(TProgramme, on_delete = models.CASCADE, verbose_name = 'Programme')

    class Meta :
        db_table = 't_axe'
        ordering = ['id_progr__int_progr', 'num_axe']
        unique_together = ['num_axe', 'id_progr']
        verbose_name = verbose_name_plural = 'T_AXE'

    # Méthodes publiques

    def get_str_with_prg(self) :
        '''Instance précédée par le programme lié'''
        return '[{}] {}'.format(self.id_progr, self)

    # Méthodes système

    def save(self, *args, **kwargs) :
        self.pk = '_'.join([str(self.id_progr.pk), self.num_axe]); super().save(*args, **kwargs)

    def __str__(self) : return '{} - {}'.format(self.num_axe, self.int_axe)

class TSousAxe(models.Model) :

    '''Ensemble des sous-axes'''

    # Colonnes
    id_ss_axe = models.CharField(max_length = 255, primary_key = True)
    int_ss_axe = models.CharField(blank = True, max_length = 255, verbose_name = 'Intitulé')
    num_ss_axe = models.CharField(max_length = 255, verbose_name = 'Numéro')
    id_axe = models.ForeignKey(TAxe, on_delete = models.CASCADE, verbose_name = 'Axe')

    class Meta :
        db_table = 't_sous_axe'
        ordering = ['id_axe__id_progr__int_progr', 'id_axe__num_axe', 'num_ss_axe']
        unique_together = ['num_ss_axe', 'id_axe']
        verbose_name = verbose_name_plural = 'T_SOUS_AXE'

    # Extra-getters

    def get_str_with_prg(self) :
        '''Instance précédée par le programme lié'''
        return '[{}] {}'.format(self.id_axe.id_progr, self)

    # Méthodes système

    def save(self, *args, **kwargs) :
        self.pk = '_'.join([self.id_axe.pk, self.num_ss_axe]); super().save(*args, **kwargs)

    def __str__(self) :
        return '{}.{} - {}'.format(self.id_axe.num_axe, self.num_ss_axe, self.int_ss_axe)

class TAction(models.Model) :

    '''Ensemble des actions'''

    # Colonnes
    id_act = models.CharField(primary_key = True, max_length = 255)
    int_act = models.CharField(blank = True, max_length = 255, verbose_name = 'Intitulé')
    num_act = models.CharField(max_length = 255, verbose_name = 'Numéro')
    id_ss_axe = models.ForeignKey(TSousAxe, on_delete = models.CASCADE, verbose_name = 'Sous-axe')

    class Meta :
        db_table = 't_action'
        ordering = [
            'id_ss_axe__id_axe__id_progr__int_progr', 'id_ss_axe__id_axe__num_axe', 'id_ss_axe__num_ss_axe', 'num_act'
        ]
        unique_together = ['num_act', 'id_ss_axe']
        verbose_name = verbose_name_plural = 'T_ACTION'

    # Méthodes système

    def save(self, *args, **kwargs) :
        self.pk = '_'.join([self.id_ss_axe.pk, self.num_act]); super().save(*args, **kwargs)

    def __str__(self) :
        return '{}.{}.{} - {}'.format(
            self.id_ss_axe.id_axe.num_axe, self.id_ss_axe.num_ss_axe, self.num_act, self.int_act
        )

class TCommune(models.Model):

    '''Ensemble des communes'''

    # Colonnes
    num_comm = models.CharField(max_length = 5, primary_key = True)
    n_comm = models.CharField(max_length = 255)

    class Meta :
        db_table = 't_commune'
        ordering = ['n_comm', 'num_comm']
        verbose_name = verbose_name_plural = 'T_COMMUNE'

    # Méthodes système

    def __str__(self) : return '{} ({})'.format(self.n_comm, self.num_comm)

class TCp(models.Model) :

    '''Ensemble des codes postaux'''

    # Colonnes
    cp_comm = models.CharField(primary_key = True, max_length = 5)

    # Relations
    code_comm = models.ManyToManyField(TCommune, through = 'TCommunesCp')

    class Meta :
        db_table = 't_cp'
        ordering = ['cp_comm']
        verbose_name = verbose_name_plural = 'T_CP'

    # Méthodes système

    def __str__(self) : return self.cp_comm

class TCommunesCp(models.Model) :

    '''Ensemble des communes pour un code postal'''

    # Colonnes
    cp_comm = models.ForeignKey(TCp, on_delete = models.CASCADE)
    num_comm = models.ForeignKey(TCommune, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_communes_cp'
        verbose_name = verbose_name_plural = 'T_COMMUNES_CP'

class TOrganisme(models.Model):

    '''Ensemble des organismes'''

    # Imports
    from app.classes.MFPhoneNumberField import Class as MFPhoneNumberField

    # Colonnes
    id_org = models.AutoField(primary_key = True)
    adr_org = models.CharField(blank = True, max_length = 255, verbose_name = 'Adresse (ligne 1)')
    bp_org = models.CharField(blank = True, max_length = 255, verbose_name = 'Boîte postale')
    cedex_org = models.CharField(blank = True, max_length = 255, verbose_name = 'Cedex')
    comm_org = models.TextField(blank = True, verbose_name = 'Commentaire')
    compl_adr_org = models.CharField(blank = True, max_length = 255, verbose_name = 'Adresse (ligne 2)')
    cont_org = models.CharField(blank = True, max_length = 255, verbose_name = 'Contact')
    courr_org = models.EmailField(blank = True, verbose_name = 'Adresse électronique')
    cp_org = models.CharField(blank = True, max_length = 5, verbose_name = 'Code postal')
    n_org = models.CharField(max_length = 255, verbose_name = 'Nom')
    port_org = MFPhoneNumberField(blank = True, verbose_name = 'Numéro de téléphone portable')
    site_web_org = models.CharField(blank = True, max_length = 255, verbose_name = 'Site web')
    tel_org = MFPhoneNumberField(blank = True, verbose_name = 'Numéro de téléphone')
    num_comm = models.ForeignKey(
        TCommune, blank = True, null = True, on_delete = models.SET_NULL, verbose_name = 'Commune'
    )

    class Meta :
        db_table = 't_organisme'
        ordering = ['n_org']
        verbose_name = verbose_name_plural = 'T_ORGANISME'

    # Méthodes publiques

    def get_str_with_types(self) :
        '''Instance précédée par le/les types d'organismes'''
        return '[{}] {}'.format(', '.join([i for i in [
            'F' if TFinanceur.objects.filter(pk = self.pk).first() else None,
            'MOA' if TMoa.objects.filter(pk = self.pk).first() else None,
            'P' if TPrestataire.objects.filter(pk = self.pk).first() else None
        ] if i]), self)

    # Méthodes système

    def __str__(self) : return self.n_org

class TMoa(TOrganisme) :

    '''Ensemble des maîtres d'ouvrages'''

    # Imports
    from app.managers.TMoaManager import Class as TMoaManager
    from app.validators import val_fich_img

    # Méthodes liées aux colonnes

    def set_logo_org_moa_upload_to(_i, _fn) :
        new_fn = '{0}.{1}'.format(_i.dim_org_moa.lower(), _fn.split('.')[-1])
        return 'logos/{0}'.format(new_fn)

    # Colonnes
    id_org_moa = models.OneToOneField(TOrganisme)
    dim_org_moa = models.CharField(
        blank = True,
        help_text = 'Utilisé pour la création d\'un numéro de dossier',
        max_length = 255,
        verbose_name = 'Diminutif'
    )
    en_act_doss = models.BooleanField(
        default = True,
        verbose_name = 'Est-il en activité (module Gestion des dossiers) ?'
    )
    en_act_doss_pgre = models.BooleanField(default = True, verbose_name = 'Est-il en activité (module PGRE) ?')
    logo_org_moa = models.FileField(
        blank = True,
        upload_to = set_logo_org_moa_upload_to,
        validators = [val_fich_img],
        verbose_name = 'Logo'
    )
    peu_doss = models.BooleanField(default = True, verbose_name = 'Est-il autorisé (module Gestion des dossiers) ?')
    peu_doss_pgre = models.BooleanField(default = True, verbose_name = 'Est-il autorisé (module PGRE) ?')

    # Manager
    objects = TMoaManager()

    # Relations
    moa = models.ManyToManyField('self', related_name = '+', symmetrical = False, through = 'TRegroupementsMoa')

    class Meta :
        db_table = 't_moa'
        verbose_name = verbose_name_plural = 'T_MOA'

    # Méthodes système

    def clean(self) :

        # Imports
        from app.models import TMoa
        from django.core.exceptions import ValidationError

        if self.dim_org_moa :
            qs_moa = TMoa.objects.filter(dim_org_moa = self.dim_org_moa)
            if self.pk :
                qs_moa = qs_moa.exclude(pk = self.pk)
            if len(qs_moa) > 0 :
                raise ValidationError({ 'dim_org_moa' : 'Le diminutif {} existe déjà.'.format(self.dim_org_moa) })

class TRegroupementsMoa(models.Model) :

    '''Ensemble des regroupements de maîtres d'ouvrages'''

    # Colonnes
    id_org_moa_anc = models.ForeignKey(
        TMoa, on_delete = models.CASCADE, related_name = 'id_org_moa_anc', verbose_name = 'Maître d\'ouvrage (ancien)'
    )
    id_org_moa_fil = models.ForeignKey(
        TMoa, on_delete = models.CASCADE, related_name = 'id_org_moa_fil', verbose_name = 'Maître d\'ouvrage (nouveau)'
    )

    class Meta :
        db_table = 't_regroupements_moa'
        verbose_name = verbose_name_plural = 'T_REGROUPEMENTS_MOA'

    def __str__(self) :
        return '{0} ({})'.format(self.id_org_moa_anc, self.id_org_moa_fil)

class TUtilisateur(User) :

    '''Ensemble des utilisateurs'''

    # Imports
    from app.classes.MFPhoneNumberField import Class as MFPhoneNumberField
    from app.managers.TUtilisateurManager import Class as TUtilisateurManager

    # Colonnes
    id_util = models.OneToOneField(User)
    port_util = MFPhoneNumberField(blank = True, verbose_name = 'Numéro de téléphone portable')
    tel_util = MFPhoneNumberField(blank = True, verbose_name = 'Numéro de téléphone')
    id_org = models.ForeignKey(
        TOrganisme, blank = True, null = True, on_delete = models.SET_NULL, verbose_name = 'Organisme'
    )

    # Manager
    objects = TUtilisateurManager()

    # Relations
    moa = models.ManyToManyField(TMoa, related_name = '+', through = 'TDroit')

    class Meta :
        db_table = 't_utilisateur'
        ordering = ['username']
        verbose_name = verbose_name_plural = 'T_UTILISATEUR'

    # Méthodes privées

    def set_permissions(self, read_or_write) :

        '''Définition des permissions d'accès aux dossiers'''

        # Initialisation des couples
        couples = []

        for drt in self.tdroit_set.all() :

            # Définition des maîtres d'ouvrage (identifiants)
            if drt.id_org_moa :
                moas = TMoa.objects.get_rmoas(moa = drt.id_org_moa.pk).values_list('pk', flat = True)
            else :
                moas = TMoa.objects.values_list('pk', flat = True)

            # Définition des types de programme (identifiants)
            if drt.id_type_progr :
                tpgs = [drt.id_type_progr.pk]
            else :
                tpgs = TTypeProgramme.objects.values_list('pk', flat = True)

            # Vérification du paramètre "read_or_write"
            if read_or_write not in ['R', 'W'] :
                raise ValueError('Le paramètre read_or_write accepte soit la valeur "R", soit la valeur "W".')

            # Gestion des couples pour la permission courante
            attr = drt.en_lect if read_or_write == 'R' else drt.en_ecr
            for moa in moas :
                for tpg in tpgs :
                    couple = (moa, tpg) # Définition d'un tuple maître d'ouvrage/type de programme
                    if attr :
                        couples.append(couple) # Ajout du tuple si permission autorisée
                    else :
                        if couple in couples : couples.remove(couple) # Retrait du tuple si permission interdite

        return set(couples)

    # Méthodes publiques

    def get_permissions(self, read_or_write) :
        '''Obtention des permissions d'accès aux dossiers'''
        return self.set_permissions(read_or_write = read_or_write)

    # Méthodes système

    def __str__(self) : return self.id_util.username

class TDroit(models.Model) :

    '''Ensemble des droits pour un utilisateur'''

    # Colonnes
    id_org_moa = models.ForeignKey(
        TMoa, blank = True, null = True, on_delete = models.CASCADE, verbose_name = 'Maître d\'ouvrage'
    )
    id_type_progr = models.ForeignKey(
        TTypeProgramme, blank = True, null = True, on_delete = models.CASCADE, verbose_name = 'Type de programme'
    )
    id_util = models.ForeignKey(TUtilisateur, on_delete = models.CASCADE, verbose_name = 'Utilisateur')
    en_ecr = models.BooleanField(verbose_name = 'Écriture')
    en_lect = models.BooleanField(verbose_name = 'Lecture')

    class Meta :
        db_table = 't_droit'
        ordering = ['id']
        unique_together = ['id_org_moa', 'id_type_progr', 'id_util']
        verbose_name = verbose_name_plural = 'T_DROIT'

class TSage(models.Model) :

    '''Ensemble des SAGE'''

    # Colonnes
    id_sage = models.AutoField(primary_key = True)
    n_sage = models.CharField(max_length = 255, verbose_name = 'Nom')

    class Meta :
        db_table = 't_sage'
        ordering = ['n_sage']
        verbose_name = verbose_name_plural = 'T_SAGE'

    # Méthodes système

    def __str__(self) : return self.n_sage

class TTypeDeclaration(models.Model) :

    '''Ensemble des types de déclaration'''

    # Colonnes
    id_type_decl = models.AutoField(primary_key = True)
    int_type_decl = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_type_declaration'
        ordering = ['int_type_decl']
        verbose_name = verbose_name_plural = 'T_TYPE_DECLARATION'

    # Méthodes système

    def __str__(self) : return self.int_type_decl

class TTypeAvancementArrete(models.Model) :

    '''Ensemble des types d'avancement pour un arrêté'''

    # Colonnes
    id_type_av_arr = models.AutoField(primary_key = True)
    int_type_av_arr = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    ordre_type_av_arr = models.PositiveIntegerField(default = 9999, verbose_name = 'Ordre (liste déroulante)')

    class Meta :
        db_table = 't_type_avancement_arrete'
        ordering = ['ordre_type_av_arr']
        verbose_name = verbose_name_plural = 'T_TYPE_AVANCEMENT_ARRETE'

    # Méthodes système

    def __str__(self) : return self.int_type_av_arr

class TDossier(models.Model) :

    '''Ensemble des dossiers'''

    # Imports
    from app.classes.MFEuroField import Class as MFEuroField
    from app.managers.TDossierManager import Class as TDossierManager
    from app.validators import val_fich_pdf

    # Méthodes liées aux colonnes

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

    # Colonnes
    id_doss = models.AutoField(primary_key = True)
    annee_prev_doss = models.PositiveIntegerField(
        blank = True, null = True, verbose_name = 'Année prévisionnelle du dossier'
    )
    chem_pj_doss = models.FileField(
        blank = True,
        upload_to = set_chem_pj_doss_upload_to,
        validators = [val_fich_pdf],
        verbose_name = '''
        Insérer le fichier scanné du mémoire technique <span class="field-complement">(fichier PDF)</span>
        '''
    )
    comm_doss = models.TextField(blank = True, verbose_name = 'Commentaire')
    comm_regl_doss = models.TextField(blank = True, verbose_name = 'Commentaire')
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
    dt_int_doss = models.DateField(auto_now_add = True, verbose_name = 'Date de création')
    est_ttc_doss = models.BooleanField()
    lib_1_doss = models.CharField(max_length = 255, verbose_name = 'Caractéristique')
    lib_2_doss = models.CharField(max_length = 255, verbose_name = 'Territoire et lieu-dit')
    mont_doss = MFEuroField(verbose_name = 'Montant du dossier présenté au CD GEMAPI')
    mont_suppl_doss = MFEuroField(default = 0, verbose_name = 'Dépassement du dossier')
    num_act = models.CharField(blank = True, max_length = 255)
    num_axe = models.CharField(blank = True, max_length = 255)
    num_doss = models.CharField(max_length = 255, unique = True)
    num_oper_budg_doss = models.CharField(
        blank = True, max_length = 255, verbose_name = 'Numéro d\'opération budgétaire'
    )
    num_ss_axe = models.CharField(blank = True, max_length = 255)
    id_progr = models.ForeignKey(TProgramme, on_delete = models.CASCADE, verbose_name = 'Programme')
    id_av = models.ForeignKey(
        TAvancement,
        on_delete = models.CASCADE,
        verbose_name = '''
        État d'avancement <span class="field-complement">(un dossier est en cours dès que le maître d'ouvrage a pris la
        délibération)</span>
        '''
    )
    id_av_cp = models.ForeignKey(
        TAvisCp,
        default = set_id_av_cp_default,
        on_delete = models.CASCADE,
        verbose_name = 'Avis du comité de programmation - CD GEMAPI'
    )
    id_doss_ass = models.ForeignKey('self', blank = True, null = True, on_delete = models.SET_NULL)
    id_fam = models.ForeignKey(TFamille, on_delete = models.DO_NOTHING)
    id_nat_doss = models.ForeignKey(TNatureDossier, on_delete = models.CASCADE, verbose_name = 'Nature du dossier')
    id_org_moa = models.ForeignKey(TMoa, on_delete = models.CASCADE)
    id_sage = models.ForeignKey(TSage, blank = True, null = True, on_delete = models.SET_NULL, verbose_name = 'SAGE')
    id_techn = models.ForeignKey(TTechnicien, on_delete = models.CASCADE, verbose_name = 'Agent responsable')
    id_type_doss = models.ForeignKey(TTypeDossier, on_delete = models.CASCADE, verbose_name = 'Type de dossier')

    # Managers
    objects = TDossierManager()

    # Relations
    type_decl = models.ManyToManyField(TTypeDeclaration, through = 'TArretesDossier')

    class Meta :
        db_table = 't_dossier'
        ordering = ['num_doss']
        verbose_name = verbose_name_plural = 'T_DOSSIER'

    # Extra-getters

    def get_view_object(self) :
        '''Instance :model:`app.VSuiviDossier`'''
        from app.models.views import VSuiviDossier
        return VSuiviDossier.objects.get(pk = self.pk)

    # Méthodes publiques

    def get_attrs(self) :
        '''Attributs'''
        from app.functions import dt_fr, obt_mont
        ht_ou_ttc = self.get_view_object().type_mont_doss
        return {
            'annee_prev_doss' : { 'label' : 'Année prévisionnelle du dossier', 'value' : self.annee_prev_doss },
            'num_doss' : { 'label' : 'Numéro du dossier', 'value' : self },
            'int_doss' : {
                'label' : 'Intitulé du dossier',
                'value' : '''
                <div class="row">
                    <div class="col-md-6">
                        <span class="red-color small u">Nature du dossier :</span>
                        {0}
                    </div>
                    <div class="col-md-6">
                        <span class="red-color small u">Territoire ou caractéristique :</span>
                        {1}
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <span class="red-color small u">Type de dossier :</span>
                        {2}
                    </div>
                    <div class="col-md-6">
                        <span class="red-color small u">Territoire ou lieu-dit précis :</span>
                        {3}
                    </div>
                </div>
                '''.format(self.id_nat_doss, self.lib_1_doss, self.id_type_doss, self.lib_2_doss)
            },
            'int_doss_pdf' : { 'label' : 'Intitulé du dossier', 'value' : self.get_int_doss() },
            'id_org_moa' : { 'label' : 'Maître d\'ouvrage', 'value' : self.id_org_moa },
            'id_progr' : { 'label' : 'Programme', 'value' : self.id_progr },
            'num_axe' : { 'label' : 'Axe', 'value' : self.num_axe },
            'num_axe_compl' : { 'label' : 'Axe', 'value' : self.get_axe_doss() },
            'num_ss_axe' : { 'label' : 'Sous-axe', 'value' : self.num_ss_axe },
            'num_act' : { 'label' : 'Action', 'value' : self.num_act },
            'id_nat_doss' : { 'label' : 'Nature du dossier', 'value' : self.id_nat_doss },
            'id_type_doss' : { 'label' : 'Type de dossier', 'value' : self.id_type_doss },
            'id_techn' : { 'label' : 'Agent responsable', 'value' : self.id_techn },
            'id_sage' : { 'label' : 'SAGE', 'value' : self.id_sage },
            'mont_doss' : {
                'label' : 'Montant {0} du dossier présenté au CD GEMAPI (en €)'.format(ht_ou_ttc),
                'value' : obt_mont(self.mont_doss)
            },
            'mont_suppl_doss' : {
                'label' : 'Dépassement {0} du dossier (en €)'.format(ht_ou_ttc),
                'value' : obt_mont(self.mont_suppl_doss)
            },
            'mont_tot_doss' : {
                'label' : 'Montant {0} total du dossier (en €)'.format(ht_ou_ttc),
                'value' : obt_mont(self.get_view_object().mont_tot_doss)
            },
            'id_av' : { 'label' : 'État d\'avancement', 'value' : self.id_av },
            'dt_delib_moa_doss' : {
                'label' : 'Date de délibération au maître d\'ouvrage', 'value' : dt_fr(self.dt_delib_moa_doss)
            },
            'id_av_cp' : { 'label' : 'Avis du comité de programmation - CD GEMAPI', 'value' : self.id_av_cp },
            'dt_av_cp_doss' : {
                'label' : 'Date de l\'avis du comité de programmation', 'value' : dt_fr(self.dt_av_cp_doss)
            },
            'chem_pj_doss' : {
                'label' : 'Consulter le fichier scanné du mémoire technique',
                'value' : self.chem_pj_doss,
                'pdf' : True
            },
            'comm_doss' : { 'label' : 'Commentaire', 'value' : self.comm_doss },
            'num_oper_budg_doss' : { 'label' : 'Numéro d\'opération budgétaire', 'value' : self.num_oper_budg_doss }
        }

    def get_axe_doss(self) :
        '''Axe complet'''
        return self.get_view_object().num_axe_compl

    def get_doss_fam(self) :
        '''Ensemble des dossiers de la famille'''
        from app.functions import dt_fr
        return [{
            'num_doss' : d,
            'int_doss' : d.get_int_doss(),
            'id_org_moa' : d.id_org_moa,
            'dt_delib_moa_doss' : dt_fr(d.dt_delib_moa_doss) or '-',
            'pk' : d.pk
        } for d in TDossier.objects.filter(id_fam = self.id_fam).exclude(pk = self.pk)]

    def get_int_doss(self) :
        '''Intitulé complet'''
        return self.get_view_object().int_doss

    def get_recap_arrs(self) :
        '''Tableau récapitulatif des arrêtés'''
        from app.functions import dt_fr
        return [{
            'id_type_decl' : a.id_type_decl,
            'id_type_av_arr' : a.id_type_av_arr,
            'num_arr' : a.num_arr or '-',
            'dt_sign_arr' : dt_fr(a.dt_sign_arr) or '-',
            'dt_lim_encl_trav_arr' : dt_fr(a.dt_lim_encl_trav_arr) or '-',
            'pk' : a.pk
        } for a in TArretesDossier.objects.filter(id_doss = self)]

    def get_recap_ddvs(self) :

        '''Tableau récapitulatif des demandes de versements'''

        # Imports
        from app.functions import dt_fr, obt_mont
        from app.models.views import VDemandeVersement

        # Initialisation de variables
        ddvs = []; mont_ddv_sum = 0

        for d in VDemandeVersement.objects.filter(id_doss = self) :

            if self.get_view_object().type_mont_doss == 'TTC' :
                mont_ddv = d.get_instance().mont_ttc_ddv
                map_ddv = d.map_ttc_ddv
            else :
                mont_ddv = d.get_instance().mont_ht_ddv
                map_ddv = d.map_ht_ddv

            # Empilement des demandes de versements
            ddvs.append({
                'id_org_fin' : d.id_org_fin,
                'mont_ddv' : obt_mont(mont_ddv),
                'dt_ddv' : dt_fr(d.get_instance().dt_ddv),
                'dt_vers_ddv' : dt_fr(d.get_instance().dt_vers_ddv) or '-',
                'map_ddv' : obt_mont(map_ddv) or '-',
                'id_type_vers' : d.get_instance().id_type_vers,
                'pk' : d.pk
            })

            # Addition de la somme
            mont_ddv_sum += mont_ddv

        return { 'tbl' : ddvs, 'mnt' : mont_ddv_sum }

    def get_recap_facs(self) :

        '''Tableau récapitulatif des factures'''

        # Imports
        from app.functions import dt_fr, obt_mont

        # Initialisation de variables
        facs = []; mont_fact_sum = 0

        # Définition du jeu de données
        qs = TFacture.objects.filter(id_doss = self)

        for f in qs :

            if self.get_view_object().type_mont_doss == 'TTC' :
                mont_fact = f.mont_ttc_fact
            else :
                mont_fact = f.mont_ht_fact

            # Empilement des factures
            facs.append({
                'id_prest' : f.id_prest,
                'id_nat_prest' : f.id_prest.id_nat_prest,
                'num_fact' : f.num_fact,
                'dt_mand_moa_fact' : dt_fr(f.dt_mand_moa_fact) or '-',
                'mont_fact' : obt_mont(mont_fact),
                'mont_ht_fact' : obt_mont(f.mont_ht_fact) or '-',
                'mont_ttc_fact' : obt_mont(f.mont_ttc_fact) or '-',
                'num_mandat_fact' : f.num_mandat_fact,
                'num_bord_fact' : f.num_bord_fact,
                'suivi_fact' : f.suivi_fact,
                'pk' : f.pk
            })

            # Calcul de la somme
            mont_fact_sum += mont_fact

        return {
            'tbl' : facs,
            'mnt' : mont_fact_sum,
            'mnt_ht' : obt_mont(sum([f.mont_ht_fact or 0 for f in qs])),
            'mnt_ttc' : obt_mont(sum([f.mont_ttc_fact or 0 for f in qs]))
        }

    def get_recap_fdvs(self) :
        '''Tableau récapitulatif des éléments composant la fiche de vie'''
        from app.functions import dt_fr
        return [{
            'comm_fdv' : fdv.comm_fdv,
            'd_fdv' : dt_fr(fdv.d_fdv),
            'lib_fdv' : fdv.lib_fdv,
            'pk' : fdv.pk
        } for fdv in TFicheVie.objects.filter(id_doss = self)]

    def get_recap_fins(self) :
        '''Tableau récapitulatif des financements'''
        from app.functions import dt_fr, obt_mont, obt_pourc; from app.models.views import VFinancement
        return [{
            'n_org' : f.n_org_fin,
            'mont_elig_fin' : (obt_mont(f.id_fin.mont_elig_fin) if f.id_fin else None) or '-',
            'pourc_elig_fin' : (obt_pourc(f.id_fin.pourc_elig_fin) if f.id_fin else None) or '-',
            'mont_part_fin' : obt_mont(f.mont_part_fin),
            'pourc_glob_fin' : obt_pourc(f.pourc_glob_fin),
            'dt_deb_elig_fin' : (dt_fr(f.id_fin.dt_deb_elig_fin) if f.id_fin else None) or '-',
            'dt_fin_elig_fin' : dt_fr(f.dt_fin_elig_fin) or '-',
            'mont_rad' : obt_mont(f.mont_rad) or '-',
            'pk' : f.id_fin.pk if f.id_fin else None
        } for f in VFinancement.objects.filter(id_doss = self)]

    def get_recap_prss(self) :

        '''Tableau récapitulatif des prestations'''

        # Imports
        from app.functions import obt_mont
        from app.models.tables import TPrestationsDossier
        from app.models.views import VSuiviPrestationsDossier

        # Initialisation de variables
        prss = []; sums = [0, 0, 0, 0, 0]

        for p in VSuiviPrestationsDossier.objects.filter(id_doss = self) :

            if self.get_view_object().type_mont_doss == 'TTC' :
                mont_fact_sum = p.mont_ttc_fact_sum
            else :
                mont_fact_sum = p.mont_ht_fact_sum

            # Empilement des prestations
            prss.append({
                'n_org' : p.id_prest.id_org_prest,
                'int_prest' : p.id_prest.int_prest,
                'mont_prest_doss' : obt_mont(p.mont_prest_doss),
                'id_nat_prest' : p.id_prest.id_nat_prest,
                'nb_aven' : p.nb_aven,
                'mont_aven_sum' : obt_mont(p.mont_aven_sum),
                'mont_fact_sum' :  obt_mont(mont_fact_sum),
                'mont_raf' : obt_mont(p.mont_raf),
                'duree_prest_doss' : TPrestationsDossier.objects.get(pk = p.pk).duree_prest_doss,
                'duree_w_os_sum' : p.duree_w_os_sum,
                'duree_w_rest_os_sum' : p.duree_w_rest_os_sum,
                'pk' : p.pk
            })

            # Calcul des sommes
            sums[0] += p.mont_prest_doss
            sums[1] += p.nb_aven
            sums[2] += p.mont_aven_sum
            sums[3] += mont_fact_sum
            sums[4] += p.mont_raf

        for i in range(0, len(sums)) :
            if i != 1 : sums[i] = obt_mont(sums[i])

        return { 'tbl' : prss, 'mnts' : sums }

    # Méthodes système

    def __str__(self) : return self.num_doss

class TDossierGeom(gismodels.Model) :

    '''Ensemble des géométries d'un dossier'''

    # Colonnes
    gid = models.UUIDField(default = uuid.uuid4, editable = False, primary_key = True)
    geom_lin = gismodels.LineStringField(blank = True, null = True, srid = 4326)
    geom_pct = gismodels.PointField(blank = True, null = True, srid = 4326)
    geom_pol = gismodels.PolygonField(blank = True, null = True, srid = 4326)
    objects = gismodels.GeoManager()
    id_doss = models.ForeignKey(TDossier, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_dossier_geom'
        verbose_name = verbose_name_plural = 'T_DOSSIER_GEOM'

class TPeriodePriseVuePhoto(models.Model) :

    '''Ensemble des périodes de prise de vue d'une photo'''

    # Colonnes
    id_ppv_ph = models.AutoField(primary_key = True)
    int_ppv_ph = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    ordre_ppv_ph = models.PositiveIntegerField(default = 9999, verbose_name = 'Ordre (liste déroulante)')

    class Meta :
        db_table = 't_periode_prise_vue_photo'
        ordering = ['ordre_ppv_ph']
        verbose_name = verbose_name_plural = 'T_PERIODE_PRISE_VUE_PHOTO'

    # Méthodes système

    def __str__(self) : return self.int_ppv_ph

class TPhoto(models.Model) :

    '''Ensemble des photos d'un dossier'''

    # Imports
    from app.validators import val_fich_img

    # Méthodes liées aux colonnes

    def set_chem_ph_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/photos/{0}'.format(new_fn)

    # Colonnes
    id_ph = models.AutoField(primary_key = True)
    chem_ph = models.FileField(
        upload_to = set_chem_ph_upload_to,
        validators = [val_fich_img],
        verbose_name = 'Insérer une photo <span class="field-complement">(taille limitée à 3 Mo)</span>'
    )
    descr_ph = models.CharField(blank = True, max_length = 255, verbose_name = 'Description')
    dt_pv_ph = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de prise de vue <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_ph = models.CharField(max_length = 255, verbose_name = 'Intitulé de la photo')
    id_doss = models.ForeignKey(TDossier, on_delete = models.CASCADE)
    id_ppv_ph = models.ForeignKey(
        TPeriodePriseVuePhoto, on_delete = models.CASCADE, verbose_name = 'Période de prise de vue'
    )

    class Meta :
        db_table = 't_photo'
        ordering = ['id_ppv_ph__ordre_ppv_ph', 'dt_pv_ph']
        verbose_name = verbose_name_plural = 'T_PHOTO'

    # Méthodes système

    def __str__(self) : return self.int_ph

class TArretesDossier(models.Model) :

    '''Ensemble des arrêtés d'un dossier'''

    # Imports
    from app.validators import val_fich_pdf

    # Méthodes liées aux colonnes

    def set_chem_pj_arr_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/reglementations/{0}'.format(new_fn)

    # Colonnes
    id_doss = models.ForeignKey(TDossier, on_delete = models.CASCADE)
    id_type_av_arr = models.ForeignKey(TTypeAvancementArrete, on_delete = models.CASCADE, verbose_name = 'Avancement')
    id_type_decl = models.ForeignKey(TTypeDeclaration, on_delete = models.CASCADE)
    chem_pj_arr = models.FileField(
        blank = True,
        upload_to = set_chem_pj_arr_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer le fichier scanné de l\'arrêté <span class="field-complement">(fichier PDF)</span>'
    )
    comm_arr = models.TextField(blank = True, verbose_name = 'Commentaire')
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
    num_arr = models.CharField(blank = True, max_length = 255, verbose_name = 'Numéro de l\'arrêté')

    class Meta :
        db_table = 't_arretes_dossier'
        ordering = ['id_type_decl']
        verbose_name = verbose_name_plural = 'T_ARRETES_DOSSIER'

class TDepartement(models.Model) :

    '''Ensemble des départements français'''

    # Colonnes
    num_dep = models.CharField(max_length = 3, primary_key = True, verbose_name = 'Numéro')
    n_dep = models.CharField(max_length = 255, verbose_name = 'Nom')

    class Meta :
        db_table = 't_departement'
        ordering = ['num_dep']
        verbose_name = verbose_name_plural = 'T_DEPARTEMENT'

    # Méthodes système

    def __str__(self) : return '{} ({})'.format(self.n_dep, self.num_dep)

class TPrestataire(TOrganisme) :

    '''Ensemble des prestataires'''

    # Colonnes
    id_org_prest = models.OneToOneField(TOrganisme)
    siret_org_prest = models.CharField(max_length = 14, unique = True, verbose_name = 'Numéro SIRET')
    num_dep = models.ForeignKey(
        TDepartement, blank = True, null = True, on_delete = models.SET_NULL, verbose_name = 'Département'
    )

    class Meta :
        db_table = 't_prestataire'
        verbose_name = verbose_name_plural = 'T_PRESTATAIRE'

class TFinanceur(TOrganisme) :

    '''Ensemble des financeurs'''

    # Colonnes
    id_org_fin = models.OneToOneField(TOrganisme)

    class Meta :
        db_table = 't_financeur'
        verbose_name = verbose_name_plural = 'T_FINANCEUR'

class TNaturePrestation(models.Model):

    '''Ensemble des natures de prestation'''

    # Colonnes
    id_nat_prest = models.AutoField(primary_key = True)
    int_nat_prest = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_nature_prestation'
        ordering = ['int_nat_prest']
        verbose_name = verbose_name_plural = 'T_NATURE_PRESTATION'

    # Méthodes système

    def __str__(self) : return self.int_nat_prest

class TPrestation(models.Model) :

    '''Ensemble des prestations'''

    # Imports
    from app.validators import val_fich_pdf

    # Méthodes liées aux colonnes

    def set_chem_pj_prest_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/prestations/{0}'.format(new_fn)

    # Colonnes
    id_prest = models.AutoField(primary_key = True)
    chem_pj_prest = models.FileField(
        blank = True,
        upload_to = set_chem_pj_prest_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer le contrat de prestation <span class="field-complement">(fichier PDF)</span>'
    )
    comm_prest = models.TextField(blank = True, verbose_name = 'Commentaire')
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
    int_prest = models.CharField(max_length = 255, verbose_name = 'Intitulé de la prestation')
    ref_prest = models.CharField(blank = True, max_length = 255, verbose_name = 'Référence de la prestation')
    id_nat_prest = models.ForeignKey(
        TNaturePrestation, on_delete = models.CASCADE, verbose_name = 'Nature de la prestation'
    )
    id_org_prest = models.ForeignKey(TPrestataire, on_delete = models.CASCADE)

    # Relations
    doss = models.ManyToManyField(TDossier, through = 'TPrestationsDossier')

    class Meta :
        db_table = 't_prestation'
        ordering = ['id_org_prest', 'int_prest', 'dt_notif_prest']
        verbose_name = verbose_name_plural = 'T_PRESTATION'

    # Extra-getters

    def get_view_object(self) :
        '''Instance :model:`app.VPrestation`'''
        from app.models.views import VPrestation
        return VPrestation.objects.get(pk = self.pk)

    # Méthodes système

    def __str__(self) :

        # Imports
        from app.functions import dt_fr

        return '{0} - {1} - {2}'.format(self.id_org_prest, dt_fr(self.dt_notif_prest) or 'NC', self.int_prest)

class TPrestationsDossier(models.Model) :

    '''Ensemble des prestations d'un dossier'''

    # Imports
    from app.classes.MFEuroField import Class as MFEuroField

    id_doss = models.ForeignKey(TDossier, on_delete = models.CASCADE)
    id_prest = models.ForeignKey(TPrestation, on_delete = models.CASCADE)
    duree_prest_doss = models.PositiveIntegerField(
        default = 0, verbose_name = 'Durée de la prestation (en nombre de jours ouvrés)'
    )
    mont_prest_doss = MFEuroField(min_value = 0.01)
    seq_aven_prest_doss = models.PositiveIntegerField(default = 1)

    class Meta :
        db_table = 't_prestations_dossier'
        verbose_name = verbose_name_plural = 'T_PRESTATIONS_DOSSIER'

    # Extra-getters

    def get_view_object(self) :
        '''Instance :model:`app.VSuiviPrestationsDossier`'''
        from app.models.views import VSuiviPrestationsDossier
        return VSuiviPrestationsDossier.objects.get(pk = pk)

class TAvenant(models.Model) :

    '''Ensemble des avenants d'une prestation d'un dossier'''

    # Imports
    from app.classes.MFEuroField import Class as MFEuroField
    from app.validators import val_fich_pdf

    # Méthodes liées aux colonnes

    def set_chem_pj_aven_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/avenants/{0}'.format(new_fn)

    # Colonnes
    id_aven = models.AutoField(primary_key = True)
    chem_pj_aven = models.FileField(
        blank = True,
        upload_to = set_chem_pj_aven_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer le fichier scanné de l\'avenant <span class="field-complement">(fichier PDF)</span>'
    )
    comm_aven = models.TextField(blank = True, verbose_name = 'Commentaire')
    dt_aven = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de fin de l\'avenant <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_aven = models.CharField(max_length = 255, verbose_name = 'Intitulé de l\'avenant')
    mont_aven = MFEuroField(blank = True, null = True, verbose_name = 'Montant [ht_ou_ttc] de l\'avenant')
    num_aven = models.IntegerField()
    id_doss = models.ForeignKey(TDossier, on_delete = models.DO_NOTHING)
    id_prest = models.ForeignKey(TPrestation, on_delete = models.DO_NOTHING)

    class Meta :
        db_table = 't_avenant'
        ordering = ['num_aven']
        verbose_name = verbose_name_plural = 'T_AVENANT'

    # Méthodes système

    def __str__(self) : return self.int_aven

class TFacture(models.Model) :

    '''Ensemble des factures d'une prestation d'un dossier'''

    # Imports
    from app.classes.MFEuroField import Class as MFEuroField
    from app.validators import val_fich_pdf

    # Méthodes liées aux colonnes

    def set_chem_pj_fact_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/factures/{0}'.format(new_fn)

    # Colonnes
    id_fact = models.AutoField(primary_key = True)
    chem_pj_fact = models.FileField(
        blank = True,
        upload_to = set_chem_pj_fact_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer le fichier scanné de la facture <span class="field-complement">(fichier PDF)</span>'
    )
    comm_fact = models.TextField(blank = True, verbose_name = 'Commentaire')
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
    mont_ht_fact = MFEuroField(blank = True, min_value = 0.01, null = True, verbose_name = 'Montant HT de la facture')
    mont_ttc_fact = MFEuroField(
        blank = True, min_value = 0.01, null = True, verbose_name = 'Montant TTC de la facture'
    )
    num_bord_fact = models.CharField(max_length = 255, verbose_name = 'Numéro de bordereau')
    num_fact = models.CharField(max_length = 255, verbose_name = 'Numéro de facture')
    num_mandat_fact = models.CharField(max_length = 255, verbose_name = 'Numéro de mandat')
    suivi_fact = models.CharField(max_length = 255)
    id_doss = models.ForeignKey(TDossier, on_delete = models.CASCADE)
    id_prest = models.ForeignKey(TPrestation, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_facture'
        ordering = ['-dt_mand_moa_fact', 'id_prest']
        verbose_name = verbose_name_plural = 'T_FACTURE'

    # Méthodes système

    def __str__(self) : return self.num_fact

class TPaiementPremierAcompte(models.Model) :

    '''Ensemble des options de paiement du premier acompte d'un financement'''

    # Colonnes
    id_paiem_prem_ac = models.AutoField(primary_key = True)
    int_paiem_prem_ac = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_paiement_premier_acompte'
        ordering = ['int_paiem_prem_ac']
        verbose_name = verbose_name_plural = 'T_PAIEMENT_PREMIER_ACOMPTE'

    # Méthodes système

    def __str__(self) : return self.int_paiem_prem_ac

class TFinancement(models.Model) :

    '''Ensemble des financements d'un dossier'''

    # Imports
    from app.classes.MFEuroField import Class as MFEuroField
    from app.classes.MFPercentField import Class as MFPercentField
    from app.validators import val_fich_pdf

    # Méthodes liées aux colonnes

    def set_chem_pj_fin_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/financements/{0}'.format(new_fn)

    # Colonnes
    id_fin = models.AutoField(primary_key = True)
    chem_pj_fin = models.FileField(
        blank = True,
        upload_to = set_chem_pj_fin_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer l\'arrêté de subvention <span class="field-complement">(fichier PDF)</span>'
    )
    comm_fin = models.TextField(blank = True, verbose_name = 'Commentaire')
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
    mont_elig_fin = MFEuroField(
        blank = True,
        min_value = 0.01,
        null = True,
        verbose_name = 'Montant [ht_ou_ttc] de l\'assiette éligible de la subvention'
    )
    mont_part_fin = MFEuroField(min_value = 0.01, verbose_name = 'Montant [ht_ou_ttc] total de la participation')
    num_arr_fin = models.CharField(blank = True, max_length = 255, verbose_name = 'Numéro de l\'arrêté ou convention')
    pourc_elig_fin = MFPercentField(blank = True, null = True, verbose_name = 'Pourcentage de l\'assiette éligible')
    pourc_real_fin = MFPercentField(blank = True, null = True, verbose_name = 'Pourcentage de réalisation des travaux')
    id_doss = models.ForeignKey(TDossier, on_delete = models.CASCADE)
    id_org_fin = models.ForeignKey(TFinanceur, on_delete = models.CASCADE, verbose_name = 'Organisme financeur')
    id_paiem_prem_ac = models.ForeignKey(
        TPaiementPremierAcompte,
        blank = True,
        null = True,
        on_delete = models.SET_NULL,
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
        verbose_name = verbose_name_plural = 'T_FINANCEMENT'

    # Extra-getters

    def get_view_object(self) :
        '''Instance :model:`app.VFinancement`'''
        from app.models.views import VFinancement
        return VFinancement.objects.get(id_fin = self.pk)

class TTypeVersement(models.Model) :

    '''Ensemble des types de versement'''

    # Colonnes
    id_type_vers = models.AutoField(primary_key = True)
    int_type_vers = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_type_versement'
        ordering = ['int_type_vers']
        verbose_name = verbose_name_plural = 'T_TYPE_VERSEMENT'

    # Méthodes système

    def __str__(self) : return self.int_type_vers

class TDemandeVersement(models.Model) :

    '''Ensemble des demandes de versement d'un financement'''

    # Imports
    from app.classes.MFEuroField import Class as MFEuroField
    from app.validators import val_fich_pdf

    # Méthodes liées aux colonnes

    def set_chem_pj_ddv_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/demandes_de_versements/{0}'.format(new_fn)

    # Colonnes
    id_ddv = models.AutoField(primary_key = True)
    chem_pj_ddv = models.FileField(
        blank = True,
        upload_to = set_chem_pj_ddv_upload_to,
        validators = [val_fich_pdf],
        verbose_name = '''
        Insérer le courrier scanné de la demande de versement <span class="field-complement">(fichier PDF)</span>
        '''
    )
    comm_ddv = models.TextField(blank = True, verbose_name = 'Commentaire')
    dt_ddv = models.DateField(
        verbose_name = 'Date de la demande de versement <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    dt_vers_ddv = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de versement <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_ddv = models.CharField(max_length = 255, verbose_name = 'Intitulé de la demande de versement')
    mont_ht_ddv = MFEuroField(
        blank = True, min_value = 0.01, null = True, verbose_name = 'Montant HT de la demande de versement'
    )
    mont_ht_verse_ddv = MFEuroField(blank = True, null = True, verbose_name = 'Montant HT versé')
    mont_ttc_ddv = MFEuroField(
        blank = True, min_value = 0.01, null = True, verbose_name = 'Montant TTC de la demande de versement'
    )
    mont_ttc_verse_ddv = MFEuroField(blank = True, null = True, verbose_name = 'Montant TTC versé')
    id_fin = models.ForeignKey(TFinancement, on_delete = models.CASCADE)
    id_type_vers = models.ForeignKey(
        TTypeVersement, on_delete = models.CASCADE, verbose_name = 'Type de demande de versement'
    )
    num_bord_ddv = models.CharField(blank = True, max_length = 255, verbose_name = 'Numéro de bordereau')
    num_titre_rec_ddv = models.CharField(blank = True, max_length = 255, verbose_name = 'Numéro de titre de recette')

    # Relations
    fact = models.ManyToManyField(TFacture, through = 'TFacturesDemandeVersement')

    class Meta :
        db_table = 't_demande_versement'
        ordering = ['-dt_ddv']
        verbose_name = verbose_name_plural = 'T_DEMANDE_VERSEMENT'

    # Extra-getters

    def get_view_object(self) :
        '''Instance :model:`app.VDemandeVersement`'''
        from app.models.views import VDemandeVersement
        return VDemandeVersement.objects.get(pk = self.pk)

    # Méthodes système

    def __str__(self) : return self.int_ddv

class TFacturesDemandeVersement(models.Model) :

    '''Ensemble des factures d'une demande de versement'''

    # Colonnes
    id_ddv = models.ForeignKey(TDemandeVersement, on_delete = models.CASCADE)
    id_fact = models.ForeignKey(TFacture, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_factures_demande_versement'
        verbose_name = verbose_name_plural = 'T_FACTURES_DEMANDE_VERSEMENT'

class TAvancementPgre(models.Model) :

    '''Ensemble des états d'avancement PGRE'''

    # Colonnes
    id_av_pgre = models.AutoField(primary_key = True)
    int_av_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé')
    ordre_av_pgre = models.PositiveIntegerField(default = 9999, verbose_name = 'Ordre (liste déroulante)')

    class Meta :
        db_table = 't_avancement_pgre'
        ordering = ['ordre_av_pgre']
        verbose_name = verbose_name_plural = 'T_AVANCEMENT_PGRE'

    # Méthodes système

    def __str__(self) : return self.int_av_pgre

class TPrioritePgre(models.Model) :

    '''Ensemble des priorités PGRE'''

    # Colonnes
    id_pr_pgre = models.AutoField(primary_key = True)
    int_pr_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_priorite_pgre'
        ordering = ['int_pr_pgre']
        verbose_name = verbose_name_plural = 'T_PRIORITE_PGRE'

    # Méthodes système

    def __str__(self) : return self.int_pr_pgre

class TInstanceConcertationPgre(models.Model) :

    '''Ensemble des instances de concertation PGRE'''

    # Colonnes
    id_ic_pgre = models.AutoField(primary_key = True)
    int_ic_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    class Meta :
        db_table = 't_instance_concertation_pgre'
        ordering = ['int_ic_pgre']
        verbose_name = verbose_name_plural = 'T_INSTANCE_CONCERTATION_PGRE'

    # Méthodes système

    def __str__(self) : return self.int_ic_pgre

class TAtelierPgre(models.Model) :

    '''Ensemble des ateliers PGRE'''

    # Colonnes
    id_atel_pgre = models.AutoField(primary_key = True)
    int_atel_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé')

    # Relations
    ic_pgre = models.ManyToManyField(TInstanceConcertationPgre, through = 'TInstancesConcertationPgreAtelierPgre')

    class Meta :
        db_table = 't_atelier_pgre'
        ordering = ['int_atel_pgre']
        verbose_name = verbose_name_plural = 'T_ATELIER_PGRE'

    # Méthodes système

    def __str__(self) : return self.int_atel_pgre

class TInstancesConcertationPgreAtelierPgre(models.Model) :

    '''Ensemble des instances de concertation PGRE pour un atelier PGRE'''

    # Colonnes
    id_atel_pgre = models.ForeignKey(TAtelierPgre, on_delete = models.CASCADE)
    id_ic_pgre = models.ForeignKey(TInstanceConcertationPgre, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_instances_concertation_pgre_atelier_pgre'
        verbose_name = verbose_name_plural = 'T_INSTANCES_CONCERTATION_PGRE_ATELIER_PGRE'

    # Méthodes système

    def __str__(self) : return '{} ({})'.format(self.id_atel_pgre, self.id_ic_pgre)

class TDossierPgre(models.Model) :

    '''Ensemble des actions PGRE'''

    # Imports
    from app.classes.MFEuroField import Class as MFEuroField
    from app.validators import val_fich_pdf

    # Méthodes liées aux colonnes

    def set_chem_pj_doss_pgre_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'actions_pgre/caracteristiques/{0}'.format(new_fn)

    # Colonnes
    id_doss_pgre = models.AutoField(primary_key = True)
    ann_prev_deb_doss_pgre = models.IntegerField(verbose_name = 'Année prévisionnelle du début de l\'action PGRE')
    chem_pj_doss_pgre = models.FileField(
        blank = True,
        upload_to = set_chem_pj_doss_pgre_upload_to,
        validators = [val_fich_pdf],
        verbose_name = 'Insérer la fiche action <span class="field-complement">(fichier PDF)</span>'
    )
    comm_doss_pgre = models.TextField(blank = True, verbose_name = 'Commentaire')
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
    int_doss_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé de l\'action PGRE')
    mont_doss_pgre = MFEuroField(default = 0, verbose_name = 'Montant de l\'action PGRE')
    num_doss_pgre = models.CharField(max_length = 255, unique = True, verbose_name = 'Numéro de l\'action PGRE')
    obj_econ_ress_doss_pgre = models.FloatField(
        verbose_name = 'Objectifs d\'économie de la ressource en eau (en m<sup>3</sup>)'
    )
    id_doss = models.ForeignKey(TDossier, blank = True, null = True, on_delete = models.SET_NULL)
    id_ic_pgre = models.ForeignKey(
        TInstanceConcertationPgre, on_delete = models.CASCADE, verbose_name = 'Instance de concertation'
    )
    id_pr_pgre = models.ForeignKey(TPrioritePgre, on_delete = models.CASCADE, verbose_name = 'Priorité')
    id_av_pgre = models.ForeignKey(TAvancementPgre, on_delete = models.CASCADE, verbose_name = 'État d\'avancement')
    id_nat_doss = models.ForeignKey(
        TNatureDossier, on_delete = models.CASCADE, verbose_name = 'Nature de l\'action PGRE'
    )

    # Relations
    atel_pgre = models.ManyToManyField(TAtelierPgre, through = 'TAteliersPgreDossierPgre')
    moa = models.ManyToManyField(TMoa, through = 'TMoaDossierPgre')
    ss_action_pgre = models.ManyToManyField('TDossierSsAction')

    class Meta :
        db_table = 't_dossier_pgre'
        ordering = ['num_doss_pgre']
        verbose_name = verbose_name_plural = 'T_DOSSIER_PGRE'

    # Méthodes publiques

    @property
    def mont_doss_pgre_ppt(self):
        if self.ss_action_pgre.exists():
            return self.ss_action_pgre.all().aggregate(montant=Sum('mont_ss_action_pgre')).get('montant', 0)
        return self.mont_doss_pgre

    @property
    def obj_econ_ress_doss_pgre_ppt(self):
        if self.ss_action_pgre.exists():
            return self.ss_action_pgre.all().aggregate(objectif=Sum('obj_econ_ress_ss_action_pgre')).get('objectif', 0)
        return self.obj_econ_ress_doss_pgre

    # Méthodes système

    def save(self, *args, **kwargs) :

        TAvancementPgreTraces = apps.get_model('app', model_name='TAvancementPgreTraces')

        # Si création d'un dossier je garde une trace de l'avancement originale
        # Sinon je garde une trace si le champ id_av_pgre a été modifié par l'opération en cours
        old = TDossierPgre.objects.get(id_doss_pgre=self.id_doss_pgre) if self.id_doss_pgre else None
        super().save(*args, **kwargs)
        if not old or self.id_av_pgre != old.id_av_pgre:
            TAvancementPgreTraces.objects.create(
                id_doss_pgre=self,
                id_av_pgre=self.id_av_pgre)

    def __str__(self) : return self.num_doss_pgre

class TAteliersPgreDossierPgre(models.Model) :

    '''Ensemble des ateliers PGRE d'une action PGRE'''

    # Colonnes
    id_atel_pgre = models.ForeignKey(TAtelierPgre, on_delete = models.CASCADE)
    id_doss_pgre = models.ForeignKey(TDossierPgre, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_ateliers_pgre_dossier_pgre'
        ordering = ['id_atel_pgre']
        verbose_name = verbose_name_plural = 'T_ATELIERS_PGRE_DOSSIER_PGRE'

class TMoaDossierPgre(models.Model) :

    '''Ensemble des maîtres d'ouvrage d'une action PGRE'''

    # Colonnes
    id_doss_pgre = models.ForeignKey(TDossierPgre, on_delete = models.CASCADE)
    id_org_moa = models.ForeignKey(TMoa, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_moa_dossier_pgre'
        ordering = ['id_org_moa']
        verbose_name = verbose_name_plural = 'T_MOA_DOSSIER_PGRE'

class TControleDossierPgre(models.Model) :

    '''Ensemble des points de contrôle d'une action PGRE'''

    # Colonnes
    id_contr_doss_pgre = models.AutoField(primary_key = True)
    dt_contr_doss_pgre = models.DateField(
        verbose_name = 'Date du contrôle <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    obj_real_contr_doss_pgre = models.FloatField(
        verbose_name = 'Objectif réalisé en terme d\'économie de la ressource en eau (en m<sup>3</sup>)'
    )
    id_doss_pgre = models.ForeignKey(TDossierPgre, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_controle_dossier_pgre'
        ordering = ['dt_contr_doss_pgre']
        verbose_name = verbose_name_plural = 'T_CONTROLE_DOSSIER_PGRE'

class TDossierPgreGeom(gismodels.Model) :

    '''Ensemble des géométries d'une action PGRE'''

    # Colonnes
    gid = models.UUIDField(default = uuid.uuid4, editable = False, primary_key = True)
    geom_lin = gismodels.LineStringField(blank = True, null = True, srid = 4326)
    geom_pct = gismodels.PointField(blank = True, null = True, srid = 4326)
    geom_pol = gismodels.PolygonField(blank = True, null = True, srid = 4326)
    objects = gismodels.GeoManager()
    id_doss_pgre = models.ForeignKey(TDossierPgre, on_delete = models.CASCADE)

    class Meta :
        db_table = 't_dossier_pgre_geom'
        verbose_name = verbose_name_plural = 'T_DOSSIER_PGRE_GEOM'

class TPhotoPgre(models.Model) :

    '''Ensemble des photos d'une action PGRE'''

    # Imports
    from app.validators import val_fich_img

    # Méthodes liées aux colonnes
    def set_chem_ph_pgre_upload_to(_i, _fn) :

        # Imports
        from app.functions import gen_cdc

        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'actions_pgre/photos/{0}'.format(new_fn)

    # Colonnes
    id_ph_pgre = models.AutoField(primary_key = True)
    chem_ph_pgre = models.FileField(
        upload_to = set_chem_ph_pgre_upload_to,
        validators = [val_fich_img],
        verbose_name = 'Insérer une photo <span class="field-complement">(taille limitée à 3 Mo)</span>'
    )
    descr_ph_pgre = models.CharField(blank = True, max_length = 255, verbose_name = 'Description')
    dt_pv_ph_pgre = models.DateField(
        blank = True,
        null = True,
        verbose_name = 'Date de prise de vue <span class="field-complement">(JJ/MM/AAAA)</span>'
    )
    int_ph_pgre = models.CharField(max_length = 255, verbose_name = 'Intitulé de la photo')
    id_doss_pgre = models.ForeignKey(TDossierPgre, on_delete = models.CASCADE)
    id_ppv_ph = models.ForeignKey(
        TPeriodePriseVuePhoto, on_delete = models.CASCADE, verbose_name = 'Période de prise de vue'
    )

    class Meta :
        db_table = 't_photo_pgre'
        ordering = ['id_ppv_ph__ordre_ppv_ph', 'dt_pv_ph_pgre']
        verbose_name = verbose_name_plural = 'T_PHOTO_PGRE'

    # Méthodes système

    def __str__(self) : return self.int_ph_pgre

class TAvancementPgreTraces(models.Model):

    '''Ensemble des états d'avancement d'une action PGRE'''

    # Colonnes
    id_trace = models.AutoField(primary_key = True)
    id_doss_pgre = models.ForeignKey('TDossierPgre', db_column = 'id_doss_pgre', on_delete = models.CASCADE)
    id_av_pgre = models.ForeignKey('TAvancementPgre', db_column = 'id_av_pgre', on_delete = models.CASCADE)
    date_modif_av = models.DateTimeField(
        auto_now_add = True, verbose_name = 'Horodatage du changement d\'état d\'avancement'
    )

    class Meta :
        db_table = 't_avancement_pgre_traces'
        ordering = ['id_trace']

class TDossierSsAction(models.Model):

    '''Ensemble des sous-actions d'une action PGRE'''

    # Imports
    from app.classes.MFEuroField import Class as MFEuroField

    # Colonnes
    id_ss_act = models.AutoField(primary_key = True)
    lib_ss_act = models.CharField(max_length = 255, verbose_name = 'Libellé')
    desc_ss_act = models.TextField(blank = True, verbose_name = 'Descriptif')
    comm_ss_act = models.TextField(blank = True, verbose_name = 'Commentaire')
    dt_prevision_ss_action_pgre = models.DateField(verbose_name = 'Prévisionnel')
    dt_deb_ss_action_pgre = models.DateField(blank = True, null = True, verbose_name = 'Début')
    dt_fin_ss_action_pgre = models.DateField(blank = True, null = True, verbose_name = 'Fin')
    mont_ss_action_pgre = MFEuroField(verbose_name = 'Montant')
    obj_econ_ress_ss_action_pgre = models.FloatField(verbose_name = 'Objectif d\'économie de ressource')
    t_nature_dossier = models.ForeignKey('TNatureDossier', db_column = 'id_nat_doss', on_delete = models.CASCADE)
    id_av_pgre = models.ForeignKey('TAvancementPgre', db_column = 'id_av_pgre', on_delete = models.CASCADE)

    # Relations
    moa = models.ManyToManyField(TMoa)

    class Meta :
        db_table = 't_dossier_pgre_ss_action'

class TFicheVie(models.Model) :

    '''Ensemble des éléments composant la fiche de vie d'un dossier'''

    from app.validators import val_fich_pdf

    def set_chem(_i, _fn):
        # Imports
        from app.functions import gen_cdc
        new_fn = '{0}.{1}'.format(gen_cdc(), _fn.split('.')[-1])
        return 'dossiers/fdv/{0}'.format(new_fn)

    # Colonnes
    id_fdv = models.AutoField(primary_key = True)
    d_fdv = models.DateField(verbose_name = 'Date')
    lib_fdv = models.CharField(max_length = 255, verbose_name = 'Événement')
    comm_fdv = models.TextField(blank = True, verbose_name = 'Commentaire')
    id_doss = models.ForeignKey(TDossier, db_column = 'id_doss', on_delete = models.CASCADE)
    chem_pj_fdv = models.FileField(
        blank = True,
        upload_to = set_chem,
        # validators = [val_fich_pdf],
        verbose_name = 'Insérer la pièce jointe. '
    )

    class Meta :
        db_table = 't_fiche_vie'
        ordering = ['-d_fdv']

class TTypeOrdreService(models.Model) :

    '''Ensemble des types d'ordre de service'''

    # Colonnes
    id_type_os = models.AutoField(primary_key = True)
    nom_type_os = models.CharField(max_length = 255, verbose_name = 'Nom')
    ordre_type_os = models.PositiveIntegerField(default = 9999, verbose_name = 'Ordre (liste déroulante)')

    class Meta :
        db_table = 't_type_ordre_service'
        ordering = ['ordre_type_os', 'nom_type_os']
        verbose_name = verbose_name_plural = 'T_TYPE_ORDRE_SERVICE'

    def __str__(self) : return self.nom_type_os

class TOrdreService(models.Model) :

    '''Ensemble des ordres de service composant une prestation d'un dossier'''

    # Colonnes
    id_os = models.AutoField(primary_key = True)
    comm_os = models.TextField(blank = True, verbose_name = 'Commentaire')
    d_emiss_os = models.DateField(verbose_name = 'Date d\'effet')
    duree_w_os = models.PositiveIntegerField(
        default = 0, verbose_name = 'Durée travaillée (en nombre de jours ouvrés)'
    )
    num_os = models.CharField(max_length = 255, verbose_name = 'Numéro de l\'ordre de service')
    obj_os = models.CharField(max_length = 255, verbose_name = 'Objet')
    id_doss = models.ForeignKey(TDossier, db_column = 'id_doss', on_delete = models.CASCADE)
    id_prest = models.ForeignKey(
        TPrestation, db_column = 'id_prest', on_delete = models.CASCADE, verbose_name = 'Prestation'
    )
    id_type_os = models.ForeignKey(
        TTypeOrdreService,
        db_column = 'id_type_os',
        on_delete = models.CASCADE,
        verbose_name = 'Type de l\'ordre de service'
    )

    class Meta :
        db_table = 't_ordre_service'
        ordering = ['d_emiss_os', 'id_type_os']