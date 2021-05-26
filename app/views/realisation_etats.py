#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.decorators import *
from app.forms.realisation_etats import FiltrerDossiers
from app.forms.realisation_etats import FiltrerPrestations
from app.functions import alim_ld
from app.functions import datatable_reset
from app.functions import get_thumbnails_menu
from django.http import HttpResponse
from django.shortcuts import render
from bs4 import BeautifulSoup
import json

'''
Cette vue permet d'afficher le menu principal du module de réalisation d'états.
request : Objet requête
'''
@verif_acc
def index(request) :
	output = HttpResponse()

	if request.method == 'GET' :

		# J'affiche le template.
		output = render(request, './realisation_etats/main.html', {
			'menu' : get_thumbnails_menu('real_etats', 2, request), 'title' : 'Réalisation d\'états' }
		)

	return output

'''
Affichage du formulaire de réalisation d'un état "dossier" ou traitement d'une requête quelconque
request : Objet "requête"
_gby : Regroupement ou sélection de dossiers ?
'''
@verif_acc
def filtr_doss(request, _gby) :

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_filtr_doss = 'FiltrerDossiers'

	if request.method == 'GET' :

		# Initialisation de la variable "historique"
		request.session['filtr_doss'] = []

		# Initialisation du formulaire et de ses attributs
		form_filtr_doss = FiltrerDossiers(prefix = pref_filtr_doss, kw_gby = _gby)

		# Définition de l'attribut <title/>
		if _gby == False :
			title = 'Réalisation d\'états en sélectionnant des dossiers'
		else :
			title = 'Réalisation d\'états en regroupant des dossiers'

		# Affichage du template
		output = render	(request, './realisation_etats/filtr_doss.html', {
			'dtab_filtr_doss' : form_filtr_doss.get_datatable(request)['table'],
			'form_filtr_doss' : form_filtr_doss.get_form(request),
			'title' : title
		})

	else :
		if 'action' in request.GET and request.GET['action'] == 'alimenter-listes' :

			# Gestion d'affichage des listes déroulantes des axes, des sous-axes et des actions
			output = HttpResponse(json.dumps(alim_ld(request)), content_type = 'application/json')

		else :

			# Soumission du formulaire
			form_filtr_doss = FiltrerDossiers(
				request.POST,
				prefix = pref_filtr_doss,
				kw_gby = _gby,
				kw_progr = request.POST.get('FiltrerDossiers-id_progr'),
				kw_axe = request.POST.get('FiltrerDossiers-zl_axe'),
				kw_ss_axe = request.POST.get('FiltrerDossiers-zl_ss_axe')
			)

			# Rafraîchissement de la datatable ou affichage des erreurs
			if form_filtr_doss.is_valid() :

				# Préparation des paramètres de la fonction datatable_reset
				dtab = form_filtr_doss.get_datatable(request)
				bs = BeautifulSoup(dtab['table'])
				if _gby == True :
					output = HttpResponse(json.dumps({ 'success' : {
						'elements' : [['#t_regr_doss', dtab['table']]],
						'new_datatables' : [['regr_doss', { 'number' : ['LAST:' + str(dtab['len_numbers'])] }]]
					}}), content_type = 'application/json')
				else :
					output = datatable_reset(dtab['table'], {
						'elements' : [['#za_tfoot_select_doss', str(bs.find('tfoot', id = 'za_tfoot_select_doss'))]]
					})
			else :

				output = HttpResponse(json.dumps({
					'{0}-{1}'.format(pref_filtr_doss, cle) : val for cle, val in form_filtr_doss.errors.items()
				}), content_type = 'application/json')


	return output

'''
Affichage du formulaire de réalisation d'un état "prestation" ou traitement d'une requête quelconque
_req : Objet "requête"
_gby : Regroupement ou sélection de prestations ?
'''
@verif_acc
def filtr_prest(_req, _gby) :

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_filtr_prest = 'FiltrerPrestations'

	if _req.method == 'GET' :

		# Initialisation de la variable "historique"
		_req.session['filtr_prest'] = []

		# Initialisation du formulaire et de ses attributs
		form_filtr_prest = FiltrerPrestations(prefix = pref_filtr_prest, kw_gby = _gby)

		# Définition de l'attribut <title/>
		if _gby == False :
			title = 'Réalisation d\'états en sélectionnant des prestations'
		else :
			title = 'Réalisation d\'états en regroupant des prestations'

		# Affichage du template
		output = render(_req, './realisation_etats/filtr_prest.html', {
			'dtab_filtr_prest' : form_filtr_prest.get_datatable(_req),
			'form_filtr_prest' : form_filtr_prest.get_form(_req),
			'title' : title
		})

	else :
		if 'action' in _req.GET and _req.GET['action'] == 'alimenter-listes' :

			# Gestion d'affichage des listes déroulantes des axes, des sous-axes et des actions
			output = HttpResponse(json.dumps(alim_ld(_req)), content_type = 'application/json')

		else :

			# Soumission du formulaire
			form_filtr_prest = FiltrerPrestations(
				_req.POST,
				prefix = pref_filtr_prest,
				kw_gby = _gby,
				kw_progr = _req.POST.get('FiltrerPrestations-zl_progr'),
				kw_axe = _req.POST.get('FiltrerPrestations-zl_axe'),
				kw_ss_axe = _req.POST.get('FiltrerPrestations-zl_ss_axe')
			)

			# Rafraîchissement de la datatable ou affichage des erreurs
			if form_filtr_prest.is_valid() :

				# Préparation des paramètres de la fonction datatable_reset
				dtab = form_filtr_prest.get_datatable(_req)
				bs = BeautifulSoup(dtab)
				if _gby == True :
					dico = {
						'elements' : [['#za_tfoot_regr_prest', str(bs.find('tfoot', id = 'za_tfoot_regr_prest'))]]
					}
				else :
					dico = {
						'elements' : [['#za_tfoot_select_prest', str(bs.find('tfoot', id = 'za_tfoot_select_prest'))]]
					}

				output = datatable_reset(dtab, dico)
			else :
				output = HttpResponse(json.dumps({
					'{0}-{1}'.format(pref_filtr_prest, cle) : val for cle, val in form_filtr_prest.errors.items()
				}), content_type = 'application/json')

	return output

'''
Etat d'avancement d'un programme (V2 réalisé par le SMMAR)
rq : Objet "requête"
'''
@verif_acc
def avancement_programme(rq) :

	# Imports
	from app.forms.realisation_etats import AvancementProgramme

	output = None

	if rq.method == 'GET' :

		# Instanciation d'un formulaire
		form = AvancementProgramme(prefix = 'AvancementProgramme')

		# Affichage du template
		output = render	(rq, './realisation_etats/avancement_programme_v2.html', {
			'datatable' : form.get_datatable(),
			'form' : form.get_form(rq = rq),
			'title' : 'Réalisation d\'états - Etat d\'avancement d\'un programme'
		})

	else :
		if rq.GET.get('action') == 'alimenter-listes' :

			# Gestion d'affichage des listes déroulantes des axes, des sous-axes et des actions
			output = HttpResponse(json.dumps(alim_ld(rq)), content_type = 'application/json')

		else :

			# Soumission du formulaire
			form = AvancementProgramme(
				rq.POST,
				prefix = 'AvancementProgramme',
				kw_prg = rq.POST.get('AvancementProgramme-zl_progr'),
				kw_axe = rq.POST.get('AvancementProgramme-zl_axe'),
				kw_ssa = rq.POST.get('AvancementProgramme-zl_ss_axe')
			)

			# Si le formulaire soumis est valide, alors rafraîchissement de la table de données
			if form.is_valid() :
				output = datatable_reset(form.get_datatable())
			# Sinon, affichage des erreurs
			else :
				output = HttpResponse(json.dumps({
					'AvancementProgramme-' + key : val for key, val in form.errors.items()
				}), content_type = 'application/json')

	return output