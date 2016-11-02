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
		if 'menu_doss' in request.session :
			reponse = request.session['menu_doss']
			del request.session['menu_doss']
	else :
		raise PermissionDenied

	return HttpResponse(reponse)