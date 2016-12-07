#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.constants import *
from django import forms

class SelectionnerDossiers(forms.Form) :

	''' Imports '''
	from app.validators import valid_mont

	# Je définis les champs du formulaire.
	cbsm_org_moa = forms.MultipleChoiceField(
		label = 'Maître d\'ouvrage',
		required = False,
		widget = forms.CheckboxSelectMultiple()
	)

	zld_progr = forms.ChoiceField(
		label = 'Programme',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zld_axe = forms.ChoiceField(
		choices = list(OPTION_INITIALE),
		label = 'Axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_ss_axe = forms.ChoiceField(
		choices = list(OPTION_INITIALE),
		label = 'Sous-axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_act = forms.ChoiceField(
		choices = list(OPTION_INITIALE),
		label = 'Action',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zl_nat_doss = forms.ChoiceField(
		label = 'Nature du dossier',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zd_dt_deb_delib_moa_doss = forms.CharField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'date form-control', 'placeholder' : 'Du' })
	)

	zd_dt_fin_delib_moa_doss = forms.CharField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'date form-control', 'placeholder' : 'au' })
	)

	zl_av_cp = forms.ChoiceField(
		label = 'Avis du comité de programmation',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zs_mont_ht_doss_min = forms.CharField(
		label = '',
		required = False,
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'placeholder' : '0 par défaut' })
	)

	zs_mont_ht_doss_max = forms.CharField(
		label = '',
		required = False,
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'placeholder' : 'infini par défaut' })
	)

	cb_doss_dep_nn_sold = forms.BooleanField(
		label = 'Dossiers dont les dépenses sont non-soldées',
		required = False,
		widget = forms.CheckboxInput()
	)

	cb_doss_ddv_nn_sold = forms.BooleanField(
		label = 'Dossiers dont les demandes de versements sont non-soldées',
		required = False,
		widget = forms.CheckboxInput()
	)

	zl_org_fin = forms.ChoiceField(
		label = 'Organisme financier',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zl_org_prest = forms.ChoiceField(
		label = 'Prestataire',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	cb_int_doss_ass = forms.BooleanField(
		label = 'Intégration des dossiers associés dans le résultat',
		required = False,
		widget = forms.CheckboxInput()
	)

	cb_ajout_select_exist = forms.BooleanField(
		label = 'Ajouter à la sélection existante',
		required = False,
		widget = forms.CheckboxInput()
	)

	def __init__(self, *args, **kwargs) :

		''' Imports '''
		from app.models import TAvisCp, TFinanceur, TMoa, TNatureDossier, TPrestataire, TProgramme
		
		super(SelectionnerDossiers, self).__init__(*args, **kwargs)

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		les_org_moa = list([(i.id_org_moa.id_org, i.id_org_moa.n_org) for i in TMoa.objects.filter(en_act = 1)])
		les_org_moa.extend([('T', 'Tous')]);
		self.fields['cbsm_org_moa'].choices = les_org_moa
		
		# J'alimente la liste déroulante des programmes.
		les_progr = list(OPTION_INITIALE)
		les_progr.extend([(i.id_progr, i.int_progr) for i in TProgramme.objects.all()])
		self.fields['zld_progr'].choices = les_progr

		# J'alimente la liste déroulante des natures de dossiers.
		les_nat_doss = list(OPTION_INITIALE)
		les_nat_doss.extend([(i.id_nat_doss, i.int_nat_doss) for i in TNatureDossier.objects.all()])
		self.fields['zl_nat_doss'].choices = les_nat_doss

		# J'alimente la liste déroulante des avis du comité de programmation.
		les_av_cp = list(OPTION_INITIALE)
		les_av_cp.extend([(i.id_av_cp, i.int_av_cp) for i in TAvisCp.objects.all()])
		self.fields['zl_av_cp'].choices = les_av_cp

		# J'alimente la liste déroulante des financeurs.
		les_org_fin = list(OPTION_INITIALE)
		les_org_fin.extend([(i.id_org_fin, i.id_org_fin.n_org) for i in TFinanceur.objects.all()])
		self.fields['zl_org_fin'].choices = les_org_fin

		# J'alimente la liste déroulante des prestataires.
		les_org_prest = list(OPTION_INITIALE)
		les_org_prest.extend([(i.id_org_prest, i.id_org_prest.n_org) for i in TPrestataire.objects.all()])
		self.fields['zl_org_prest'].choices = les_org_prest

	def clean(self) :

		''' Imports '''
		from app.functions import nett_val
		from datetime import datetime

		# Je récupère les données utiles du formulaire pré-valide.
		cleaned_data = super(SelectionnerDossiers, self).clean()
		v_dt_deb_delib_moa_doss = nett_val(cleaned_data.get('zd_dt_deb_delib_moa_doss'))
		v_dt_fin_delib_moa_doss = nett_val(cleaned_data.get('zd_dt_fin_delib_moa_doss'))
		v_mont_ht_doss_min = nett_val(cleaned_data.get('zs_mont_ht_doss_min'))
		v_mont_ht_doss_max = nett_val(cleaned_data.get('zs_mont_ht_doss_max'))

		# Je gère le renseignement de la période de délibération au maître d'ouvrage d'un dossier.
		if v_dt_deb_delib_moa_doss is not None :
			if v_dt_fin_delib_moa_doss is None :
				self.add_error('zd_dt_fin_delib_moa_doss', MESSAGES['required'])

		if v_dt_fin_delib_moa_doss is not None :
			if v_dt_deb_delib_moa_doss is None :
				self.add_error('zd_dt_deb_delib_moa_doss', MESSAGES['required'])

		if v_dt_deb_delib_moa_doss is not None and v_dt_fin_delib_moa_doss is not None :

			# Je récupère les différentes parties des dates concernées.
			deb = v_dt_deb_delib_moa_doss.split('/')
			fin = v_dt_fin_delib_moa_doss.split('/')

			# J'instancie deux objets "datetime".
			datetime_deb = datetime(int(deb[2]), int(deb[1]), int(deb[0]))
			datetime_fin = datetime(int(fin[2]), int(fin[1]), int(fin[0]))

			if datetime_deb > datetime_fin :
				self.add_error(
					'zd_dt_deb_delib_moa_doss', 'La date de début saisie est postérieure à la date de fin saisie.'
				)
				self.add_error(
					'zd_dt_fin_delib_moa_doss', 'La date de fin saisie est antérieure à la date de début saisie.'
				)

		# Je gère le renseignement des montants HT d'un dossier.
		if v_mont_ht_doss_min is not None and v_mont_ht_doss_max is not None :
			if int(v_mont_ht_doss_min) > int(v_mont_ht_doss_max) :
				self.add_error(
					'zs_mont_ht_doss_min', 'Le montant minimum saisi est supérieur au montant maximum saisi.'
				)
				self.add_error(
					'zs_mont_ht_doss_max', 'Le montant maximum saisi est inférieur au montant minimum saisi.'
				)