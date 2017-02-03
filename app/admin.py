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

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ['int_nat_doss']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_nat_doss'),
			)
		}),
	)

# Je peux désormais gérer les natures de dossiers.
admin.site.register(TNatureDossier, ANatureDossier)

class ATechnicien(admin.ModelAdmin) :

	# Je déclare les actions supplémentaires.
	def set_en_act_techn_on(_madm, _r, _qs) :
		_qs.update(en_act_techn = True)
	set_en_act_techn_on.short_description = 'Rendre les T_TECHNICIEN sélectionnés actifs'

	def set_en_act_techn_off(_madm, _r, _qs) :
		_qs.update(en_act_techn = False)
	set_en_act_techn_off.short_description = 'Rendre les T_TECHNICIEN sélectionnés inactifs'

	# Je mets en forme la première colonne du tableau.
	def n_comp_techn(self, _o) :
		return '{0} {1}'.format(_o.n_techn, _o.pren_techn)
	n_comp_techn.allow_tags = True
	n_comp_techn.short_description = 'Nom complet'

	# J'initialise les paramètres.
	actions = [set_en_act_techn_on, set_en_act_techn_off, admin.actions.delete_selected]
	list_display = ('n_comp_techn', 'en_act_techn')
	list_filter = (
		('en_act_techn', admin.BooleanFieldListFilter),
	)

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('n_techn'),
				('pren_techn'),
				('en_act_techn')
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
				('ordre_av')
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
	def set_en_act_progr_on(_madm, _r, _qs) :
		_qs.update(en_act_progr = True)
	set_en_act_progr_on.short_description = 'Rendre les T_PROGRAMME sélectionnés actifs'

	def set_en_act_progr_off(_madm, _r, _qs) :
		_qs.update(en_act_progr = False)
	set_en_act_progr_off.short_description = 'Rendre les T_PROGRAMME sélectionnés inactifs'

	# J'initialise les paramètres.
	actions = [set_en_act_progr_on, set_en_act_progr_off, admin.actions.delete_selected]
	list_display = ['int_progr', 'id_type_progr', 'en_act_progr']
	list_filter = (
		'id_type_progr',
		('en_act_progr', admin.BooleanFieldListFilter),
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
				('en_act_progr')
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

	# Je mets en forme la première colonne du tableau.
	def axe(self, _o) :
		return '{0} - {1}'.format(_o.num_axe, _o.int_axe)
	axe.allow_tags = True
	axe.short_description = 'Axe'

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ('axe', 'id_progr')
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
	def ss_axe(self, _o) :
		return '{0}.{1} - {2}'.format(_o.id_axe.num_axe, _o.num_ss_axe, _o.int_ss_axe)
	ss_axe.allow_tags = True
	ss_axe.short_description = 'Sous-axe'

	def int_progr(self, _o) :
		return _o.id_axe.id_progr.int_progr
	int_progr.allow_tags = True
	int_progr.short_description = 'Programme'

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ('ss_axe', 'int_progr')
	list_filter = ['id_axe__id_progr']

	# Je déclare les champs en lecture seule lors d'une mise à jour.
	def get_readonly_fields(self, _r, _o = None) :
		if _o :
			return self.readonly_fields + ('num_ss_axe',)
		return self.readonly_fields

	form = MSousAxe

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('zl_axe'),
				('num_ss_axe'),
				('int_ss_axe')
			)
		}),
		('Autres', {
			'fields' : (
				('mont_ht_ss_axe'),
				('mont_ttc_ss_axe'),
				('ech_ss_axe')
			)
		})
	)

# Je peux désormais gérer les sous-axes.
admin.site.register(TSousAxe, ASousAxe)

class AAction(admin.ModelAdmin) :

	# Je mets en forme les colonnes du tableau.
	def act(self, _o) :
		return '{0}.{1}.{2} - {3}'.format(_o.id_ss_axe.id_axe.num_axe, _o.id_ss_axe.num_ss_axe, _o.num_act, _o.int_act)
	act.allow_tags = True
	act.short_description = 'Action'

	def int_progr(self, _o) :
		return _o.id_ss_axe.id_axe.id_progr.int_progr
	int_progr.allow_tags = True
	int_progr.short_description = 'Programme'

	# J'initialise les paramètres.
	actions = [admin.actions.delete_selected]
	list_display = ('act', 'int_progr')
	list_filter = ['id_ss_axe__id_axe__id_progr']

	# Je déclare les champs en lecture seule lors d'une mise à jour.
	def get_readonly_fields(self, _r, _o = None) :
		if _o :
			return self.readonly_fields + ('num_act',)
		return self.readonly_fields

	form = MAction

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('zl_ss_axe'),
				('num_act'),
				('int_act')
			)
		}),
		('Autres', {
			'fields' : (
				('mont_ht_act'),
				('mont_ttc_act'),
				('ech_act')
			)
		})
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
	def set_en_act_org_moa_on(_madm, _r, _qs) :
		_qs.update(en_act_org_moa = True)
	set_en_act_org_moa_on.short_description = 'Rendre les T_MOA sélectionnés actifs'

	def set_en_act_org_moa_off(_madm, _r, _qs) :
		_qs.update(en_act_org_moa = False)
	set_en_act_org_moa_off.short_description = 'Rendre les T_MOA sélectionnés inactifs'

	# J'initialise les paramètres.
	actions = [set_en_act_org_moa_on, set_en_act_org_moa_off, admin.actions.delete_selected]
	inlines = [AMoaInline]
	list_display = ['n_org', 'en_act_org_moa']
	list_filter = (
		('en_act_org_moa', admin.BooleanFieldListFilter),
	)

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
		('Options', {
			'fields' : (
				('dim_org_moa'),
				('en_act_org_moa')
			)
		}),
		('Autres', {
			'fields' : (
				('comm_org'),
				('logo_org_moa')
			)
		})
	)

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
				('zl_org'),
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
				('is_superuser')
			)
		}),
	)

	add_fieldsets = (
		('Informations générales', {
			'fields' : (
				('last_name'),
				('first_name'),
				('email'),
				('zl_org')
			)
		}),
		('Identifiants', {
			'fields' : (
				('username'),
				('zs_pwd1'),
				('zs_pwd2')
			)
		})
	)

# Je peux désormais gérer les utilisateurs.
admin.site.register(TUtilisateur, AUtilisateur)

# Je retire les fonctionnalités de base.
admin.site.unregister(User)
admin.site.unregister(Group)

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
	list_display = ['n_org']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('n_org'),
				('siret_org_prest'),
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
				('num_dep'),
				('comm_org'),
			)
		})
	)

# Je peux désormais gérer les prestataires.
admin.site.register(TPrestataire, APrestataire)

class AFinanceur(admin.ModelAdmin) :

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