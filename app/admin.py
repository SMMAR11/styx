#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.forms.admin import *
from app.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

# Je désactive l'action de base.
admin.site.disable_action('delete_selected')

class ANatureDossier(admin.ModelAdmin) :

	# Je déclare les actions supplémentaires.
	def set_peu_doss_on(_madm, _r, _qs) :
		_qs.update(peu_doss = True)
	set_peu_doss_on.short_description = '''
	Rendre les T_NATURE_DOSSIER sélectionnés utilisables pour le module de gestion des dossiers
	'''

	def set_peu_doss_off(_madm, _r, _qs) :
		_qs.update(peu_doss = False)
	set_peu_doss_off.short_description = '''
	Rendre les T_NATURE_DOSSIER sélectionnés inutilisables pour le module de gestion des dossiers
	'''

	def set_peu_doss_pgre_on(_madm, _r, _qs) :
		_qs.update(peu_doss_pgre = True)
	set_peu_doss_pgre_on.short_description = '''
	Rendre les T_NATURE_DOSSIER sélectionnés utilisables pour le module de gestion des actions PGRE
	'''

	def set_peu_doss_pgre_off(_madm, _r, _qs) :
		_qs.update(peu_doss_pgre = False)
	set_peu_doss_pgre_off.short_description = '''
	Rendre les T_NATURE_DOSSIER sélectionnés inutilisables pour le module de gestion des actions PGRE
	'''

	# J'initialise les paramètres.
	actions = [
		set_peu_doss_on,
		set_peu_doss_off,
		set_peu_doss_pgre_on,
		set_peu_doss_pgre_off,
		admin.actions.delete_selected
	]
	list_display = ['int_nat_doss', 'peu_doss', 'peu_doss_pgre']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_nat_doss'),
			)
		}),
		('Options', {
			'fields' : (
				('peu_doss'),
				('peu_doss_pgre')
			)
		})
	)

# Je peux désormais gérer les natures de dossiers.
admin.site.register(TNatureDossier, ANatureDossier)

class ATechnicien(admin.ModelAdmin) :

	# Je déclare les actions supplémentaires.
	def set_en_act_on(_madm, _r, _qs) :
		_qs.update(en_act = True)
	set_en_act_on.short_description = 'Rendre les T_TECHNICIEN sélectionnés actifs'

	def set_en_act_off(_madm, _r, _qs) :
		_qs.update(en_act = False)
	set_en_act_off.short_description = 'Rendre les T_TECHNICIEN sélectionnés inactifs'

	# Je mets en forme la première colonne du tableau.
	def n_comp_techn(self, _o) :
		return '{0} {1}'.format(_o.n_techn, _o.pren_techn)
	n_comp_techn.allow_tags = True
	n_comp_techn.short_description = 'Nom complet'

	# J'initialise les paramètres.
	actions = [set_en_act_on, set_en_act_off, admin.actions.delete_selected]
	list_display = ('n_comp_techn', 'en_act')
	list_filter = (
		('en_act', admin.BooleanFieldListFilter),
	)

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('n_techn'),
				('pren_techn'),
				('en_act')
			)
		}),
	)

# Je peux désormais gérer les techniciens.
admin.site.register(TTechnicien, ATechnicien)

class AAvisCp(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_av_cp']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_av_cp'),
			)
		}),
	)

# Je peux désormais gérer les avis du comité de programmation.
admin.site.register(TAvisCp, AAvisCp)

class AAvancement(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_av', 'ordre_av']	

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_av'),
				('ordre_av'),
				('id_av_pere'),
			)
		}),
	)

# Je peux désormais gérer les états d'avancements d'un dossier.
admin.site.register(TAvancement, AAvancement)

class ATypeProgramme(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_type_progr']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_progr'),
			)
		}),
	)

# Je peux désormais gérer les types de programmes.
admin.site.register(TTypeProgramme, ATypeProgramme)

class ATypeGeom(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_type_geom']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_geom'),
			)
		}),
	)

# Je peux désormais gérer les types de géométries.
admin.site.register(TTypeGeom, ATypeGeom)

class ATypeProgrammeInline(admin.TabularInline) :

	extra = 0
	model = TTypeDossier.type_progr.through
	verbose_name = ''

class ATypeGeomInline(admin.TabularInline) :

	extra = 0
	model = TTypeDossier.type_geom.through
	verbose_name = ''

class ATypeDossier(admin.ModelAdmin) :

	# Je mets en forme la dernière colonne du tableau.
	def les_type_progr(self, _o) :
		arr = []
		for tp in _o.type_progr.all() :
			arr.append(tp.int_type_progr)
		return ', '.join(arr)
	les_type_progr.allow_tags = True
	les_type_progr.short_description = 'Type(s) de programme(s)'

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	inlines = [ATypeProgrammeInline, ATypeGeomInline]
	list_display = ['int_type_doss', 'les_type_progr']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_doss'),
			)
		}),
	)

# Je peux désormais gérer les types de dossiers.
admin.site.register(TTypeDossier, ATypeDossier)

class AProgramme(admin.ModelAdmin) :

	# Je déclare les actions supplémentaires.
	def set_en_act_on(_madm, _r, _qs) :
		_qs.update(en_act = True)
	set_en_act_on.short_description = 'Rendre les T_PROGRAMME sélectionnés actifs'

	def set_en_act_off(_madm, _r, _qs) :
		_qs.update(en_act = False)
	set_en_act_off.short_description = 'Rendre les T_PROGRAMME sélectionnés inactifs'

	# J'initialise les paramètres.
	actions = [set_en_act_on, set_en_act_off, admin.actions.delete_selected]
	list_display = ['int_progr', 'id_type_progr', 'en_act']
	list_filter = (
		'id_type_progr',
		('en_act', admin.BooleanFieldListFilter),
	)

	# Je déclare les champs en lecture seule lors d'une mise à jour.
	def get_readonly_fields(self, _r, _o = None) :
		if _o :
			return self.readonly_fields + ('dim_progr',)
		return self.readonly_fields

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_progr'),
				('id_type_progr'),
				('en_act')
			)
		}),
		('Options', {
			'fields' : (
				('dim_progr'),
				('seq_progr')
			)
		})
	)

# Je peux désormais gérer les programmes.
admin.site.register(TProgramme, AProgramme)

class AAxe(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ('__str__', 'id_progr')
	list_filter = ['id_progr']

	# Je déclare les champs en lecture seule lors d'une mise à jour.
	def get_readonly_fields(self, _r, _o = None) :
		if _o :
			return self.readonly_fields + ('num_axe', 'id_progr')
		return self.readonly_fields

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('id_progr'),
				('num_axe'),
				('int_axe')
			)
		}),
	)

# Je peux désormais gérer les axes.
admin.site.register(TAxe, AAxe)

class ASousAxe(admin.ModelAdmin) :

	# Je mets en forme les colonnes du tableau.
	def int_progr(self, _o) :
		return _o.id_axe.id_progr.int_progr
	int_progr.allow_tags = True
	int_progr.short_description = 'Programme'

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ('__str__', 'int_progr')
	list_filter = ['id_axe__id_progr']

	# Je déclare les champs en lecture seule lors d'une mise à jour.
	def get_readonly_fields(self, _r, _o = None) :
		if _o :
			return self.readonly_fields + ('id_axe', 'num_ss_axe')
		return self.readonly_fields

	form = MSousAxe

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('id_axe'),
				('num_ss_axe'),
				('int_ss_axe')
			)
		}),
	)

# Je peux désormais gérer les sous-axes.
admin.site.register(TSousAxe, ASousAxe)

class AAction(admin.ModelAdmin) :

	# Je mets en forme les colonnes du tableau.
	def int_progr(self, _o) :
		return _o.id_ss_axe.id_axe.id_progr.int_progr
	int_progr.allow_tags = True
	int_progr.short_description = 'Programme'

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ('__str__', 'int_progr')
	list_filter = ['id_ss_axe__id_axe__id_progr']

	# Je déclare les champs en lecture seule lors d'une mise à jour.
	def get_readonly_fields(self, _r, _o = None) :
		if _o :
			return self.readonly_fields + ('id_ss_axe', 'num_act')
		return self.readonly_fields

	form = MAction

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('id_ss_axe'),
				('num_act'),
				('int_act')
			)
		}),
	)

# Je peux désormais gérer les actions.
admin.site.register(TAction, AAction)

class AMoaInline(admin.TabularInline) :

	extra = 0
	fk_name = 'id_org_moa_fil'
	model = TMoa.moa.through
	verbose_name = ''

class AMoa(admin.ModelAdmin) :

	# Je déclare les actions supplémentaires.
	def set_peu_doss_on(_madm, _r, _qs) :
		_qs.update(peu_doss = True)
	set_peu_doss_on.short_description = '''
	Rendre les T_MOA sélectionnés utilisables pour le module de gestion des dossiers
	'''

	def set_peu_doss_off(_madm, _r, _qs) :
		_qs.update(peu_doss = False)
	set_peu_doss_off.short_description = '''
	Rendre les T_MOA sélectionnés inutilisables pour le module de gestion des dossiers
	'''

	def set_en_act_doss_on(_madm, _r, _qs) :
		_qs.update(en_act_doss = True)
	set_en_act_doss_on.short_description = '''
	Rendre les T_MOA sélectionnés actifs pour le module de gestion des dossiers
	'''

	def set_en_act_doss_off(_madm, _r, _qs) :
		_qs.update(en_act_doss = False)
	set_en_act_doss_off.short_description = '''
	Rendre les T_MOA sélectionnés inactifs pour le module de gestion des dossiers
	'''

	def set_peu_doss_pgre_on(_madm, _r, _qs) :
		_qs.update(peu_doss_pgre = True)
	set_peu_doss_pgre_on.short_description = '''
	Rendre les T_MOA sélectionnés utilisables pour le module de gestion des actions PGRE
	'''

	def set_peu_doss_pgre_off(_madm, _r, _qs) :
		_qs.update(peu_doss_pgre = False)
	set_peu_doss_pgre_off.short_description = '''
	Rendre les T_MOA sélectionnés inutilisables pour le module de gestion des actions PGRE
	'''

	def set_en_act_doss_pgre_on(_madm, _r, _qs) :
		_qs.update(en_act_doss_pgre = True)
	set_en_act_doss_pgre_on.short_description = '''
	Rendre les T_MOA sélectionnés actifs pour le module de gestion des actions PGRE
	'''

	def set_en_act_doss_pgre_off(_madm, _r, _qs) :
		_qs.update(en_act_doss_pgre = False)
	set_en_act_doss_pgre_off.short_description = '''
	Rendre les T_MOA sélectionnés inactifs pour le module de gestion des actions PGRE
	'''

	# J'initialise les paramètres.
	actions = [
		set_peu_doss_on,
		set_peu_doss_off,
		set_en_act_doss_on,
		set_en_act_doss_off,
		set_peu_doss_pgre_on,
		set_peu_doss_pgre_off,
		set_en_act_doss_pgre_on,
		set_en_act_doss_pgre_off,
		admin.actions.delete_selected
	]
	inlines = [AMoaInline]
	list_display = ['n_org', 'peu_doss', 'en_act_doss', 'peu_doss_pgre', 'en_act_doss_pgre']
	list_filter = (
		('peu_doss', admin.BooleanFieldListFilter),
		('en_act_doss', admin.BooleanFieldListFilter),
		('peu_doss_pgre', admin.BooleanFieldListFilter),
		('en_act_doss_pgre', admin.BooleanFieldListFilter)
	)

	# Je mets en forme le formulaire.
	fields = [
		'n_org',
		'dim_org_moa',
		'peu_doss',
		'en_act_doss',
		'peu_doss_pgre',
		'en_act_doss_pgre',
		'logo_org_moa'
	]

# Je peux désormais gérer les maîtres d'ouvrages.
admin.site.register(TMoa, AMoa)

class ADroitInline(admin.TabularInline) :

	extra = 0
	model = TUtilisateur.moa.through
	verbose_name = ''

class AUtilisateur(UserAdmin) :

	# Je déclare les actions supplémentaires.
	def set_is_active_on(_madm, _r, _qs) :
		_qs.update(is_active = True)
	set_is_active_on.short_description = 'Rendre les T_UTILISATEUR sélectionnés actifs'

	def set_is_active_off(_madm, _r, _qs) :
		_qs.update(is_active = False)
	set_is_active_off.short_description = 'Rendre les T_UTILISATEUR sélectionnés inactifs'

	# J'initialise les paramètres.
	actions = [set_is_active_on, set_is_active_off, admin.actions.delete_selected]
	inlines = [ADroitInline]
	list_display = ['username', 'last_name', 'first_name', 'email', 'id_org', 'is_active', 'is_superuser', 'last_login']
	list_filter = (
		('is_active', admin.BooleanFieldListFilter),
		('is_superuser', admin.BooleanFieldListFilter)
	)
	search_fields = ('username',)

	form = MUtilisateurUpdate
	add_form = MUtilisateurCreate

	# Je mets en forme les formulaires.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('last_name'),
				('first_name'),
				('email'),
				('id_org'),
				('tel_util'),
				('port_util')
			)
		}),
		('Identifiants', {
			'fields' : (
				('username'),
				('password')
			)
		}),
		('Permissions', {
			'fields' : (
				('is_active'),
				('is_staff'),
				('is_superuser'),
				('groups')
			)
		})
	)

	add_fieldsets = (
		('Informations générales', {
			'fields' : (
				('last_name'),
				('first_name'),
				('email'),
				('id_org')
			)
		}),
		('Identifiants', {
			'fields' : (
				('username'),
				('zs_pwd1'),
				('zs_pwd2')
			)
		}),
		('Options', {
			'fields' : (
				('cb_est_techn'),
			)
		}),
		('Permissions', {
			'fields' : (
				('groups'),
			)
		}),
	)

# Je peux désormais gérer les utilisateurs.
admin.site.register(TUtilisateur, AUtilisateur)

# Je retire les fonctionnalités de base.
admin.site.unregister(User)
#admin.site.unregister(Group)

class ASage(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['n_sage']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('n_sage'),
			)
		}),
	)

# Je peux désormais gérer les SAGE.
admin.site.register(TSage, ASage)

class ATypeDeclaration(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_type_decl']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_decl'),
			)
		}),
	)

# Je peux désormais gérer les types de déclarations.
admin.site.register(TTypeDeclaration, ATypeDeclaration)

class ATypeAvancementArrete(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_type_av_arr', 'ordre_type_av_arr']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_av_arr'),
			)
		}),
		('Options', {
			'fields' : (
				('ordre_type_av_arr'),
			)
		})
	)

# Je peux désormais gérer les types d'avancements d'un arrêté.
admin.site.register(TTypeAvancementArrete, ATypeAvancementArrete)

class APeriodePriseVuePhoto(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_ppv_ph', 'ordre_ppv_ph']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_ppv_ph'),
			)
		}),
		('Options', {
			'fields' : (
				('ordre_ppv_ph'),
			)
		})
	)

# Je peux désormais gérer les périodes de prise de vue d'une photo.
admin.site.register(TPeriodePriseVuePhoto, APeriodePriseVuePhoto)

class APrestataire(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['n_org', 'siret_org_prest']

	# Je mets en forme le formulaire.
	fields = [
		'n_org',
		'siret_org_prest',
		'num_dep'
	]

# Je peux désormais gérer les prestataires.
admin.site.register(TPrestataire, APrestataire)

class AFinanceur(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['n_org']

	# Je mets en forme le formulaire.
	fields = ['n_org']

# Je peux désormais gérer les financeurs.
admin.site.register(TFinanceur, AFinanceur)

class ANaturePrestation(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_nat_prest']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_nat_prest'),
			)
		}),
	)

# Je peux désormais gérer les natures de prestations.
admin.site.register(TNaturePrestation, ANaturePrestation)

class APaiementPremierAcompte(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_paiem_prem_ac']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_paiem_prem_ac'),
			)
		}),
	)

# Je peux désormais gérer les types de paiements du premier acompte.
admin.site.register(TPaiementPremierAcompte, APaiementPremierAcompte)

class ATypeVersement(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_type_vers']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_vers'),
			)
		}),
	)

# Je peux désormais gérer les types de versements.
admin.site.register(TTypeVersement, ATypeVersement)

class AAvancementPgre(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_av_pgre', 'ordre_av_pgre']	

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_av_pgre'),
				('ordre_av_pgre')
			)
		}),
	)

# Je peux désormais gérer les états d'avancements d'une action PGRE.
admin.site.register(TAvancementPgre, AAvancementPgre)

class APrioritePgre(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_pr_pgre']	

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_pr_pgre'),
			)
		}),
	)

# Je peux désormais gérer les niveaux de priorité d'une action PGRE.
admin.site.register(TPrioritePgre, APrioritePgre)

class AInstanceConcertationPgre(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_ic_pgre']	

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_ic_pgre'),
			)
		}),
	)

# Je peux désormais gérer les instances de concertation PGRE.
admin.site.register(TInstanceConcertationPgre, AInstanceConcertationPgre)

class AInstanceConcertationPgreInline(admin.TabularInline) :

	extra = 0
	model = TAtelierPgre.ic_pgre.through
	verbose_name = ''

class AAtelierPgre(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	inlines = [AInstanceConcertationPgreInline]
	list_display = ['int_atel_pgre']	

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_atel_pgre'),
			)
		}),
	)

# Je peux désormais gérer les ateliers PGRE.
admin.site.register(TAtelierPgre, AAtelierPgre)

class AOrganisme(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['n_org']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('n_org'),
				('tel_org'),
				('port_org'),
				('courr_org'),
				('site_web_org')
			)
		}),
		('Adresse', {
			'fields' : (
				('adr_org'),
				('compl_adr_org'),
				('cp_org'),
				('num_comm'),
				('cedex_org'),
				('bp_org')
			)
		}),
		('Autres', {
			'fields' : (
				('comm_org'),
			)
		})
	)

# Je peux désormais gérer les organismes (exclus de l'héritage).
admin.site.register(TOrganisme, AOrganisme)

class ATypeOrdreService(admin.ModelAdmin) :

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	fields = list_display = ['nom_type_os', 'ordre_type_os']

# Je peux désormais gérer les types d'ordres de service
admin.site.register(TTypeOrdreService, ATypeOrdreService)

# ---------------------------------------------------------------------
# PROGRAMMATION
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Administration du modèle TCDGemapiCdg
# ---------------------------------------------------------------------

# Administration du modèle TDdsCdg
class DdsCdgInline(admin.TabularInline):

	# Options
	extra = 0
	fields = ('dds_id',)
	model = TCDGemapiCdg.dds.through
	verbose_name = 'Dossier'
	verbose_name_plural = 'Dossiers'

# Administration du modèle TCDGemapiCdg
class CDGemapiCdg(admin.ModelAdmin):

	# Options
	actions = (admin.actions.delete_selected,)
	fields = ('cdg_date', 'cdg_com')
	inlines = (DdsCdgInline,)
	list_display = ('__str__',)
	list_filter = ('cdg_date',)

admin.site.register(TCDGemapiCdg, CDGemapiCdg)

# ---------------------------------------------------------------------
# Administration du modèle TDdsCdg
# ---------------------------------------------------------------------

# Administration du modèle TAcpFinDdsCdg
class AcpFinDdsCdgInline(admin.TabularInline):

	# Options
	extra = 0
	fields = ('fin_id', 'acp_id', 'acpfinddscdg_com')
	model = TAcpFinDdsCdg
	verbose_name = 'Avis d\'un partenaire'
	verbose_name_plural = 'Avis des partenaires'

# Administration du modèle TDdsCdg
class DdsCdg(admin.ModelAdmin):

	# Imports
	from app.forms.admin import UpdateDdsCdgAdmin

	# Options
	actions = (admin.actions.delete_selected,)
	fields = ('dds_id', 'int_doss', 'cdg_id', 'acp_id', 'ddscdg_com')
	form = UpdateDdsCdgAdmin
	inlines = (AcpFinDdsCdgInline,)
	list_display = (
		'dds_id',
		'int_doss',
		'cdg_id',
		'acp_id',
		'ddscdg_pdf_modifie'
	)
	list_filter = ('cdg_id',)

	# Méthodes Django

	def get_readonly_fields(self, rq, obj=None):
		if obj:
			return self.readonly_fields + ('cdg_id', 'dds_id')
		return self.readonly_fields

	def has_add_permission(self, rq):
		return False

	def has_delete_permission(self, rq, obj=None):
		return False

	def render_change_form(self, rq, cntxt, *args, **kwargs):
		self.change_form_template = 'admin/app/change_form_ddscdg.html'
		extra = {
			'fins': '''
	        Le plan de financement peut être modifié en utilisant <a
	        class="related-widget-wrapper-link change-related"
	        href="../../../findds/{}/change/?_popup=1&ddscdg={}" id="change_findds"
	        >ce formulaire</a>.
	        '''.format(cntxt['original'].dds_id.pk, cntxt['original'].pk)
		}
		cntxt.update(extra)
		return super().render_change_form(rq, cntxt, *args, **kwargs)

	# Méthodes colonnes

	def int_doss(self, obj):
		from app.models import VSuiviDossier
		return VSuiviDossier.objects.get(pk=obj.dds_id.pk).int_doss
	int_doss.allow_tags = True
	int_doss.short_description = 'Intitulé du dossier'

admin.site.register(TDdsCdg, DdsCdg)

# ---------------------------------------------------------------------
# Administration du modèle FinDds
# ---------------------------------------------------------------------

# Administration du modèle TFinancement
class FinInline(admin.TabularInline):

	# Imports
	from app.forms.admin import UpdateFinAdmin

	# Options
	extra = 0
	fields = (
		'id_org_fin',
		'mont_elig_fin',
		'pourc_elig_fin',
		'mont_part_fin'
	)
	form = UpdateFinAdmin
	model = TFinancement
	ordering = ('id_org_fin',)
	verbose_name = 'Financement'
	verbose_name_plural = 'Plan de financement du dossier'

# Administration du modèle FinDds
class FinDdsAdmin(admin.ModelAdmin):

	"""Administration du modèle FinDds"""

	# Options
	fields = ('num_doss', 'mont_doss')
	inlines = (FinInline,)
	list_display = (
		'num_doss',
		'id_nat_doss',
		'id_type_doss',
		'lib_1_doss',
		'lib_2_doss'
	)
	search_fields = ('num_doss',)

	# Méthodes Django

	def get_readonly_fields(self, rq, obj=None):
		if obj:
			return self.readonly_fields + ('mont_doss', 'num_doss')
		return self.readonly_fields

	def has_add_permission(self, rq):
		return False

	def has_delete_permission(self, rq, obj=None):
		return False

	def save_model(self, rq, obj, form, change):
		ddscdg = rq.GET.get('ddscdg')
		if ddscdg:
			oDdsCdg = TDdsCdg.objects.get(pk=ddscdg)
			oDdsCdg.ddscdg_pdf_modifie = True
			oDdsCdg.save()
		return super().save_model(rq, obj, form, change)

admin.site.register(FinDds, FinDdsAdmin)

# ---------------------------------------------------------------------
# Administration du modèle TProgrammeDetaillePrg
# ---------------------------------------------------------------------

# Filtrage personnalisé par programme d'actions
class PrgProListFilter(admin.SimpleListFilter):

	# Options
	parameter_name = 'pro'
	title = 'Programme d\'actions'

	# Méthodes Django

	def lookups(self, rq, mdl_admin):

		# Imports
		from app.models import TProgramme

		# Définition des programmes d'actions
		qsPros = TProgramme.objects.none()
		for iPrg in mdl_admin.get_queryset(rq):
			qsPros |= TProgramme.objects.filter(pk=iPrg.get_pro().pk)

		return ((iPrg.pk, iPrg) for iPrg in qsPros)

	def queryset(self, rq, qs):
		if self.value():
			return qs.filter(act_id__startswith=(self.value() + '_'))
		return qs

# Administration du modèle TProgrammeDetaillePrg
class ProgrammeDetaillePrg(admin.ModelAdmin):

	"""Administration du modèle FinDds"""

	# Options
	fieldsets = (
		('Informations générales', {
			'fields': (
				('prg_id'),
				('act_id'),
				('moa_id')
			)
		}),
		('Programme d\'actions', {
			'fields': (
				('prg_mnt1'),
				('prg_mnt_est_ttc'),
				('prg_nbre_dos')
			)
		}),
		('Autres', {
			'fields': (
				('prg_mnt_contrac_autres'),
				('prg_mnt_comman_autres'),
				('prg_mnt_factu_autres')
			)
		})
	)
	list_display = (
		'prg_id',
		'pro',
		'act_id_str',
		'moa_id',
		'prg_mnt1',
		'prg_mnt_est_ttc',
		'prg_nbre_dos',
		'prg_mnt_contrac_autres',
		'prg_mnt_comman_autres',
		'prg_mnt_factu_autres'
	)
	list_filter = (PrgProListFilter,)
	ordering = ('act_id',)

	# Méthodes Django

	def get_readonly_fields(self, rq, obj=None):
		if obj:
			return self.readonly_fields + ('prg_id', 'act_id', 'moa_id')
		return self.readonly_fields

	def has_add_permission(self, rq):
		return False

	def has_delete_permission(self, rq, obj=None):
		return False

	# Méthodes

	def act_id_str(self, obj):
		"""
		Colonne act_id
		"""
		return obj.get_brn()
	act_id_str.short_description = 'Axe/Action'

	def pro(self, obj):
		"""
		Programme d'actions
		"""
		return obj.get_pro()
	pro.short_description = 'Programme d\'actions'
	
admin.site.register(TProgrammeDetaillePrg, ProgrammeDetaillePrg)