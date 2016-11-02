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
		from app.functions import crypt_val
		from app.models import TUtilisateur

		# Je récupère les données utiles du formulaire pré-valide.
		cleaned_data = super(Identifier, self).clean()
		v_pseudo_util = cleaned_data.get('zs_pseudo_util')
		v_mdp_util = crypt_val(cleaned_data.get('zs_mdp_util'))

		# Je déclare des booléens me permettant de jauger l'état de l'identification.
		pseudo_trouve = False
		mdp_trouve = False

		# Je stocke dans un tableau tous les utilisateurs référencés dans la base de données.
		les_util = TUtilisateur.objects.all()

		# Je parcours chaque utilisateur afin de vérifier si l'identification est possible ou non.
		for un_util in les_util :
			if v_pseudo_util == un_util.pseudo_util :
				pseudo_trouve = True
				if v_mdp_util == un_util.mdp_util :
					mdp_trouve = True

		# Je définis les messages d'erreurs.
		if pseudo_trouve == True :
			if mdp_trouve == False :
				self.add_error('zs_mdp_util', 'Veuillez saisir le bon mot de passe lié à ce compte.')
		else :
			self.add_error('zs_pseudo_util', 'Aucun compte n\'est lié à ce courriel.')

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