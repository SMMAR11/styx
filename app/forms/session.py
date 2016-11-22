#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.constants import *
from django import forms

class Identifier(forms.Form) :
	
	# Je définis les champs du formulaire.
	zs_pseudo_util = forms.CharField(
		error_messages = MESSAGES,
		label = 'Nom d\'utilisateur',
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_mdp_util = forms.CharField(
		error_messages = MESSAGES,
		label = 'Mot de passe',
		widget = forms.PasswordInput(attrs = { 'class' : 'form-control' })
	)

	def clean(self) :

		''' Imports '''
		from app.functions import nett_val
		from django.contrib.auth import authenticate

		# Je récupère les données utiles du formulaire pré-valide.
		cleaned_data = super(Identifier, self).clean()
		v_pseudo_util = nett_val(cleaned_data.get('zs_pseudo_util'))
		v_mdp_util = nett_val(cleaned_data.get('zs_mdp_util'))

		if v_pseudo_util is not None and v_mdp_util is not None :

			# Je vérifie l'existence d'un objet TUtilisateur.
			obj_util = authenticate(username = v_pseudo_util, password = v_mdp_util)

			# Je renvoie une erreur si aucun objet TUtilisateur n'a
			if obj_util is None :
				self.add_error('zs_pseudo_util', None)
				self.add_error('zs_mdp_util', 'Les identifiants rentrés sont incorrects.')

class OublierMotDePasse(forms.Form) :

	''' Imports '''
	from app.validators import valid_courr

	# Je définis le champ du formulaire.
	zs_courr_util = forms.CharField(
		error_messages = MESSAGES,
		label = 'Adresse électronique' + CHAMP_REQUIS,
		widget = forms.TextInput(attrs = { 'class' : 'form-control' }),
		validators = [valid_courr]
	)

	def clean_zs_courr_util(self) :

		''' Imports '''
		from app.models import TUtilisateur

		# Je récupère le courriel saisi.
		v_courr_util = self.cleaned_data['zs_courr_util']

		# Je déclare un booléen me permettant de voir si le courriel saisi est lié ou non à un compte.
		courriel_trouve = False

		# Je stocke dans un tableau tous les utilisateurs référencés dans la base de données.
		les_util = TUtilisateur.objects.all()

		# Je parcours chaque utilisateur afin de vérifier si le courriel saisi est lié ou non à un compte.
		for un_util in les_util :
			if v_courr_util == un_util.courr_util :
				courriel_trouve = True

		# Je définis le message d'erreur.
		if courriel_trouve == False :
			raise forms.ValidationError('Veuillez saisir le courriel lié à votre compte.')

		return v_courr_util