#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from django.views.decorators.csrf import csrf_exempt

'''
Cette vue permet de savoir l'onglet actif du menu des dossiers.
request : Objet requête
'''
@csrf_exempt
def retourner_onglet_actif(request) :

	''' Imports '''
	from django.core.exceptions import PermissionDenied
	from django.http import HttpResponse
	
	reponse = '#ong_caracteristiques'

	if request.method == 'POST' :
		if 'app-nav' in request.session :
			reponse = request.session['app-nav']
			del request.session['app-nav']
	else :
		raise PermissionDenied

	return HttpResponse(reponse)

'''
Cette vue permet l'autocomplétion d'une zone de saisie à partir de données stockées dans la base de données.
request : Objet requête
'''
@csrf_exempt
def autocompleter(request) :

	''' Imports '''
	from app.models import TPrestataire
	from django.http import HttpResponse
	import json

	reponse = HttpResponse()

	if request.method == 'GET' :
		if 'action' in request.GET and 'q' in request.GET :

			# Je stocke la valeur de chaque paramètre "GET".
			get_action = request.GET['action']
			req = request.GET['q']
			
			# Je traite le cas où l'autocomplétion porte sur les numéros SIRET.
			if get_action == 'lister-siret' :

				status = True

				# Je prépare le tableau des prestataires.
				tab_org_prest = []
				for un_org_prest in TPrestataire.objects.all() :
					if req in un_org_prest.siret_org_prest :
						tab_org_prest.append({
							'siret_org_prest' : un_org_prest.siret_org_prest,
							'n_org' : un_org_prest.n_org,
						})

				if len(tab_org_prest) == 0 :
					status = False

				# J'envoie le tableau des prestataires.
				reponse = HttpResponse(
					json.dumps({
						'status' : status,
						'error' : None,
						'data' : {
							'org_prest' : tab_org_prest
						}
					}),
					content_type = 'application/json'
				)

	return reponse