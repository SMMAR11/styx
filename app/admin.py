#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.forms.admin import *
from app.functions import *
from app.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

# Je désactive l'option de base afin de pouvoir trier les options par ordre alphabétique.
admin.site.disable_action('delete_selected')

class ANatureDossier(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_nat_doss']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_nat_doss'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les natures de dossiers.
admin.site.register(TNatureDossier, ANatureDossier)

class ATechnicien(admin.ModelAdmin) :

	# J'initialise les actions supplémentaires.
	def en_act(modeladmin, request, queryset) :
		queryset.update(en_act = True)
	en_act.short_description = 'Rendre les Techniciens sélectionnés actifs'

	def en_inact(modeladmin, request, queryset) :
		queryset.update(en_act = False)
	en_inact.short_description = 'Rendre les Techniciens sélectionnés inactifs'

	# Je mets en forme la première colonne du tableau.
	def techn(self, p_obj) :
		return '{0} {1}'.format(p_obj.n_techn, p_obj.pren_techn)
	techn.allow_tags = True
	techn.short_description = 'Nom complet'

	# Je paramètre les différentes options.
	list_display = ('techn', 'en_act')
	actions = [en_act, en_inact, admin.actions.delete_selected]
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

# J'ajoute la possibilité de gérer les techniciens.
admin.site.register(TTechnicien, ATechnicien)

class AAvisCp(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_av_cp']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_av_cp'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les avis du comité de programmation.
admin.site.register(TAvisCp, AAvisCp)

class AAvancement(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_av']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_av'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les états d'avancements.
admin.site.register(TAvancement, AAvancement)

class ATypeProgramme(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_type_progr']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_progr'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les types de programmes.
admin.site.register(TTypeProgramme, ATypeProgramme)

class ATypeDossierInline(admin.TabularInline) :

	model = TTypeDossier.type_progr.through
	extra = 0
	verbose_name = ''

class ATypeDossier(admin.ModelAdmin) :

	# Je mets en forme la dernière colonne du tableau.
	def les_type_progr(self, p_obj) :
		tab = []
		for un_obj in p_obj.type_progr.all() :
			tab.append(un_obj.int_type_progr)
		return ', '.join(tab)
	les_type_progr.allow_tags = True
	les_type_progr.short_description = 'Type(s) de programme(s)'

	# Je paramètre les différentes options.
	list_display = ['int_type_doss', 'les_type_progr']
	actions = [admin.actions.delete_selected]
	inlines = [ATypeDossierInline]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_doss'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les types de dossiers.
admin.site.register(TTypeDossier, ATypeDossier)

class AProgramme(admin.ModelAdmin) :

	# Je mets en forme la dernière colonne du tableau.
	def int_type_progr(self, p_obj) :
		return p_obj.id_type_progr.int_type_progr
	int_type_progr.allow_tags = True
	int_type_progr.short_description = 'Type de programme'

	# Je paramètre les différentes options.
	list_display = ['int_progr', 'int_type_progr']
	actions = [admin.actions.delete_selected]
	list_filter = ['id_type_progr']

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_progr'),
				('id_type_progr')
			)
		}),
		('Options', {
			'fields' : (
				('dim_progr'),
				('seq_progr')
			)
		})
	)

	# J'initialise les champs en lecture seule lors d'une modification.
	def get_readonly_fields(self, request, obj = None) :
		if obj :
			return self.readonly_fields + ('dim_progr',)
		return self.readonly_fields

# J'ajoute la possibilité de gérer les programmes.
admin.site.register(TProgramme, AProgramme)

class AAxe(admin.ModelAdmin) :

	# Je mets en forme la première colonne du tableau.
	def axe(self, p_obj) :
		return '{0} - {1}'.format(p_obj.num_axe, p_obj.int_axe)
	axe.allow_tags = True
	axe.short_description = 'Axe'

	# Je paramètre les différentes options.
	list_display = ('axe', 'id_progr')
	actions = [admin.actions.delete_selected]
	list_filter = ['id_progr']

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

	# J'initialise les champs en lecture seule lors d'une modification.
	def get_readonly_fields(self, request, obj = None) :
		if obj :
			return self.readonly_fields + ('num_axe', 'id_progr')
		return self.readonly_fields

# J'ajoute la possibilité de gérer les axes.
admin.site.register(TAxe, AAxe)

class ASousAxe(admin.ModelAdmin) :

	# Je mets en forme les colonnes du tableau.
	def ss_axe(self, p_obj) :
		return '{0}.{1} - {2}'.format(p_obj.id_axe.num_axe, p_obj.num_ss_axe, p_obj.int_ss_axe)
	ss_axe.allow_tags = True
	ss_axe.short_description = 'Sous-axe'

	def int_progr(self, p_obj) :
		return p_obj.id_axe.id_progr.int_progr
	int_progr.allow_tags = True
	int_progr.short_description = 'Programme'

	# Je paramètre les différentes options.
	list_display = ('ss_axe', 'int_progr')
	actions = [admin.actions.delete_selected]
	list_filter = ['id_axe__id_progr']

	form = MSousAxe

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('les_axes'),
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

	# J'initialise les champs en lecture seule lors d'une modification.
	def get_readonly_fields(self, request, obj = None) :
		if obj :
			return self.readonly_fields + ('num_ss_axe',)
		return self.readonly_fields

# J'ajoute la possibilité de gérer les sous-axes.
admin.site.register(TSousAxe, ASousAxe)

class AAction(admin.ModelAdmin) :

	# Je mets en forme les colonnes du tableau.
	def act(self, p_obj) :
		return '{0}.{1}.{2} - {3}'.format(
			p_obj.id_ss_axe.id_axe.num_axe, p_obj.id_ss_axe.num_ss_axe, index_alpha(p_obj.num_act), p_obj.int_act
		)
	act.allow_tags = True
	act.short_description = 'Action'

	def int_progr(self, p_obj) :
		return p_obj.id_ss_axe.id_axe.id_progr.int_progr
	int_progr.allow_tags = True
	int_progr.short_description = 'Programme'

	# Je paramètre les différentes options.
	list_display = ('act', 'int_progr')
	actions = [admin.actions.delete_selected]
	list_filter = ['id_ss_axe__id_axe__id_progr']

	form = MAction

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('les_ss_axes'),
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

	# J'initialise les champs en lecture seule lors d'une modification.
	def get_readonly_fields(self, request, obj = None) :
		if obj :
			return self.readonly_fields + ('num_act',)
		return self.readonly_fields

# J'ajoute la possibilité de gérer les actions.
admin.site.register(TAction, AAction)

class AUtilisateur(UserAdmin) :

	# Je paramètre les différentes options.
	list_display = ['username', 'last_name', 'first_name', 'email', 'is_staff', 'last_login']
	actions = [admin.actions.delete_selected]
	search_fields = ('username',)
	list_filter = (
		('is_staff', admin.BooleanFieldListFilter),
		('is_superuser', admin.BooleanFieldListFilter),
		('is_active', admin.BooleanFieldListFilter)
	)

	# Je détermine le formulaire utilisé pour l'ajout ou la mise à jour d'un objet TUtilisateur.
	form = MUtilisateurUpdate
	add_form = MUtilisateurCreate

	# Je mets en forme le formulaire de modification.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('last_name'),
				('first_name'),
				('email'),
				('les_org'),
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

	# Je mets en forme le formulaire d'ajout.
	add_fieldsets = (
		('Informations générales', {
			'fields' : (
				('last_name'),
				('first_name'),
				('email'),
				('les_org')
			)
		}),
		('Identifiants', {
			'fields' : (
				('username'),
				('password1'),
				('password2')
			)
		})
	)

# J'ajoute la possibilité de gérer les utilisateurs.
admin.site.register(TUtilisateur, AUtilisateur)

# Je retire les fonctionnalités du mode d'administration de base.
admin.site.unregister(User)
admin.site.unregister(Group)

class AMoaInline(admin.TabularInline) :

	model = TMoa.moa.through
	fk_name = 'id_org_moa_fil'
	extra = 0
	verbose_name = ''

class AMoa(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['n_org']
	actions = [admin.actions.delete_selected]
	inlines = [AMoaInline]

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
				('id_comm'),
				('cedex_org'),
				('bp_org')
			)
		}),
		('Options', {
			'fields' : (
				('dim_org_moa'),
				('en_act')
			)
		}),
		('Autres', {
			'fields' : (
				('comm_org'),
			)
		})
	)

# J'ajoute la possibilité de gérer les maîtres d'ouvrages.
admin.site.register(TMoa, AMoa)

class ARiviere(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['n_riv']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('n_riv'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les rivières.
admin.site.register(TRiviere, ARiviere)

class AUnite(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_unit']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_unit'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les unités de mesures.
admin.site.register(TUnite, AUnite)

class APortee(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_port']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_port'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les portées de dossiers.
admin.site.register(TPortee, APortee)

class APeriodePriseVuePhoto(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_ppv_ph']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_ppv_ph'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les périodes de prise de vue d'une photo.
admin.site.register(TPeriodePriseVuePhoto, APeriodePriseVuePhoto)

class ATypeDeclaration(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_type_decl']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_decl'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les types de déclarations.
admin.site.register(TTypeDeclaration, ATypeDeclaration)

class ATypeAvancementArrete(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_type_av_arr']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_av_arr'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les types d'avancements d'un arrêté.
admin.site.register(TTypeAvancementArrete, ATypeAvancementArrete)

class APrestataire(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['n_org', 'siret_org_prest']
	ordering = ['n_org']
	actions = [admin.actions.delete_selected]

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
				('id_comm'),
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

# J'ajoute la possibilité de gérer les prestataires.
admin.site.register(TPrestataire, APrestataire)

class AFinanceur(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['n_org']
	ordering = ['n_org']
	actions = [admin.actions.delete_selected]

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
				('id_comm'),
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

# J'ajoute la possibilité de gérer les financeurs.
admin.site.register(TFinanceur, AFinanceur)

class ANaturePrestation(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_nat_prest']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_nat_prest'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les natures de prestations.
admin.site.register(TNaturePrestation, ANaturePrestation)

class APaiementPremierAcompte(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_paiem_prem_ac']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_paiem_prem_ac'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les types de paiements du premier acompte.
admin.site.register(TPaiementPremierAcompte, APaiementPremierAcompte)

class ATypeVersement(admin.ModelAdmin) :

	# Je paramètre les différentes options.
	list_display = ['int_type_vers']
	actions = [admin.actions.delete_selected]

	# Je mets en forme le formulaire.
	fieldsets = (
		('Informations générales', {
			'fields' : (
				('int_type_vers'),
			)
		}),
	)

# J'ajoute la possibilité de gérer les types de paiements du premier acompte.
admin.site.register(TTypeVersement, ATypeVersement)