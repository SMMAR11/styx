#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.decorators import *
from django.views.decorators.csrf import csrf_exempt

'''
Cette vue permet d'afficher le menu principal du module de gestion des actions PGRE.
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
		output = render(request, './pgre/main.html', { 'title' : 'Gestion des actions PGRE' })

	return output

'''
Cette vue permet d'afficher la page de création d'une action PGRE ou de traiter une action.
request : Objet requête
'''
@verif_acc
@nett_f
@csrf_exempt
def cr_act_pgre(request) :

	# Imports
	from app.forms.pgre import GererActionPgre
	from app.functions import alim_ld
	from app.functions import dt_fr
	from app.functions import filtr_doss
	from app.functions import gen_t_ch_doss
	from app.functions import init_f
	from app.functions import init_fm
	from app.models import TInstancesConcertationPgreAtelierPgre
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = HttpResponse()

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_cr_act_pgre = GererActionPgre(prefix = 'GererActionPgre')

		# Je déclare un tableau qui stocke le contenu de certaines fenêtres modales.
		t_cont_fm = {
			'ch_doss' : gen_t_ch_doss(request)
		}

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('ch_doss', 'Choisir un dossier de correspondance', t_cont_fm['ch_doss']),
			init_fm('cr_act_pgre', 'Créer une action PGRE')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./pgre/cr_act_pgre.html',
			{ 'f_cr_act_pgre' : init_f(f_cr_act_pgre), 't_fm' : t_fm, 'title' : 'Créer une action PGRE' }
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois filtrer les ateliers selon l'instance de concertation choisie.
			if get_action == 'filtrer-ateliers' :

				try :

					# Je stocke les ateliers concernés par l'instance de concertation.
					qs_ic_pgre_atel_pgre = TInstancesConcertationPgreAtelierPgre.objects.filter(
						id_ic_pgre = request.POST.get('GererActionPgre-id_ic_pgre')
					).order_by('id_atel_pgre')

					t_atel_pgre = [(
						a.id_atel_pgre.int_atel_pgre,
						'''
						<input type="checkbox" class="pull-right" id="id_GererActionPgre-cbsm_atel_pgre_{0}" 
						name="GererActionPgre-cbsm_atel_pgre" value="{1}">
						'''.format(index, a.id_atel_pgre.pk)
					) for index, a in enumerate(qs_ic_pgre_atel_pgre)]

				except :
					t_atel_pgre = []

				# J'envoie le tableau des ateliers filtrés.
				output = HttpResponse(
					json.dumps({
						'bypass' : True, 
						'success' : { 'datatable' : t_atel_pgre, 'datatable_name' : 'ch_cbsm_atel_pgre' }
					}), content_type = 'application/json'
				)

			# Je traite le cas où je dois alimenter les listes déroulantes des axes, des sous-axes, des actions et des
			# types de dossiers.
			if get_action == 'alimenter-listes' :

				# J'affiche ou je cache certaines listes déroulantes selon les données qu'elles contiennent.
				output = HttpResponse(json.dumps(alim_ld(request)), content_type = 'application/json')

			# Je traite le cas où je dois filtrer les dossiers selon certains critères.
			if get_action == 'filtrer-dossiers' :

				# Je prépare le tableau des dossiers filtrés.
				t_doss = [(
					d.num_doss,
					'{0} - {1} - {2} - {3}'.format(d.id_nat_doss, d.id_type_doss, d.lib_1_doss, d.lib_2_doss),
					d.id_org_moa.n_org,
					dt_fr(d.dt_delib_moa_doss) or '-',
					'<span class="choose-icon pointer pull-right" title="Choisir le dossier"></span>'
				) for d in filtr_doss(request)]

				# J'envoie le tableau des dossiers filtrés.
				output = HttpResponse(
					json.dumps({ 'success' : { 'datatable' : t_doss }}), content_type = 'application/json'
				)

		else :

			# Je soumets le formulaire.
			f_cr_act_pgre = GererActionPgre(
				request.POST,
				request.FILES, 
				prefix = 'GererActionPgre',
				k_util = request.user,
				k_ic_pgre = request.POST.get('GererActionPgre-id_ic_pgre')
			)

			if f_cr_act_pgre.is_valid() :

				# Je créé la nouvelle instance TDossierPgre.
				o_nvelle_act_pgre = f_cr_act_pgre.save(commit = False)
				o_nvelle_act_pgre.save()

				# J'affiche le message de succès.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'L\'action PGRE n°{0} a été créée avec succès.'.format(o_nvelle_act_pgre),
						'redirect' : reverse('index')
					}}), 
					content_type = 'application/json'
				)

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_cr_act_pgre.errors.items() :
					t_err['GererActionPgre-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output