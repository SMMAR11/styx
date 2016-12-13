#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.decorators import *
from django.views.decorators.csrf import csrf_exempt

'''
Gestion des caractéristiques
'''

'''
Cette vue permet d'afficher le menu principal du module de gestion des dossiers.
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
			'./gestion_dossiers/main.html',
			{ 'title' : 'Gestion des dossiers' }
		)

	return reponse

'''
Cette vue permet soit d'afficher la page de création d'un dossier, soit de traiter l'un des formulaires de la page. 
request : Objet requête
'''
@nett_form
@verif_acces
def creer_dossier(request) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererDossier
	from app.functions import alim_liste
	from app.functions import conv_none
	from app.functions import crypt_val
	from app.functions import filtr_doss
	from app.functions import gen_tabl_chois_doss
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import integer
	from app.functions import nett_val
	from app.functions import reecr_dt
	from app.functions import upload_fich
	from app.models import TAction
	from app.models import TAvancement
	from app.models import TAvisCp
	from app.models import TAxe
	from app.models import TDossier
	from app.models import TFamille
	from app.models import TInstanceConcertation
	from app.models import TMoa
	from app.models import TNatureDossier
	from app.models import TPgre
	from app.models import TProgramme
	from app.models import TRiviere
	from app.models import TRivieresDossier
	from app.models import TSousAxe
	from app.models import TTechnicien
	from app.models import TTypeDossier
	from app.models import TTypesProgrammesTypeDossier
	from app.models import TUnite
	from datetime import date
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	from styx.settings import MEDIA_ROOT
	import json
	import os
	import time

	reponse = HttpResponse()

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_creer_doss = GererDossier(prefix = 'CreerDossier')

		# Je déclare le contenu de certaines fenêtres modales.
		tab_cont_fm = {
			'choisir_dossier_associe' : gen_tabl_chois_doss(request, reverse('creer_dossier'))
		}

		# Je déclare un tableau de fenêtres modales.
		tab_fm = [
			init_fm('creer_dossier', 'Créer un dossier'),
			init_fm(
				'choisir_dossier_associe', 'Ajouter un dossier associé', tab_cont_fm['choisir_dossier_associe']
			)
		]

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/creer_dossier.html',
			{ 'f1' : init_form(f_creer_doss), 'les_fm' : tab_fm, 'title' : 'Créer un dossier' }
		)

	else :

		# Je vérifie le nombre de paramètres "GET" afin de savoir si je dois créer un dossier ou non.
		if len(request.GET) > 0 :

			if 'action' in request.GET :

				# Je traite le cas où je veux filtrer les dossiers dans la fenêtre de choix d'un dossier associé.
				if request.GET['action'] == 'filtrer-dossiers' :

					# Je stocke dans un tableau les dossiers filtrés.
					les_doss_filtr = filtr_doss(request)

					if les_doss_filtr['status'] == True :

						# Je prépare le contenu du tableau HTML des dossiers filtrés.
						tab_doss_filtr = []
						for un_doss in les_doss_filtr['data'] :
							tab_doss_filtr.append([
								conv_none(un_doss.num_doss),
								conv_none(un_doss.id_org_moa.id_org_moa.n_org),
								conv_none(reecr_dt(un_doss.dt_delib_moa_doss)) or 'En projet',
								'<span class="bt-choisir pointer pull-right" title="Choisir le dossier"></span>'
							])

						# Je mets à jour le tableau HTML des dossiers filtrés.
						reponse = HttpResponse(json.dumps(
							{ 'success' : tab_doss_filtr }), content_type = 'application/json'
						)

					else :

						# J'affiche les erreurs.
						reponse = HttpResponse(json.dumps(les_doss_filtr['data']), content_type = 'application/json')

			else :

				# J'alimente les listes déroulantes des axes, des sous-axes, des actions et des types de dossiers.
				reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

		else :

			# Je vérifie la validité du formulaire de création d'un dossier.
			f_creer_doss = GererDossier(request.POST, request.FILES)

			# Je rajoute un choix valide pour certaines listes déroulantes (prévention d'erreurs).
			post_progr = request.POST.get('zld_progr')
			post_axe = request.POST.get('zld_axe')
			post_ss_axe = request.POST.get('zld_ss_axe')
			post_act = request.POST.get('zld_act')
			post_type_doss = request.POST.get('zld_type_doss')

			axe_valide = False
			try :
				TAxe.objects.get(id_progr = post_progr, num_axe = post_axe)
				axe_valide = True
			except :
				if post_axe == 'D' :
					axe_valide = True
				else :
					pass

			if axe_valide == True :
				f_creer_doss.fields['zld_axe'].choices = [(post_axe, post_axe)]

			ss_axe_valide = False
			try :
				TSousAxe.objects.get(id_axe = '{0}_{1}'.format(post_progr, post_axe), num_ss_axe = post_ss_axe)
				ss_axe_valide = True
			except :
				if post_ss_axe == 'D' :
					ss_axe_valide = True
				else :
					pass

			if ss_axe_valide == True :
				f_creer_doss.fields['zld_ss_axe'].choices = [(post_ss_axe, post_ss_axe)]

			act_valide = False
			try :
				TAction.objects.get(
					id_ss_axe = '{0}_{1}_{2}'.format(post_progr, post_axe, post_ss_axe), num_act = post_act
				)
				act_valide = True
			except :
				if post_act == 'D' :
					act_valide = True
				else :
					pass

			if act_valide == True :
				f_creer_doss.fields['zld_act'].choices = [(post_act, post_act)]

			type_doss_valide = False
			try :
				TTypesProgrammesTypeDossier.objects.get(
					id_type_progr = TProgramme.objects.get(id_progr = post_progr).id_type_progr.id_type_progr,
					id_type_doss = post_type_doss
				)
				type_doss_valide = True
			except :
				if post_type_doss == 'D' :
					type_doss_valide = True
				else :
					pass

			if type_doss_valide == True :
				f_creer_doss.fields['zld_type_doss'].choices = [(post_type_doss, post_type_doss)]

			if f_creer_doss.is_valid() :

				# Je récupère et nettoie les données du formulaire valide.
				cleaned_data = f_creer_doss.cleaned_data
				v_doss_ass = nett_val(cleaned_data['za_doss_ass'])
				v_org_moa = nett_val(integer(cleaned_data['zl_org_moa']), True)
				v_progr = nett_val(integer(cleaned_data['zld_progr']), True) 
				v_axe = nett_val(integer(cleaned_data['zld_axe']), True)
				v_ss_axe = nett_val(integer(cleaned_data['zld_ss_axe']), True)
				v_act = nett_val(integer(cleaned_data['zld_act']), True)
				v_nat_doss = nett_val(integer(cleaned_data['zl_nat_doss']), True)
				v_type_doss = nett_val(integer(cleaned_data['zld_type_doss']), True)
				v_terr_doss = nett_val(cleaned_data['zs_terr_doss'])
				v_ld_doss = nett_val(cleaned_data['zs_ld_doss'])
				v_techn = nett_val(integer(cleaned_data['zl_techn']), True)
				v_mont_ht_doss = nett_val(cleaned_data['zs_mont_ht_doss'])
				v_mont_ttc_doss = nett_val(cleaned_data['zs_mont_ttc_doss'])
				v_av = nett_val(integer(cleaned_data['zl_av']), True)
				v_dt_delib_moa_doss = nett_val(cleaned_data['zd_dt_delib_moa_doss'])
				v_av_cp = nett_val(integer(cleaned_data['zl_av_cp']), True)
				v_dt_av_cp_doss = nett_val(cleaned_data['zd_dt_av_cp_doss'])
				v_obj_dds_doss = nett_val(cleaned_data['zu_chem_dds_doss'])
				v_comm_doss = nett_val(cleaned_data['zs_comm_doss'])
				v_quant_objs_pgre = nett_val(cleaned_data['zs_quant_objs_pgre'])
				v_quant_real_pgre = nett_val(cleaned_data['zs_quant_real_pgre'])
				v_unit = nett_val(integer(cleaned_data['zl_unit']), True)
				v_tab_riv = request.POST.getlist('cbsm_riv')
				v_inst_conc = nett_val(integer(cleaned_data['zl_inst_conc']), True)

				# Je prépare la valeur de chaque constituant du numéro de dossier.
				dim_progr = TProgramme.objects.get(id_progr = v_progr).dim_progr
				dim_org_moa = TMoa.objects.get(id_org_moa = v_org_moa).dim_org_moa
				seq_progr = str(TProgramme.objects.get(id_progr = v_progr).seq_progr).zfill(2)

				# Je stocke la valeur du numéro de dossier.
				v_num_doss = '{0}-{1}-{2}'.format(dim_progr, dim_org_moa, seq_progr)

				# Je vérifie l'existence d'un objet TDossier lié au dossier associé.
				obj_doss_ass = None
				try :
					obj_doss_ass = TDossier.objects.get(num_doss = v_doss_ass)
				except :
					pass

				# Je désigne la valeur de la famille selon la présence ou non d'un dossier associé.
				if obj_doss_ass is None :

					# Je créé un nouvel objet TFamille.
					obj_nvelle_fam = TFamille()
					obj_nvelle_fam.save()

					# Je récupère l'identifiant du nouvel objet TFamille.
					v_fam = obj_nvelle_fam.id_fam

				else :

					# J'inclus le futur objet TDossier dans une famille existante.
					v_fam = TDossier.objects.get(id_doss = obj_doss_ass.id_doss).id_fam.id_fam

				# J'initialise l'instance du nouveau dossier.
				obj_nv_doss = TDossier()
				if TProgramme.objects.get(id_progr = v_progr).int_progr == 'PGRE' :
					obj_nv_doss = TPgre()

				# Je remplis les données attributaires du nouvel objet.
				obj_nv_doss.comm_doss = v_comm_doss
				obj_nv_doss.dt_av_cp_doss = v_dt_av_cp_doss
				obj_nv_doss.dt_delib_moa_doss = v_dt_delib_moa_doss
				obj_nv_doss.dt_int_doss = date.today()
				obj_nv_doss.ld_doss = v_ld_doss
				obj_nv_doss.mont_ht_doss = v_mont_ht_doss
				obj_nv_doss.mont_ttc_doss = v_mont_ttc_doss
				obj_nv_doss.num_doss = v_num_doss
				obj_nv_doss.terr_doss = v_terr_doss
				obj_nv_doss.num_act = v_act
				obj_nv_doss.num_axe = v_axe
				obj_nv_doss.num_ss_axe = v_ss_axe
				obj_nv_doss.id_progr = TProgramme.objects.get(id_progr = v_progr)
				obj_nv_doss.id_av = TAvancement.objects.get(id_av = v_av)
				obj_nv_doss.id_av_cp = TAvisCp.objects.get(id_av_cp = v_av_cp)
				obj_nv_doss.id_doss_ass = obj_doss_ass
				obj_nv_doss.id_fam = TFamille.objects.get(id_fam = v_fam)
				obj_nv_doss.id_nat_doss = TNatureDossier.objects.get(id_nat_doss = v_nat_doss)
				obj_nv_doss.id_org_moa = TMoa.objects.get(id_org_moa = v_org_moa)
				obj_nv_doss.id_techn = TTechnicien.objects.get(id_techn = v_techn)
				obj_nv_doss.id_type_doss = TTypeDossier.objects.get(id_type_doss = v_type_doss)				

				# Je fais le lien avec la table t_pgre si et seulement si l'intitulé du programme renseigné est "PGRE".
				if TProgramme.objects.get(id_progr = v_progr).int_progr == 'PGRE' :

					# Je vérifie l'existence d'un objet TUnite.
					obj_unit = None
					try :
						obj_unit = TUnite.objects.get(id_unit = v_unit)
					except :
						pass

					# Je vérifie l'existence d'un objet TInstanceConcertation.
					obj_inst_conc = None
					try :
						obj_inst_conc = TInstanceConcertation.objects.get(id_inst_conc = v_inst_conc)
					except :
						pass

					# Je complète les données attributaires du nouvel objet.
					obj_nv_doss.quant_objs_pgre = v_quant_objs_pgre
					obj_nv_doss.quant_real_pgre = v_quant_real_pgre
					obj_nv_doss.id_inst_conc = obj_inst_conc
					obj_nv_doss.id_unit = obj_unit

				# Je créé un nouvel objet.
				obj_nv_doss.save()

				# Je parcours le tableau des rivières sélectionnées.
				for i in range(0, len(v_tab_riv)) :

					# Je tente de convertir la valeur de la rivière courante en un nombre entier. Si celle-ci n'est pas
					# un nombre entier, alors elle prend -1.
					v_riv = integer(v_tab_riv[i])

					# Je créé un nouvel objet TRivieresDossier.
					if v_riv > 0 :
						obj_nvelle_riv_doss = TRivieresDossier.objects.create(
							id_pgre = TPgre.objects.get(id_pgre = obj_nv_doss),
							id_riv = TRiviere.objects.get(id_riv = v_riv)
						)

				# J'incrémente le séquentiel du programme renseigné.
				obj_progr_doss = TProgramme.objects.get(id_progr = v_progr)
				obj_progr_doss.seq_progr = int(obj_progr_doss.seq_progr) + 1
				obj_progr_doss.save()

				# Je stocke le chemin vers le répertoire "dossiers" (racine).
				chem_rac = '{0}/{1}'.format(MEDIA_ROOT, 'dossiers')

				# Je stocke le chemin vers le répertoire destiné au nouveau dossier.
				chem_doss = '{0}/{1}'.format(chem_rac, obj_nv_doss.num_doss)

				# J'initialise le chemin de chaque dossier du répertoire destiné au nouveau dossier.
				tab_doss_rep = [
					chem_doss,
					'{0}/{1}'.format(chem_doss, 'caracteristiques'),
					'{0}/{1}'.format(chem_doss, 'plan_de_financement'),
					'{0}/{1}'.format(chem_doss, 'prestations'),
					'{0}/{1}'.format(chem_doss, 'factures'),
					'{0}/{1}'.format(chem_doss, 'demandes_de_versement'),
					'{0}/{1}'.format(chem_doss, 'reglementations'),
					'{0}/{1}'.format(chem_doss, 'photos'),
				]

				# J'initialise le répertoire du nouveau dossier.
				for i in range(0, len(tab_doss_rep)) :
					os.mkdir(tab_doss_rep[i])

				# J'uploade le fichier de DDS du dossier après sa création si et seulement un fichier PDF a été
				# spécifié.
				if v_obj_dds_doss is not None :

					# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
					n_fich = crypt_val('{0}-{1}'.format(
						request.user.id, time.strftime('%d%m%Y%H%M%S')
					))
					v_chem_dds_doss = 'dossiers/{0}/caracteristiques/{1}.pdf'.format(obj_nv_doss.num_doss, n_fich)

					# J'uploade le fichier.
					upload_fich(v_obj_dds_doss, v_chem_dds_doss)

					# Je mets à jour l'objet TDossier.
					obj_nv_doss.chem_dds_doss = v_chem_dds_doss
					obj_nv_doss.save()

				# J'affiche le message de succès.
				reponse = HttpResponse(
					json.dumps({
						'success' : 'Le dossier a été créé avec succès. Son numéro est {0}.'.format(
							obj_nv_doss.num_doss
						),
						'redirect' : reverse('consulter_dossier', args = [obj_nv_doss.id_doss])
					}),
					content_type = 'application/json'
				)

				# Je renseigne l'onglet actif après rechargement de la page.
				request.session['app-nav'] = '#ong_caracteristiques'

			else :

				# J'affiche les erreurs.
				reponse = HttpResponse(json.dumps(f_creer_doss.errors), content_type = 'application/json')

	return reponse

'''
Cette vue permet soit d'afficher la page de modification d'un dossier, soit de traiter l'un des formulaires de la page.
request : Objet requête
p_doss : Identifiant du dossier à modifier
'''
@nett_form
@verif_acces
def modifier_dossier(request, p_doss) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererDossier, GererDossier_Reglementation
	from app.functions import alim_liste
	from app.functions import conv_none
	from app.functions import crypt_val
	from app.functions import filtr_doss
	from app.functions import gen_tabl_chois_doss
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import integer
	from app.functions import nett_val
	from app.functions import reecr_dt
	from app.functions import upload_fich
	from app.models import TAction
	from app.models import TAvancement
	from app.models import TAvisCp
	from app.models import TAxe
	from app.models import TDossier
	from app.models import TFamille
	from app.models import TInstanceConcertation
	from app.models import TNatureDossier
	from app.models import TPgre
	from app.models import TProgramme
	from app.models import TRiviere
	from app.models import TRivieresDossier
	from app.models import TSousAxe
	from app.models import TTechnicien
	from app.models import TTypeDossier
	from app.models import TTypesProgrammesTypeDossier
	from app.models import TUnite
	from app.models import TDossierGeom
	from django.contrib.gis import geos
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404, render
	from styx.settings import MEDIA_ROOT, MEDIA_URL
	import json
	import os
	import time

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = get_object_or_404(TDossier, id_doss = p_doss)

		# Je déclare des objets "formulaire" permettant une future manipulation des champs.
		f_modif_doss = GererDossier(prefix = 'ModifierDossier', k_doss = obj_doss.id_doss)

		# Je déclare le contenu de certaines fenêtres modales.
		tab_cont_fm = {
			'choisir_dossier_associe' : gen_tabl_chois_doss(
				request, reverse('modifier_dossier', args = [obj_doss.id_doss])
			)
		}

		# Je déclare un tableau de fenêtres modales.
		tab_fm = [
			init_fm('modifier_dossier', 'Modifier un dossier'),
			init_fm(
				'choisir_dossier_associe', 'Modifier un dossier associé', tab_cont_fm['choisir_dossier_associe']
			)
		]

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/modifier_dossier.html',
			{
				'f1' : init_form(f_modif_doss),
				'le_doss' : obj_doss,
				'les_fm' : tab_fm,
				'title' : 'Modifier un dossier'
			}
		)

	else :

		# Je vérifie l'existence d'un objet TDossier.
		try :
			obj_doss = TDossier.objects.get(id_doss = p_doss)
		except :
			return HttpResponse()

		if 'action' in request.GET :

			# Je retiens le nom du paramètre "GET".
			get_action = request.GET['action']

			# Je traite le cas où je veux filtrer les dossiers dans la fenêtre de choix d'un dossier associé.
			if get_action == 'filtrer-dossiers' :

				# Je stocke dans un tableau les dossiers filtrés.
				les_doss_filtr = filtr_doss(request)

				if les_doss_filtr['status'] == True :

					# Je prépare le contenu du tableau HTML des dossiers filtrés.
					tab_doss_filtr = []
					for un_doss in les_doss_filtr['data'] :
						tab_doss_filtr.append([
							conv_none(un_doss.num_doss),
							conv_none(un_doss.id_org_moa.id_org_moa.n_org),
							conv_none(reecr_dt(un_doss.dt_delib_moa_doss)) or 'En projet',
							'<span class="bt-choisir pointer pull-right" title="Choisir le dossier"></span>'
						])

					# Je mets à jour le tableau HTML des dossiers filtrés.
					reponse = HttpResponse(json.dumps(
						{ 'success' : tab_doss_filtr }), content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs.
					reponse = HttpResponse(json.dumps(les_doss_filtr['data']), content_type = 'application/json')

			# Je traite le cas où je veux modifier l'onglet "Caractéristiques".
			elif get_action == 'modifier-caracteristiques' :

				# Je vérifie la validité du formulaire de modification d'un dossier.
				f_modif_doss = GererDossier(request.POST, request.FILES, k_modif = True)

				# Je rajoute un choix valide pour certaines listes déroulantes (prévention d'erreurs).
				post_progr = request.POST.get('zld_progr')
				post_axe = request.POST.get('zld_axe')
				post_ss_axe = request.POST.get('zld_ss_axe')
				post_act = request.POST.get('zld_act')
				post_type_doss = request.POST.get('zld_type_doss')
				post_techn = request.POST.get('zl_techn')

				axe_valide = False
				try :
					TAxe.objects.get(id_progr = post_progr, num_axe = post_axe)
					axe_valide = True
				except :
					if post_axe == 'D' :
						axe_valide = True
					else :
						pass

				if axe_valide == True :
					f_modif_doss.fields['zld_axe'].choices = [(post_axe, post_axe)]

				ss_axe_valide = False
				try :
					TSousAxe.objects.get(id_axe = '{0}_{1}'.format(post_progr, post_axe), num_ss_axe = post_ss_axe)
					ss_axe_valide = True
				except :
					if post_ss_axe == 'D' :
						ss_axe_valide = True
					else :
						pass

				if ss_axe_valide == True :
					f_modif_doss.fields['zld_ss_axe'].choices = [(post_ss_axe, post_ss_axe)]

				act_valide = False
				try :
					TAction.objects.get(
						id_ss_axe = '{0}_{1}_{2}'.format(post_progr, post_axe, post_ss_axe), num_act = post_act
					)
					act_valide = True
				except :
					if post_act == 'D' :
						act_valide = True
					else :
						pass

				if act_valide == True :
					f_modif_doss.fields['zld_act'].choices = [(post_act, post_act)]

				type_doss_valide = False
				try :
					TTypesProgrammesTypeDossier.objects.get(
						id_type_progr = TProgramme.objects.get(id_progr = post_progr).id_type_progr.id_type_progr,
						id_type_doss = post_type_doss
					)
					type_doss_valide = True
				except :
					if post_type_doss == 'D' :
						type_doss_valide = True
					else :
						pass

				if type_doss_valide == True :
					f_modif_doss.fields['zld_type_doss'].choices = [(post_type_doss, post_type_doss)]

				techn_valide = False
				try :
					TTechnicien.objects.get(id_techn = post_techn)
					techn_valide = True
				except :
					if post_techn == 'D' :
						techn_valide = True
					else :
						pass

				if techn_valide == True :
					f_modif_doss.fields['zl_techn'].choices = [(post_techn, post_techn)]

				if f_modif_doss.is_valid() :

					# Je récupère et nettoie les données du formulaire valide.
					cleaned_data = f_modif_doss.cleaned_data
					v_doss_ass = nett_val(cleaned_data['za_doss_ass'])
					v_org_moa = nett_val(integer(cleaned_data['zl_org_moa']), True)
					v_progr = nett_val(integer(cleaned_data['zld_progr']), True) 
					v_axe = nett_val(integer(cleaned_data['zld_axe']), True)
					v_ss_axe = nett_val(integer(cleaned_data['zld_ss_axe']), True)
					v_act = nett_val(integer(cleaned_data['zld_act']), True)
					v_nat_doss = nett_val(integer(cleaned_data['zl_nat_doss']), True)
					v_type_doss = nett_val(integer(cleaned_data['zld_type_doss']), True)
					v_terr_doss = nett_val(cleaned_data['zs_terr_doss'])
					v_ld_doss = nett_val(cleaned_data['zs_ld_doss'])
					v_techn = nett_val(integer(cleaned_data['zl_techn']), True)
					v_mont_ht_doss = nett_val(cleaned_data['zs_mont_ht_doss'])
					v_mont_ttc_doss = nett_val(cleaned_data['zs_mont_ttc_doss'])
					v_av = nett_val(integer(cleaned_data['zl_av']), True)
					v_dt_delib_moa_doss = nett_val(cleaned_data['zd_dt_delib_moa_doss'])
					v_av_cp = nett_val(integer(cleaned_data['zl_av_cp']), True)
					v_dt_av_cp_doss = nett_val(cleaned_data['zd_dt_av_cp_doss'])
					v_obj_dds_doss = nett_val(cleaned_data['zu_chem_dds_doss'])
					v_dds_doss = nett_val(cleaned_data['za_chem_dds_doss'])
					v_comm_doss = nett_val(cleaned_data['zs_comm_doss'])
					v_quant_objs_pgre = nett_val(cleaned_data['zs_quant_objs_pgre'])
					v_quant_real_pgre = nett_val(cleaned_data['zs_quant_real_pgre'])
					v_unit = nett_val(integer(cleaned_data['zl_unit']), True)
					v_tab_riv = request.POST.getlist('cbsm_riv')
					v_inst_conc = nett_val(integer(cleaned_data['zl_inst_conc']), True)

					# Je déclare le tableaux des données attributaires modifiées.
					tab_champs = {}

					# Je vérifie l'existence d'un objet TDossier lié au dossier associé.
					obj_doss_ass = None
					try :
						obj_doss_ass = TDossier.objects.get(num_doss = v_doss_ass)
					except :
						pass

					# Je désigne la valeur de la famille selon deux paramètres : la valeur de l'ancien dossier associé
					# et celle du nouveau dossier associé.
					if obj_doss_ass is None :

						if obj_doss.id_doss_ass is None :

							# Je traite le cas où la famille reste intacte.
							v_fam = obj_doss.id_fam.id_fam

						else :

							# Je créé un nouvel objet TFamille.
							obj_nvelle_fam = TFamille()
							obj_nvelle_fam.save()

							# Je récupère l'identifiant du nouvel objet TFamille.
							v_fam = obj_nvelle_fam.id_fam

					else :

						# J'inclus l'objet TDossier dans une famille existante.
						v_fam = TDossier.objects.get(id_doss = obj_doss_ass.id_doss).id_fam.id_fam

						# J'inclus également dans la même famille tous les dossiers dont l'objet TDossier est le
						# dossier associé.
						TDossier.objects.filter(id_doss_ass = obj_doss.id_doss).update(
							id_fam = TFamille.objects.get(id_fam = v_fam)
						)

					# Je déclare une variable stockant le chemin du fichier à effacer du serveur média.
					fich_a_eff = None

					if v_obj_dds_doss is None :
						if v_dds_doss is None :
							fich_a_eff = obj_doss.chem_dds_doss

							# Je mets à jour le chemin du fichier vers une valeur nulle car aucun fichier ne sera
							# uploadé.
							tab_champs['chem_dds_doss'] = None

					else :
						fich_a_eff = obj_doss.chem_dds_doss

						# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
						n_fich = crypt_val('{0}-{1}'.format(
							request.user.id, time.strftime('%d%m%Y%H%M%S')
						))
						v_chem_dds_doss = 'dossiers/{0}/caracteristiques/{1}.pdf'.format(obj_doss.num_doss, n_fich)

						# J'uploade le fichier.
						upload_fich(v_obj_dds_doss, v_chem_dds_doss)

						# Je mets à jour le chemin du fichier vers le chemin du nouveau fichier uploadé.
						tab_champs['chem_dds_doss'] = v_chem_dds_doss

					# Je tente d'effacer le fichier du serveur média si et seulement si la variable dédiée n'est pas
					# nulle.
					if fich_a_eff is not None :
						try :
							os.remove('{0}/{1}'.format(MEDIA_ROOT, fich_a_eff))
						except :
							pass

					# J'empile le tableau des données attributaires liées à un objet TDossier.
					tab_champs['comm_doss'] = v_comm_doss
					tab_champs['dt_av_cp_doss'] = v_dt_av_cp_doss
					tab_champs['dt_delib_moa_doss'] = v_dt_delib_moa_doss
					tab_champs['ld_doss'] = v_ld_doss
					tab_champs['mont_ht_doss'] = v_mont_ht_doss
					tab_champs['mont_ttc_doss'] = v_mont_ttc_doss
					tab_champs['terr_doss'] = v_terr_doss
					tab_champs['num_act'] = v_act
					tab_champs['num_ss_axe'] = v_ss_axe
					tab_champs['num_axe'] = v_axe
					tab_champs['id_av'] = TAvancement.objects.get(id_av = v_av)
					tab_champs['id_av_cp'] = TAvisCp.objects.get(id_av_cp = v_av_cp)
					tab_champs['id_doss_ass'] = obj_doss_ass
					tab_champs['id_fam'] = TFamille.objects.get(id_fam = v_fam)
					tab_champs['id_nat_doss'] = TNatureDossier.objects.get(id_nat_doss = v_nat_doss)
					tab_champs['id_techn'] = TTechnicien.objects.get(id_techn = v_techn)
					tab_champs['id_type_doss'] = TTypeDossier.objects.get(id_type_doss = v_type_doss)

					if TProgramme.objects.get(id_progr = obj_doss.id_progr.id_progr).int_progr == 'PGRE' :

						# Je vérifie l'existence d'un objet TUnite.
						obj_unit = None
						try :
							obj_unit = TUnite.objects.get(id_unit = v_unit)
						except :
							pass

						# Je vérifie l'existence d'un objet TInstanceConcertation.
						obj_inst_conc = None
						try :
							obj_inst_conc = TInstanceConcertation.objects.get(id_inst_conc = v_inst_conc)
						except :
							pass

						# J'empile le tableau des données attributaires liées à un objet TPgre.
						tab_champs['quant_objs_pgre'] = v_quant_objs_pgre
						tab_champs['quant_real_pgre'] = v_quant_real_pgre
						tab_champs['id_inst_conc'] = obj_inst_conc
						tab_champs['id_unit'] = obj_unit

					# Je mets à jour l'objet.
					obj_doss_modif = TDossier.objects.filter(id_doss = obj_doss.id_doss)
					if TProgramme.objects.get(id_progr = obj_doss.id_progr.id_progr).int_progr == 'PGRE' :
						obj_doss_modif = TPgre.objects.filter(id_doss = obj_doss.id_doss)
					obj_doss_modif.update(**tab_champs)

					# Je supprime tous les objets TRivieresDossier dont l'identifiant du dossier PGRE est celui du
					# dossier en cours de modification.
					TRivieresDossier.objects.filter(id_pgre = obj_doss.id_doss).delete()

					# Je parcours le tableau des rivières sélectionnées.
					for i in range(0, len(v_tab_riv)) :

						# Je tente de convertir la valeur de la rivière courante en un nombre entier. Si celle-ci n'est
						# pas un nombre entier, alors elle prend -1.
						v_riv = integer(v_tab_riv[i])

						# Je créé un nouvel objet TRivieresDossier.
						if v_riv > 0 :
							obj_nvelle_riv_doss = TRivieresDossier.objects.create(
								id_pgre = TPgre.objects.get(id_doss = obj_doss.id_doss),
								id_riv = TRiviere.objects.get(id_riv = v_riv)
							)

					# Je supprime les familles vierges.
					for une_fam in TFamille.objects.all() :
						try :
							une_fam.delete()
						except :
							pass

					# J'affiche le message de succès.
					reponse = HttpResponse(
						json.dumps({
							'success' : 'Le dossier a été mis à jour avec succès.',
							'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
						}),
						content_type = 'application/json'
					)

					# Je renseigne l'onglet actif après rechargement de la page.
					request.session['app-nav'] = '#ong_caracteristiques'

				else :

					# J'affiche les erreurs.
					reponse = HttpResponse(json.dumps(f_modif_doss.errors), content_type = 'application/json')

			# Je traite le cas où je veux modifier l'onglet "Réglementations".
			elif get_action == 'modifier-reglementations' :

				# Je vérifie la validité du formulaire de modification d'un dossier.
				f_modif_doss = GererDossier_Reglementation(request.POST)

				if f_modif_doss.is_valid() :

					# Je récupère et nettoie la donnée du formulaire valide.
					cleaned_data = f_modif_doss.cleaned_data
					v_comm_regl_doss = nett_val(cleaned_data['zs_comm_regl_doss'])

					# Je mets à jour l'objet TDossier.
					obj_doss.comm_regl_doss = v_comm_regl_doss
					obj_doss.save()

					# J'affiche le message de succès.
					reponse = HttpResponse(
						json.dumps({
							'success' : 'Le dossier a été mis à jour avec succès.',
							'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
						}),
						content_type = 'application/json'
					)

					# Je renseigne l'onglet actif après rechargement de la page.
					request.session['app-nav'] = '#ong_reglementations'

				else :

					# J'affiche les erreurs.
					reponse = HttpResponse(json.dumps(f_modif_doss.errors), content_type = 'application/json')

			# Je traite le cas où je veux modifier la géométrie des objets associés dossier.
			elif get_action == 'modifier-geom' :

				# On commence par supprimer toutes les géométries déjà existantes
				TDossierGeom.objects.filter(id_doss = obj_doss).delete()

				if request.POST['edit-geom'] :
					# Il peut y avoir plusieurs objets envoyés, on split pour boucler
					editgeom = request.POST['edit-geom'].split(';')

					# On créé un nouvel objet pour chaque géométrie
					for g in editgeom :

						geom = geos.GEOSGeometry(g)

						geom_doss = TDossierGeom(id_doss = obj_doss)

						if geom and isinstance(geom, geos.Polygon):
							geom_doss.geom_pol = geom

						if geom and isinstance(geom, geos.LineString):
							geom_doss.geom_lin = geom

						if geom and isinstance(geom, geos.Point):
							geom_doss.geom_pct = geom

						geom_doss.save()

				# J'affiche le message de succès.
				reponse = HttpResponse(
					json.dumps({
						'success' : 'La géométrie a été mise à jour avec succès.',
						'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
					}),
					content_type = 'application/json'
				)

				# Je renseigne l'onglet actif après rechargement de la page.
				request.session['app-nav'] = '#ong_cartographie'
		else :

			# J'alimente les listes déroulantes des axes, des sous-axes, des actions et des types de dossiers.
			reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

	return reponse

'''
Cette vue permet de supprimer un dossier.
request : Objet requête
p_doss : Identifiant du dossier à supprimer
'''
@csrf_exempt
@verif_acces
def supprimer_dossier(request, p_doss) :

	''' Imports '''
	from app.models import TDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from styx.settings import MEDIA_ROOT
	import json
	import shutil

	reponse = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = None
		try :
			obj_doss = TDossier.objects.get(id_doss = p_doss)
		except :
			return HttpResponse()

		# Je stocke le numéro de dossier de l'objet TDossier en cours de suppression.
		v_num_doss = obj_doss.num_doss

		# Je supprime l'objet TDossier.
		obj_doss.delete()

		# Je supprime le répertoire lié à l'objet TDossier.
		try :
			shutil.rmtree('{0}/dossiers/{1}'.format(MEDIA_ROOT, v_num_doss))
		except :
			pass

		# J'affiche le message de succès de la procédure de suppression d'une photo.
		reponse = HttpResponse(
			json.dumps({
				'success' : 'Le dossier a été supprimé avec succès.',
				'redirect' : reverse('choisir_dossier')
			}),
			content_type = 'application/json'
		)

	return reponse

'''
Cette vue permet d'afficher la page permettant de choisir un dossier.
request : Objet requête
'''
@nett_form
@verif_acces
def choisir_dossier(request) :

	''' Imports '''
	from app.forms.gestion_dossiers import ChoisirDossier
	from app.functions import alim_liste, conv_none, filtr_doss, init_form, reecr_dt
	from app.models import TDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	reponse = HttpResponse()

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_ch_doss = ChoisirDossier()

		# Je créé un tableau de dossiers.
		tab_doss = []
		for un_doss in TDossier.objects.all() :
			tab_doss.append({
				'id_doss' : un_doss.id_doss,
				'num_doss' : conv_none(un_doss.num_doss),
				'n_moa' : conv_none(un_doss.id_org_moa.id_org_moa.n_org),
				'dt_delib_moa_doss' : conv_none(reecr_dt(un_doss.dt_delib_moa_doss)) or 'En projet'
			})

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/choisir_dossier.html',
			{
				'f1' : init_form(f_ch_doss),
				'les_doss' : tab_doss,
				'title' : 'Choisir un dossier'
			}
		)

	else :
		if 'action' in request.GET :

			# Je traite le cas où je veux filtrer les dossiers.
			if request.GET['action'] == 'filtrer-dossiers' :

				# Je stocke dans un tableau les dossiers filtrés.
				les_doss_filtr = filtr_doss(request)

				if les_doss_filtr['status'] == True :

					# Je prépare le contenu du tableau HTML des dossiers filtrés.
					tab_doss_filtr = []
					for un_doss in les_doss_filtr['data'] :
						tab_doss_filtr.append([
							conv_none(un_doss.num_doss),
							conv_none(un_doss.id_org_moa.id_org_moa.n_org),
							conv_none(reecr_dt(un_doss.dt_delib_moa_doss)) or 'En projet',
							'<a href="{0}" class="bt-consulter pull-right" title="Consulter le dossier"></a>'.format(
								reverse('consulter_dossier', args = [un_doss.id_doss])
							)
						])

					# Je mets à jour le tableau HTML des dossiers filtrés.
					reponse = HttpResponse(json.dumps({ 'success' : tab_doss_filtr }), content_type = 'application/json')

				else :

					# J'affiche les erreurs.
					reponse = HttpResponse(json.dumps(les_doss_filtr['data']), content_type = 'application/json')

		else :

			# J'alimente les listes déroulantes des axes, des sous-axes et des actions.
			reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

	return reponse

'''
Cette vue permet d'afficher la page de consultation d'un dossier.
request : Objet requête
p_doss : Identifiant du dossier consulté
'''
@csrf_exempt
@nett_form
@verif_acces
def consulter_dossier(request, p_doss) :

	''' Imports '''
	from app.forms.gestion_dossiers import ChoisirPrestation
	from app.forms.gestion_dossiers import GererDemandeDeVersement
	from app.forms.gestion_dossiers import GererDossier_Reglementation
	from app.forms.gestion_dossiers import GererFacture
	from app.forms.gestion_dossiers import GererFinancement
	from app.forms.gestion_dossiers import GererPhoto
	from app.forms.gestion_dossiers import GererPrestation
	from app.forms.gestion_dossiers import RepartirMontantsPrestation
	from app.functions import aff_mess_suppr
	from app.functions import ajout_aven
	from app.functions import calc_interv
	from app.functions import conv_none
	from app.functions import float_to_int
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import init_pg_cons
	from app.functions import integer
	from app.functions import obt_pourc
	from app.functions import reecr_dt
	from app.functions import valid_mont
	from app.models import TArretesDossier
	from app.models import TAvenant
	from app.models import TDossier
	from app.models import TFacture
	from app.models import TInstanceConcertation
	from app.models import TPgre
	from app.models import TPhoto
	from app.models import TPrestation
	from app.models import TPrestationsDossier
	from app.models import TRivieresDossier
	from app.models import TTypeDeclaration
	from app.models import TUnite
	from app.models import TDossierGeom
	from django.contrib.gis import geos
	from app.sql_views import VFinancement
	from app.sql_views import VSuiviDossier
	from app.sql_views import VSuiviPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404, render
	from django.template.context_processors import csrf
	from styx.settings import MEDIA_URL
	import json

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = get_object_or_404(TDossier, id_doss = p_doss)

		# Récupération des géométries du dossier s'il y en a
		qs_geomdoss = TDossierGeom.objects.filter(id_doss = obj_doss)
		geom_doss = []
		for g in qs_geomdoss :
			if g.geom_pol is not None :
				la_geom = geos.GEOSGeometry(g.geom_pol)
			if g.geom_lin is not None :
				la_geom = geos.GEOSGeometry(g.geom_lin)
			if g.geom_pct is not None :
				la_geom = geos.GEOSGeometry(g.geom_pct)

			geom_doss.append(la_geom.geojson)
			
		# Récupération du/des type(s) de géométrie autorisée pour ce dossier
			
		# J'instancie des objets "formulaire".
		f_modif_doss = GererDossier_Reglementation(prefix = 'ModifierDossier', k_doss = obj_doss.id_doss)
		f_ajout_ph = GererPhoto(prefix = 'AjouterPhoto', k_doss = obj_doss.id_doss)
		f_ajout_fin = GererFinancement(prefix = 'AjouterFinancement', k_doss = obj_doss.id_doss)
		f_ajout_prest = GererPrestation(prefix = 'AjouterPrestation', k_doss = obj_doss.id_doss)
		f_ajout_fact = GererFacture(prefix = 'AjouterFacture', k_doss = obj_doss.id_doss)
		f_ch_prest = ChoisirPrestation(prefix = 'ChoisirPrestation', k_doss = obj_doss.id_doss)
		f_ajout_ddv = GererDemandeDeVersement(prefix = 'AjouterDemandeDeVersement', k_doss = obj_doss.id_doss)

		# J'initialise les champs de certains formulaires.
		tab_ajout_ph = init_form(f_ajout_ph)
		tab_ajout_fin = init_form(f_ajout_fin)
		tab_ajout_prest = init_form(f_ajout_prest)
		tab_ajout_fact = init_form(f_ajout_fact)
		tab_ch_prest = init_form(f_ch_prest)
		tab_ajout_ddv = init_form(f_ajout_ddv)

		# Je récupère l'ensemble des prestations pouvant être reliées avec le dossier courant.
		les_prest_filtr = TPrestation.objects.filter(
			tprestationsdossier__id_doss__id_org_moa__id_org_moa = obj_doss.id_org_moa.id_org_moa
		).exclude(tprestationsdossier__id_doss__id_doss = obj_doss.id_doss).distinct().order_by('int_prest')

		# Je prépare le contenu du tableau HTML des prestations pouvant être reliées avec le dossier courant.
		tab_lg_prest = []
		for une_prest in les_prest_filtr :

			# Je récupère l'ensemble des dossiers affectés par la prestation courante.
			tab_doss_prest = []
			for un_doss_prest in TPrestationsDossier.objects.filter(id_prest = une_prest.id_prest).order_by(
				'id_doss__num_doss'
			) :
				tab_doss_prest.append(conv_none(un_doss_prest.id_doss.num_doss))

			# J'initialise une ligne du tableau HTML des prestations.
			lg_prest = '''
			<tr>
				<td>{0}</td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
				<td>{4}</td>
				<td>{5}</td>
			</tr>
			'''.format(
				conv_none(une_prest.int_prest),
				conv_none(reecr_dt(une_prest.dt_notif_prest)),
				conv_none(float_to_int(une_prest.mont_ht_tot_prest)),
				conv_none(float_to_int(une_prest.mont_ttc_tot_prest)),
				', '.join(tab_doss_prest),
				'<span class="bt-choisir pointer pull-right" title="Choisir la prestation" action="{0}?action=repartir-montants&prestation={1}"></span>'.format(
					reverse('consulter_dossier', args = [obj_doss.id_doss]),
					une_prest.id_prest
				)
			)

			# J'ajoute la ligne du tableau HTML des prestations.
			tab_lg_prest.append(lg_prest)

		# Je déclare le contenu de certaines fenêtres modales.
		tab_cont_fm = {
			'ajouter_ddv' : '''
			<form name="form_ajouter_ddv" method="post" action="{0}" class="c-theme" enctype="multipart/form-data">
				<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
				{2}
				{3}
				{4}
				{5}
				<div class="row">
					<div class="col-sm-6">{6}</div>
					<div class="col-sm-6">{7}</div>
				</div>
				<div class="row">
					<div class="col-sm-6">{8}</div>
					<div class="col-sm-6">{9}</div>
				</div>
				<div class="row">
					<div class="col-sm-6">{10}</div>
					<div class="col-sm-6">{11}</div>
				</div>
				{12}
				{13}
				<button type="submit" class="bt-vert btn center-block to-unfocus">Valider</button>
			</form>
			'''.format(
				reverse('ajouter_demande_versement'),
				csrf(request)['csrf_token'],
				tab_ajout_ddv['za_num_doss'],
				tab_ajout_ddv['zl_org_fin'],
				tab_ajout_ddv['zl_type_vers'],
				tab_ajout_ddv['zs_int_ddv'],
				tab_ajout_ddv['zs_mont_ht_ddv'],
				tab_ajout_ddv['zs_mont_ttc_ddv'],
				tab_ajout_ddv['zd_dt_ddv'],
				tab_ajout_ddv['zd_dt_vers_ddv'],
				tab_ajout_ddv['zs_mont_ht_verse_ddv'],
				tab_ajout_ddv['zs_mont_ttc_verse_ddv'],
				tab_ajout_ddv['zu_chem_pj_ddv'],
				tab_ajout_ddv['zs_comm_ddv']
			),
			'ajouter_facture' : '''
			<form name="form_ajouter_facture" method="post" action="{0}" class="c-theme" enctype="multipart/form-data">
				<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
				{2}
				{3}
				{4}
				{5}
				<div class="row">
					<div class="col-sm-6">{6}</div>
					<div class="col-sm-6">{7}</div>
				</div>
				{8}
				<div class="row">
					<div class="col-sm-6">{9}</div>
					<div class="col-sm-6">{10}</div>
				</div>
				{11}
				{12}
				{13}
				<button type="submit" class="bt-vert btn center-block to-unfocus">Valider</button>
			</form>
			'''.format(
				reverse('ajouter_facture'),
				csrf(request)['csrf_token'],
				tab_ajout_fact['za_num_doss'],
				tab_ajout_fact['zl_prest'],
				tab_ajout_fact['zs_num_fact'],
				tab_ajout_fact['zd_dt_mand_moa_fact'],
				tab_ajout_fact['zs_mont_ht_fact'],
				tab_ajout_fact['zs_mont_ttc_fact'],
				tab_ajout_fact['zd_dt_rec_fact'],
				tab_ajout_fact['zs_num_mandat'],
				tab_ajout_fact['zs_num_bord'],
				tab_ajout_fact['zl_suivi_fact'],
				tab_ajout_fact['zu_chem_pj_fact'],
				tab_ajout_fact['zs_comm_fact']
			),
			'ajouter_financement' : '''
			<form name="form_ajouter_financement" method="post" action="{0}" class="c-theme" enctype="multipart/form-data">
				<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
				{2}
				{3}
				{4}
				<div class="row">
					<div class="col-sm-6">{5}</div>
					<div class="col-sm-6">{6}</div>
				</div>
				{7}
				<div class="row">
					<div class="col-sm-6">{8}</div>
					<div class="col-sm-6">{9}</div>
				</div>
				{10}
				<div class="row">
					<div class="col-sm-6">{11}</div>
					<div class="col-sm-6">{12}</div>
				</div>
				<div class="row">
					<div class="col-sm-6">{13}</div>
					<div class="col-sm-6">{14}</div>
				</div>
				<div class="row">
					<div class="col-sm-6">{15}</div>
					<div class="col-sm-6">{16}</div>
				</div>
				{17}
				{18}
				<button type="submit" class="bt-vert btn center-block to-unfocus">Valider</button>
			</form>
			'''.format(
				reverse('ajouter_financement'),
				csrf(request)['csrf_token'],
				tab_ajout_fin['za_num_doss'],
				tab_ajout_fin['zl_org_fin'],
				tab_ajout_fin['zs_num_arr_fin'],
				tab_ajout_fin['zs_mont_ht_elig_fin'],
				tab_ajout_fin['zs_mont_ttc_elig_fin'],
				tab_ajout_fin['zs_pourc_elig_fin'],
				tab_ajout_fin['zs_mont_ht_part_fin'],
				tab_ajout_fin['zs_mont_ttc_part_fin'],
				tab_ajout_fin['zd_dt_deb_elig_fin'],
				tab_ajout_fin['zs_duree_valid_fin'],
				tab_ajout_fin['zs_duree_pror_fin'],
				tab_ajout_fin['zd_dt_lim_deb_oper_fin'],
				tab_ajout_fin['zd_dt_lim_prem_ac_fin'],
				tab_ajout_fin['zl_paiem_prem_ac'],
				tab_ajout_fin['zs_pourc_real_fin'],
				tab_ajout_fin['zu_chem_pj_fin'],
				tab_ajout_fin['zs_comm_fin']
			),
			'ajouter_photo' : '''
			<form name="form_ajouter_photo" method="post" action="{0}" class="c-theme" enctype="multipart/form-data">
				<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
				{2}
				<div class="row">
					<div class="col-sm-6">
						{3}
					</div>
					<div class="col-sm-6">
						{4}
					</div>
				</div>
				{5}
				{6}
				{7}
				<button type="submit" class="bt-vert btn center-block to-unfocus">Valider</button>
			</form>
			'''.format(
				reverse('ajouter_photo'),
				csrf(request)['csrf_token'],
				tab_ajout_ph['za_num_doss'],
				tab_ajout_ph['zs_int_ph'],
				tab_ajout_ph['zs_descr_ph'],
				tab_ajout_ph['zl_ppv_ph'],
				tab_ajout_ph['zd_dt_pv_ph'],
				tab_ajout_ph['zu_chem_ph']
			),
			'ajouter_prestation' : '''
			<div class="field-wrapper">
				<p class="c-theme">La prestation est-elle déjà existante dans un autre dossier ?</p>
				<label class="c-police radio-inline">
					<input type="radio" name="rb_prest_exist" value="1">Oui
				</label>
				<label class="c-police radio-inline">
					<input type="radio" name="rb_prest_exist" value="0" checked>Non
				</label>
			</div>
			<div id="za_prest_nvelle">
				<form name="form_ajouter_prestation" method="post" action="{0}" class="c-theme" enctype="multipart/form-data">
					<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
					{2}
					<div class="row">
						<div class="col-sm-6">
							{3}
						</div>
						<div class="col-sm-6 vertical-align-icon-link">
							<span class="bt-ajouter-acteur icon-link">Ajouter un prestataire</span>
						</div>
					</div>
					{4}
					<div class="row">
						<div class="col-sm-6">
							{5}
						</div>
						<div class="col-sm-6">
							{6}
						</div>
					</div>
					<div class="row">
						<div class="col-sm-6">
							{7}
						</div>
						<div class="col-sm-6">
							{8}
						</div>
					</div>
					{9}
					{10}
					{11}
					<button type="submit" class="center-block btn bt-vert to-unfocus">Valider</button>
				</form>	
			</div>
			<div id="za_prest_exist" style="display: none;">
				<form name="form_choisir_prestation" method="post" action="{12}?action=filtrer-prestations" class="c-theme">
					<input name="csrfmiddlewaretoken" value="{13}" type="hidden">
					<fieldset style="padding-bottom: 0;">
						<legend>Rechercher par</legend>
						<div class="form-content">
							{14}
							{15}
							{16}
						</div>
					</fieldset>
				</form>
				<br />
				<p class="c-theme">Choisir une prestation</p>
				<div style="overflow: auto">
					<table class="display table" id="tab_choisir_prestation">
						<thead>
							<tr>
								<th>Intitulé</th>
								<th>Date de notification</th>
								<th>Montant HT (en €)</th>
								<th>Montant TTC (en €)</th>
								<th>Dossiers</th>
								<th></th>
							</tr>
						</thead>
						<tbody>{17}</tbody>
					</table>
				</div>
			</div>
			'''.format(
				reverse('ajouter_prestation'),
				csrf(request)['csrf_token'],
				tab_ajout_prest['za_num_doss'],
				tab_ajout_prest['zsac_siret_org_prest'],
				tab_ajout_prest['zs_int_prest'],
				tab_ajout_prest['zs_mont_ht_tot_prest'],
				tab_ajout_prest['zs_mont_ttc_tot_prest'],
				tab_ajout_prest['zd_dt_notif_prest'],
				tab_ajout_prest['zd_dt_fin_prest'],
				tab_ajout_prest['zl_nat_prest'],
				tab_ajout_prest['zu_chem_pj_prest'],
				tab_ajout_prest['zs_comm_prest'],
				reverse('consulter_dossier', args = [obj_doss.id_doss]),
				csrf(request)['csrf_token'],
				tab_ch_prest['zl_progr'],
				tab_ch_prest['zl_org_moa'],
				tab_ch_prest['zl_org_prest'],
				'\n'.join(tab_lg_prest)
			)
		}

		# Je déclare un tableau de fenêtres modales.
		tab_fm = [
			init_fm('afficher_photo', 'Consulter une photo'),
			init_fm('ajouter_avenant', 'Ajouter un avenant'),
			init_fm(
				'ajouter_financement', 
				'Ajouter un organisme dans le plan de financement', 
				tab_cont_fm['ajouter_financement']
			),
			init_fm('ajouter_ddv', 'Ajouter une demande de versement', tab_cont_fm['ajouter_ddv']),
			init_fm('ajouter_photo', 'Ajouter une photo', tab_cont_fm['ajouter_photo']),
			init_fm('ajouter_facture', 'Ajouter une facture', tab_cont_fm['ajouter_facture']),
			init_fm('ajouter_prestation', 'Ajouter/relier une prestation', tab_cont_fm['ajouter_prestation']),
			init_fm('modifier_carto', 'Modifier la géométrie'),
			init_fm('modifier_dossier', 'Modifier un dossier'),
			init_fm('relier_prestation', 'Relier une prestation'),
			init_fm('supprimer_arrete', 'Êtes-vous certain de supprimer cet arrêté ?'),
			init_fm('supprimer_dossier', 'Êtes-vous certain de supprimer ce dossier ?'),
			init_fm('supprimer_photo', 'Êtes-vous certain de supprimer cette photo ?')
		]

		# Je vérifie l'existence d'un objet TPgre.
		obj_doss_pgre = None
		try :
			obj_doss_pgre = TPgre.objects.get(id_doss = obj_doss.id_doss)
		except :
			pass

		# J'initialise la valeur de certains attributs.
		v_quant_objs_pgre = None
		v_quant_real_pgre = None
		v_unit = None
		v_riv = None
		v_inst_conc = None

		if obj_doss_pgre is not None :

			# Je renseigne la valeur des attributs non-liés à une autre table.
			v_quant_objs_pgre = obj_doss_pgre.quant_objs_pgre
			v_quant_real_pgre = obj_doss_pgre.quant_real_pgre

			# Je tente de récupérer la valeur de l'unité.
			try :
				v_unit = TUnite.objects.get(id_unit = obj_doss_pgre.id_unit.id_unit).int_unit
			except :
				pass

			# Je récupère les rivières impactées par le dossier PGRE.
			les_riv_doss = TRivieresDossier.objects.filter(id_pgre = obj_doss.id_doss).order_by('id_riv__n_riv')

			# Je stocke dans un tableau le nom de chaque rivière impactée par le dossier PGRE.
			tab_riv_doss = []
			for une_riv_doss in les_riv_doss :
				tab_riv_doss.append(une_riv_doss.id_riv.n_riv)

			# Je mets en forme la valeur du champ "Rivières impactées".
			v_riv = ', '.join(tab_riv_doss)

			# Je tente de récupérer la valeur de l'instance de concertation du dossier.
			try :
				v_inst_conc = TInstanceConcertation.objects.get(
					id_inst_conc = obj_doss_pgre.id_inst_conc.id_inst_conc
				).int_inst_conc
			except :
				pass

		# Je prépare la page de consultation des caractéristiques d'un dossier.
		tab_attr_doss = {
			'num_doss' : { 'label' : 'Numéro du dossier', 'value' : conv_none(obj_doss.num_doss) },
			'int_doss' :
			{
				'label' : 'Intitulé du dossier',
				'value' : '{0} - {1} - {2} - {3}'.format(
					obj_doss.id_nat_doss.int_nat_doss,
					obj_doss.id_type_doss.int_type_doss,
					obj_doss.terr_doss,
					obj_doss.ld_doss
				)
			},
			'n_org' : { 'label' : 'Maître d\'ouvrage', 'value' : conv_none(obj_doss.id_org_moa.id_org_moa.n_org) },
			'int_progr' : { 'label' : 'Programme', 'value' : conv_none(obj_doss.id_progr.int_progr) },
			'id_axe' : { 'label' : 'Axe', 'value' : conv_none(obj_doss.num_axe) },
			'id_ss_axe' : { 'label' : 'Sous-axe', 'value' : conv_none(obj_doss.num_ss_axe) },
			'id_act' : { 'label' : 'Action', 'value' : conv_none(obj_doss.num_act) },
			'int_nat_doss' :
			{
				'label' : 'Nature du dossier', 'value' : conv_none(obj_doss.id_nat_doss.int_nat_doss)
			},
			'int_type_doss' :
			{
				'label' : 'Type du dossier', 'value' : conv_none(obj_doss.id_type_doss.int_type_doss)
			},
			'mont_ht_doss' :
			{
				'label' : 'Montant HT du dossier (en €)', 'value' : conv_none(float_to_int(obj_doss.mont_ht_doss))
			},
			'mont_ttc_doss' :
			{
				'label' : 'Montant TTC du dossier (en €)', 'value' : conv_none(float_to_int(obj_doss.mont_ttc_doss))
			},
			'techn' :
			{
				'label' : 'Technicien',
				'value' : '{0} {1}'.format(
					conv_none(obj_doss.id_techn.n_techn), conv_none(obj_doss.id_techn.pren_techn)
				)
			},
			'int_av' : { 'label' : 'État d\'avancement du dossier', 'value' : conv_none(obj_doss.id_av.int_av) },
			'dt_delib_moa_doss' :
			{
				'label' : 'Date de délibération au maître d\'ouvrage',
				'value' : conv_none(reecr_dt(obj_doss.dt_delib_moa_doss))
			},
			'int_av_cp' :
			{
				'label' : 'Avis du comité de programmation', 'value' : conv_none(obj_doss.id_av_cp.int_av_cp)
			},
			'dt_av_cp_doss' :
			{
				'label' : 'Date de l\'avis du comité de programmation',
				'value' : conv_none(reecr_dt(obj_doss.dt_av_cp_doss))
			},
			'comm_doss' : { 'label' : 'Commentaire', 'value' : conv_none(obj_doss.comm_doss), 'textarea' : True },
			'quant_objs_pgre' : 
			{
				'label' : 'Quantification des objectifs', 
				'value' : conv_none(float_to_int(v_quant_objs_pgre, False))
			},
			'quant_real_pgre' : 
			{
				'label' : 'Réalisé', 'value' : conv_none(float_to_int(v_quant_real_pgre, False))
			},
			'int_unit' : { 'label' : 'Unité', 'value' : conv_none(v_unit) },
			'n_riv' : { 'label' : 'Rivières impactées', 'value' : conv_none(v_riv) },
			'int_inst_conc' : { 'label' : 'Instance de concertation', 'value' : conv_none(v_inst_conc) }
		}

		# Je récupère les dossiers appartenant à la même famille que le dossier consulté.
		les_doss_fam = TDossier.objects.filter(id_fam = obj_doss.id_fam.id_fam).exclude(id_doss = obj_doss.id_doss)

		# Je stocke dans un tableau les données mises en forme de chaque dossier de la famille.
		tab_doss_fam = []
		for un_doss_fam in les_doss_fam :

			# Je déclare un indicateur booléen permettant de savoir si l'objet TDossier courant est associé à l'objet
			# TDossier général.
			est_ass = False

			# Je vérifie l'existence d'un objet TDossier lié au dossier associé.
			obj_doss_ass = None
			try :
				obj_doss_ass = obj_doss.id_doss_ass
			except :
				pass

			# Je regarde si l'objet TDossier courant est associé à l'objet TDossier général.
			if obj_doss_ass is not None and obj_doss_ass.id_doss == un_doss_fam.id_doss :
				est_ass = True

			tab_doss_fam.append({
				'id_doss' : un_doss_fam.id_doss,
				'num_doss' : conv_none(un_doss_fam.num_doss),
				'n_moa' : conv_none(un_doss_fam.id_org_moa.id_org_moa.n_org),
				'dt_delib_moa_doss' : conv_none(reecr_dt(un_doss_fam.dt_delib_moa_doss)) or 'En projet',
				'int_progr' : conv_none(un_doss_fam.id_progr.int_progr),
				'int_nat_doss' : conv_none(un_doss_fam.id_nat_doss.int_nat_doss),
				'est_ass' : est_ass
			})

		# Je pointe vers un objet VSuiviDossier qui me permet de retrouver les restes à financer et à utiliser du 
		# dossier.
		obj_suivi_doss = VSuiviDossier.objects.get(id_doss = obj_doss.id_doss)

		# Je stocke les financements du dossier.
		les_fin = VFinancement.objects.filter(id_doss = obj_doss.id_doss)

		# Je stocke dans un tableau les données mises en forme de chaque financement du dossier.
		tab_fin = []

		for un_fin in les_fin :

			# J'initialise le nom du maître d'ouvrage.
			v_n_org = 'Autofinancement - {0}'.format(obj_doss.id_org_moa.n_org)
			try :
				v_n_org = conv_none(un_fin.id_org_fin.id_org_fin.n_org)
			except :
				pass

			tab_fin.append({
				'id_fin' : un_fin.id_fin,
				'n_org' : v_n_org,
				'mont_ht_tot_subv_fin' : conv_none(float_to_int(un_fin.mont_ht_part_fin)),
				'dt_deb_elig_fin' : conv_none(reecr_dt(un_fin.dt_deb_elig_fin)),
				'dt_fin_elig_fin' : conv_none(reecr_dt(un_fin.dt_fin_elig_fin))
			})

			# Je trie le tableau des financeurs par ordre alphabétique du nom.
			tab_fin = sorted(tab_fin, key = lambda tup : tup['n_org'])

		# Je stocke les prestations du dossier.
		les_prest_doss = TPrestationsDossier.objects.filter(id_doss = obj_doss.id_doss).order_by(
			'id_prest__id_org_prest__id_org_prest__n_org', '-id_prest__dt_notif_prest'
		)

		# Je stocke dans un tableau les données mises en forme de chaque prestation du dossier.
		tab_prest_doss = []

		for une_prest_doss in les_prest_doss :

			# Je récupère les identifiants du dossier et de la prestation courante.
			v_doss = une_prest_doss.id_doss.id_doss
			v_prest = une_prest_doss.id_prest.id_prest

			# Je pointe vers l'objet VSuiviPrestationsDossier afin de récupérer les restes à payer.
			obj_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(id_doss = v_doss, id_prest = v_prest)

			tab_prest_doss.append({
				'id_prest' : une_prest_doss.id_prest.id_prest,
				'n_org' : conv_none(une_prest_doss.id_prest.id_org_prest.id_org_prest.n_org),
				'mont_ht_prest' : conv_none(float_to_int(une_prest_doss.mont_ht_prest)),
				'nb_aven' : conv_none(len(TAvenant.objects.filter(id_doss = v_doss, id_prest = v_prest))),
				'mont_ht_aven_sum' : conv_none(float_to_int(obj_suivi_prest_doss.mont_ht_aven_sum)),
				'mont_ht_fact_sum' : conv_none(float_to_int(obj_suivi_prest_doss.mont_ht_fact_sum)),
				'mont_ht_rap' : conv_none(float_to_int(obj_suivi_prest_doss.mont_ht_rap))
			})

		# Je stocke les factures du dossier.
		les_fact_doss = TFacture.objects.filter(id_doss = obj_doss.id_doss).order_by(
			'id_prest__id_org_prest__n_org', '-id_prest__dt_notif_prest'
		)

		# Je stocke dans un tableau les données mises en forme de chaque facture du dossier.
		tab_fact_doss = []

		for une_fact_doss in les_fact_doss :
			tab_fact_doss.append({
				'id_fact' : une_fact_doss.id_fact,
				'prest' : '{0} : {1}'.format(
					conv_none(une_fact_doss.id_prest.id_org_prest.n_org),
					conv_none(reecr_dt(une_fact_doss.id_prest.dt_notif_prest))
				),
				'num_fact' : conv_none(une_fact_doss.num_fact),
				'dt_mand_moa_fact' : conv_none(reecr_dt(une_fact_doss.dt_mand_moa_fact)),
				'mont_ht_fact' : conv_none(float_to_int(une_fact_doss.mont_ht_fact)),
			})

		# Je stocke les différents types de déclarations.
		les_arr = TTypeDeclaration.objects.all()

		# Je parcours les différents types de déclarations afin d'implémenter l'onglet "Réglementations".
		i = -1
		cont_regl = ''
		for un_arr in les_arr :

			# J'incrémente le sommet.
			i += 1

			# Je stocke la valeur du modulo pour la valeur courante du sommet.
			mod = i % 2

			# J'initialise ou je réinitialise le contenu d'un élément <div/> possédant la classe "row".
			if mod == 0 :
				cont_row = ''

			# Je vérifie l'existence d'un objet TArretesDossier.
			obj_arr = None
			try :
				obj_arr = TArretesDossier.objects.get(id_doss = obj_doss.id_doss, id_type_decl = un_arr.id_type_decl)
			except :
				pass

			# Je récupère la valeur de chaque champ si et seulement si l'objet TArretesDossier existe.
			if obj_arr is not None :
				v_int_type_av_arr = obj_arr.id_type_av_arr.int_type_av_arr
				v_num_arr = obj_arr.num_arr
				v_dt_sign_arr = obj_arr.dt_sign_arr
				v_dt_lim_encl_trav_arr = obj_arr.dt_lim_encl_trav_arr
			else :
				v_int_type_av_arr = None
				v_num_arr = None
				v_dt_sign_arr = None
				v_dt_lim_encl_trav_arr = None

			# Je prépare la page de consultation d'un arrêté.
			tab_attr_arr = {
				'int_type_av_arr' : { 
					'label' : 'Avancement', 'value' : conv_none(v_int_type_av_arr)
				},
				'num_arr' : { 'label' : 'Numéro de l\'arrêté', 'value' : conv_none(v_num_arr) },
				'dt_sign_arr' : 
				{ 
					'label' : 'Date de signature de l\'arrêté', 'value' : conv_none(reecr_dt(v_dt_sign_arr))
				},
				'dt_lim_encl_trav_arr' :
				{
					'label' : 'Date limite d\'enclenchement des travaux',
					'value' : conv_none(reecr_dt(v_dt_lim_encl_trav_arr))
				}
			}

			# Je mets en forme les attributs.
			tab_attr_arr = init_pg_cons(tab_attr_arr)

			# J'initialise les options disponibles pour chaque arrêté.
			bt_pdf = ''
			if obj_arr is None :
				opt_dispo = '''
				<div class="col-xs-6">
					<a href="{0}" class="bt-ajouter icon-link">Ajouter</a>
				</div>
				'''.format(reverse('ajouter_arrete', args = [obj_doss.id_doss, un_arr.id_type_decl]))
			else :
				opt_dispo = '''
				<div class="col-xs-3">
					<a href="{0}" class="bt-modifier icon-link">Modifier</a>
				</div>
				<div class="col-xs-3">
					<span class="bt-supprimer bt_supprimer_arrete icon-link" data-target="#fm_supprimer_arrete" action="{1}?action=supprimer-arrete&dossier={2}&arrete={3}">Supprimer</span>
				</div>
				'''.format(
						reverse('modifier_arrete', args = [obj_doss.id_doss, un_arr.id_type_decl]),
						reverse('consulter_dossier', args = [obj_doss.id_doss]),
						obj_doss.id_doss,
						un_arr.id_type_decl,
					)

				if obj_arr.chem_pj_arr is not None :
					bt_pdf = '''
					<div class="col-xs-6">
						<a href="{0}" target="blank" class="bt-pdf icon-link">Consulter le fichier scanné de l'arrêté</a>
					</div>
					'''.format(MEDIA_URL + obj_arr.chem_pj_arr)

			# Je complète le contenu d'un élément <div/> possédant la classe "row".
			cont_row += '''
			<div class="col-sm-6">
				<div class="alt-thumbnail">
					<p class="b c-theme-fonce text-center">{0}</p>
					<br />
					{1}
					{2}
					{3}
					{4}
					<div class="row">
						{5}
						{6}
					</div>
				</div>
			</div>
			'''.format(
				conv_none(un_arr.int_type_decl),
				tab_attr_arr['int_type_av_arr'],
				tab_attr_arr['num_arr'],
				tab_attr_arr['dt_sign_arr'],
				tab_attr_arr['dt_lim_encl_trav_arr'],
				opt_dispo,
				bt_pdf
			)

			# Je vérifie si je dois terminer ou non l'élément <div/> possédant la classe "row".
			row_term = False
			if mod == 1 :
				row_term = True
			if i + 1 == len(les_arr) and mod == 0 :
				row_term = True
			if row_term == True :
				cont_regl += '''
				<div class="row">
					{0}
				</div>
				'''.format(cont_row)

		# Je récupère les photos du dossier.
		les_ph = TPhoto.objects.filter(id_doss = obj_doss.id_doss).order_by('-dt_pv_ph')

		# Je stocke dans un tableau les données mises en forme de chaque photo du dossier.
		tab_ph = []
		for une_ph in les_ph :
			tab_ph.append({
				'id_ph' : une_ph.id_ph,
				'chem_ph' : conv_none(une_ph.chem_ph),
				'int_ph' : conv_none(une_ph.int_ph),
				'int_ppv_ph' : conv_none(une_ph.id_ppv_ph.int_ppv_ph),
				'dt_pv_ph' : conv_none(reecr_dt(une_ph.dt_pv_ph))
			})

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/consulter_dossier.html',
			{
				'f1' : init_form(f_modif_doss),
				'le_doss' : obj_doss,
				'les_geoms' : geom_doss,
				'les_attr_doss' : init_pg_cons(tab_attr_doss),
				'les_doss_fam' : tab_doss_fam,
				'les_fact_doss' : tab_fact_doss,
				'les_fin' : tab_fin,
				'les_fm' : tab_fm,
				'les_ph' : tab_ph,
				'les_prest_doss' : tab_prest_doss,
				'les_arr' : cont_regl,
				'mont_ht_doss' : float_to_int(obj_doss.mont_ht_doss),
				'mont_ht_raf' : float_to_int(obj_suivi_doss.mont_ht_raf),
				'mont_ht_rau' : float_to_int(obj_suivi_doss.mont_ht_rau),
				'title' : 'Consulter un dossier'
			}
		)

	else :

		# Je vérifie l'existence d'un objet TDossier
		try :
			obj_doss = TDossier.objects.get(id_doss = p_doss)
		except :
			return HttpResponse()

		if 'action' in request.GET :

			# Je retiens le nom du paramètre "GET".
			get_action = request.GET['action']
				
			# Je traite le cas où je veux supprimer une photo.
			if get_action == 'supprimer-photo' and 'photo' in request.GET :

				# Je prépare la réponse AJAX.
				reponse = HttpResponse(aff_mess_suppr('{0}?photo={1}'.format(
					reverse('supprimer_photo'),
					request.GET['photo']
				)))

			# Je traite le cas où je veux afficher une photo.
			if get_action == 'afficher-photo' and 'photo' in request.GET :
				
				# Je verifie l'existence d'un objet TPhoto.
				try :
					obj_ph = TPhoto.objects.get(id_ph = request.GET['photo'])
				except :
					return HttpResponse()

				# Je prépare la page de consultation d'une photo.
				tab_attr_ph = {
					'num_doss' : { 'label' : 'Numéro du dossier', 'value' : conv_none(obj_ph.id_doss.num_doss) },
					'int_ph' : { 'label' : 'Intitulé de la photo', 'value' : conv_none(obj_ph.int_ph) },
					'descr_ph' : { 'label' : 'Description de la photo', 'value' : conv_none(obj_ph.descr_ph) },
					'int_ppv_ph' :
					{
						'label' : 'Période de la prise de vue de la photo',
						'value' : conv_none(obj_ph.id_ppv_ph.int_ppv_ph)
					},
					'dt_pv_ph' :
					{
						'label' : 'Date de la prise de vue de la photo',
						'value' : conv_none(reecr_dt(obj_ph.dt_pv_ph))
					}
				}

				# Je mets en forme les attributs.
				tab_attr_ph = init_pg_cons(tab_attr_ph)

				# Je prépare la réponse AJAX.
				reponse = HttpResponse(
					'''
					<fieldset class="c-theme subfieldset" style="padding-bottom : 0;">
						<legend class="sublegend">Visualisation</legend>
						<div class="attribute-wrapper text-center">
							<img src="{0}" id="img_consulter_photo"/>
						</div>
					</fieldset>
					<fieldset class="c-theme subfieldset" style="padding-bottom : 0; margin-bottom : 0;">
						<legend class="sublegend">Caractéristiques</legend>
						{1}
						<div class="row">
							<div class="col-xs-6">{2}</div>
							<div class="col-xs-6">{3}</div>
						</div>
						<div class="row">
							<div class="col-xs-6">{4}</div>
							<div class="col-xs-6">{5}</div>
						</div>
					</fieldset>
					'''.format(
						MEDIA_URL + obj_ph.chem_ph,
						tab_attr_ph['num_doss'],
						tab_attr_ph['int_ph'],
						tab_attr_ph['descr_ph'],
						tab_attr_ph['int_ppv_ph'],
						tab_attr_ph['dt_pv_ph']
					)
				)

			# Je traite le cas où je veux supprimer un dossier.
			if get_action == 'supprimer-dossier' :

				# Je prépare la réponse AJAX.
				reponse = HttpResponse(aff_mess_suppr(
					reverse('supprimer_dossier', args = [obj_doss.id_doss]),
					'''
					La suppression du dossier entraîne également la suppression des opérations effectuées sur celui-ci.
					Cette opération est irréversible.
					'''
				))

			# Je traite le cas où je veux délier un arrêté pour un dossier.
			if get_action == 'supprimer-arrete' and 'dossier' in request.GET and 'arrete' in request.GET :

				# Je prépare la réponse AJAX.
				reponse = HttpResponse(aff_mess_suppr('{0}?dossier={1}&arrete={2}'.format(
					reverse('supprimer_arrete'), request.GET['dossier'], request.GET['arrete']
				)))

			# Je traite le cas où je veux filtrer les prestations.
			if get_action == 'filtrer-prestations' :

				# Je vérifie la validité du formulaire de recherche d'une prestation.
				f_ch_prest = ChoisirPrestation(request.POST, k_doss = obj_doss.id_doss)

				if f_ch_prest.is_valid() :

					# Je récupère et nettoie les données du formulaire valide.
					cleaned_data = f_ch_prest.cleaned_data
					v_progr = integer(cleaned_data['zl_progr'])
					v_org_prest = integer(cleaned_data['zl_org_prest'])
					v_org_moa = integer(cleaned_data['zl_org_moa'])

					# Je déclare le tableau qui stockera les conditions de la requête SQL.
					tab_and = {}

					# J'empile les tableaux des conditions.
					if v_progr > -1 :
						tab_and['tprestationsdossier__id_doss__id_progr__id_progr'] = v_progr

					if v_org_prest > -1 :
						tab_and['id_org_prest'] = v_org_prest

					if v_org_moa > -1 :
						tab_and['tprestationsdossier__id_doss__id_org_moa__id_org_moa'] = v_org_moa

					les_prest_filtr = TPrestation.objects.filter(**tab_and).exclude(
						tprestationsdossier__id_doss__id_doss = obj_doss.id_doss
					).distinct().order_by('int_prest')

					# Je prépare le contenu du tableau HTML des prestations filtrées.
					tab_prest_filtr = []
					for une_prest in les_prest_filtr :

						tab_doss_prest = []
						for un_doss_prest in TPrestationsDossier.objects.filter(id_prest = une_prest.id_prest).order_by(
							'id_doss__num_doss'
						) :
							tab_doss_prest.append(conv_none(un_doss_prest.id_doss.num_doss))

						tab_prest_filtr.append([
							conv_none(une_prest.int_prest),
							conv_none(reecr_dt(une_prest.dt_notif_prest)),
							conv_none(float_to_int(une_prest.mont_ht_tot_prest)),
							conv_none(float_to_int(une_prest.mont_ttc_tot_prest)),
							', '.join(tab_doss_prest),
							'<span class="bt-choisir pointer pull-right" title="Choisir la prestation" action="{0}?action=repartir-montants&prestation={1}"></span>'.format(
								reverse('consulter_dossier', args = [obj_doss.id_doss]),
								une_prest.id_prest
							)
						])

					# Je mets à jour le tableau HTML des dossiers filtrés.
					reponse = HttpResponse(json.dumps({ 'success' : tab_prest_filtr }), content_type = 'application/json')

				else :

					# J'affiche les erreurs.
					reponse = HttpResponse(json.dumps(f_ch_prest.errors), content_type = 'application/json')

			# Je traite le cas où je veux répartir les montants d'une prestation.
			if get_action == 'repartir-montants' :

				if 'prestation' in request.GET :

					# Je retiens le nom du paramètre "GET".
					get_prest = request.GET['prestation']

					# Je récupère les dossiers affectés à la prestation choisie.
					les_prest_doss = TPrestationsDossier.objects.filter(id_prest = get_prest).order_by(
						'id_doss__num_doss'
					)

					if len(les_prest_doss) > 0 :

						# Je déclare un tableau qui contiendra les lignes du tableau HTML de répartition des montants
						# de la prestation choisie.
						tab_lg = []

						for index, une_prest_doss in enumerate(les_prest_doss) :

							# Je stocke l'identifiant du dossier courant ainsi que celui de la prestation courante (c'
							# est-à-dire de celle qui a été choisie !).
							id_doss = une_prest_doss.id_doss.id_doss
							id_prest = une_prest_doss.id_prest.id_prest

							# J'instancie un objet "formulaire".
							f_rep_mont_prest = RepartirMontantsPrestation(
								prefix = 'RepartirMontantsPrestation{0}'.format(index), 
								k_doss = id_doss, 
								k_prest = id_prest
							)

							# J'initialise les champs du formulaire.
							tab_rep_mont_prest = init_form(f_rep_mont_prest)

							# Je pointe vers un objet VSuiviPrestationsDossier.
							obj_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(
								id_doss = id_doss, id_prest = id_prest
							)

							# Je pointe vers un objet VSuiviDossier.
							obj_suivi_doss = VSuiviDossier.objects.get(id_doss = id_doss)

							# Je mets en forme les lignes du tableau HTML relatives aux dossiers déjà reliés à la
							# prestation choisie.
							lg = '''
							<tr>
								<td class="b">
									{0}
									{1}
								</td>
								<td>{2}</td>
								<td>{3}</td>
								<td>{4}</td>
								<td>{5}</td>
								<td>{6}</td>
							</tr>
							'''.format(
								conv_none(une_prest_doss.id_doss.num_doss),
								tab_rep_mont_prest['za_doss'],
								tab_rep_mont_prest['zs_mont_ht_prest_doss'],
								tab_rep_mont_prest['zs_mont_ttc_prest_doss'],
								float_to_int(obj_suivi_prest_doss.mont_ht_aven_sum),
								float_to_int(obj_suivi_prest_doss.mont_ht_fact_sum),
								float_to_int(obj_suivi_doss.mont_ht_rau)
							)

							# J'empile le tableau des lignes.
							tab_lg.append(lg)

						# J'instancie un objet "formulaire".
						f_rep_mont_prest = RepartirMontantsPrestation(prefix = 'RepartirMontantsPrestation')

						# J'initialise les champs du formulaire.
						tab_rep_mont_prest = init_form(f_rep_mont_prest)

						# Je pointe vers un objet VSuiviDossier.
						obj_suivi_doss = VSuiviDossier.objects.get(id_doss = obj_doss.id_doss)

						# Je mets en forme la ligne du tableau HTML relative au dossier en cours de consultation.
						nvelle_lg = '''
						<tr style="background-color: #F8B862;">
							<td class="b">
								{0}
								{1}
							</td>
							<td>{2}</td>
							<td>{3}</td>
							<td>{4}</td>
							<td>{5}</td>
							<td>{6}</td>
						</tr>
						'''.format(
							conv_none(obj_doss.num_doss),
							tab_rep_mont_prest['za_doss'],
							tab_rep_mont_prest['zs_mont_ht_prest_doss'],
							tab_rep_mont_prest['zs_mont_ttc_prest_doss'],
							0,
							0,
							float_to_int(obj_suivi_doss.mont_ht_rau)
						)

						# J'empile le tableau des lignes.
						tab_lg.append(nvelle_lg)

						reponse = HttpResponse('''
						<div id="za_tab_montants_prestation" style="padding-top : 15px;">
							<p class="c-theme">Redistribuer les montants dédiés de cette prestation</p>
							<form action="{0}?action=relier-prestation&prestation={1}" method="post" name="form_relier_prestation" class="alert-user">
								<input name="csrfmiddlewaretoken" value="{2}" type="hidden">
								<div style="overflow: auto">
									<table class="display table" id="tab_montants_prestation">
										<thead>
											<tr>
												<th>N° du dossier</th>
												<th>Montant HT sans avenants (en €)</th>
												<th>Montant TTC sans avenants (en €)</th>
												<th>Somme HT des avenants (en €)</th>
												<th>Somme HT des factures émises (en €)</th>
												<th>Reste à engager HT pour le dossier (en €)</th>
											</tr>
										</thead>
										<tbody>{3}</tbody>
									</table>
								</div>
								<span class="za_erreur_groupee"></span>
								<br />
								<button type="submit" class="bt-vert btn center-block to-unfocus" data-target="#fm_relier_prestation">Valider</button>
							</form>
						</div>
						'''.format(
							reverse('consulter_dossier', args = [obj_doss.id_doss]),
							get_prest,
							csrf(request)['csrf_token'],
							'\n'.join(tab_lg)
						))

			# Je traite le cas où je veux relier une prestation à un dossier.
			if get_action == 'relier-prestation' :

				if 'prestation' in request.GET :

					# Je vérifie l'existence d'un objet TPrestation.
					obj_prest = None
					try :
						obj_prest = TPrestation.objects.get(id_prest = request.GET['prestation'])
					except :
						return HttpResponse()

					# Je récupère les données.
					v_tab_doss = request.POST.getlist('za_doss')
					v_tab_mont_ht_prest = request.POST.getlist('zs_mont_ht_prest_doss')
					v_tab_mont_ttc_prest = request.POST.getlist('zs_mont_ttc_prest_doss')

					# Je déclare deux tableaux : le tableau des lignes du tableau HTML et le tableau des erreurs de
					# traitement.
					tab_lg = []
					tab_err = []

					for i in range(0, len(v_tab_doss)) :
						
						# Je vérifie le format des montants saisis.
						if valid_mont(
							v_tab_mont_ht_prest[i], False
						) == True or valid_mont(
						v_tab_mont_ttc_prest[i], False
						) == True :
							tab_err.append('Veuillez vérifier les valeurs renseignées.')

						# J'empile ou je réinitialise le tableau selon la validité de la ligne courante.
						if len(tab_err) == 0 :
							tab_lg.append(
								[v_tab_doss[i], float(v_tab_mont_ht_prest[i]), float(v_tab_mont_ttc_prest[i])]
							)
						else :
							tab_lg = []

					# J'initialise les variables qui vont calculer les sommes des montants HT et TTC après
					# redistribution.
					somme_ht = 0
					somme_ttc = 0

					if len(tab_lg) > 0 :
						for i in range(0, len(tab_lg)) :

							# Je vérifie l'existence d'un objet VSuiviPrestationsDossier.
							obj_suivi_prest_doss = None
							try :
								obj_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(
									id_doss = tab_lg[i][0],
									id_prest = obj_prest.id_prest
								)
							except :
								pass

							if obj_suivi_prest_doss is not None :

								# J'obtiens l'intervalle de valeurs HT et l'intervalle de valeurs TTC disponibles pour le
								# couple prestation/dossier courant.
								tab_bornes = calc_interv(obj_suivi_prest_doss.id_doss, obj_suivi_prest_doss.id_prest)

								# Je vérifie que chaque montant est inclu dans son intervalle respectif.
								if tab_lg[i][1] < tab_bornes['ht']['min'] or tab_lg[i][1] > tab_bornes['ht']['max'] :
									tab_err.append(
										'Veuillez vérifier le montant HT renseigné pour le dossier {0}.'.format(
											TDossier.objects.get(id_doss = obj_suivi_prest_doss.id_doss).num_doss
										)
									)

								if tab_lg[i][2] < tab_bornes['ttc']['min'] or tab_lg[i][2] > tab_bornes['ttc']['max'] :
									tab_err.append(
										'Veuillez vérifier le montant TTC renseigné pour le dossier {0}.'.format(
											TDossier.objects.get(id_doss = obj_suivi_prest_doss.id_doss).num_doss
										)
									)

							# Je cumule les montants HT et TTC.
							somme_ht += tab_lg[i][1]
							somme_ttc += tab_lg[i][2]

						# Je pointe vers un objet VSuiviDossier.
						obj_suivi_doss = VSuiviDossier.objects.get(id_doss = obj_doss.id_doss)

						# Je vérifie la borne maximale du dossier dont on veut relier la prestation.
						if tab_lg[len(tab_lg) - 1][1] > obj_suivi_doss.mont_ht_rau :
							tab_err.append(
								'Veuillez vérifier le montant HT renseigné pour le dossier {0}.'.format(
									obj_doss.num_doss
								)
							)

						if tab_lg[len(tab_lg) - 1][2] > obj_suivi_doss.mont_ttc_rau :
							tab_err.append(
								'Veuillez vérifier le montant TTC renseigné pour le dossier {0}.'.format(
									obj_doss.num_doss
								)
							)

						# Je mets à jour le tableau des lignes en ajoutant l'identifiant du dossier consulté.
						tab_lg[len(tab_lg) - 1][0] = obj_doss.id_doss

					# Je vérifie que chaque somme de montants après redistribution est égale au montant total respectif
					# de la prestation.
					if obj_prest.mont_ht_tot_prest != somme_ht :
						tab_err.append(
							'La somme des montants HT n\'est pas égale à {0} €.'.format(
								float_to_int(obj_prest.mont_ht_tot_prest)
							)
						)

					if obj_prest.mont_ttc_tot_prest != somme_ttc :
						tab_err.append(
							'La somme des montants TTC n\'est pas égale à {0} €.'.format(
								float_to_int(obj_prest.mont_ttc_tot_prest)
							)
						)

					if len(tab_err) == 0 :

						# Je mets à jour la prestation.
						for i in range(0, len(tab_lg)) :

							# Je requête sur l'enregistrement courant.
							qry = TPrestationsDossier.objects.filter(
								id_doss = tab_lg[i][0], id_prest = obj_prest.id_prest
							)

							# Je mets à jour l'enregistrement si la requête renvoie un enregistrement, sinon j'en créé
							# un.
							if len(qry) > 0 :
								qry.update(
									mont_ht_prest = tab_lg[i][1], mont_ttc_prest = tab_lg[i][2]
								)
							else :
								TPrestationsDossier.objects.create(
									id_doss = obj_doss,
									id_prest = obj_prest,
									mont_ht_prest = tab_lg[i][1],
									mont_ttc_prest = tab_lg[i][2]
								)

						# J'affiche le message de succès.
						reponse = HttpResponse(
							json.dumps({
								'success' : 'La prestation a été reliée au dossier {0} avec succès.'.format(
									obj_doss.num_doss
								),
								'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss]),
								'close' : 'ajouter_prestation'
							}),
							content_type = 'application/json'
						)

					else :

						# J'affiche les erreurs.
						reponse = HttpResponse(json.dumps({ 'errors' : tab_err }), content_type = 'application/json')

			# Je traite le cas où je dois afficher le formulaire d'ajout d'un avenant.
			if get_action == 'afficher-form-avenant' :

				if 'prestation' in request.GET :
					reponse = HttpResponse(ajout_aven(
						request,
						'GET',
						request.GET['prestation'],
						obj_doss.id_doss,
						reverse('consulter_dossier', args = [obj_doss.id_doss])
					))

			# Je traite le cas où je dois ajouter un avenant.
			if get_action == 'ajouter-avenant' :
				reponse = ajout_aven(
					request,
					'POST',
					None,
					None,
					None,
					reverse('consulter_dossier', args = [obj_doss.id_doss]),
					'#ong_prestations',
				)

	return reponse

'''
Gestion des photos
'''

'''
Cette vue permet d'ajouter une photo dans la base de données.
request : Objet requête
'''
@verif_acces
def ajouter_photo(request) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererPhoto
	from app.functions import crypt_val, integer, nett_val, upload_fich
	from app.models import TDossier, TPeriodePriseVuePhoto, TPhoto
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json
	import time

	reponse = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie la validité du formulaire d'ajout d'une photo.
		f_ajout_ph = GererPhoto(request.POST, request.FILES)

		if f_ajout_ph.is_valid() :

			# Je récupère et nettoie les données du formulaire valide.
			cleaned_data = f_ajout_ph.cleaned_data
			v_num_doss = nett_val(cleaned_data['za_num_doss'])
			v_int_ph = nett_val(cleaned_data['zs_int_ph'])
			v_descr_ph = nett_val(cleaned_data['zs_descr_ph'])
			v_ppv_ph = nett_val(integer(cleaned_data['zl_ppv_ph']), True)
			v_dt_pv_ph = nett_val(cleaned_data['zd_dt_pv_ph'])
			v_obj_ph = nett_val(cleaned_data['zu_chem_ph'])

			# Je pointe vers l'objet TDossier consulté.
			obj_doss = TDossier.objects.get(num_doss = v_num_doss)

			# Je récupère l'extension du fichier uploadé.
			split = v_obj_ph.name.split('.')
			ext_ph = split[len(split) - 1]

			# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
			n_fich = crypt_val('{0}-{1}'.format(request.user.id, time.strftime('%d%m%Y%H%M%S')))
			v_chem_ph = 'dossiers/{0}/photos/{1}.{2}'.format(obj_doss.num_doss, n_fich, ext_ph)

			# J'uploade le fichier.
			upload_fich(v_obj_ph, v_chem_ph)

			# Je remplis les données attributaires du nouvel objet TPhoto.
			obj_nv_ph = TPhoto(
				chem_ph = v_chem_ph,
				descr_ph = v_descr_ph,
				dt_pv_ph = v_dt_pv_ph,
				int_ph = v_int_ph,
				id_doss = obj_doss,
				id_ppv_ph = TPeriodePriseVuePhoto.objects.get(id_ppv_ph = v_ppv_ph)
			)

			# Je créé un nouvel objet TPhoto.
			obj_nv_ph.save()

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'La photo a été ajoutée avec succès.',
					'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_photos'

		else :

			# J'affiche les erreurs.
			reponse = HttpResponse(json.dumps(f_ajout_ph.errors), content_type = 'application/json')

	return reponse

'''
Cette vue permet de supprimer une photo.
request : Objet requête
'''
@csrf_exempt
@verif_acces
def supprimer_photo(request) :

	''' Imports '''
	from app.models import TPhoto
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from styx.settings import MEDIA_ROOT
	import json
	import os

	reponse = HttpResponse()

	if request.method == 'POST' :
		if 'photo' in request.GET :

			# Je vérifie l'existence d'un objet TPhoto.
			try :
				obj_ph = TPhoto.objects.get(id_ph = request.GET['photo'])
			except :
				return HttpResponse()

			# Je tente d'effacer le fichier photo du serveur média.
			try :
				os.remove('{0}/{1}'.format(MEDIA_ROOT, obj_ph.chem_ph))
			except :
				pass

			# Je récupère l'identifiant du dossier rattaché à la photo.
			id_doss = obj_ph.id_doss.id_doss

			# Je supprime l'objet TPhoto.
			obj_ph.delete()

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'La photo a été supprimée avec succès.',
					'redirect' : reverse('consulter_dossier', args = [id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_photos'

	return reponse

'''
Cette vue permet d'afficher la page de modification d'une photo.
request : Objet requête
p_ph : Identifiant de la photo à modifier
'''
@nett_form
@verif_acces
def modifier_photo(request, p_ph) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererPhoto
	from app.functions import crypt_val, init_fm, init_form, integer, nett_val, upload_fich
	from app.models import TDossier, TPeriodePriseVuePhoto, TPhoto
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404, render
	from styx.settings import MEDIA_ROOT
	import json
	import os
	import time

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je vérifie l'existence d'un objet TPhoto.
		obj_ph = get_object_or_404(TPhoto, id_ph = p_ph)

		# J'instancie un objet "formulaire".
		f_modif_ph = GererPhoto(prefix = 'ModifierPhoto', k_ph = obj_ph.id_ph)

		# Je déclare un tableau de fenêtres modales.
		tab_fm = [
			init_fm('modifier_photo', 'Modifier une photo')
		]

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/modifier_photo.html',
			{
				'f1' : init_form(f_modif_ph),
				'la_ph' : obj_ph,
				'le_doss' : obj_ph.id_doss,
				'les_fm' : tab_fm,
				'title' : 'Modifier une photo'
			}
		)

	else :

		# Je vérifie l'existence d'un objet TPhoto.
		obj_ph = None
		try :
			obj_ph = TPhoto.objects.get(id_ph = p_ph)
		except :
			return HttpResponse()

		# Je vérifie la validité du formulaire de mise à jour d'une photo.
		f_modif_ph = GererPhoto(request.POST, request.FILES, k_modif = True)

		if f_modif_ph.is_valid() :

			# Je récupère et nettoie les données du formulaire valide.
			cleaned_data = f_modif_ph.cleaned_data
			v_num_doss = nett_val(cleaned_data['za_num_doss'])
			v_int_ph = nett_val(cleaned_data['zs_int_ph'])
			v_descr_ph = nett_val(cleaned_data['zs_descr_ph'])
			v_ppv_ph = nett_val(integer(cleaned_data['zl_ppv_ph']), True)
			v_dt_pv_ph = nett_val(cleaned_data['zd_dt_pv_ph'])
			v_obj_ph = nett_val(cleaned_data['zu_chem_ph'])

			# Je pointe vers l'objet TDossier consulté.
			obj_doss = TDossier.objects.get(num_doss = v_num_doss)

			# Je remplis les données attributaires de l'objet TPhoto à modifier.
			obj_ph.descr_ph = v_descr_ph
			obj_ph.dt_pv_ph = v_dt_pv_ph
			obj_ph.int_ph = v_int_ph
			obj_ph.id_doss = obj_doss
			obj_ph.id_ppv_ph = TPeriodePriseVuePhoto.objects.get(id_ppv_ph = v_ppv_ph)

			if v_obj_ph is not None :
				
				# Je tente d'effacer la photo du serveur média vù qu'elle est inutile.
				try :
					os.remove('{0}/{1}'.format(MEDIA_ROOT, obj_ph.chem_ph))
				except :
					pass

				# Je récupère l'extension du fichier uploadé.
				split = v_obj_ph.name.split('.')
				ext_ph = split[len(split) - 1]

				# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
				n_fich = crypt_val('{0}-{1}'.format(request.user.id, time.strftime('%d%m%Y%H%M%S')))
				v_chem_ph = 'dossiers/{0}/photos/{1}.{2}'.format(obj_doss.num_doss, n_fich, ext_ph)

				# J'uploade le fichier.
				upload_fich(v_obj_ph, v_chem_ph)

				# Je mets à jour le chemin de la photo vers le chemin de la nouvelle photo uploadée.
				obj_ph.chem_ph = v_chem_ph	

			# Je mets à jour l'objet TPhoto.
			obj_ph.save()

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'La photo a été modifiée avec succès.',
					'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_photos'

		else :

			# J'affiche les erreurs.
			reponse = HttpResponse(json.dumps(f_modif_ph.errors), content_type = 'application/json')

	return reponse

'''
Gestion des arrêtés
'''

'''
Cette vue permet soit d'afficher la page d'ajout d'un arrêté, soit de traiter le formulaire de la page. 
request : Objet requête
p_doss : Identifiant du dossier rattaché à l'arrêté
p_arr : Identifiant du type de déclaration
'''
@nett_form
@verif_acces
def ajouter_arrete(request, p_doss, p_arr) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererArrete
	from app.functions import crypt_val, init_fm, init_form, integer, nett_val, upload_fich
	from app.models import TArretesDossier, TDossier, TTypeAvancementArrete, TTypeDeclaration
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404, render
	import json
	import time

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je vérifie l'existence des objets TDossier et TTypeDeclaration.
		obj_doss = get_object_or_404(TDossier, id_doss = p_doss)
		obj_arr = get_object_or_404(TTypeDeclaration, id_type_decl = p_arr)

		# J'instancie un objet "formulaire".
		f_ajout_arr = GererArrete(prefix = 'AjouterArrete', k_doss = obj_doss.id_doss, k_arr = obj_arr.id_type_decl)

		# Je déclare un tableau de fenêtres modales.
		tab_fm = [
			init_fm('ajouter_arrete', 'Ajouter un arrêté')
		]

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/ajouter_arrete.html',
			{
				'f1' : init_form(f_ajout_arr),
				'l_arr' : obj_arr,
				'le_doss' : obj_doss,
				'les_fm' : tab_fm,
				'title' : 'Ajouter un arrêté'
			}
		)

	else :

		# Je vérifie l'existence d'un objet TDossier.
		try :
			obj_doss = TDossier.objects.get(id_doss = p_doss)
		except :
			return HttpResponse()

		# Je vérifie l'existence d'un objet TTypeDeclaration.
		try :
			obj_arr = TTypeDeclaration.objects.get(id_type_decl = p_arr)
		except :
			return HttpResponse()

		# Je vérifie la validité du formulaire d'ajout d'un arrêté.
		f_ajout_arr = GererArrete(request.POST, request.FILES)

		if f_ajout_arr.is_valid() :

			# Je récupère et nettoie les données du formulaire valide.
			cleaned_data = f_ajout_arr.cleaned_data
			v_type_av_arr = nett_val(integer(cleaned_data['zl_type_av_arr']), True)
			v_num_arr = nett_val(cleaned_data['zs_num_arr'])
			v_dt_sign_arr = nett_val(cleaned_data['zd_dt_sign_arr'])
			v_dt_lim_encl_trav_arr = nett_val(cleaned_data['zd_dt_lim_encl_trav_arr'])
			v_obj_arr = nett_val(cleaned_data['zu_chem_pj_arr'])

			# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
			n_fich = crypt_val('{0}-{1}'.format(request.user.id, time.strftime('%d%m%Y%H%M%S')))
			v_chem_pj_arr = 'dossiers/{0}/reglementations/{1}.pdf'.format(obj_doss.num_doss, n_fich)

			# J'uploade le fichier.
			upload_fich(v_obj_arr, v_chem_pj_arr)

			# Je créé un nouvel objet TArretesDossier.
			obj_nv_arr_doss = TArretesDossier.objects.create(
				id_doss = obj_doss,
				id_type_av_arr = TTypeAvancementArrete.objects.get(id_type_av_arr = v_type_av_arr),
				id_type_decl = obj_arr,
				chem_pj_arr = v_chem_pj_arr,
				dt_lim_encl_trav_arr = v_dt_lim_encl_trav_arr,
				dt_sign_arr = v_dt_sign_arr,
				num_arr = v_num_arr
			)

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'L\'arrêté a été ajouté avec succès.',
					'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_reglementations'

		else :

			# J'affiche les erreurs.
			reponse = HttpResponse(json.dumps(f_ajout_arr.errors), content_type = 'application/json')
			
	return reponse

'''
Cette vue permet soit d'afficher la page de modification d'un arrêté, soit de traiter le formulaire de la page. 
request : Objet requête
p_doss : Identifiant du dossier rattaché à l'arrêté
p_arr : Identifiant du type de déclaration
'''
@nett_form
@verif_acces
def modifier_arrete(request, p_doss, p_arr) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererArrete
	from app.functions import crypt_val, init_fm, init_form, integer, nett_val, upload_fich
	from app.models import TArretesDossier, TTypeAvancementArrete
	from django.http import HttpResponse
	from django.core.urlresolvers import reverse
	from django.shortcuts import get_object_or_404, render
	from styx.settings import MEDIA_ROOT
	import json
	import os
	import time

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je vérifie l'existence d'un objet TArretesDossier.
		obj_arr_doss = get_object_or_404(TArretesDossier, id_doss = p_doss, id_type_decl = p_arr)

		# J'instancie un objet "formulaire".
		f_modif_arr = GererArrete(
			prefix = 'ModifierArrete', 
			k_doss = obj_arr_doss.id_doss.id_doss,
			k_arr = obj_arr_doss.id_type_decl.id_type_decl
		)

		# Je déclare un tableau de fenêtres modales.
		tab_fm = [
			init_fm('modifier_arrete', 'Modifier un arrêté')
		]

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/modifier_arrete.html',
			{
				'f1' : init_form(f_modif_arr),
				'l_arr' : obj_arr_doss.id_type_decl,
				'le_doss' : obj_arr_doss.id_doss,
				'les_fm' : tab_fm,
				'title' : 'Modifier un arrêté'
			}
		)

	else :
		
		# Je vérifie l'existence d'un objet TArretesDossier.
		obj_arr_doss = None
		try :
			obj_arr_doss = TArretesDossier.objects.get(id_doss = p_doss, id_type_decl = p_arr)
		except :
			pass

		# Je vérifie la validité du formulaire de mise à jour d'un arrêté.
		f_modif_arr = GererArrete(request.POST, request.FILES, k_modif = True)

		if f_modif_arr.is_valid() :

			# Je récupère et nettoie les données du formulaire valide.
			cleaned_data = f_modif_arr.cleaned_data
			v_type_av_arr = nett_val(integer(cleaned_data['zl_type_av_arr']), True)
			v_num_arr = nett_val(cleaned_data['zs_num_arr'])
			v_dt_sign_arr = nett_val(cleaned_data['zd_dt_sign_arr'])
			v_dt_lim_encl_trav_arr = nett_val(cleaned_data['zd_dt_lim_encl_trav_arr'])
			v_obj_arr = nett_val(cleaned_data['zu_chem_pj_arr'])

			# Je remplis les données attributaires de l'objet TArretesDossier à modifier.
			obj_arr_doss.dt_lim_encl_trav_arr = v_dt_lim_encl_trav_arr
			obj_arr_doss.dt_sign_arr = v_dt_sign_arr
			obj_arr_doss.num_arr = v_num_arr
			obj_arr_doss.id_type_av_arr = TTypeAvancementArrete.objects.get(id_type_av_arr = v_type_av_arr)

			if v_obj_arr is not None :
				
				# Je tente d'effacer le fichier scanné de l'arrêté du serveur média vù qu'il est inutile.
				try :
					os.remove('{0}/{1}'.format(MEDIA_ROOT, obj_arr_doss.chem_pj_arr))
				except :
					pass

				# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
				n_fich = crypt_val('{0}-{1}'.format(request.user.id, time.strftime('%d%m%Y%H%M%S')))
				v_chem_pj_arr = 'dossiers/{0}/reglementations/{1}.pdf'.format(obj_arr_doss.id_doss.num_doss, n_fich)

				# J'uploade le fichier.
				upload_fich(v_obj_arr, v_chem_pj_arr)

				# Je mets à jour le chemin du fichier scanné de l'arrêté.
				obj_arr_doss.chem_pj_arr = v_chem_pj_arr	

			# Je mets à jour l'objet TArretesDossier.
			obj_arr_doss.save()

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'L\'arrêté a été modifié avec succès.',
					'redirect' : reverse('consulter_dossier', args = [obj_arr_doss.id_doss.id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_reglementations'

		else :

			# J'affiche les erreurs.
			reponse = HttpResponse(json.dumps(f_modif_arr.errors), content_type = 'application/json')

	return reponse

'''
Cette vue permet de supprimer un arrêté.
request : Objet requête
'''
@csrf_exempt
@verif_acces
def supprimer_arrete(request) :

	''' Imports '''
	from app.models import TArretesDossier, TDossier, TTypeDeclaration
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from styx.settings import MEDIA_ROOT
	import json
	import os

	reponse = HttpResponse()

	if request.method == 'POST' :
		if 'dossier' in request.GET and 'arrete' in request.GET :

			# Je vérifie l'existence d'un objet TDossier.
			try :
				obj_doss = TDossier.objects.get(id_doss = request.GET['dossier'])
			except :
				return HttpResponse()

			# Je vérifie l'existence d'un objet TTypeDeclaration.
			try :
				obj_arr = TTypeDeclaration.objects.get(id_type_decl = request.GET['arrete'])
			except :
				return HttpResponse()

			# Je récupère les arrêtés d'un dossier à supprimer (si tout va bien, un seul enregistrement sera repéré).
			les_arr_doss = TArretesDossier.objects.filter(
				id_doss = obj_doss.id_doss, id_type_decl = obj_arr.id_type_decl
			)

			# Je tente d'effacer le fichier de l'arrêté de chaque enregistrement du serveur média.
			for un_arr_doss in les_arr_doss :
				try :
					os.remove('{0}/{1}'.format(MEDIA_ROOT, un_arr_doss.chem_pj_arr))
				except :
					pass

			# Je supprime les objets TArretesDossier.
			les_arr_doss.delete()

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'L\'arrêté a été supprimé avec succès.',
					'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_reglementations'

	return reponse

'''
Gestion des financements
'''

'''
Cette vue permet soit de traiter le formulaire d'ajout d'un financement. 
request : Objet requête
'''
@verif_acces
def ajouter_financement(request) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererFinancement
	from app.functions import crypt_val, integer, nett_val, upload_fich
	from app.models import TDossier, TFinancement, TFinanceur, TPaiementPremierAcompte
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json
	import time

	reponse = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie la validité du formulaire d'ajout d'un financement.
		f_ajout_fin = GererFinancement(request.POST, request.FILES)

		if f_ajout_fin.is_valid() :

			# Je récupère et nettoie les données du formulaire valide.
			cleaned_data = f_ajout_fin.cleaned_data
			v_num_doss = nett_val(cleaned_data['za_num_doss'])
			v_org_fin = nett_val(integer(cleaned_data['zl_org_fin']), True)
			v_num_arr_fin = nett_val(cleaned_data['zs_num_arr_fin'])
			v_mont_ht_elig_fin = nett_val(cleaned_data['zs_mont_ht_elig_fin'])
			v_mont_ttc_elig_fin = nett_val(cleaned_data['zs_mont_ttc_elig_fin'])
			v_pourc_elig_fin = nett_val(float(cleaned_data['zs_pourc_elig_fin']) / 100)
			v_mont_ht_part_fin = nett_val(cleaned_data['zs_mont_ht_part_fin'])
			v_mont_ttc_part_fin = nett_val(cleaned_data['zs_mont_ttc_part_fin'])
			v_dt_deb_elig_fin = nett_val(cleaned_data['zd_dt_deb_elig_fin'])
			v_duree_valid_fin = nett_val(cleaned_data['zs_duree_valid_fin'])
			v_duree_pror_fin = nett_val(cleaned_data['zs_duree_pror_fin']) or 0
			v_dt_lim_deb_oper_fin = nett_val(cleaned_data['zd_dt_lim_deb_oper_fin'])
			v_dt_lim_prem_ac_fin = nett_val(cleaned_data['zd_dt_lim_prem_ac_fin'])
			v_paiem_prem_ac = nett_val(integer(cleaned_data['zl_paiem_prem_ac']), True)
			v_pourc_real_fin = nett_val(cleaned_data['zs_pourc_real_fin'])
			v_obj_fin = nett_val(cleaned_data['zu_chem_pj_fin'])
			v_comm_fin = nett_val(cleaned_data['zs_comm_fin'])

			# Je pointe vers l'objet TDossier consulté.
			obj_doss = TDossier.objects.get(num_doss = v_num_doss)
				
			if v_pourc_real_fin is not None :
				v_pourc_real_fin = float(v_pourc_real_fin) / 100

			# Je vérifie l'existence d'un objet TPaiementPremierAcompte.
			obj_paiem_prem_ac = None
			try :
				obj_paiem_prem_ac = TPaiementPremierAcompte.objects.get(id_paiem_prem_ac = v_paiem_prem_ac)
			except :
				pass

			# J'initialise l'objet TFinanceur.
			obj_fin = None
			if v_org_fin > 0 :
				obj_fin = TFinanceur.objects.get(id_org_fin = v_org_fin)

			if v_obj_fin is None :
				v_chem_pj_fin = None
			else :

				# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
				n_fich = crypt_val('{0}-{1}'.format(request.user.id, time.strftime('%d%m%Y%H%M%S')))
				v_chem_pj_fin = 'dossiers/{0}/plan_de_financement/{1}.pdf'.format(obj_doss.num_doss, n_fich)

				# J'uploade le fichier.
				upload_fich(v_obj_fin, v_chem_pj_fin)

			# Je remplis les données attributaires du nouvel objet TFinancement.
			obj_nv_fin = TFinancement(
				chem_pj_fin = v_chem_pj_fin,
				comm_fin = v_comm_fin,
				dt_deb_elig_fin = v_dt_deb_elig_fin,
				dt_lim_deb_oper_fin = v_dt_lim_deb_oper_fin,
				dt_lim_prem_ac_fin = v_dt_lim_prem_ac_fin,
				duree_pror_fin = v_duree_pror_fin,
				duree_valid_fin = v_duree_valid_fin,
				mont_ht_elig_fin = v_mont_ht_elig_fin,
				mont_ttc_elig_fin = v_mont_ttc_elig_fin,
				mont_ht_part_fin = v_mont_ht_part_fin,
				mont_ttc_part_fin = v_mont_ttc_part_fin,
				num_arr_fin = v_num_arr_fin,
				pourc_elig_fin = v_pourc_elig_fin,
				pourc_real_fin = v_pourc_real_fin,
				id_doss = obj_doss,
				id_org_fin = obj_fin,
				id_paiem_prem_ac = obj_paiem_prem_ac
			)

			# Je créé un nouvel objet TFinancement.
			obj_nv_fin.save()

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'Le financement a été ajouté avec succès.',
					'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_financements'

		else :

			# J'affiche les erreurs.
			reponse = HttpResponse(json.dumps(f_ajout_fin.errors), content_type = 'application/json')

	return reponse

'''
Gestion des prestations
'''

'''
Cette vue permet soit de traiter le formulaire d'ajout d'une prestation. 
request : Objet requête
'''
@verif_acces
def ajouter_prestation(request) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererPrestation
	from app.functions import conv_none
	from app.functions import crypt_val
	from app.functions import float_to_int
	from app.functions import integer
	from app.functions import nett_val
	from app.functions import reecr_dt
	from app.functions import upload_fich
	from app.models import TDossier, TNaturePrestation, TPrestataire, TPrestation, TPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json
	import time

	reponse = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie la validité du formulaire d'ajout d'une prestation.
		f_ajout_prest = GererPrestation(request.POST, request.FILES)

		if f_ajout_prest.is_valid() :

			# Je récupère et nettoie les données du formulaire valide.
			cleaned_data = f_ajout_prest.cleaned_data
			v_num_doss = nett_val(cleaned_data['za_num_doss'])
			v_siret_org_prest = nett_val(cleaned_data['zsac_siret_org_prest'])
			v_int_prest = nett_val(cleaned_data['zs_int_prest'])
			v_mont_ht_tot_prest = nett_val(cleaned_data['zs_mont_ht_tot_prest'])
			v_mont_ttc_tot_prest = nett_val(cleaned_data['zs_mont_ttc_tot_prest'])
			v_dt_notif_prest = nett_val(cleaned_data['zd_dt_notif_prest'])
			v_dt_fin_prest = nett_val(cleaned_data['zd_dt_fin_prest'])
			v_nat_prest = nett_val(integer(cleaned_data['zl_nat_prest']), True)
			v_obj_prest = nett_val(cleaned_data['zu_chem_pj_prest'])
			v_comm_prest = nett_val(cleaned_data['zs_comm_prest'])

			# Je pointe vers l'objet TDossier consulté.
			obj_doss = TDossier.objects.get(num_doss = v_num_doss)
					
			if v_obj_prest is None :
				v_chem_pj_prest = None
			else :

				# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
				n_fich = crypt_val('{0}-{1}'.format(request.user.id, time.strftime('%d%m%Y%H%M%S')))
				v_chem_pj_prest = 'dossiers/{0}/prestations/{1}.pdf'.format(obj_doss.num_doss, n_fich)
					
				# J'uploade le fichier.
				upload_fich(v_obj_prest, v_chem_pj_prest)

			# Je remplis les données attributaires du nouvel objet TPrestation.
			obj_nvelle_prest = TPrestation(
				chem_pj_prest = v_chem_pj_prest,
				comm_prest = v_comm_prest,
				dt_fin_prest = v_dt_fin_prest,
				dt_notif_prest = v_dt_notif_prest,
				int_prest = v_int_prest,
				mont_ht_tot_prest = v_mont_ht_tot_prest,
				mont_ttc_tot_prest = v_mont_ttc_tot_prest,
				id_nat_prest = TNaturePrestation.objects.get(id_nat_prest = v_nat_prest),
				id_org_prest = TPrestataire.objects.get(siret_org_prest = v_siret_org_prest)
			)

			# Je créé un nouvel objet TPrestation.
			obj_nvelle_prest.save()

			# Je fais le lien avec la table t_prestations_dossier.
			obj_nvelle_prest_doss = TPrestationsDossier.objects.create(
				id_doss = obj_doss,
				id_prest = obj_nvelle_prest,
				mont_ht_prest = v_mont_ht_tot_prest,
				mont_ttc_prest = v_mont_ttc_tot_prest
			)

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'La prestation a été ajoutée avec succès.',
					'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_prestations'

		else :

			# J'affiche les erreurs.
			reponse = HttpResponse(json.dumps(f_ajout_prest.errors), content_type = 'application/json')

	return reponse

'''
Cette vue permet d'afficher la page de consultation d'une prestation. 
request : Objet requête
p_prest : Identifiant de la prestation
'''
@nett_form
@verif_acces
def consulter_prestation(request, p_prest) :

	''' Imports '''
	from app.forms.gestion_dossiers import RechercherAvenants
	from app.functions import ajout_aven
	from app.functions import conv_none
	from app.functions import float_to_int
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import init_pg_cons
	from app.functions import integer
	from app.functions import nett_val
	from app.functions import reecr_dt
	from app.models import TAvenant, TPrestation, TPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404, render
	import json

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je vérifie l'existence d'un objet TPrestation.
		obj_prest = get_object_or_404(TPrestation, id_prest = p_prest)

		# J'instancie des objets "formulaire".
		f_rech_aven = RechercherAvenants(prefix = 'RechercherAvenants', k_prest = obj_prest.id_prest)

		# Je déclare le contenu de certaines fenêtres modales.
		tab_cont_fm = {
			'ajouter_avenant' : ajout_aven(
				request,
				'GET',
				obj_prest.id_prest, 
				None, 
				reverse('consulter_prestation', args = [obj_prest.id_prest]))
		}

		# Je déclare un tableau de fenêtres modales.
		tab_fm = [
			init_fm('ajouter_avenant', 'Ajouter un avenant', tab_cont_fm['ajouter_avenant'])
		]

		# Je prépare la page de consultation des caractéristiques d'une prestation.
		tab_attr_prest = {
			'n_org' : { 'label' : 'Prestataire', 'value' : conv_none(obj_prest.id_org_prest.n_org) },
			'int_prest' : { 'label' : 'Intitulé de la prestation', 'value' : conv_none(obj_prest.int_prest) },
			'mont_ht_tot_prest' :
			{
				'label' : 'Montant HT total de la prestation (en €)',
				'value' : float_to_int(conv_none(obj_prest.mont_ht_tot_prest))
			},
			'mont_ttc_tot_prest' :
			{
				'label' : 'Montant TTC total de la prestation (en €)',
				'value' : float_to_int(conv_none(obj_prest.mont_ttc_tot_prest))
			},
			'dt_notif_prest' :
			{
				'label' : 'Date de notification de la prestation',
				'value' : conv_none(reecr_dt(obj_prest.dt_notif_prest))
			},
			'dt_fin_prest' :
			{
				'label' : 'Date de fin de la prestation',
				'value' : conv_none(reecr_dt(obj_prest.dt_fin_prest))
			},
			'int_nat_prest' : 
			{
				'label' : 'Nature de la prestation',
				'value' : conv_none(obj_prest.id_nat_prest.int_nat_prest)
			},
			'comm_prest' : 
			{ 
				'label' : 'Commentaire', 'value' : conv_none(obj_prest.comm_prest), 'textarea' : True 
			}
		}

		# Je récupère les dossiers reliés à l'objet TPrestation.
		les_doss_prest = TPrestationsDossier.objects.filter(id_prest = obj_prest.id_prest).order_by(
			'id_doss__num_doss'
		)

		# Je stocke dans un tableau les données mises en forme de chaque dossier relié à l'objet TPrestation.
		tab_doss_prest = []
		for un_doss_prest in les_doss_prest :
			tab_doss_prest.append({
				'id_doss' : un_doss_prest.id_doss.id_doss,
				'num_doss' : conv_none(un_doss_prest.id_doss.num_doss),
				'mont_ht_prest' : float_to_int(conv_none(un_doss_prest.mont_ht_prest)),
			})

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/consulter_prestation.html',
			{
				'f1' : init_form(f_rech_aven),
				'la_prest' : obj_prest,
				'les_attr_prest' : init_pg_cons(tab_attr_prest),
				'les_doss_prest' : tab_doss_prest,
				'les_fm' : tab_fm,
				'title' : 'Consulter une prestation'
			}
		)

	else :

		# Je vérifie l'existence d'un objet TPrestation.
		obj_prest = None
		try :
			obj_prest = TPrestation.objects.get(id_prest = p_prest)
		except :
			return HttpResponse()

		if 'action' in request.GET :

			# Je retiens le nom du paramètre "GET".
			get_action = request.GET['action']

			# Je traite le cas où je dois ajouter un avenant.
			if get_action == 'ajouter-avenant' :
				reponse = ajout_aven(
					request,
					'POST',
					None,
					None,
					None,
					reverse('consulter_prestation', args = [obj_prest.id_prest]),
					'#ong_avenants'
				)

			# Je traite le cas où je dois rechercher les avenants d'un couple prestation/dossier.
			if get_action == 'rechercher-avenants' :

				# Je vérifie la validité du formulaire de recherche des avenants d'un dossier.
				f_rech_aven = RechercherAvenants(request.POST, k_prest = obj_prest.id_prest)

				if f_rech_aven.is_valid() :

					# Je récupère et nettoie les données du formulaire valide.
					cleaned_data = f_rech_aven.cleaned_data
					v_doss = nett_val(integer(cleaned_data['zl_doss']), True)

					# Je récupère les avenants d'un couple prestation/dossier.
					les_aven_prest = TAvenant.objects.filter(id_prest = obj_prest.id_prest, id_doss = v_doss).order_by(
						'dt_aven'
					)

					# Je prépare le contenu du tableau HTML des avenants d'un couple prestation/dossier.
					tab_aven_prest = []
					for index, un_aven_prest in enumerate(les_aven_prest) :
						tab_aven_prest.append([
							index + 1,
							conv_none(un_aven_prest.int_aven),
							conv_none(reecr_dt(un_aven_prest.dt_aven)),
							conv_none(float_to_int(un_aven_prest.mont_ht_aven))
						])

					# Je mets à jour le tableau HTML des avenants d'un couple prestation/dossier.
					reponse = HttpResponse(
						json.dumps({ 'success' : tab_aven_prest }), content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs.
					reponse = HttpResponse(json.dumps(f_rech_aven.errors), content_type = 'application/json')

	return reponse

'''
Gestion des factures
'''

'''
Cette vue permet soit de traiter le formulaire d'ajout d'une facture.
request : Objet requête
'''
@verif_acces
def ajouter_facture(request) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererFacture
	from app.functions import crypt_val
	from app.functions import integer
	from app.functions import nett_val
	from app.functions import upload_fich
	from app.models import TDossier, TFacture, TPrestation, TPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json
	import time

	reponse = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie la validité du formulaire d'ajout d'une facture.
		f_ajout_fact = GererFacture(request.POST, request.FILES)

		# Je rajoute un choix valide pour la liste déroulante des prestations d'un dossier (prévention d'erreurs).
		post_prest = request.POST.get('zl_prest')
		try :
			TPrestation.objects.get(id_prest = post_prest)
			f_ajout_fact.fields['zl_prest'].choices = [(post_prest, post_prest)]
		except :
			pass

		if f_ajout_fact.is_valid() :

			# Je récupère et nettoie les données du formulaire valide.
			cleaned_data = f_ajout_fact.cleaned_data
			v_num_doss = nett_val(cleaned_data['za_num_doss'])
			v_prest = nett_val(integer(cleaned_data['zl_prest']), True)
			v_num_fact = nett_val(cleaned_data['zs_num_fact'])
			v_dt_mand_moa_fact = nett_val(cleaned_data['zd_dt_mand_moa_fact'])
			v_mont_ht_fact = nett_val(cleaned_data['zs_mont_ht_fact'])
			v_mont_ttc_fact = nett_val(cleaned_data['zs_mont_ttc_fact'])
			v_dt_rec_fact = nett_val(cleaned_data['zd_dt_rec_fact'])
			v_num_mandat = nett_val(cleaned_data['zs_num_mandat'])
			v_num_bord = nett_val(cleaned_data['zs_num_bord'])
			v_suivi_fact = nett_val(integer(cleaned_data['zl_suivi_fact']), True)
			v_obj_fact = nett_val(cleaned_data['zu_chem_pj_fact'])
			v_comm_fact = nett_val(cleaned_data['zs_comm_fact'])

			# Je pointe vers l'objet TDossier consulté.
			obj_doss = TDossier.objects.get(num_doss = v_num_doss)

			# Je pointe vers un objet TPrestationsDossier.
			obj_prest_doss = TPrestationsDossier.objects.get(id_doss = obj_doss.id_doss, id_prest = v_prest)
			
			# J'initialise l'intitulé du suivi de la facture selon deux paramètres : la valeur de la liste déroulante
			# statique et le séquentiel relatif à la valeur de la liste déroulante statique.
			if v_suivi_fact == 1 :
				v_suivi_fact = 'Acompte {0}'.format(obj_prest_doss.seq_ac)
				obj_prest_doss.seq_ac = int(obj_prest_doss.seq_ac) + 1
			else :
				v_suivi_fact = 'Solde {0}'.format(obj_prest_doss.seq_solde)
				obj_prest_doss.seq_solde = int(obj_prest_doss.seq_solde) + 1

			if v_obj_fact is None :
				v_chem_pj_fact = None
			else :

				# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
				n_fich = crypt_val('{0}-{1}'.format(request.user.id, time.strftime('%d%m%Y%H%M%S')))
				v_chem_pj_fact = 'dossiers/{0}/factures/{1}.pdf'.format(obj_doss.num_doss, n_fich)

				# J'uploade le fichier.
				upload_fich(v_obj_fact, v_chem_pj_fact)

			# Je remplis les données attributaires du nouvel objet TFacture.
			obj_nvelle_fact = TFacture(
				chem_pj_fact = v_chem_pj_fact,
				comm_fact = v_comm_fact,
				dt_mand_moa_fact = v_dt_mand_moa_fact,
				dt_rec_fact = v_dt_rec_fact,
				mont_ht_fact = v_mont_ht_fact,
				mont_ttc_fact = v_mont_ttc_fact,
				num_bord = v_num_bord,
				num_fact = v_num_fact,
				num_mandat = v_num_mandat,
				suivi_fact = v_suivi_fact,
				id_doss = obj_doss,
				id_prest = TPrestation.objects.get(id_prest = v_prest)
			)

			# Je créé un nouvel objet TFacture.
			obj_nvelle_fact.save()

			# Je mets à jour l'objet TPrestationsDossier (séquentiel lié au suivi de la facture saisie).
			obj_prest_doss.save()

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'La facture a été ajoutée avec succès.',
					'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_factures'

		else :

			# J'affiche les erreurs.
			reponse = HttpResponse(json.dumps(f_ajout_fact.errors), content_type = 'application/json')

	return reponse

'''
Gestion des demandes de versements
'''

'''
Cette vue permet soit de traiter le formulaire d'ajout d'une demande de versement. 
request : Objet requête
'''
@verif_acces
def ajouter_demande_versement(request) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererDemandeDeVersement
	from app.functions import nett_val
	from app.models import TDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json

	reponse = HttpResponse()

	if request.method == 'POST' :

		# J'initialise la valeur du paramètre k_doss.
		v_id_doss = None
		try :
			v_id_doss = TDossier.objects.get(num_doss = request.POST['za_num_doss']).id_doss
		except :
			pass

		# Je vérifie la validité du formulaire d'ajout d'une demande de versement.
		f_ajout_ddv = GererDemandeDeVersement(request.POST, request.FILES, k_doss = v_id_doss)

		if f_ajout_ddv.is_valid() :

			# Je récupère et nettoie les données du formulaire valide.
			cleaned_data = f_ajout_ddv.cleaned_data
			v_num_doss = nett_val(cleaned_data['za_num_doss'])

			# Je pointe vers l'objet TDossier consulté.
			obj_doss = TDossier.objects.get(num_doss = v_num_doss)
				
			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'La demande de versement a été ajoutée avec succès.',
					'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = '#ong_demandes_versements'

		else :

			# J'affiche les erreurs.
			reponse = HttpResponse(json.dumps(f_ajout_ddv.errors), content_type = 'application/json')

	return reponse
