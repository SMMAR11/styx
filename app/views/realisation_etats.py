#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.decorators import *

'''
Cette vue permet d'afficher le menu principal du module de réalisation d'états.
request : Objet requête
'''
@verif_acc
def index(request) :

	# Imports
	from django.http import HttpResponse
	from django.shortcuts import render

	output = HttpResponse()

	if request.method == 'GET' :

		# J'affiche le template.
		output = render(request, './realisation_etats/main.html', { 'title' : 'Réalisation d\'états' })

	return output