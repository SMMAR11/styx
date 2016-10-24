from app.constants import *
from datetime import date
from django.core.exceptions import ValidationError
import re

'''
Ce validateur renvoie une erreur si la valeur saisie contient un point-virgule.
p_valeur : Valeur saisie
'''
def valid_cdc(p_valeur) :

	if ';' in p_valeur :
		raise ValidationError('Le caractère ";" est interdit.')

'''
Ce validateur renvoie une erreur si le format du courriel saisi est incorrect.
p_valeur : Courriel saisi
'''
def valid_courr(p_valeur) :

	if not re.match(r'[^@]+@[^@]+\.[^@]+', p_valeur) :
		raise ValidationError('Veuillez saisir un courriel valide.')

'''
Ce validateur renvoie une erreur si le montant saisi est incorrect.
p_valeur : Montant saisi
'''
def valid_mont(p_valeur) :

	# J'essaie de convertir le montant saisi en nombre décimal.
	try :

		# Je convertis le montant saisi en nombre décimal.
		float(p_valeur)

		# Je transforme le montant saisi en un tableau de caractères.
		str_valeur = str(p_valeur)

		# Je traite le cas où le montant saisi est un nombre décimal.
		if '.' in str_valeur :

			# J'initialise deux variables booléennes, me permettant de calculer le nombre de décimales du montant 
			# saisi.
			separateur_trouve = False
			cpt_decimales = 0

			for i in range(0, len(str_valeur)) :

				# J'incrémente le compteur de décimales dès le moment où le séparateur a été trouvé.
				if separateur_trouve == True :
					cpt_decimales += 1

				# J'informe que le séparateur a été trouvé.
				if '.' in str_valeur[i] :
					separateur_trouve = True

			# Je revoie une erreur si le montant saisi comporte plus de deux décimales.
			if cpt_decimales > 2 :
				raise ValidationError(MESSAGES['invalid'])

	except ValueError :
		raise ValidationError(MESSAGES['invalid'])

'''
Ce validateur renvoie une erreur si la valeur saisie ne correspond pas à un nombre.
p_valeur : Valeur saisie
'''
def valid_nb(p_valeur) :

	# J'essaie de convertir la valeur saisie en nombre décimal.
	try :
		float(p_valeur)
	except ValueError :
		raise ValidationError(MESSAGES['invalid'])

'''
Ce validateur renvoie une erreur si le numéro SIRET saisi est incorrect.
p_valeur : Numéro SIRET saisi
'''
def valid_siret(p_valeur) :

	# Je renvoie une erreur si le numéro SIRET saisi ne comporte pas quatorze caractères.
	if len(p_valeur) != 14 :
		raise ValidationError(MESSAGES['invalid'])
	else :

		# Je renvoie une erreur si le numéro SIRET saisi comporte un ou plusieurs caractères non-numériques.
		try :
			int(p_valeur)
		except ValueError :
			raise ValidationError(MESSAGES['invalid'])