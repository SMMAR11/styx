#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.constants import *
from app.functions import init_mess_err
from django import forms

class RechercherDossiers(forms.Form) :

	# Imports
	from app.validators import val_mont_pos

	# Je définis les champs du formulaire.
	cbsm_org_moa = forms.MultipleChoiceField(
		label = 'Maître(s) d\'ouvrage(s)|Nom|__zcc__', required = False, widget = forms.SelectMultiple()
	)
	zl_progr = forms.ChoiceField(
		choices = [DEFAULT_OPTION], label = 'Programme', required = False, widget = forms.Select()
	)
	zl_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_ss_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Sous-axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_act = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Action',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_nat_doss = forms.ChoiceField(
		choices = [DEFAULT_OPTION], label = 'Nature du dossier', required = False, widget = forms.Select()
	)
	zd_dt_deb_delib_moa_doss = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'Du' })
	)
	zd_dt_fin_delib_moa_doss = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'au' })
	)
	zl_av_cp = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Avis du comité de programmation',
		required = False,
		widget = forms.Select()
	)
	zs_mont_doss_min = forms.FloatField(
		label = '',
		required = False,
		validators = [val_mont_pos],
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : '0 par défaut' })
	)
	zs_mont_doss_max = forms.FloatField(
		label = '',
		required = False,
		validators = [val_mont_pos],
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : 'infini par défaut' })
	)
	cb_doss_dep_nn_sold = forms.BooleanField(
		label = 'Dossiers dont les dépenses sont non-soldées', required = False, widget = forms.CheckboxInput()
	)
	cb_doss_ddv_nn_sold = forms.BooleanField(
		label = 'Dossiers dont les demandes de versements sont non-soldées',
		required = False,
		widget = forms.CheckboxInput()
	)
	zl_org_fin = forms.ChoiceField(
		choices = [DEFAULT_OPTION], label = 'Organisme financier', required = False, widget = forms.Select()
	)
	zl_org_prest = forms.ChoiceField(
		choices = [DEFAULT_OPTION], label = 'Prestataire', required = False, widget = forms.Select()
	)
	cb_integr_doss_ass = forms.BooleanField(
		label = 'Intégration des dossiers associés dans le résultat',
		required = False,
		widget = forms.CheckboxInput()
	)
	cb_ajout_select_exist = forms.BooleanField(
		label = 'Ajouter à la sélection existante', required = False, widget = forms.CheckboxInput()
	)

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TAction
		from app.models import TAvisCp
		from app.models import TAxe
		from app.models import TFinanceur
		from app.models import TMoa
		from app.models import TNatureDossier
		from app.models import TPrestataire
		from app.models import TProgramme
		from app.models import TSousAxe

		# Je déclare le tableau des arguments.
		k_progr = kwargs.pop('k_progr', None)
		k_axe = kwargs.pop('k_axe', None)
		k_ss_axe = kwargs.pop('k_ss_axe', None)
		
		super(RechercherDossiers, self).__init__(*args, **kwargs)
		init_mess_err(self, False)

		# J'alimente les listes déroulantes personalisées.
		self.fields['cbsm_org_moa'].choices = [[m.pk, '|'.join([str(m), '__zcc__'])] for m in TMoa.objects.filter(
			peu_doss = True, en_act_doss = True
		)]
		self.fields['zl_progr'].choices += [(p.pk, p) for p in TProgramme.objects.all()]
		if k_progr :
			self.fields['zl_axe'].choices = [(a.pk, a) for a in TAxe.objects.filter(id_progr = k_progr)]
			if k_axe :
				self.fields['zl_ss_axe'].choices = [(sa.pk, sa) for sa in TSousAxe.objects.filter(id_axe = k_axe)]
				if k_ss_axe :
					self.fields['zl_act'].choices = [(a.pk, a) for a in TAction.objects.filter(id_ss_axe = k_ss_axe)]
		self.fields['zl_nat_doss'].choices += [(nd.pk, nd) for nd in TNatureDossier.objects.filter(peu_doss = True)]
		self.fields['zl_av_cp'].choices += [(a.pk, a) for a in TAvisCp.objects.all()]
		self.fields['zl_org_fin'].choices += [(f.pk, f) for f in TFinanceur.objects.all()]
		self.fields['zl_org_prest'].choices += [(p.pk, p) for p in TPrestataire.objects.all()]

	def clean(self) :

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(RechercherDossiers, self).clean()
		v_dt_deb_delib_moa_doss = cleaned_data.get('zd_dt_deb_delib_moa_doss')
		v_dt_fin_delib_moa_doss = cleaned_data.get('zd_dt_fin_delib_moa_doss')

		# Je gère le renseignement de la période de délibération au maître d'ouvrage d'un dossier.
		if v_dt_deb_delib_moa_doss and not v_dt_fin_delib_moa_doss :
			self.add_error('zd_dt_fin_delib_moa_doss', ERROR_MESSAGES['required'])

		if v_dt_fin_delib_moa_doss and not v_dt_deb_delib_moa_doss :
			self.add_error('zd_dt_deb_delib_moa_doss', ERROR_MESSAGES['required'])

class RechercherPrestations(forms.Form) :

	# Imports
	from app.validators import val_mont_pos

	# Je définis les champs du formulaire.
	zl_org_prest = forms.ChoiceField(
		choices = [DEFAULT_OPTION], label = 'Prestataire', required = False, widget = forms.Select()
	)
	cbsm_org_moa = forms.MultipleChoiceField(
		label = 'Maître(s) d\'ouvrage(s)|Nom|__zcc__', required = False, widget = forms.SelectMultiple()
	)
	zl_progr = forms.ChoiceField(
		choices = [DEFAULT_OPTION], label = 'Programme', required = False, widget = forms.Select()
	)
	zl_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_ss_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Sous-axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_act = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Action',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zd_dt_deb_notif_prest = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'Du' })
	)
	zd_dt_fin_notif_prest = forms.DateField(
		label = '', 
		required = False, 
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'au' })
	)
	zl_nat_prest = forms.ChoiceField(
		choices = [DEFAULT_OPTION], label = 'Nature de la prestation', required = False, widget = forms.Select()
	)
	zs_mont_prest_min = forms.FloatField(
		label = '',
		required = False,
		validators = [val_mont_pos],
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : '0 par défaut' })
	)
	zs_mont_prest_max = forms.FloatField(
		label = '',
		required = False,
		validators = [val_mont_pos],
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : 'infini par défaut' })
	)
	zl_dep = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Département d\'origine du prestataire',
		required = False,
		widget = forms.Select()
	)
	cb_ajout_select_exist = forms.BooleanField(
		label = 'Ajouter à la sélection existante', required = False, widget = forms.CheckboxInput()
	)

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TAction
		from app.models import TAxe
		from app.models import TDepartement
		from app.models import TMoa
		from app.models import TNaturePrestation
		from app.models import TPrestataire
		from app.models import TProgramme
		from app.models import TSousAxe

		# Je déclare le tableau des arguments.
		k_progr = kwargs.pop('k_progr', None)
		k_axe = kwargs.pop('k_axe', None)
		k_ss_axe = kwargs.pop('k_ss_axe', None)
		
		super(RechercherPrestations, self).__init__(*args, **kwargs)
		init_mess_err(self, False)

		# J'alimente les listes déroulantes personalisées.
		self.fields['zl_org_prest'].choices += [(p.pk, p) for p in TPrestataire.objects.all()]
		self.fields['cbsm_org_moa'].choices = [[m.pk, '|'.join([str(m), '__zcc__'])] for m in TMoa.objects.filter(
			peu_doss = True, en_act_doss = True
		)]
		self.fields['zl_progr'].choices += [(p.pk, p) for p in TProgramme.objects.all()]
		if k_progr :
			self.fields['zl_axe'].choices = [(a.pk, a) for a in TAxe.objects.filter(id_progr = k_progr)]
			if k_axe :
				self.fields['zl_ss_axe'].choices = [(sa.pk, sa) for sa in TSousAxe.objects.filter(id_axe = k_axe)]
				if k_ss_axe :
					self.fields['zl_act'].choices = [(a.pk, a) for a in TAction.objects.filter(id_ss_axe = k_ss_axe)]
		self.fields['zl_nat_prest'].choices += [(np.pk, np) for np in TNaturePrestation.objects.all()]
		self.fields['zl_dep'].choices += [(d.pk, d) for d in TDepartement.objects.all()]

	def clean(self) :

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(RechercherPrestations, self).clean()
		v_dt_deb_notif_prest = cleaned_data.get('zd_dt_deb_notif_prest')
		v_dt_fin_notif_prest = cleaned_data.get('zd_dt_fin_notif_prest')

		# Je gère le renseignement de la période de notification d'une prestation.
		if v_dt_deb_notif_prest and not v_dt_fin_notif_prest :
			self.add_error('zd_dt_fin_notif_prest', ERROR_MESSAGES['required'])

		if v_dt_fin_notif_prest and not v_dt_deb_notif_prest :
			self.add_error('zd_dt_deb_notif_prest', ERROR_MESSAGES['required'])