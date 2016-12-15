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

	tab_caract = [';', '"']
	for i in range(0, len(p_valeur)) :
		if any(s in p_valeur[i] for s in tab_caract) :
			raise ValidationError('Le caractère « {0} » est interdit.'.format(p_valeur[i]))

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
p_etre_nul : Puis-je renseigner un montant nul ?
'''
def valid_mont(p_etre_nul = True) :

	def func(p_valeur) :

		''' Imports '''
		from django.core.exceptions import ValidationError

		# J'initialise la valeur de la variable de sortie de la fonction.
		erreur = False

		# Je prépare le processus de validation.
		str_valeur = str(p_valeur)
		tab_caract = []

		# J'empile le tableau des caractères non-numériques.
		for i in range(0, len(str_valeur)) :
			try :
				int(str_valeur[i])
			except :
				tab_caract.append(str_valeur[i])

		# J'initialise un indicateur booléen permettant de jauger la validité du montant saisi.
		valide = False

		# Je traite le cas où le montant saisi est un nombre décimal.
		if len(tab_caract) == 1 and '.' in tab_caract :

			valide = True

			# J'initialise deux variables, me permettant de calculer le nombre de décimales du montant saisi.
			sep_trouve = False
			cpt_dec = 0

			for i in range(0, len(str_valeur)) :

				# J'incrémente le compteur de décimales dès le moment où le séparateur a été trouvé.
				if sep_trouve == True :
					cpt_dec += 1

				# J'informe que le séparateur a été trouvé.
				if tab_caract[0] in str_valeur[i] :
					sep_trouve = True

				# Je renvoie une erreur si le montant saisi comporte plus de deux décimales.
				if cpt_dec > 2 :
					raise ValidationError(MESSAGES['invalid'])

			# Je renvoie une erreur si le séparateur est le dernier caractère.
			if tab_caract[0] in str_valeur[len(str_valeur) - 1] :
				raise ValidationError(MESSAGES['invalid'])

		# Je traite le cas où le montant saisi est un nombre entier.
		if len(tab_caract) == 0 and str_valeur != '' :
			valide = True

		if str_valeur == '0' :
			if p_etre_nul == False :
				raise ValidationError(MESSAGES['invalid'])

		if valide == False :
			raise ValidationError(MESSAGES['invalid'])

	return func

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