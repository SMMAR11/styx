#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.constants import *

'''
Ce validateur renvoie une erreur si la valeur saisie contient un caractère indésirable.
_v : Valeur saisie
'''
def val_cdc(_v) :

	# Imports
	from django.core.exceptions import ValidationError

	t = [';', '"']
	for i in range(0, len(_v)) :
		if any(s in _v[i] for s in t) :
			raise ValidationError('Le caractère « {0} » est interdit.'.format(_v[i]))

'''
Ce validateur renvoie une erreur si le format du courriel saisi est incorrect.
p_valeur : Courriel saisi
'''
def val_courr(_v) :

	# Imports
	from django.core.exceptions import ValidationError
	import re

	if not re.match(r'[^@]+@[^@]+\.[^@]+', _v) :
		raise ValidationError('Veuillez saisir un courriel valide.')

'''
Ce validateur renvoie une erreur si l'extension d'un fichier uploadé n'est pas au format image autorisé.
_v : Fichier uploadé
'''
def val_fich_img(_v) :

	# Imports
	from app.functions import verif_ext_fich
	from django.core.exceptions import ValidationError

	if verif_ext_fich(_v, ('.bmp', '.gif', '.jpg', '.jpeg', '.png')) == True :
		raise ValidationError('Veuillez choisir un fichier au format BMP, GIF, JPG, JPEG ou PNG.')

	t = 3
	if _v.size > t * 1048576 :
		raise ValidationError(
			'Veuillez choisir un fichier dont la taille est inférieure ou égale à {0} Mo.'.format(t)
		)

	return _v

'''
Ce validateur renvoie une erreur si l'extension d'un fichier uploadé n'est pas au format PDF.
_v : Fichier uploadé
'''
def val_fich_pdf(_v) :

	# Imports
	from app.functions import verif_ext_fich
	from django.core.exceptions import ValidationError

	if verif_ext_fich(_v, '.pdf') == True :
		raise ValidationError('Veuillez choisir un fichier au format PDF.')

	t = 20
	if _v.size > t * 1048576 :
		raise ValidationError(
			'Veuillez choisir un fichier dont la taille est inférieure ou égale à {0} Mo.'.format(t)
		)

	return _v

'''
Ce validateur renvoie une erreur si la valeur saisie n'est pas conforme.
_v : Valeur saisie
'''
def val_mont_nul(_v) :

	# Imports
	from app.functions import verif_mont
	from django.core.exceptions import ValidationError

	if verif_mont(_v, True) == True :
		raise ValidationError(ERROR_MESSAGES['invalid'])

	return _v

'''
Ce validateur renvoie une erreur si la valeur saisie n'est pas conforme.
_v : Valeur saisie
'''
def val_mont_pos(_v) :

	# Imports
	from app.functions import verif_mont
	from django.core.exceptions import ValidationError

	if verif_mont(_v, False) == True :
		raise ValidationError(ERROR_MESSAGES['invalid'])

	return _v

'''
Ce validateur renvoie une erreur si la valeur saisie n'est pas comprise dans l'intervalle ]0; 100].
_v : Valeur saisie
'''
def val_pourc(_v) :

	# Imports
	from django.core.exceptions import ValidationError
	
	if not 0 < _v <= 100 :
		raise ValidationError(ERROR_MESSAGES['invalid'])

'''
Ce validateur renvoie une erreur si la valeur saisie ne ressemble pas à un numéro SIRET.
_v : Valeur saisie
'''
def val_siret(_v) :

	# Imports
	from django.core.exceptions import ValidationError

	err = False

	if len(_v) != 14 :
		err = True
	else :
		try :
			int(_v)
		except :
			err = True

	if err == True :
		raise ValidationError(ERROR_MESSAGES['invalid'])

	return _v

'''
Ce validateur renvoie une erreur si la valeur saisie ne ressemble pas à un numéro de téléphone.
_v : Valeur saisie
'''
def val_tel(_v) :

	# Imports
	from django.core.exceptions import ValidationError

	err = False

	if len(_v) != 10 :
		err = True
	else :
		try :
			int(_v)
		except :
			err = True

	if err == True :
		raise ValidationError(ERROR_MESSAGES['invalid'])

	return _v