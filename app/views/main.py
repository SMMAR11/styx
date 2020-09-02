#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.decorators import *

'''
Cette vue permet d'afficher la page principale ou de traiter l'un des formulaires de celle-ci.
request : Objet requête
'''
def index(request) :

	# Imports
	from app.forms.main import Identifier
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import get_thumbnails_menu
	from django.contrib.auth import authenticate, login
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = HttpResponse()

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_id = Identifier()

		# Je déclare un tableau de fenêtres modales, dont le contenu diffère selon l'état de la session.
		if request.user.is_authenticated() :
			t_fm = []
		else :
			t_fm = [
				init_fm('id', 'Identification')
			]

		if request.user.is_authenticated() :
			title = 'Accueil'
		else :
			title = 'Identification'

		# J'affiche le template.
		output = render(
			request,
			'./main/main.html',
			{ 'f_id' : init_f(f_id), 'menu' : get_thumbnails_menu('__ALL__', 3), 't_fm' : t_fm, 'title' : title }
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			if get_action == 'identifier' :

				# Je soumets le formulaire.
				f_id = Identifier(request.POST)

				if f_id.is_valid() :

					# Je récupère les données du formulaire valide.
					cleaned_data = f_id.cleaned_data

					# Je déclare la session.
					login(request, authenticate(
						username = cleaned_data.get('zs_username'), password = cleaned_data.get('zs_password')
					))

					# J'affiche le message de succès.
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'Bienvenue sur STYX !', 'redirect' : reverse('index')
						}}),
						content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs.
					output = HttpResponse(json.dumps(f_id.errors), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page principale dès la fermeture de la session active.
request : Objet requête
'''
@verif_acc
def deconnect(request) :

	# Imports
	from django.contrib.auth import logout
	from django.http import HttpResponse
	from django.shortcuts import redirect

	output = HttpResponse()

	if request.method == 'GET' :

		# Je vide les variables de session.
		for c in list(request.session.keys()) :
			del request.session[c]

		# Je ferme la session.
		logout(request)

		# Je suis redirigé vers la page principale.
		output = redirect('index')

	return output

'''
Cette vue permet d'afficher la page de modification d'un compte utilisateur ou de traiter le formulaire de mise à jour
de celui-ci.
request : Objet requête
'''
@verif_acc
def modif_util(request) :

	# Imports
	from app.forms.main import GererUtilisateur
	from app.functions import init_f
	from app.functions import init_fm
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = HttpResponse()

	# Je pointe vers l'objet TUtilisateur relatif à l'utilisateur connecté.
	o_util = TUtilisateur.objects.get(pk = request.user.id)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_util = GererUtilisateur(instance = o_util)

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_util', 'Modifier son compte')
		]

		# J'affiche le template.
		output = render(
			request,
			'./main/modif_util.html',
			{ 'f_modif_util' : init_f(f_modif_util), 't_fm' : t_fm, 'title' : 'Modifier mon compte' }
		)

	else :

		# Je soumets le formulaire.
		f_modif_util = GererUtilisateur(request.POST, instance = o_util)

		if f_modif_util.is_valid() :

			# Je modifie l'instance TUtilisateur.
			o_util_modif = f_modif_util.save(commit = False)
			o_util_modif.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'L\'utilisateur {0} a été mis à jour avec succès.'.format(o_util.username),
					'redirect' : reverse('cons_util')
				}}),
				content_type = 'application/json'
			)

		else :

			# J'affiche les erreurs.
			output = HttpResponse(json.dumps(f_modif_util.errors), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de consultation d'un compte utilisateur.
request : Objet requête
'''
@verif_acc
def cons_util(request) :

	# Imports
	from app.functions import init_pg_cons
	from app.models import TDroit
	from app.models import TUtilisateur
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = HttpResponse()

	# Je pointe vers l'objet TUtilisateur.
	o_util = TUtilisateur.objects.get(pk = request.user.id)

	if request.method == 'GET' :

		# Je prépare les champs dont on veut seulement consulter.
		t_attrs_util = {
			'username' : { 'label' : 'Nom d\'utilisateur', 'value' : o_util.username },
			'last_name' : { 'label' : 'Nom', 'value' : o_util.last_name },
			'first_name' : { 'label' : 'Prénom', 'value' : o_util.first_name },
			'email' : { 'label' : 'Adresse électronique', 'value' : o_util.email },
			'id_org' : { 'label' : 'Organisme', 'value' : o_util.id_org },
			'tel_util' : { 'label' : 'Numéro de téléphone', 'value' : o_util.tel_util or '' },
			'port_util' : { 'label' : 'Numéro de téléphone portable', 'value' : o_util.port_util or '' }
		}

		# J'affiche le template.
		output = render(
			request,
			'./main/cons_util.html',
			{
				'qs_droit' : TDroit.objects.filter(id_util = o_util).order_by('id'),
				't_attrs_util' : init_pg_cons(t_attrs_util),
				'title' : 'Consulter mon compte',
				'u' : o_util
			}
		)

	return output

'''
Cette vue permet d'afficher la page relative à une erreur 403.
request : Objet requête
'''
def h_403(request) :

	# Imports
	from django.shortcuts import render_to_response
	from django.template import RequestContext

	# J'affiche le template.
	output = render_to_response(
		'./handlers/template.html',
		RequestContext(request, { 'message' : 'L\'accès à cette page est interdit.', 'title' : 'Erreur 403' })
	)
	output.status_code = 403

	return output

'''
Cette vue permet d'afficher la page relative à une erreur 404.
request : Objet requête
'''
def h_404(request) :

	# Imports
	from django.shortcuts import render_to_response
	from django.template import RequestContext

	# J'affiche le template.
	output = render_to_response(
		'./handlers/template.html',
		RequestContext(request, {
			'message' : 'La page que vous recherchez n\'existe pas ou a été déplacée.', 'title' : 'Erreur 404'
		})
	)
	output.status_code = 404

	return output

'''
Cette vue permet d'afficher la page relative à une erreur 500.
request : Objet requête
'''
def h_500(request) :

	# Imports
	from django.shortcuts import render_to_response
	from django.template import RequestContext

	# J'affiche le template.
	output = render_to_response(
		'./handlers/template.html',
		RequestContext(request, {
			'message' : 'Erreur interne du serveur.', 'title' : 'Erreur 500'
		})
	)
	output.status_code = 500

	return output

'''
Cette vue permet l'autocomplétion d'une zone de saisie à partir de données stockées dans la base de données.
request : Objet requête
'''
def autocompl(request) :

	# Imports
	from app.models import TPrestataire
	from django.db.models import Q
	from django.http import HttpResponse
	import json

	output = HttpResponse()

	if request.method == 'GET' :
		if 'action' in request.GET and 'q' in request.GET :

			# Je stocke la valeur des paramètres "GET" dont les clés sont "action" et "q".
			get_action = request.GET['action']
			get_q = request.GET['q']

			# Je traite le cas où je dois autocompléter la liste des prestataires dont la séquence saisie est contenue
			# dans leur numéro SIRET.
			if get_action == 'autocompleter-siret' :

				# J'initialise le tableau des prestataires.
				t_org_prest = []
				for p in TPrestataire.objects.all() :
					for elem in [p.siret_org_prest, p.n_org.lower()] :
						if get_q.lower() in elem :
							t_org_prest.append({
								'siret_org_prest' : p.siret_org_prest,
								'n_org' : p.n_org
							})

				# J'envoie le tableau des prestataires.
				output = HttpResponse(
					json.dumps({ 'data' : { 'org_prest' : t_org_prest }}), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page d'assistance technique.
request : Objet requête
'''
@verif_acc
def assist(request) :

	# Imports
	from django.http import HttpResponse
	from django.shortcuts import render

	output = HttpResponse()

	if request.method == 'GET' :

		# J'affiche le template.
		output = render(
			request,
			'./main/assist.html',
			{ 'title' : 'Assistance' }
		)

	return output

'''
Affichage des alertes
_req : Objet requête
'''
@verif_acc
def alert(_req) :

	# Import
	from app.context_processors import set_alerts
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		alerts = set_alerts(_req)

		# Affichage du template
		output = render(
			_req,
			'./main/alertes.html',
			{ 'alerts_list': alerts['alerts_list'], 'title' : 'Alertes' }
		)

	return output