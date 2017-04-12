#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.constants import *
from app.functions import init_mess_err
from django import forms

class Identifier(forms.Form) :
	
	zs_username = forms.CharField(
		error_messages = ERROR_MESSAGES, 
		label = 'Nom d\'utilisateur', 
		widget = forms.TextInput(attrs = { 'class' : 'my-form-control' })
	)

	zs_password = forms.CharField(
		error_messages = ERROR_MESSAGES,
		label = 'Mot de passe', 
		widget = forms.PasswordInput(attrs = { 'class' : 'my-form-control' })
	)

	def clean(self) :

		# Imports
		from django.contrib.auth import authenticate

		# Je récupère les données du formulaire pré-valide.
		cleaned_data = super(Identifier, self).clean()
		v_username = cleaned_data.get('zs_username')
		v_password = cleaned_data.get('zs_password')

		# Je vérifie l'état de l'identification.
		if v_username and v_password :
			o_util = authenticate(username = v_username, password = v_password)
			if o_util is None :
				self.add_error('__all__', 'Les identifiants rentrés sont incorrects.')
			else :
				if not o_util.is_active :
					self.add_error('__all__', 'Votre compte est désactivé.')

class GererUtilisateur(forms.ModelForm) :

	class Meta :

		# Imports
		from app.models import TUtilisateur

		fields = ('email', 'first_name', 'last_name', 'port_util', 'tel_util')
		model = TUtilisateur
		widgets = { 'email' : forms.TextInput(attrs = { 'input-group-addon' : 'email' }) }

	def __init__(self, *args, **kwargs) :

		super(GererUtilisateur, self).__init__(*args, **kwargs)
		init_mess_err(self)
