#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.constants import *
from django import forms

class GererActionPgre(forms.ModelForm) :

	cbsm_atel_pgre = forms.MultipleChoiceField(label = 'Atelier(s) concerné(s);Nom', widget = forms.SelectMultiple())
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
	cbsm_org_moa = forms.MultipleChoiceField(label = 'Maître(s) d\'ouvrage(s);Nom', widget = forms.SelectMultiple())

	class Meta :

		# Imports
		from app.models import TDossierPgre

		exclude = ['atel_pgre', 'id_doss', 'moa']
		fields = '__all__'
		model = TDossierPgre

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TInstancesConcertationPgreAtelierPgre
		from app.models import TMoa

		# Je déclare le tableau des arguments.
		self.k_util = kwargs.pop('k_util', None)
		k_ic_pgre = kwargs.pop('k_ic_pgre', None)

		super(GererActionPgre, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				split = self.fields[cle].label.split(';')
				split[0] = split[0] + REQUIRED
				self.fields[cle].label = ';'.join(split)

		# J'alimente la liste déroulante des ateliers concernés par une instance de concertation.
		if k_ic_pgre :
			try :
				t_atel_pgre = [(
					a.id_atel_pgre.pk, a.id_atel_pgre
				) for a in TInstancesConcertationPgreAtelierPgre.objects.filter(id_ic_pgre = k_ic_pgre)]
			except :
				t_atel_pgre = []
			self.fields['cbsm_atel_pgre'].choices = t_atel_pgre

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		t_org_moa = [(m.pk, m) for m in TMoa.objects.filter(peu_doss_pgre = True, en_act_doss_pgre = True)]
		self.fields['cbsm_org_moa'].choices = t_org_moa

	def clean(self) :

		# Imports
		from app.functions import ger_droits
		from app.models import TDossier
		from app.models import TMoa
		from styx.settings import PGRE_PK

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
				if ger_droits(self.k_util, [o_org_moa.pk, PGRE_PK], False, False) == False :
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

		o = super(GererActionPgre, self).save(commit = False)

		# Je vérifie l'existence d'un objet TDossier.
		try :
			o_doss = TDossier.objects.get(num_doss = self.cleaned_data.get('za_doss_corr'))
		except :
			o_doss = None

		o.id_doss = o_doss
		o.save()
		for a in self.cleaned_data.get('cbsm_atel_pgre') :
			TAteliersPgreDossierPgre.objects.create(id_atel_pgre = TAtelierPgre.objects.get(pk = a), id_doss_pgre = o)
		for m in self.cleaned_data.get('cbsm_org_moa') :
			TMoaDossierPgre.objects.create(id_doss_pgre = o, id_org_moa = TMoa.objects.get(pk = m))

		return o