from app.constants import *
from app.functions import *
from app.models import *
from app.validators import *
from datetime import datetime
from django import forms

class SelectionnerDossiers(forms.Form) :

	# Je définis les champs du formulaire.
	cbsm_moa = forms.MultipleChoiceField(
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
		error_messages = MESSAGES,
		label = 'Axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_ss_axe = forms.ChoiceField(
		choices = list(OPTION_INITIALE),
		error_messages = MESSAGES,
		label = 'Sous-axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_act = forms.ChoiceField(
		choices = list(OPTION_INITIALE),
		error_messages = MESSAGES,
		label = 'Action',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zl_nat_doss = forms.ChoiceField(
		label = 'Nature du dossier',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zd_dt_delib_moa_doss_tr_deb = forms.CharField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'date form-control', 'placeholder' : 'Du' })
	)

	zd_dt_delib_moa_doss_tr_fin = forms.CharField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'date form-control', 'placeholder' : 'au' })
	)

	zl_av_cp = forms.ChoiceField(
		label = 'Avis du comité de programmation',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zl_org_fin = forms.ChoiceField(
		label = 'Organisme financier',
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

	cb_doss_dep_non_sold = forms.BooleanField(
		label = 'Dossiers dont les dépenses sont non-soldées',
		required = False,
		widget = forms.CheckboxInput()
	)

	cb_doss_ddv_non_sold = forms.BooleanField(
		label = 'Dossiers dont les demandes de versements sont non-soldées',
		required = False,
		widget = forms.CheckboxInput()
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
		
		super(SelectionnerDossiers, self).__init__(*args, **kwargs)

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		les_moa = list([(i.id_org_moa.id_org, i.id_org_moa.n_org) 
			for i in TMoa.objects.filter(en_act = 1).order_by('id_org_moa__n_org')]
		)
		les_moa.extend([('T', 'Tous')]);
		self.fields['cbsm_moa'].choices = les_moa
		
		# J'alimente la liste déroulante des programmes.
		les_programmes = list(OPTION_INITIALE)
		les_programmes.extend([(i.id_progr, i.int_progr) 
			for i in TProgramme.objects.order_by('int_progr')]
		)
		self.fields['zld_progr'].choices = les_programmes

		# J'alimente la liste déroulante des natures de dossier.
		les_natures_dossier = list(OPTION_INITIALE)
		les_natures_dossier.extend([(i.id_nat_doss, i.int_nat_doss) 
			for i in TNatureDossier.objects.order_by('int_nat_doss')]
		)
		self.fields['zl_nat_doss'].choices = les_natures_dossier

		# J'alimente la liste déroulante des avis du comité de programmation.
		les_avis_cp = list(OPTION_INITIALE)
		les_avis_cp.extend([(i.id_av_cp, i.int_av_cp)
			for i in TAvisCp.objects.order_by('int_av_cp')]
		)
		self.fields['zl_av_cp'].choices = les_avis_cp

		# J'alimente la liste déroulante des financeurs.
		les_financeurs = list(OPTION_INITIALE)
		les_financeurs.extend([(i.id_org_fin, i.id_org_fin.n_org)
			for i in TFinanceur.objects.order_by('id_org_fin__n_org')]
		)
		self.fields['zl_org_fin'].choices = les_financeurs

		# J'alimente la liste déroulante des prestataires.
		les_prestataires = list(OPTION_INITIALE)
		les_prestataires.extend([(i.id_org_prest, i.id_org_prest.n_org)
			for i in TPrestataire.objects.order_by('id_org_prest__n_org')]
		)
		self.fields['zl_org_prest'].choices = les_prestataires

	def clean(self) :

		# Je récupère les données utiles du formulaire pré-valide.
		tab_donnees = super(SelectionnerDossiers, self).clean()
		v_date_debut_deliberation_moa_dossier = nett_val(tab_donnees.get('zd_dt_delib_moa_doss_tr_deb'))
		v_date_fin_deliberation_moa_dossier = nett_val(tab_donnees.get('zd_dt_delib_moa_doss_tr_fin'))
		v_montant_ht_dossier_min = nett_val(tab_donnees.get('zs_mont_ht_doss_min'))
		v_montant_ht_dossier_max = nett_val(tab_donnees.get('zs_mont_ht_doss_max'))

		# Je gère le renseignement de la période de délibération au maître d'ouvrage d'un dossier.
		if v_date_debut_deliberation_moa_dossier is not None :
			if v_date_fin_deliberation_moa_dossier is None :
				self.add_error('zd_dt_delib_moa_doss_tr_fin', MESSAGES['required'])

		if v_date_fin_deliberation_moa_dossier is not None :
			if v_date_debut_deliberation_moa_dossier is None :
				self.add_error('zd_dt_delib_moa_doss_tr_deb', MESSAGES['required'])

		if v_date_debut_deliberation_moa_dossier is not None and v_date_fin_deliberation_moa_dossier is not None :
			deb = v_date_debut_deliberation_moa_dossier.split('/')
			fin = v_date_fin_deliberation_moa_dossier.split('/')
			if datetime(int(deb[2]), int(deb[1]), int(deb[0])) > datetime(int(fin[2]), int(fin[1]), int(fin[0])) :
				self.add_error(
					'zd_dt_delib_moa_doss_tr_deb', 'La date de début saisie est postérieure à la date de fin saisie.'
				)
				self.add_error(
					'zd_dt_delib_moa_doss_tr_fin', 'La date de fin saisie est antérieure à la date de début saisie.'
				)

		# Je gère le renseignement des montants d'un dossier.
		if v_montant_ht_dossier_min is not None and v_montant_ht_dossier_max is not None :
			if int(v_montant_ht_dossier_min) > int(v_montant_ht_dossier_max) :
				self.add_error('zs_mont_ht_doss_min', 'Le montant minimum saisi est supérieur au montant maximum saisi.')
				self.add_error('zs_mont_ht_doss_max', 'Le montant maximum saisi est inférieur au montant minimum saisi.')