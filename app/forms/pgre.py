#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.constants import *
from app.functions import init_mess_err
from django import forms


class GererActionPgre(forms.ModelForm) :

	# Imports
	from app.classes.FFEuroField import Class as FFEuroField
	from app.models import TDossierSsAction

	cbsm_atel_pgre = forms.MultipleChoiceField(
		label = 'Atelier(s) concerné(s)|Nom|__zcc__', widget = forms.SelectMultiple()
	)
	rb_doss_corr = forms.ChoiceField(
		choices = [(True, 'Oui'), (False, 'Non')],
		initial = False,
		label = 'Cette action PGRE correspond-t-elle à un dossier ?',
		required = False,
		widget = forms.RadioSelect()
	)
	za_doss_corr = forms.CharField(
		label = 'Dossier de correspondance', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	cbsm_org_moa = forms.MultipleChoiceField(
		label = 'Maître(s) d\'ouvrage(s)|Nom|__zcc__', widget = forms.SelectMultiple()
	)
	zl_nat_doss = forms.ChoiceField(label = 'Nature de l\'action PGRE', widget = forms.Select())

	mont_doss_pgre = FFEuroField(
		label = 'Montant de l\'action PGRE',
		required = True
	)

	obj_econ_ress_doss_pgre = forms.FloatField(
		label= "Objectifs d'économie de la ressource en eau (en m<sup>3</sup>)",
		required = True
	)

	ss_action_pgre = forms.ModelMultipleChoiceField(
		TDossierSsAction.objects.all(), required=False,
		label="Sous Actions PGRE")


	class Meta :

		# Imports
		from app.models import TDossierPgre

		exclude = ['atel_pgre', 'id_doss', 'id_nat_doss', 'moa']
		fields = '__all__'
		model = TDossierPgre
		widgets = {
			'dt_deb_doss_pgre' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_fin_doss_pgre' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }),
		}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr
		from app.models import TAteliersPgreDossierPgre
		from app.models import TInstancesConcertationPgreAtelierPgre
		from app.models import TMoa
		from app.models import TMoaDossierPgre
		from app.models import TNatureDossier

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		self.k_util = kwargs.pop('k_util', None)
		k_ic_pgre = kwargs.pop('k_ic_pgre', None)

		# Mise en forme de certaines données
		if instance :

			kwargs.update(initial = {
				'dt_deb_doss_pgre' : dt_fr(instance.dt_deb_doss_pgre) if instance.dt_deb_doss_pgre else '',
				'dt_fin_doss_pgre' : dt_fr(instance.dt_fin_doss_pgre) if instance.dt_fin_doss_pgre else '',
				'mont_doss_pgre' : instance.mont_doss_pgre_ppt,
				'obj_econ_ress_doss_pgre' : instance.obj_econ_ress_doss_pgre_ppt,
			})

		super(GererActionPgre, self).__init__(*args, **kwargs)
		init_mess_err(self)

		# J'alimente la liste déroulante des ateliers concernés par une instance de concertation.
		if k_ic_pgre :
			try :
				t_atel_pgre = [[
					a.id_atel_pgre.pk,
					'|'.join([str(a.id_atel_pgre), '__zcc__'])
				] for a in TInstancesConcertationPgreAtelierPgre.objects.filter(id_ic_pgre = k_ic_pgre).order_by(
					'id_atel_pgre'
				)]
			except :
				t_atel_pgre = []
			self.fields['cbsm_atel_pgre'].choices = t_atel_pgre

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		t_org_moa = [[
			m.pk,
			'|'.join([str(m), '__zcc__'])
		] for m in TMoa.objects.filter(peu_doss_pgre = True, en_act_doss_pgre = True)]
		self.fields['cbsm_org_moa'].choices = t_org_moa

		# J'alimente la liste déroulante des natures d'actions PGRE.
		t_nat_doss = [(nd.pk, nd) for nd in TNatureDossier.objects.filter(peu_doss_pgre = True)]
		t_nat_doss.insert(0, DEFAULT_OPTION)
		self.fields['zl_nat_doss'].choices = t_nat_doss

		i = self.instance

		# J'affiche la valeur initiale de chaque champ personnalisé.
		if i.pk :
			self.fields['cbsm_atel_pgre'].initial = [a.id_atel_pgre.pk
				for a in TAteliersPgreDossierPgre.objects.filter(id_doss_pgre = i)
			]
			self.fields['za_doss_corr'].initial = i.id_doss
			self.fields['cbsm_org_moa'].initial = [m.id_org_moa.pk for m in TMoaDossierPgre.objects.filter(
				id_doss_pgre = i
			)]
			self.fields['zl_nat_doss'].initial = i.id_nat_doss.pk
			if i.ss_action_pgre.exists():
				self.fields['mont_doss_pgre'].disabled = True
				self.fields['obj_econ_ress_doss_pgre'].disabled = True


	def clean(self) :

		# Imports
		from app.functions import ger_droits
		from app.models import TDossier
		from app.models import TMoa
		from styx.settings import T_DONN_BDD_INT

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererActionPgre, self).clean()
		v_doss_corr = cleaned_data.get('za_doss_corr')
		v_org_moa = cleaned_data.get('cbsm_org_moa')
		v_dt_deb_doss_pgre = cleaned_data.get('dt_deb_doss_pgre')
		v_dt_fin_doss_pgre = cleaned_data.get('dt_fin_doss_pgre')

		i = self.instance

		# Je renvoie une erreur si l'utilisateur n'a pas les droits pour créer une action PGRE spécifique.
		if not i.pk and v_org_moa :
			for m in v_org_moa :
				o_org_moa = TMoa.objects.get(pk = m)
				if ger_droits(self.k_util, [(o_org_moa.pk, T_DONN_BDD_INT['PGRE_PK'])], False, False) == False :
					self.add_error(
						'cbsm_org_moa',
						'''
						Vous n\'avez pas les permissions requises pour créer une action PGRE pour le maître d\'ouvrage
						« {0} ».
						'''.format(o_org_moa)
					)

		# Je renvoie une erreur s'il y a une incohérence entre les dates de début et de fin de l'action PGRE.
		if v_dt_deb_doss_pgre and v_dt_fin_doss_pgre and v_dt_deb_doss_pgre > v_dt_fin_doss_pgre :
			self.add_error(
				'dt_deb_doss_pgre', 'Veuillez saisir une date de début postérieure ou égale à la date de fin.'
			)
			self.add_error(
				'dt_fin_doss_pgre', 'Veuillez saisir une date de fin antérieure ou égale à la date de début.'
			)

		# Je renvoie une erreur si le numéro du dossier de correspondance n'existe pas.
		if v_doss_corr :
			try :
				TDossier.objects.get(num_doss = v_doss_corr)
			except :
				self.add_error('za_doss_corr', 'Le dossier {0} n\'existe pas.'.format(v_doss_corr))

	def save(self, commit = True) :

		# Imports
		from app.models import TAtelierPgre
		from app.models import TAteliersPgreDossierPgre
		from app.models import TDossier
		from app.models import TMoa
		from app.models import TMoaDossierPgre
		from app.models import TNatureDossier

		o = super(GererActionPgre, self).save(commit = False)

		# Je vérifie l'existence d'un objet TDossier.
		try :
			o_doss = TDossier.objects.get(num_doss = self.cleaned_data.get('za_doss_corr'))
		except :
			o_doss = None

		o.id_doss = o_doss
		o.id_nat_doss = TNatureDossier.objects.get(pk = self.cleaned_data.get('zl_nat_doss'))
		o.save()

		# Je fais le lien avec la table TAteliersPgreDossierPgre.
		TAteliersPgreDossierPgre.objects.filter(id_doss_pgre = o).delete()
		for a in self.cleaned_data.get('cbsm_atel_pgre') :
			TAteliersPgreDossierPgre.objects.create(id_atel_pgre = TAtelierPgre.objects.get(pk = a), id_doss_pgre = o)

		# Je fais le lien avec la table TMoaDossierPgre.
		TMoaDossierPgre.objects.filter(id_doss_pgre = o).delete()
		for m in self.cleaned_data.get('cbsm_org_moa') :
			TMoaDossierPgre.objects.create(id_doss_pgre = o, id_org_moa = TMoa.objects.get(pk = m))

		return o

class GererPhotoPgre(forms.ModelForm) :

	za_num_doss_pgre = forms.CharField(
		label = 'Numéro de l\'action PGRE', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)

	class Meta :

		# Imports
		from app.models import TPhotoPgre

		exclude = ['id_doss_pgre']
		fields = '__all__'
		model = TPhotoPgre
		widgets = { 'dt_pv_ph_pgre' : forms.DateInput(attrs = { 'input-group-addon' : 'date' }) }

	def __init__(self, *args, **kwargs) :

		# Je déclare le tableau des arguments.
		k_doss_pgre = kwargs.pop('k_doss_pgre', None)

		super(GererPhotoPgre, self).__init__(*args, **kwargs)
		init_mess_err(self)

		i = self.instance
		if not i.pk :
			self.fields['za_num_doss_pgre'].initial = k_doss_pgre
		else :
			self.fields['za_num_doss_pgre'].initial = i.id_doss_pgre

	def clean(self) :

		# Imports
		from app.models import TDossierPgre

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererPhotoPgre, self).clean()
		v_num_doss_pgre = cleaned_data.get('za_num_doss_pgre')

		# Je vérifie l'existence d'un objet TDossierPgre.
		if not self.instance.pk :
			try :
				TDossierPgre.objects.get(num_doss_pgre = v_num_doss_pgre)
			except :
				self.add_error('za_num_doss_pgre', 'L\'action PGRE n\'existe pas.')

	def save(self, commit = True) :

		# Imports
		from app.models import TDossierPgre

		o = super(GererPhotoPgre, self).save(commit = False)
		i = self.instance
		if i.pk :
			o.id_doss_pgre = i.id_doss_pgre
		else :
			o.id_doss_pgre = TDossierPgre.objects.get(num_doss_pgre = self.cleaned_data.get('za_num_doss_pgre'))
		if commit :
			o.save()

		return o

class GererControleActionPgre(forms.ModelForm) :

	za_num_doss_pgre = forms.CharField(
		label = 'Numéro de l\'action PGRE', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)

	class Meta :

		# Imports
		from app.models import TControleDossierPgre

		exclude = ['id_doss_pgre']
		fields = '__all__'
		model = TControleDossierPgre
		widgets = { 'dt_contr_doss_pgre' : forms.TextInput(attrs = { 'input-group-addon' : 'date' })}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		self.k_doss_pgre = kwargs.pop('k_doss_pgre', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'dt_contr_doss_pgre' : dt_fr(instance.dt_contr_doss_pgre)
			})

		super(GererControleActionPgre, self).__init__(*args, **kwargs)
		init_mess_err(self)

		i = self.instance
		if not i.pk :
			self.fields['za_num_doss_pgre'].initial = self.k_doss_pgre
		else :
			self.fields['za_num_doss_pgre'].initial = i.id_doss_pgre

	def clean(self) :

		# Imports
		from app.functions import dt_fr
		from app.models import TControleDossierPgre
		from datetime import date
		from django.db.models import Max

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererControleActionPgre, self).clean()
		v_dt_contr_doss_pgre = cleaned_data.get('dt_contr_doss_pgre')

		i = self.instance
		annee = date.today().year

		# J'initialise l'identifiant de l'action PGRE.
		if i.pk :
			v_id_doss_pgre = i.id_doss_pgre
		else :
			v_id_doss_pgre = self.k_doss_pgre

		# Je stocke la date du dernier point de contrôle s'il y a (instance ou non).
		qs_aggr_pdc = TControleDossierPgre.objects.filter(
			id_doss_pgre = v_id_doss_pgre, dt_contr_doss_pgre__year = annee
		)
		if i.pk :
			qs_aggr_pdc = qs_aggr_pdc.exclude(pk = i.pk)
		qs_aggr_pdc = qs_aggr_pdc.aggregate(Max('dt_contr_doss_pgre'))
		v_dt_contr_doss_pgre_max = qs_aggr_pdc['dt_contr_doss_pgre__max']

		# Je renvoie une erreur si la date du contrôle est antérieure ou égale à la date du dernier point de contrôle.
		if v_dt_contr_doss_pgre and v_dt_contr_doss_pgre_max and v_dt_contr_doss_pgre.year == annee:
			if v_dt_contr_doss_pgre <= v_dt_contr_doss_pgre_max :
				self.add_error('dt_contr_doss_pgre', 'Veuillez saisir une date postérieure au {0}.'.format(dt_fr(
					v_dt_contr_doss_pgre_max
				)))

		# Je renvoie une erreur si le point de contrôle n'est pas inclus dans l'année courante.
		if v_dt_contr_doss_pgre and v_dt_contr_doss_pgre.year != annee :
			self.add_error('dt_contr_doss_pgre', 'Veuillez saisir une date comprise dans l\'année {0}.'.format(annee))

	def save(self, commit = True) :

		o = super(GererControleActionPgre, self).save(commit = False)
		i = self.instance
		if i.pk :
			o.id_doss_pgre = i.id_doss_pgre
		else :
			o.id_doss_pgre = self.k_doss_pgre
		if commit :
			o.save()

		return o

class ChoisirActionPgre(forms.Form) :

	zl_org_moa = forms.ChoiceField(label = 'Maître d\'ouvrage', required = False, widget = forms.Select())
	zl_ic_pgre = forms.ChoiceField(label = 'Instance de concertation', required = False, widget = forms.Select())
	zl_atel_pgre = forms.ChoiceField(label = 'Atelier concerné', required = False, widget = forms.Select())
	zl_nat_doss = forms.ChoiceField(label = 'Nature de l\'action PGRE', required = False, widget = forms.Select())

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TAtelierPgre
		from app.models import TInstanceConcertationPgre
		from app.models import TMoa
		from app.models import TNatureDossier

		# Je déclare le tableau des arguments.
		k_org_moa = kwargs.pop('k_org_moa', None)

		super(ChoisirActionPgre, self).__init__(*args, **kwargs)

		# Je définis les messages d'erreurs personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES

		if k_org_moa :
			self.fields['zl_org_moa'].initial = k_org_moa

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		t_org_moa = [(m.pk, m) for m in TMoa.objects.filter(peu_doss_pgre = True, en_act_doss_pgre = True)]
		t_org_moa.insert(0, DEFAULT_OPTION)
		self.fields['zl_org_moa'].choices = t_org_moa

		# J'alimente la liste déroulante des instances de concertation.
		t_ic_pgre = [(i.pk, i) for i in TInstanceConcertationPgre.objects.all()]
		t_ic_pgre.insert(0, DEFAULT_OPTION)
		self.fields['zl_ic_pgre'].choices = t_ic_pgre

		# J'alimente la liste déroulante des ateliers concernés.
		t_atel_pgre = [(a.pk, a) for a in TAtelierPgre.objects.all()]
		t_atel_pgre.insert(0, DEFAULT_OPTION)
		self.fields['zl_atel_pgre'].choices = t_atel_pgre

		# J'alimente la liste déroulante des natures d'actions PGRE.
		t_nat_doss = [(nd.pk, nd) for nd in TNatureDossier.objects.filter(peu_doss_pgre = True)]
		t_nat_doss.insert(0, DEFAULT_OPTION)
		self.fields['zl_nat_doss'].choices = t_nat_doss

class FiltrerActionsPgre(forms.ModelForm) :

	# Import
	from app.models import TProgramme

	# Champs
	cbsm_atel_pgre = forms.MultipleChoiceField(
		label = 'Atelier(s) concerné(s)|Nom|__zcc__', required = False, widget = forms.SelectMultiple()
	)
	zl_progr = forms.ModelChoiceField(
		label = 'Programme du dossier de correspondance', queryset = TProgramme.objects.all(), required = False
	)
	cbsm_org_moa = forms.MultipleChoiceField(
		label = 'Maître(s) d\'ouvrage(s)|Nom|__zcc__', required = False, widget = forms.SelectMultiple()
	)
	zs_obj_econ_min_ress_doss_pgre = forms.FloatField(
		label = '',
		required = False,
		widget = forms.NumberInput(attrs = { 'placeholder' : '- infini par défaut' })
	)
	zs_obj_econ_max_ress_doss_pgre = forms.FloatField(
		label = '',
		required = False,
		widget = forms.NumberInput(attrs = { 'placeholder' : 'infini par défaut' })
	)
	zs_ann_prev_min_deb_doss_pgre = forms.IntegerField(
		label = '', required = False, widget = forms.NumberInput(attrs = { 'placeholder' : 'De' })
	)
	zs_ann_prev_max_deb_doss_pgre = forms.IntegerField(
		label = '', required = False, widget = forms.NumberInput(attrs = { 'placeholder' : 'à' })
	)
	zd_dt_deb_min_doss_pgre = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'Du' })
	)
	zd_dt_deb_max_doss_pgre = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'au' })
	)
	zd_dt_fin_min_doss_pgre = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'Du' })
	)
	zd_dt_fin_max_doss_pgre = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'au' })
	)
	cb_ajout_select_exist = forms.BooleanField(
		label = 'Ajouter à la sélection existante', required = False, widget = forms.CheckboxInput()
	)

	class Meta :

		# Import
		from app.models import TDossierPgre

		fields = [
			'id_av_pgre',
			'id_ic_pgre',
			'id_nat_doss',
			'id_pr_pgre'
		]
		model = TDossierPgre

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TAtelierPgre
		from app.models import TMoa

		super(FiltrerActionsPgre, self).__init__(*args, **kwargs)

		# Passage des champs requis à l'état non-requis
		for elem in list(self.fields) : self.fields[elem].required = False

		init_mess_err(self)

		# Définition des choix de certaines listes déroulantes
		self.fields['cbsm_atel_pgre'].choices = \
		[[apgre.pk, '|'.join([str(apgre), '__zcc__'])] for apgre in TAtelierPgre.objects.all()]
		self.fields['cbsm_org_moa'].choices = [[m.pk, '|'.join([str(m), '__zcc__'])] for m in TMoa.objects.filter(
			peu_doss_pgre = True, en_act_doss_pgre = True
		)]

	def get_form(self, _req) :

		# Imports
		from app.functions import init_f
		from django.template.context_processors import csrf

		form = init_f(self)

		return '''
		<form action="" method="post" name="f_filtr_act_pgre" onsubmit="soum_f(event);">
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			<fieldset class="my-fieldset">
				<legend>Rechercher par</legend>
				<div>
					{}
					{}
					{}
					{}
					{}
					Objectifs d'économie de la ressource en eau compris entre (en m<sup>3</sup>)
					<div class="row">
						<div class="col-xs-6">{}</div>
						<div class="col-xs-6">{}</div>
					</div>
					Année prévisionnelle du début de l'action PGRE
					<div class="row">
						<div class="col-xs-6">{}</div>
						<div class="col-xs-6">{}</div>
					</div>
					Période de début de l'action PGRE
					<div class="row">
						<div class="col-xs-6">{}</div>
						<div class="col-xs-6">{}</div>
					</div>
					Période de fin de l'action PGRE
					<div class="row">
						<div class="col-xs-6">{}</div>
						<div class="col-xs-6">{}</div>
					</div>
					{}
					{}
					<div class="checkboxes-group">{}</div>
					<div class="buttons-group">
						<button class="green-btn my-btn" type="reset">Réinitialiser</button>
						<button class="green-btn my-btn" type="submit">Valider</button>
					</div>
				</div>
			</fieldset>
		</form>
		'''.format(
			csrf(_req)['csrf_token'],
			form['id_ic_pgre'],
			form['cbsm_atel_pgre'],
			form['zl_progr'],
			form['cbsm_org_moa'],
			form['id_pr_pgre'],
			form['zs_obj_econ_min_ress_doss_pgre'],
			form['zs_obj_econ_max_ress_doss_pgre'],
			form['zs_ann_prev_min_deb_doss_pgre'],
			form['zs_ann_prev_max_deb_doss_pgre'],
			form['zd_dt_deb_min_doss_pgre'],
			form['zd_dt_deb_max_doss_pgre'],
			form['zd_dt_fin_min_doss_pgre'],
			form['zd_dt_fin_max_doss_pgre'],
			form['id_nat_doss'],
			form['id_av_pgre'],
			form['cb_ajout_select_exist']
		)

	def get_datatable(self, _req, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr
		from app.models import TDossierPgre
		from app.models import TUtilisateur
		from django.urls import reverse
		from styx.settings import T_DONN_BDD_INT

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_ic_pgre = self.fields['id_ic_pgre'].initial
			val_atel_pgre = self.fields['cbsm_atel_pgre'].initial
			val_progr = self.fields['zl_progr'].initial
			val_org_moa = self.fields['cbsm_org_moa'].initial
			val_pr_pgre = self.fields['id_pr_pgre'].initial
			val_obj_econ_min_ress_doss_pgre = self.fields['zs_obj_econ_min_ress_doss_pgre'].initial
			val_obj_econ_max_ress_doss_pgre = self.fields['zs_obj_econ_max_ress_doss_pgre'].initial
			val_ann_prev_min_deb_doss_pgre = self.fields['zs_ann_prev_min_deb_doss_pgre'].initial
			val_ann_prev_max_deb_doss_pgre = self.fields['zs_ann_prev_max_deb_doss_pgre'].initial
			val_dt_deb_min_doss_pgre = self.fields['zd_dt_deb_min_doss_pgre'].initial
			val_dt_deb_max_doss_pgre = self.fields['zd_dt_deb_max_doss_pgre'].initial
			val_dt_fin_min_doss_pgre = self.fields['zd_dt_fin_min_doss_pgre'].initial
			val_dt_fin_max_doss_pgre = self.fields['zd_dt_fin_max_doss_pgre'].initial
			val_nat_doss = self.fields['id_nat_doss'].initial
			val_av_pgre = self.fields['id_av_pgre'].initial
			val_ajout_select_exist = self.fields['cb_ajout_select_exist'].initial
		else :
			cleaned_data = self.cleaned_data
			val_ic_pgre = cleaned_data.get('id_ic_pgre')
			val_atel_pgre = cleaned_data.get('cbsm_atel_pgre')
			val_progr = cleaned_data.get('zl_progr')
			val_org_moa = cleaned_data.get('cbsm_org_moa')
			val_pr_pgre = cleaned_data.get('id_pr_pgre')
			val_obj_econ_min_ress_doss_pgre = cleaned_data.get('zs_obj_econ_min_ress_doss_pgre')
			val_obj_econ_max_ress_doss_pgre = cleaned_data.get('zs_obj_econ_max_ress_doss_pgre')
			val_ann_prev_min_deb_doss_pgre = cleaned_data.get('zs_ann_prev_min_deb_doss_pgre')
			val_ann_prev_max_deb_doss_pgre = cleaned_data.get('zs_ann_prev_max_deb_doss_pgre')
			val_dt_deb_min_doss_pgre = cleaned_data.get('zd_dt_deb_min_doss_pgre')
			val_dt_deb_max_doss_pgre = cleaned_data.get('zd_dt_deb_max_doss_pgre')
			val_dt_fin_min_doss_pgre = cleaned_data.get('zd_dt_fin_min_doss_pgre')
			val_dt_fin_max_doss_pgre = cleaned_data.get('zd_dt_fin_max_doss_pgre')
			val_nat_doss = cleaned_data.get('id_nat_doss')
			val_av_pgre = cleaned_data.get('id_av_pgre')
			val_ajout_select_exist = cleaned_data.get('cb_ajout_select_exist')

		# Initialisation des conditions de la requête
		ands = {}

		# Préparation des conditions
		if val_ic_pgre : ands['id_ic_pgre'] = val_ic_pgre
		if val_atel_pgre : ands['tatelierspgredossierpgre__id_atel_pgre__in'] = val_atel_pgre
		if val_progr : ands['id_doss__id_progr'] = val_progr
		if val_org_moa : ands['tmoadossierpgre__id_org_moa__in'] = val_org_moa
		if val_pr_pgre : ands['id_pr_pgre'] = val_pr_pgre
		if val_obj_econ_min_ress_doss_pgre is not None :
			ands['obj_econ_ress_doss_pgre__gte'] = val_obj_econ_min_ress_doss_pgre
		if val_obj_econ_max_ress_doss_pgre is not None :
			ands['obj_econ_ress_doss_pgre__lte'] = val_obj_econ_max_ress_doss_pgre
		if val_ann_prev_min_deb_doss_pgre is not None :
			ands['ann_prev_deb_doss_pgre__gte'] = val_ann_prev_min_deb_doss_pgre
		if val_ann_prev_max_deb_doss_pgre is not None :
			ands['ann_prev_deb_doss_pgre__lte'] = val_ann_prev_max_deb_doss_pgre
		if val_dt_deb_min_doss_pgre : ands['dt_deb_doss_pgre__gte'] = val_dt_deb_min_doss_pgre
		if val_dt_deb_max_doss_pgre : ands['dt_deb_doss_pgre__lte'] = val_dt_deb_max_doss_pgre
		if val_dt_fin_min_doss_pgre : ands['dt_fin_doss_pgre__gte'] = val_dt_fin_min_doss_pgre
		if val_dt_fin_max_doss_pgre : ands['dt_fin_doss_pgre__lte'] = val_dt_fin_max_doss_pgre
		if val_nat_doss : ands['id_nat_doss'] = val_nat_doss
		if val_av_pgre : ands['id_av_pgre'] = val_av_pgre

		# Préparation du jeu de données des actions PGRE
		_qs_doss_pgre = TDossierPgre.objects.filter(**ands)

		# Filtrage des droits d'accès (un utilisateur ne peut accéder
		# aux actions PGRE dont il n'a aucune permission en lecture a
		# minima)
		qs_doss_pgre = TDossierPgre.objects.none()
		permissions = TUtilisateur.objects.get(pk=_req.user.pk) \
			.get_permissions(read_or_write='R')
		for iGre in _qs_doss_pgre:
			for iMoaGre in iGre.tmoadossierpgre_set.all():
				if (
					iMoaGre.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']
				) in permissions:
					qs_doss_pgre |= TDossierPgre.objects.filter(pk=iGre.pk)

		# Réinitialisation de la variable "historique" si l'option "Ajouter à la sélection existante" n'est pas cochée
		if not val_ajout_select_exist : _req.session['filtr_act_pgre'] = []

		# Empilement de la variable "historique"
		_req.session['filtr_act_pgre'] += [dpgre.pk for dpgre in qs_doss_pgre]

		# Suppression de variables
		del ands, qs_doss_pgre

		# Initialisation des balises <tr/>
		trs = []

		for dpgre in TDossierPgre.objects.filter(pk__in = _req.session.get('filtr_act_pgre')) :

			# Préparation des colonnes
			tds = [
				dpgre.num_doss_pgre,
				dpgre.int_doss_pgre,
				dpgre.id_ic_pgre,
				', '.join([str(apgre) for apgre in dpgre.atel_pgre.all()]),
				dpgre.id_doss or '-',
				', '.join([str(m) for m in dpgre.moa.all()]),
				dpgre.id_pr_pgre,
				dpgre.obj_econ_ress_doss_pgre,
				dpgre.ann_prev_deb_doss_pgre,
				dt_fr(dpgre.dt_deb_doss_pgre) or '-',
				dt_fr(dpgre.dt_fin_doss_pgre) or '-',
				dpgre.id_nat_doss,
				dpgre.id_av_pgre,
				'<a href="{0}" class="consult-icon pull-right" title="Consulter l\'action PGRE"></a>'.format(
					reverse('cons_act_pgre', args = [dpgre.pk])
				)
			]

			# Empilement des balises <tr/>
			trs.append('<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tds])))

			# Suppression de variables
			del dpgre, tds

		return '''
		<div class="my-table" id="t_select_act_pgre">
			<table>
				<thead>
					<tr>
						<th>N° de l'action PGRE</th>
						<th>Intitulé de l'action PGRE</th>
						<th>Instance de concertation</th>
						<th>Atelier(s) concerné(s)</th>
						<th>Dossier de correspondance</th>
						<th>Maître(s) d'ouvrage(s)</th>
						<th>Priorité</th>
						<th>Objectifs d'économie de la ressource en eau (en m<sup>3</sup>)</th>
						<th>Année prévisionnelle du début de l'action PGRE</th>
						<th>Date de début de l'action PGRE</th>
						<th>Date de fin de l'action PGRE</th>
						<th>Nature de l'action PGRE</th>
						<th>État d'avancement</th>
						<th></th>
					</tr>
				</thead>
				<tbody>{}</tbody>
			</table>
		</div>
		'''.format(''.join(trs))

class GererSsActionPgre(forms.ModelForm):

	# Imports
	from app.classes.FFEuroField import Class as FFEuroField
	from app.models import TNatureDossier
	from app.models import TAvancementPgre

	lib_ss_act = forms.CharField(label = 'Libellé', required = True)

	desc_ss_act = forms.CharField(
		label = 'Descriptif', widget = forms.TextInput(), required = False)

	comm_ss_act = forms.CharField(
		label = 'Commentaire', widget = forms.Textarea, required = False)

	dt_prevision_ss_action_pgre = forms.DateField(
		label='Prévisionnel', required=True,
        widget=forms.TextInput(
            attrs={ 'input-group-addon' : 'date' }))

	dt_deb_ss_action_pgre = forms.DateField(
		label = 'Début', required=True,
		widget=forms.TextInput(
			attrs={ 'input-group-addon' : 'date' }))

	dt_fin_ss_action_pgre = forms.DateField(
		label = 'Fin', required=True,
        widget=forms.TextInput(
            attrs={ 'input-group-addon' : 'date' }))

	mont_ss_action_pgre = FFEuroField(label = "Montant", required = True)

	obj_econ_ress_ss_action_pgre = forms.FloatField(
		label = "Objectif d'économie de ressource", required = True)

	moa = forms.MultipleChoiceField(
		label = 'Maître(s) d\'ouvrage(s)|Nom|__zcc__', required = False, widget = forms.SelectMultiple()
	)

	t_nature_dossier = forms.ModelChoiceField(
		label = 'Nature de la sous-action PGRE',
		queryset = TNatureDossier.objects.filter(peu_doss_pgre = True),
		empty_label="Sélectionnez une nature de sous-action")

	id_av_pgre = forms.ModelChoiceField(
		label = 'Avancement de la sous-action',
		queryset = TAvancementPgre.objects.all(),
		empty_label="Sélectionnez l'etat d'avancement de la sous-action")

	za_num_doss_pgre = forms.CharField(
		label = 'Numéro de l\'action PGRE',
		required = False,
		widget = forms.TextInput(attrs = { 'readonly' : True })
	)

	class Meta:
		from app.models import TDossierSsAction
		model = TDossierSsAction
		fields = '__all__'

	def __init__(self, *args, **kwargs):

		from app.models import TMoa
		from app.models import TNatureDossier
		from app.functions import dt_fr

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		self.k_doss_pgre = kwargs.pop('k_doss_pgre', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'dt_prevision_ss_action_pgre' : dt_fr(instance.dt_prevision_ss_action_pgre) if instance.dt_prevision_ss_action_pgre else '',
				'dt_deb_ss_action_pgre' : dt_fr(instance.dt_deb_ss_action_pgre) if instance.dt_deb_ss_action_pgre else '',
				'dt_fin_ss_action_pgre' : dt_fr(instance.dt_fin_ss_action_pgre) if instance.dt_fin_ss_action_pgre else '',
			})


		super().__init__(*args, **kwargs)
		init_mess_err(self)

		# Définition des choix de certaines listes déroulantes
		self.fields['moa'].choices = [[m.pk, '|'.join([str(m), '__zcc__'])] for m in TMoa.objects.filter(
			peu_doss_pgre = True, en_act_doss_pgre = True
		)]
		self.fields['za_num_doss_pgre'].initial = self.k_doss_pgre

		# J'alimente la liste déroulante des natures de sous actions PGRE.
		t_nat_doss = [(nd.pk, nd) for nd in TNatureDossier.objects.filter(peu_doss_pgre = True)]
		t_nat_doss.insert(0, DEFAULT_OPTION)
		self.fields['t_nature_dossier'].choices = t_nat_doss

	def clean(self):
		# Je renvoie une erreur s'il y a une incohérence entre les dates de début et de fin de l'action PGRE.
		dt_deb_ss_action_pgre = self.cleaned_data.get('dt_deb_ss_action_pgre')
		dt_fin_ss_action_pgre = self.cleaned_data.get('dt_fin_ss_action_pgre')
		if dt_deb_ss_action_pgre and dt_fin_ss_action_pgre and dt_deb_ss_action_pgre > dt_fin_ss_action_pgre :
			self.add_error(
				'dt_deb_ss_action_pgre', 'Veuillez saisir une date de début postérieure ou égale à la date de fin.'
			)
			self.add_error(
				'dt_fin_ss_action_pgre', 'Veuillez saisir une date de fin antérieure ou égale à la date de début.'
			)
	def save(self, *args, **kwargs):
		return super().save(*args, **kwargs)
