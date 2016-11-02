#!/usr/bin/env python
#-*- coding: utf-8

'''
Cette vue permet d'afficher le template relatif à une erreur 403.
request : Objet requête
'''
def handler_403(request) :

	''' Imports '''
	from django.shortcuts import render_to_response
	from django.template import RequestContext

	reponse = render_to_response(
		'./autres/handlers/403.html',
		RequestContext(
			request,
			{ 'title' : 'Erreur 403' },
		)
	)

	reponse.status_code = 403

	return reponse

'''
Cette vue permet d'afficher le template relatif à une erreur 404.
request : Objet requête
'''
def handler_404(request) :

	''' Imports '''
	from django.shortcuts import render_to_response
	from django.template import RequestContext

	reponse = render_to_response(
		'./autres/handlers/404.html',
		RequestContext(
			request,
			{ 'title' : 'Erreur 404' },
		)
	)

	reponse.status_code = 404

	return reponse