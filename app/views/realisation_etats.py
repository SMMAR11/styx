#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.decorators import *

'''
Cette vue permet d'afficher le menu du module de réalisation des états.
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
			'./realisation_etats/main.html',
			{ 'title' : 'Réalisation d\'états' }
		)

	return reponse

'''
Cette vue permet soit d'afficher le formulaire de sélection des dossiers, soit de le traiter.
request : Objet requête
'''
@nett_form
@verif_acces
def selectionner_dossiers(request) :

	''' Imports '''
	from app.forms.realisation_etats import SelectionnerDossiers
	from app.functions import alim_liste
	from app.functions import chang_form_dt
	from app.functions import conv_none
	from app.functions import float_to_int
	from app.functions import init_form
	from app.functions import integer
	from app.functions import nett_val
	from app.functions import reecr_dt
	from app.functions import suppr_doubl_dtable
	from app.models import TAction, TAxe, TDossier, TRegroupementMoa, TSousAxe
	from django.core.urlresolvers import reverse
	from django.db.models import Q
	from django.http import HttpResponse
	from django.shortcuts import render
	from functools import reduce
	from itertools import chain
	import json
	import operator

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je déclare un tableau de session qui contiendra l'ensemble des dossiers sélectionnés après X recherches (avec
		# doublons).
		request.session['doss_select'] = []

		# J'instancie un objet "formulaire".
		f_select_doss = SelectionnerDossiers()

		# J'affiche le template.
		reponse = render(
			request,
			'./realisation_etats/selectionner_dossiers.html',
			{ 'f1' : init_form(f_select_doss), 'title' : 'Réalisation d\'états en sélectionnant des dossiers' }
		)

	else :
		if 'action' in request.GET :
			if request.GET['action'] == 'filtrer-dossiers' :

				# Je vérifie la validité du formulaire de sélection des dossiers.
				f_select_doss = SelectionnerDossiers(request.POST)

				# Je rajoute un choix valide pour certaines listes déroulantes (prévention d'erreurs).
				post_progr = request.POST.get('zld_progr')
				post_axe = request.POST.get('zld_axe')
				post_ss_axe = request.POST.get('zld_ss_axe')
				post_act = request.POST.get('zld_act')

				axe_valide = False
				try :
					TAxe.objects.get(id_progr = post_progr, num_axe = post_axe)
					axe_valide = True
				except :
					if post_axe == 'D' or post_axe == 'DBP' :
						axe_valide = True
					else :
						pass

				if axe_valide == True :
					f_select_doss.fields['zld_axe'].choices = [(post_axe, post_axe)]

				ss_axe_valide = False
				try :
					TSousAxe.objects.get(id_axe = '{0}_{1}'.format(post_progr, post_axe), num_ss_axe = post_ss_axe)
					ss_axe_valide = True
				except :
					if post_ss_axe == 'D' or post_ss_axe == 'DBP' :
						ss_axe_valide = True
					else :
						pass

				if ss_axe_valide == True :
					f_select_doss.fields['zld_ss_axe'].choices = [(post_ss_axe, post_ss_axe)]

				act_valide = False
				try :
					TAction.objects.get(
						id_ss_axe = '{0}_{1}_{2}'.format(post_progr, post_axe, post_ss_axe), num_act = post_act
					)
					act_valide = True
				except :
					if post_act == 'D' or post_act == 'DBP' :
						act_valide = True
					else :
						pass

				if act_valide == True :
					f_select_doss.fields['zld_act'].choices = [(post_act, post_act)]

				if f_select_doss.is_valid() :

					# Je récupère et nettoie les données du formulaire valide.
					cleaned_data = f_select_doss.cleaned_data
					v_tab_org_moa = request.POST.getlist('cbsm_org_moa')
					v_progr = integer(cleaned_data['zld_progr'])
					v_axe = integer(cleaned_data['zld_axe'])
					v_ss_axe = integer(cleaned_data['zld_ss_axe'])
					v_act = integer(cleaned_data['zld_act'])
					v_nat_doss = integer(cleaned_data['zl_nat_doss'])
					v_dt_deb_delib_moa_doss = chang_form_dt(nett_val(cleaned_data['zd_dt_deb_delib_moa_doss']))
					v_dt_fin_delib_moa_doss = chang_form_dt(nett_val(cleaned_data['zd_dt_fin_delib_moa_doss']))
					v_av_cp = integer(cleaned_data['zl_av_cp'])
					v_mont_ht_doss_min = nett_val(cleaned_data['zs_mont_ht_doss_min'])
					v_mont_ht_doss_max = nett_val(cleaned_data['zs_mont_ht_doss_max'])
					v_doss_dep_nn_sold = cleaned_data['cb_doss_dep_nn_sold']
					v_int_doss_ass = cleaned_data['cb_int_doss_ass']
					v_ajout_select_exist = cleaned_data['cb_ajout_select_exist']

					# Je déclare des tableaux qui stockeront les conditions de la requête SQL.
					tab_or = []
					tab_and = {}

					# J'empile les tableaux des conditions.
					for i in range(0, len(v_tab_org_moa)) :

						# Je tente de convertir la valeur du maître d'ouvrage courant en un nombre entier. Si celle-ci n'est
						# pas un nombre entier, alors elle prend -1.
						v_org_moa = integer(v_tab_org_moa[i])

						if v_org_moa > -1 :
							tab_or.append(Q(**{ 'id_org_moa' : v_org_moa }))
							for un_couple_moa in TRegroupementMoa.objects.filter(id_org_moa_fil = v_org_moa) :
								tab_or.append(Q(**{ 'id_org_moa' : un_couple_moa.id_org_moa_anc }))
							
					if v_progr > -1 :
						tab_and['id_progr'] = v_progr

					if v_axe > -1 :
						tab_and['num_axe'] = v_axe

					if v_ss_axe > -1 :
						tab_and['num_ss_axe'] = v_ss_axe

					if v_act > -1 :
						tab_and['num_act'] = v_act

					if v_nat_doss > -1 :
						tab_and['id_nat_doss'] = v_nat_doss

					if v_dt_deb_delib_moa_doss is not None :
						tab_and['dt_delib_moa_doss__gte'] = v_dt_deb_delib_moa_doss

					if v_dt_fin_delib_moa_doss is not None :
						tab_and['dt_delib_moa_doss__lte'] = v_dt_fin_delib_moa_doss

					if v_av_cp > -1 :
						tab_and['id_av_cp'] = v_av_cp

					if v_mont_ht_doss_min is not None :
						tab_and['mont_ht_doss__gte'] = v_mont_ht_doss_min

					if v_mont_ht_doss_max is not None :
						tab_and['mont_ht_doss__lte'] = v_mont_ht_doss_max

					if len(tab_or) == 0 :
						tab_or.append(Q(**{ 'id_org_moa' : -1 }))

					les_doss = TDossier.objects.filter(reduce(operator.or_, tab_or), **tab_and)

					# Je retire les dossiers soldés si et seulement l'option associée est cochée.
					if v_doss_dep_nn_sold == True :
						les_doss = les_doss.exclude(id_av__int_av = 'Soldé')

					# J'ajoute les dossiers d'une même famille si et seulement si l'option associée est cochée.
					if v_int_doss_ass == True :

						# Je récupère la famille de chaque dossier.
						tab_fam = []
						for un_doss in les_doss :
							tab_fam.append(un_doss.id_fam.id_fam)

						# Je supprime les doublons de famille.
						tab_fam = list(set(tab_fam))

						# Je déclare un tableau qui stockera les conditions de la requête SQL et je l'empile.
						tab_or = []
						for i in range(0, len(tab_fam)) :
							tab_or.append(Q(**{ 'id_fam' : int(tab_fam[i]) }))

						if len(tab_or) == 0 :
							tab_or.append(Q(**{ 'id_fam' : -1 }))

						# Je récupère les dossiers sélectionnés (+ les dossiers associés).
						les_doss = TDossier.objects.filter(reduce(operator.or_, tab_or))

					# Je trie les dossiers sélectionnés.
					les_doss = les_doss.order_by('-dt_delib_moa_doss', 'num_doss')

					# J'empile le tableau des dossiers sélectionnés.
					tab_doss_filtr = []
					for un_doss in les_doss :
						tab_doss_filtr.append([
							conv_none(un_doss.num_doss),
							conv_none(un_doss.int_doss),
							conv_none(un_doss.id_org_moa.id_org_moa.n_org),
							conv_none(reecr_dt(un_doss.dt_delib_moa_doss)),
							conv_none(un_doss.id_progr.int_progr),
							conv_none(un_doss.id_nat_doss.int_nat_doss),
							conv_none(float_to_int(un_doss.mont_ht_doss)),
							'<a href="{0}" class="bt-consulter pull-right"></a>'.format(
								reverse('consulter_dossier', args = [un_doss.id_doss])
							)
						])

					# Je reviens à l'état initial lorsque l'option associée est décochée.
					if v_ajout_select_exist == False :
						request.session['doss_select'] = []
					else :
						request.session['doss_select'] = [request.session['doss_select']]

					# J'empile le tableau de session des dossiers sélectionnés après X recherches (avec doublons).
					request.session['doss_select'].append(tab_doss_filtr)

					# Je supprime les doublons des dossiers sélectionnés.
					request.session['doss_select'] = suppr_doubl_dtable(request.session['doss_select'])
							
					# J'envoie la liste des dossiers sélectionnés.
					reponse = HttpResponse(
						json.dumps({ 'success' : request.session['doss_select'] }), content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs du formulaire.
					reponse = HttpResponse(json.dumps(f_select_doss.errors), content_type = 'application/json')

		else :

			# J'alimente les listes déroulantes des axes, des sous-axes, des actions et des types de dossiers.
			reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

	return reponse

'''
Cette vue permet soit de générer un état en sélectionnant les dossiers.
request : Objet requête
p_complet : Export complet ou non ?
'''
@verif_acces
def exporter_csv_selectionner_dossiers(request, p_complet) :

	''' Imports '''
	from app.functions import conv_none, crypt_val, float_to_int, reecr_dt
	from app.models import TDossier
	from django.http import HttpResponse
	from django.shortcuts import redirect
	from styx.settings import MEDIA_ROOT, MEDIA_URL
	import csv
	import time

	reponse = HttpResponse()

	if request.method == 'GET' :

		# J'initialise le nom du fichier CSV ainsi que le chemin de destination.
		n_fich = crypt_val('{0}-{1}'.format(request.user.id, time.strftime('%d%m%Y%H%M%S')))
		chem_fich = '{0}/temp/{1}.csv'.format(MEDIA_ROOT, n_fich)

		# J'ouvre le fichier CSV.
		with open(chem_fich, 'w', newline = '') as fich :

			# Je définis le droit d'écriture ainsi que le délimiteur.
			writer = csv.writer(fich, delimiter = ';')

			if 'doss_select' in request.session :

				# J'importe l'ensemble des dossiers sélectionnés après X recherches (sans doublons).
				tab_lg = request.session['doss_select']

				if p_complet == False :

					# J'écris l'en-tête du fichier CSV.
					writer.writerow((
						'numero_du_dossier',
						'intitule_du_dossier',
						'moa_du_dossier',
						'date_de_deliberation_au_moa_du_dossier',
						'programme_du_dossier',
						'nature_du_dossier',
						'montant_ht_du_dossier'
					))

					# Je parcours la datatable afin de pouvoir compléter le fichier CSV.
					for i in range(0, len(tab_lg)) :
						lg = tab_lg[i]
						tab_cell_lg = []
						for j in range(0, len(lg) - 1) :
							cell = lg[j]
							tab_cell_lg.append(cell)

						# J'écris une ligne du fichier CSV.
						writer.writerow(tab_cell_lg)

				else :

					for i in range(0, len(tab_lg)) :

						# Je récupère le numéro du dossier courant.
						v_num_doss = tab_lg[i][0]

						# [TODO] (numéro du dossier associé...) 
						obj_doss = TDossier.objects.get(num_doss = v_num_doss)

						tab_cell_lg = [
							conv_none(obj_doss.comm_doss),
							conv_none(obj_doss.descr_doss),
							conv_none(reecr_dt(obj_doss.dt_av_cp_doss)),
							conv_none(reecr_dt(obj_doss.dt_delib_moa_doss)),
							conv_none(obj_doss.int_doss),
							conv_none(float_to_int(obj_doss.mont_ht_doss)),
							conv_none(float_to_int(obj_doss.mont_ttc_doss)),
							conv_none(obj_doss.num_doss),
							conv_none(obj_doss.id_nat_doss.int_nat_doss),
							conv_none(obj_doss.id_type_doss.int_type_doss),
							conv_none(obj_doss.num_act),
							conv_none(obj_doss.num_ss_axe),
							conv_none(obj_doss.num_axe),
							conv_none(obj_doss.id_progr.int_progr),
							conv_none(obj_doss.id_av_cp.int_av_cp),
							'{0} {1}'.format(conv_none(obj_doss.id_techn.n_techn), conv_none(obj_doss.id_techn.pren_techn)),
							conv_none(obj_doss.id_org_moa.id_org_moa.n_org),
							conv_none(obj_doss.id_av.int_av)
						]

						# J'écris une ligne du fichier CSV.
						writer.writerow(tab_cell_lg)

			# Je ferme le fichier CSV.
			fich.close()

		# Je permets le téléchargement du fichier CSV produit.
		reponse = redirect('{0}/temp/{1}.csv'.format(MEDIA_URL, n_fich))

		return reponse