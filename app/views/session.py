#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.decorators import *

'''
Cette vue permet soit d'afficher la page principale, soit de traiter l'un des formulaires de la page principale. 
request : Objet requête
'''
@nett_form
def index(request) :

	''' Imports '''
	from app.forms.session import Identifier, OublierMotDePasse
	from app.functions import init_fm, init_form
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	from django.template.context_processors import csrf
	import json

	reponse = HttpResponse()

	if request.method == 'GET' :

		# J'instancie des objets "formulaire".
		f_id = Identifier()
		f_oub_mdp = OublierMotDePasse()

		# J'initialise les champs du formulaire de demande de réinitialisation du mot de passe.
		tab_oub_mdp = init_form(f_oub_mdp)

		# Je déclare le contenu de certaines fenêtres modales.
		tab_cont_fm = {
			'oublier_mdp' : '''
			<form name="form_oublier_mdp" method="post" action="{0}?action=oublier-mdp" class="c-theme">
				<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
				{2}
				<button type="submit" class="center-block btn bt-vert to-unfocus">Valider</button>
			</form>
			'''.format(reverse('index'), csrf(request)['csrf_token'], tab_oub_mdp['zs_courr_util'])
		}

		# Je déclare un tableau de fenêtres modales qui varie selon l'état de la session. De plus, j'initialise la
		# valeur de la balise <title/>.
		if 'util' in request.session :
			tab_fm = []
			title = 'Accueil'
		else :
			tab_fm = [
				init_fm('identification', 'Identification'),
				init_fm('oublier_mdp', 'Oubli de votre mot de passe', tab_cont_fm['oublier_mdp'])
			]
			title = 'Identification'

		# J'affiche le template.
		reponse = render(
			request,
			'./main.html',
			{ 'f1' : init_form(f_id), 'les_fm' : tab_fm, 'title' : title }
		)

	else :

		if 'action' in request.GET :

			# Je retiens le nom du paramètre "GET".
			get_action = request.GET['action']

			# Je traite le cas lié à la soumission du formulaire d'identification.
			if get_action == 'identifier' :

				# Je vérifie la validité du formulaire d'identification.
				f_id = Identifier(request.POST)

				if f_id.is_valid() :

					# Je récupère les données du formulaire valide.
					cleaned_data = f_id.cleaned_data
					v_pseudo_util = cleaned_data['zs_pseudo_util']
					v_mdp_util = cleaned_data['zs_mdp_util']

					# Je récupère les données attributaires d'un objet TUtilisateur (utilisateur connecté).
					obj_util = TUtilisateur.objects.get(pseudo_util = v_pseudo_util)

					# Je déclare la session.
					request.session['util'] = {
						'id_util' : obj_util.id_util, 'n_util' : obj_util.n_util, 'pren_util' : obj_util.pren_util
					}

					# J'affiche le message de succès.
					reponse = HttpResponse(
						json.dumps({ 'success' : 'Bienvenue sur STYX !', 'redirect' : reverse('index') }), 
						content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs du formulaire.
					reponse = HttpResponse(json.dumps(f_id.errors), content_type = 'application/json')

			# Je traite le cas lié à la soumission du formulaire de réinitialisation du mot de passe.
			if get_action == 'oublier-mdp' :

				# Je vérifie la validité du formulaire de réinitialisation du mot de passe.
				f_oub_mdp = OublierMotDePasse(request.POST)

				if f_oub_mdp.is_valid() :

					# Je récupère la donnée du formulaire valide.
					cleaned_data = f_oub_mdp.cleaned_data
					v_courr_util = cleaned_data['zs_courr_util']

					# J'envoie un mail au courriel renseigné.
					# [TODO]

					# J'affiche le message de succès.
					reponse = HttpResponse(
						json.dumps({ 
							'success' : 'Un email a été envoyé à {0}.'.format(v_courr_util),
							'redirect' : reverse('index')
						}), 
						content_type = 'application/json'
					)
					
				else :

					# J'affiche les erreurs du formulaire.
					reponse = HttpResponse(json.dumps(f_oub_mdp.errors), content_type = 'application/json')

	return reponse

'''
Cette vue permet d'afficher la page principale dès la fermeture de la session active.
request : Objet requête
'''
@verif_acces
def deconnecter(request) :

	''' Imports '''
	from django.http import HttpResponse
	from django.shortcuts import redirect

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je vide les variables de session si la session est active.
		if 'util' in request.session :
			for une_cle in list(request.session.keys()) :
				del request.session[une_cle]

		# Je suis redirigé vers la page principale.
		reponse = redirect('index')

	return reponse

'''
Cette vue permet d'afficher la page de consultation du compte utilisateur.
request : Objet requête
'''
@verif_acces
def consulter_compte(request) :

	''' Imports '''
	from django.http import HttpResponse
	from django.shortcuts import render

	reponse = HttpResponse()

	if request.method == 'GET' :

		# J'affiche le template.
		reponse = render(
			request,
			'./autres/gestion_compte/consulter_compte.html',
			{ 'title' : 'Consulter mon compte' }
		)

	return reponse