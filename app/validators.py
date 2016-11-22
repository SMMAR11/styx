#!/usr/bin/env python
#-*- coding: utf-8

from app.constants import *

'''
Ce validateur renvoie une erreur si la valeur saisie contient un point-virgule.
p_valeur : Valeur saisie
'''
def valid_cdc(p_valeur) :

	''' Imports '''
	from django.core.exceptions import ValidationError

	if ';' in p_valeur :
		raise ValidationError('Le caractère ";" est interdit.')

'''
Ce validateur renvoie une erreur si le format du courriel saisi est incorrect.
p_valeur : Courriel saisi
'''
def valid_courr(p_valeur) :

	''' Imports '''
	from django.core.exceptions import ValidationError
	import re

	if not re.match(r'[^@]+@[^@]+\.[^@]+', p_valeur) :
		raise ValidationError('Veuillez saisir un courriel valide.')

'''
Ce validateur renvoie une erreur si la valeur saisie n'est pas un nombre entier.
p_valeur : Valeur saisie
'''
def valid_int(p_valeur) :

	''' Imports '''
	from django.core.exceptions import ValidationError

	try :

		# Je tente de convertir la valeur saisie en un nombre entier.
		p_valeur = int(p_valeur)

		# Je vérifie que l'entier est supérieur à 0.
		if p_valeur < 0 :
			raise ValidationError(MESSAGES['invalid'])

	except ValueError :
		raise ValidationError(MESSAGES['invalid'])

'''
Ce validateur renvoie une erreur si le montant saisi est incorrect.
p_valeur : Montant saisi
'''
def valid_mont(p_valeur) :

	''' Imports '''
	from django.core.exceptions import ValidationError

	try :

		# Je tente de convertir le montant saisi en nombre décimal.
		p_valeur = float(p_valeur)

		# Je vérifie si le montant saisi est positif ou nul.
		if p_valeur >= 0 :

			# Je transforme le montant saisi en un tableau de caractères.
			str_valeur = str(p_valeur)

			# Je traite le cas où le montant saisi est un nombre décimal.
			if '.' in str_valeur :

				# J'initialise deux variables booléennes, me permettant de calculer le nombre de décimales du montant 
				# saisi.
				sep_trouve = False
				cpt_dec = 0

				for i in range(0, len(str_valeur)) :

					# J'incrémente le compteur de décimales dès le moment où le séparateur a été trouvé.
					if sep_trouve == True :
						cpt_dec += 1

					# J'informe que le séparateur a été trouvé.
					if '.' in str_valeur[i] :
						sep_trouve = True

				# Je revoie une erreur si le montant saisi comporte plus de deux décimales.
				if cpt_dec > 2 :
					raise ValidationError(MESSAGES['invalid'])

		else :
			raise ValidationError(MESSAGES['invalid'])

	except ValueError :
		raise ValidationError(MESSAGES['invalid'])

'''
Ce validateur renvoie une erreur si la valeur saisie ne correspond pas à un nombre.
p_valeur : Valeur saisie
'''
def valid_nb(p_valeur) :

	''' Imports '''
	from django.core.exceptions import ValidationError

	try :
		float(p_valeur)
	except ValueError :
		raise ValidationError(MESSAGES['invalid'])

'''
Ce validateur renvoie une erreur si le pourcentage renseigné est incorrect.
p_valeur : Pourcentage saisi
'''
def valid_pourc(p_valeur) :

	''' Imports '''
	from django.core.exceptions import ValidationError

	try :

		# Je tente de convertir la valeur saisie en nombre décimal.
		p_valeur = float(p_valeur)

		# Je vérifie que le pourcentage est compris entre 0 et 100 %.
		if p_valeur < 0 or p_valeur > 100 :
			raise ValidationError(MESSAGES['invalid'])
			
	except ValueError :
		raise ValidationError(MESSAGES['invalid'])

'''
Ce validateur renvoie une erreur si le numéro SIRET saisi est incorrect.
p_valeur : Numéro SIRET saisi
'''
def valid_siret(p_valeur) :

	''' Imports '''
	from django.core.exceptions import ValidationError

	if len(p_valeur) != 14 :

		# Je renvoie une erreur si le numéro SIRET saisi ne comporte pas quatorze caractères.
		raise ValidationError(MESSAGES['invalid'])
		
	else :

		# Je renvoie une erreur si le numéro SIRET saisi comporte un ou plusieurs caractères non-numériques.
		try :
			int(p_valeur)
		except ValueError :
			raise ValidationError(MESSAGES['invalid'])