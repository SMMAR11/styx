#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.constants import *
from app.functions import init_mess_err
from django import forms

class GererActionPgre(forms.ModelForm) :

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

	class Meta :

		# Imports
		from app.models import TDossierPgre

		exclude = ['atel_pgre', 'id_doss', 'id_nat_doss', 'moa']
		fields = '__all__'
		model = TDossierPgre
		widgets = {
			'dt_deb_doss_pgre' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_fin_doss_pgre' : forms.TextInput(attrs = { 'input-group-addon' : 'date' })
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
				'dt_deb_doss_pgre' : dt_fr(instance.dt_deb_doss_pgre),
				'dt_fin_doss_pgre' : dt_fr(instance.dt_fin_doss_pgre)
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