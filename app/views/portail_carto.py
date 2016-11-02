#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.decorators import *

'''
Cette vue permet d'afficher le menu du portail cartographique.
request : Objet requête
'''
@verif_acces
def index(request) :

	''' Imports '''
	from django.http import HttpResponse
	from django.shortcuts import render

	reponse = HttpResponse()

	if request.method == 'GET' :

		# J'affiche le template.
		reponse = render(
			request,
			'./portail_carto/main.html',
			{ 'title' : 'Portail cartographique' }
		)

	return reponse

@verif_acces
def consulter_carto(request, p_dossier) :

	''' Imports '''
	from app.models import TDossier
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404, render

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = get_object_or_404(TDossier, id_doss = p_dossier)

		# J'affiche le template.
		reponse = render(
			request,
			'./portail_carto/consulter_carto.html',
			{ 'title' : 'Consulter un objet géographique' }
		)

	return reponse