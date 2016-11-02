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
	from app.functions import filtr_doss
	from app.functions import gen_tabl_chois_doss
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import integer
	from app.functions import nett_val
	from app.functions import reecr_dt
	from app.models import TAction
	from app.models import TAvancement
	from app.models import TAvisCp
	from app.models import TAxe
	from app.models import TDossier
	from app.models import TFamille
	from app.models import TMoa
	from app.models import TNatureDossier
	from app.models import TPgre
	from app.models import TPortee
	from app.models import TProgramme
	from app.models import TRiviere
	from app.models import TRivieresDossier
	from app.models import TSousAxe
	from app.models import TTechnicien
	from app.models import TTypeDossier
	from app.models import TUnite
	from datetime import date
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	from styx.settings import MEDIA_ROOT
	import json
	import os

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

					# Je prépare le contenu du tableau HTML des dossiers filtrés.
					tab_doss_filtr = []
					for un_doss in les_doss_filtr :
						tab_doss_filtr.append([
							conv_none(un_doss.num_doss),
							conv_none(un_doss.int_doss),
							conv_none(un_doss.id_org_moa.id_org_moa.n_org),
							conv_none(reecr_dt(un_doss.dt_delib_moa_doss)),
							'<span class="bt-choisir pointer pull-right" onclick="ajout_doss_ass(event)" title="Choisir le dossier"></span>'
						])

					# Je mets à jour le tableau HTML des dossiers filtrés.
					reponse = HttpResponse(json.dumps(
						{ 'success' : tab_doss_filtr }), content_type = 'application/json'
					)

			else :

				# J'alimente les listes déroulantes des axes, des sous-axes, des actions et des types de dossiers.
				reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

		else :

			# Je vérifie la validité du formulaire de création d'un dossier.
			f_creer_doss = GererDossier(request.POST)

			# Je rajoute un choix valide pour certaines listes déroulantes (prévention d'erreurs).
			post_progr = request.POST.get('zld_progr')
			post_axe = request.POST.get('zld_axe')
			post_ss_axe = request.POST.get('zld_ss_axe')
			post_act = request.POST.get('zld_act')
			post_type_doss = request.POST.get('zld_type_doss')

			axe_valide = False
			try :
				TAxe.objects.get(id_progr = post_progr, id_axe = post_axe)
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
				TSousAxe.objects.get(id_progr = post_progr, id_axe = post_axe, id_ss_axe = post_ss_axe)
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
					id_progr = post_progr, id_axe = post_axe, id_ss_axe = post_ss_axe, id_act = post_act
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
				TTypeDossier.objects.get(id_progr = post_progr, id_type_doss = post_type_doss)
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
				v_int_doss = nett_val(cleaned_data['zs_int_doss'])
				v_descr_doss = nett_val(cleaned_data['zs_descr_doss'])
				v_doss_ass = nett_val(cleaned_data['za_doss_ass'])
				v_org_moa = nett_val(integer(cleaned_data['zl_org_moa']), True)
				v_progr = nett_val(integer(cleaned_data['zld_progr']), True) 
				v_axe = nett_val(integer(cleaned_data['zld_axe']), True)
				v_ss_axe = nett_val(integer(cleaned_data['zld_ss_axe']), True)
				v_act = nett_val(integer(cleaned_data['zld_act']), True)
				v_type_doss = nett_val(integer(cleaned_data['zld_type_doss']), True)
				v_nat_doss = nett_val(integer(cleaned_data['zl_nat_doss']), True)
				v_techn = nett_val(integer(cleaned_data['zl_techn']), True)
				v_mont_ht_doss = nett_val(cleaned_data['zs_mont_ht_doss'])
				v_mont_ttc_doss = nett_val(cleaned_data['zs_mont_ttc_doss'])
				v_av = nett_val(integer(cleaned_data['zl_av']), True)
				v_dt_delib_moa_doss = nett_val(cleaned_data['zd_dt_delib_moa_doss'])
				v_av_cp = nett_val(integer(cleaned_data['zl_av_cp']), True)
				v_dt_av_cp_doss = nett_val(cleaned_data['zd_dt_av_cp_doss'])
				v_chem_dds_doss = nett_val(cleaned_data['zu_chem_dds_doss'])
				v_comm_doss = nett_val(cleaned_data['zs_comm_doss'])
				v_quant_objs_pgre = nett_val(cleaned_data['zs_quant_objs_pgre'])
				v_quant_real_pgre = nett_val(cleaned_data['zs_quant_real_pgre'])
				v_unit = nett_val(integer(cleaned_data['zl_unit']), True)
				v_tab_riv = request.POST.getlist('cbsm_riv')
				v_port = nett_val(integer(cleaned_data['zl_port']), True)

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

				# Je remplis les données attributaires du nouvel objet TDossier.
				obj_nv_doss = TDossier(
					chem_dds_doss = v_chem_dds_doss,
					comm_doss = v_comm_doss,
					descr_doss = v_descr_doss,
					dt_av_cp_doss = v_dt_av_cp_doss,
					dt_delib_moa_doss = v_dt_delib_moa_doss,
					dt_int_doss = date.today(),
					int_doss = v_int_doss,
					mont_ht_doss = v_mont_ht_doss,
					mont_ttc_doss = v_mont_ttc_doss,
					num_doss = v_num_doss,
					id_act = v_act,
					id_ss_axe = v_ss_axe,
					id_axe = v_axe,
					id_progr = TProgramme.objects.get(id_progr = v_progr),
					id_av = TAvancement.objects.get(id_av = v_av),
					id_av_cp = TAvisCp.objects.get(id_av_cp = v_av_cp),
					id_doss_ass = obj_doss_ass,
					id_fam = TFamille.objects.get(id_fam = v_fam),
					id_nat_doss = TNatureDossier.objects.get(id_nat_doss = v_nat_doss),
					id_org_moa = TMoa.objects.get(id_org_moa = v_org_moa),
					id_techn = TTechnicien.objects.get(id_techn = v_techn),
					id_type_doss = TTypeDossier.objects.get(id_type_doss = v_type_doss),				
				)

				# Je créé un nouvel objet TDossier.
				obj_nv_doss.save()

				# J'incrémente le séquentiel du programme renseigné.
				obj_progr_doss = TProgramme.objects.get(id_progr = v_progr)
				obj_progr_doss.seq_progr = int(obj_progr_doss.seq_progr) + 1
				obj_progr_doss.save()

				# Je fais le lien avec la table t_pgre si et seulement si l'intitulé du programme renseigné est "PGRE".
				if TProgramme.objects.get(id_progr = v_progr).int_progr == 'PGRE' :

					# Je vérifie l'existence d'un objet TUnite.
					obj_unit = None
					try :
						obj_unit = TUnite.objects.get(id_unit = v_unit)
					except :
						pass

					# Je vérifie l'existence d'un objet TPortee.
					obj_port = None
					try :
						obj_port = TPortee.objects.get(id_port = v_port)
					except :
						pass

					# Je remplis les données attributaires du nouvel objet TPgre.
					obj_nv_doss_pgre = TPgre(
						id_pgre = TDossier.objects.get(id_doss = obj_nv_doss.id_doss),
						quant_objs_pgre = v_quant_objs_pgre,
						quant_real_pgre = v_quant_real_pgre,
						id_port = obj_port,
						id_unit = obj_unit
					)

					# Je créé un nouvel objet TPgre.
					obj_nv_doss_pgre.save()

					# Je parcours le tableau des rivières sélectionnées.
					for i in range(0, len(v_tab_riv)) :

						# Je tente de convertir la valeur de la rivière courante en un nombre entier. Si celle-ci n'est
						# pas un nombre entier, alors elle prend -1.
						v_riv = integer(v_tab_riv[i])

						# Je créé un nouvel objet TRivieresDossier.
						if v_riv > 0 :
							obj_nvelle_riv_doss = TRivieresDossier.objects.create(
								id_pgre = TPgre.objects.get(id_pgre = obj_nv_doss_pgre),
								id_riv = TRiviere.objects.get(id_riv = v_riv)
							)

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
				request.session['menu_doss'] = '#ong_caracteristiques'

			else :

				# J'affiche les erreurs du formulaire.
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
	from app.functions import filtr_doss
	from app.functions import gen_tabl_chois_doss
	from app.functions import init_fm
	from app.functions import init_form
	from app.functions import integer
	from app.functions import nett_val
	from app.functions import reecr_dt
	from app.models import TAction
	from app.models import TAvancement
	from app.models import TAvisCp
	from app.models import TAxe
	from app.models import TDossier
	from app.models import TFamille
	from app.models import TMoa
	from app.models import TNatureDossier
	from app.models import TPgre
	from app.models import TPortee
	from app.models import TProgramme
	from app.models import TRiviere
	from app.models import TRivieresDossier
	from app.models import TSousAxe
	from app.models import TTechnicien
	from app.models import TTypeDossier
	from app.models import TUnite
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404, render
	import json

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

				# Je prépare le contenu du tableau HTML des dossiers filtrés.
				tab_doss_filtr = []
				for un_doss in les_doss_filtr :
					tab_doss_filtr.append([
						conv_none(un_doss.num_doss),
						conv_none(un_doss.int_doss),
						conv_none(un_doss.id_org_moa.id_org_moa.n_org),
						conv_none(reecr_dt(un_doss.dt_delib_moa_doss)),
						'<span class="bt-choisir pointer pull-right" onclick="ajout_doss_ass(event)" title="Choisir le dossier"></span>'
					])

				# Je mets à jour le tableau HTML des dossiers filtrés.
				reponse = HttpResponse(json.dumps(
					{ 'success' : tab_doss_filtr }), content_type = 'application/json'
				)

			# Je traite le cas où je veux modifier l'onglet "Caractéristiques".
			elif get_action == 'modifier-caracteristiques' :

				# Je vérifie la validité du formulaire de modification d'un dossier.
				f_modif_doss = GererDossier(request.POST)

				# Je rajoute un choix valide pour certaines listes déroulantes (prévention d'erreurs).
				post_progr = request.POST.get('zld_progr')
				post_axe = request.POST.get('zld_axe')
				post_ss_axe = request.POST.get('zld_ss_axe')
				post_act = request.POST.get('zld_act')
				post_type_doss = request.POST.get('zld_type_doss')

				axe_valide = False
				try :
					TAxe.objects.get(id_progr = post_progr, id_axe = post_axe)
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
					TSousAxe.objects.get(id_progr = post_progr, id_axe = post_axe, id_ss_axe = post_ss_axe)
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
						id_progr = post_progr, id_axe = post_axe, id_ss_axe = post_ss_axe, id_act = post_act
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
					TTypeDossier.objects.get(id_progr = post_progr, id_type_doss = post_type_doss)
					type_doss_valide = True
				except :
					if post_type_doss == 'D' :
						type_doss_valide = True
					else :
						pass

				if type_doss_valide == True :
					f_modif_doss.fields['zld_type_doss'].choices = [(post_type_doss, post_type_doss)]

				if f_modif_doss.is_valid() :

					# Je récupère et nettoie les données du formulaire valide.
					cleaned_data = f_modif_doss.cleaned_data
					v_int_doss = nett_val(cleaned_data['zs_int_doss'])
					v_descr_doss = nett_val(cleaned_data['zs_descr_doss'])
					v_doss_ass = nett_val(cleaned_data['za_doss_ass'])
					v_org_moa = nett_val(integer(cleaned_data['zl_org_moa']), True)
					v_progr = nett_val(integer(cleaned_data['zld_progr']), True) 
					v_axe = nett_val(integer(cleaned_data['zld_axe']), True)
					v_ss_axe = nett_val(integer(cleaned_data['zld_ss_axe']), True)
					v_act = nett_val(integer(cleaned_data['zld_act']), True)
					v_type_doss = nett_val(integer(cleaned_data['zld_type_doss']), True)
					v_nat_doss = nett_val(integer(cleaned_data['zl_nat_doss']), True)
					v_techn = nett_val(integer(cleaned_data['zl_techn']), True)
					v_mont_ht_doss = nett_val(cleaned_data['zs_mont_ht_doss'])
					v_mont_ttc_doss = nett_val(cleaned_data['zs_mont_ttc_doss'])
					v_av = nett_val(integer(cleaned_data['zl_av']), True)
					v_dt_delib_moa_doss = nett_val(cleaned_data['zd_dt_delib_moa_doss'])
					v_av_cp = nett_val(integer(cleaned_data['zl_av_cp']), True)
					v_dt_av_cp_doss = nett_val(cleaned_data['zd_dt_av_cp_doss'])
					v_chem_dds_doss = nett_val(cleaned_data['zu_chem_dds_doss'])
					v_comm_doss = nett_val(cleaned_data['zs_comm_doss'])
					v_quant_objs_pgre = nett_val(cleaned_data['zs_quant_objs_pgre'])
					v_quant_real_pgre = nett_val(cleaned_data['zs_quant_real_pgre'])
					v_unit = nett_val(integer(cleaned_data['zl_unit']), True)
					v_tab_riv = request.POST.getlist('cbsm_riv')
					v_port = nett_val(integer(cleaned_data['zl_port']), True)

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

					# Je remplis les données attributaires de l'objet TDossier à modifier.
					obj_doss.chem_dds_doss = v_chem_dds_doss
					obj_doss.comm_doss = v_comm_doss
					obj_doss.descr_doss = v_descr_doss
					obj_doss.dt_av_cp_doss = v_dt_av_cp_doss
					obj_doss.dt_delib_moa_doss = v_dt_delib_moa_doss
					obj_doss.int_doss = v_int_doss
					obj_doss.mont_ht_doss = v_mont_ht_doss
					obj_doss.mont_ttc_doss = v_mont_ttc_doss
					obj_doss.id_act = v_act
					obj_doss.id_ss_axe = v_ss_axe
					obj_doss.id_axe = v_axe
					obj_doss.id_progr = TProgramme.objects.get(id_progr = v_progr)
					obj_doss.id_av = TAvancement.objects.get(id_av = v_av)
					obj_doss.id_av_cp = TAvisCp.objects.get(id_av_cp = v_av_cp)
					obj_doss.id_doss_ass = obj_doss_ass
					obj_doss.id_fam = TFamille.objects.get(id_fam = v_fam)
					obj_doss.id_nat_doss = TNatureDossier.objects.get(id_nat_doss = v_nat_doss)
					obj_doss.id_org_moa = TMoa.objects.get(id_org_moa = v_org_moa)
					obj_doss.id_techn = TTechnicien.objects.get(id_techn = v_techn)
					obj_doss.id_type_doss = TTypeDossier.objects.get(id_type_doss = v_type_doss)

					# Je mets à jour l'objet TDossier.
					obj_doss.save()

					# Je supprime les familles vierges.
					for une_fam in TFamille.objects.all() :
						try :
							une_fam.delete()
						except :
							pass

					# Je fais le lien avec la table t_pgre si et seulement si l'intitulé du programme renseigné est "PGRE".
					if TProgramme.objects.get(id_progr = v_progr).int_progr == 'PGRE' :

						# Je vérifie l'existence d'un objet TUnite.
						obj_unit = None
						try :
							obj_unit = TUnite.objects.get(id_unit = v_unit)
						except :
							pass

						# Je vérifie l'existence d'un objet TPortee.
						obj_port = None
						try :
							obj_port = TPortee.objects.get(id_port = v_port)
						except :
							pass

						# Je remplis les données attributaires de l'objet TPgre à modifier.
						obj_doss_pgre = TPgre.objects.get(id_pgre = obj_doss.id_doss)
						obj_doss_pgre.quant_objs_pgre = v_quant_objs_pgre
						obj_doss_pgre.quant_real_pgre = v_quant_real_pgre
						obj_doss_pgre.id_port = obj_port
						obj_doss_pgre.id_unit = obj_unit

						# Je mets à jour l'objet TPgre dans la base de données.
						obj_doss_pgre.save()

						# Je supprime tous les objets TRivieresDossier dont l'identifiant du dossier PGRE est celui du
						# dossier en cours de modification.
						TRivieresDossier.objects.filter(id_pgre = TPgre.objects.get(id_pgre = obj_doss_pgre)).delete()

						# Je parcours le tableau des rivières sélectionnées.
						for i in range(0, len(v_tab_riv)) :

							# Je tente de convertir la valeur de la rivière courante en un nombre entier. Si celle-ci n'est
							# pas un nombre entier, alors elle prend -1.
							v_riv = integer(v_tab_riv[i])

							# Je créé un nouvel objet TRivieresDossier.
							if v_riv > 0 :
								obj_nvelle_riv_doss = TRivieresDossier.objects.create(
									id_pgre = TPgre.objects.get(id_pgre = obj_doss_pgre),
									id_riv = TRiviere.objects.get(id_riv = v_riv)
								)

					# J'affiche le message de succès.
					reponse = HttpResponse(
						json.dumps({
							'success' : 'Le dossier a été mis à jour avec succès.',
							'redirect' : reverse('consulter_dossier', args = [obj_doss.id_doss])
						}),
						content_type = 'application/json'
					)

					# Je renseigne l'onglet actif après rechargement de la page.
					request.session['menu_doss'] = '#ong_caracteristiques'

				else :

					# J'affiche les erreurs du formulaire.
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
					request.session['menu_doss'] = '#ong_reglementations'

				else :

					# J'affiche les erreurs du formulaire.
					reponse = HttpResponse(json.dumps(f_modif_doss.errors), content_type = 'application/json')

		else :

			# J'alimente les listes déroulantes des axes, des sous-axes, des actions et des types de dossiers.
			reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

	return reponse

'''
Cette vue permet de supprimer un dossier.
request : Objet requête
p_dossier : Identifiant du dossier à supprimer
'''
@csrf_exempt
@verif_acces
def supprimer_dossier(request, p_dossier) :

	''' Imports '''
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json

	reponse = None

	if request.method == 'POST' :

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
		for un_doss in TDossier.objects.order_by('-dt_delib_moa_doss', 'num_doss') :
			tab_doss.append({
				'id_doss' : un_doss.id_doss,
				'num_doss' : conv_none(un_doss.num_doss),
				'int_doss' : conv_none(un_doss.int_doss),
				'n_moa' : conv_none(un_doss.id_org_moa.id_org_moa.n_org),
				'dt_delib_moa_doss' : conv_none(reecr_dt(un_doss.dt_delib_moa_doss))
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

				# Je prépare le contenu du tableau HTML des dossiers filtrés.
				tab_doss_filtr = []
				for un_doss in les_doss_filtr :
					tab_doss_filtr.append([
						conv_none(un_doss.num_doss),
						conv_none(un_doss.int_doss),
						conv_none(un_doss.id_org_moa.id_org_moa.n_org),
						conv_none(reecr_dt(un_doss.dt_delib_moa_doss)),
						'<a href="{0}" class="bt-consulter pull-right" title="Consulter le dossier"></a>'.format(
							reverse('consulter_dossier', args = [un_doss.id_doss])
						)
					])

				# Je mets à jour le tableau HTML des dossiers filtrés.
				reponse = HttpResponse(json.dumps({ 'success' : tab_doss_filtr }), content_type = 'application/json')

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
	from app.forms.gestion_dossiers import GererDossier_Reglementation, GererPhoto
	from app.functions import aff_mess_suppr, conv_none, float_to_int, init_fm, init_form, init_pg_cons, reecr_dt
	from app.models import TArretesDossier, TDossier, TPgre, TPhoto, TPortee, TRivieresDossier, TTypeDeclaration, TUnite
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404, render
	from django.template.context_processors import csrf
	from styx.settings import MEDIA_URL

	reponse = HttpResponse()

	if request.method == 'GET' :

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = get_object_or_404(TDossier, id_doss = p_doss)

		# J'instancie des objets "formulaire".
		f_modif_doss = GererDossier_Reglementation(prefix = 'ModifierDossier', k_doss = obj_doss.id_doss)
		f_ajout_ph = GererPhoto(prefix = 'AjouterPhoto', k_doss = obj_doss.id_doss)

		# J'initialise les champs de certains formulaires.
		tab_ajout_ph = init_form(f_ajout_ph)

		# Je déclare le contenu de certaines fenêtres modales.
		tab_cont_fm = {
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
			)
		}

		# Je déclare un tableau de fenêtres modales.
		tab_fm = [
			init_fm('afficher_photo', 'Consulter une photo'),
			init_fm('ajouter_photo', 'Ajouter une photo', tab_cont_fm['ajouter_photo']),
			init_fm('modifier_dossier', 'Modifier un dossier'),
			init_fm('supprimer_arrete', 'Êtes-vous certain de supprimer cet arrêté ?'),
			init_fm('supprimer_dossier', 'Êtes-vous certain de supprimer ce dossier ?'),
			init_fm('supprimer_photo', 'Êtes-vous certain de supprimer cette photo ?')
		]

		# Je vérifie l'existence d'un objet TPgre.
		obj_doss_pgre = None
		try :
			obj_doss_pgre = TPgre.objects.get(id_pgre = obj_doss.id_doss)
		except :
			pass

		# J'initialise la valeur de certains attributs.
		v_quant_objs_pgre = None
		v_quant_real_pgre = None
		v_unit = None
		v_riv = None
		v_port = None

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

			# Je tente de récupérer la valeur de la portée du dossier.
			try :
				v_port = TPortee.objects.get(id_port = obj_doss_pgre.id_port.id_port).int_port
			except :
				pass

		# Je prépare la page de consultation des caractéristiques d'un dossier.
		tab_attr_doss = {
			'num_doss' : { 'label' : 'Numéro du dossier', 'value' : conv_none(obj_doss.num_doss) },
			'int_doss' : { 'label' : 'Intitulé du dossier', 'value' : conv_none(obj_doss.int_doss) },
			'n_org' : { 'label' : 'Maître d\'ouvrage', 'value' : conv_none(obj_doss.id_org_moa.id_org_moa.n_org) },
			'int_progr' : { 'label' : 'Programme', 'value' : conv_none(obj_doss.id_progr.int_progr) },
			'id_axe' : { 'label' : 'Axe', 'value' : conv_none(obj_doss.id_axe) },
			'id_ss_axe' : { 'label' : 'Sous-axe', 'value' : conv_none(obj_doss.id_ss_axe) },
			'id_act' : { 'label' : 'Action', 'value' : conv_none(obj_doss.id_act) },
			'int_type_doss' :
			{
				'label' : 'Type du dossier', 'value' : conv_none(obj_doss.id_type_doss.int_type_doss)
			},
			'int_nat_doss' :
			{
				'label' : 'Nature du dossier', 'value' : conv_none(obj_doss.id_nat_doss.int_nat_doss)
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
			'descr_doss' : 
			{
				'label' : 'Description du dossier et de ses objectifs',
				'value' : conv_none(obj_doss.descr_doss)
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
			'int_port' : { 'label' : 'Portée du dossier', 'value' : conv_none(v_port) }
		}

		# Je récupère les dossiers appartenant à la même famille que le dossier consulté.
		les_doss_fam = TDossier.objects.filter(id_fam = obj_doss.id_fam.id_fam).exclude(
			id_doss = obj_doss.id_doss
		).order_by('-dt_delib_moa_doss', 'num_doss')

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
				'int_doss' : conv_none(un_doss_fam.int_doss),
				'n_moa' : conv_none(un_doss_fam.id_org_moa.id_org_moa.n_org),
				'dt_delib_moa_doss' : conv_none(reecr_dt(un_doss_fam.dt_delib_moa_doss)),
				'int_progr' : conv_none(un_doss_fam.id_progr.int_progr),
				'int_nat_doss' : conv_none(un_doss_fam.id_nat_doss.int_nat_doss),
				'est_ass' : est_ass
			})

		# Je stocke les différents types de déclarations.
		les_arr = TTypeDeclaration.objects.order_by('id_type_decl')

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
					<div class="icon-link">
						<div><span class="bt-ajouter"></span></div>
						<div><a href="{0}">Ajouter</a></div>
					</div>
				</div>
				'''.format(reverse('ajouter_arrete', args = [obj_doss.id_doss, un_arr.id_type_decl]))
			else :
				opt_dispo = '''
				<div class="col-xs-3">
					<div class="icon-link">
						<div><span class="bt-modifier"></span></div>
						<div><a href="{0}">Modifier</a></div>
					</div>
				</div>
				<div class="col-xs-3">
					<div class="icon-link">
						<div><span class="bt-supprimer"></span></div>
						<div><span class="bt_supprimer_arrete" data-target="#fm_supprimer_arrete" action="{1}?action=supprimer-arrete&dossier={2}&arrete={3}">Supprimer</span></div>
					</div>
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
						<div class="icon-link">
							<div><span class="bt-pdf"></span></div>
							<div><a href="{0}" target="blank">Consulter le fichier de l'arrêté</a></div>
						</div>
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

		# Je récupère les photos d'un dossier.
		les_ph = TPhoto.objects.filter(id_doss = obj_doss.id_doss).order_by('-dt_pv_ph')

		# Je stocke dans un tableau les données mises en forme de chaque photo d'un dossier.
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
				'les_attr_doss' : init_pg_cons(tab_attr_doss),
				'les_doss_fam' : tab_doss_fam,
				'les_fm' : tab_fm,
				'les_ph' : tab_ph,
				'les_arr' : cont_regl,
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
				contenu = aff_mess_suppr('{0}?photo={1}'.format(
					reverse('supprimer_photo'),
					request.GET['photo']
				))

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
					'num_ph' : { 'label' : 'Numéro de la photo', 'value' : conv_none(obj_ph.num_ph) },
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
				contenu = '''
				<div class="attribute-wrapper text-center">
					<img src="{0}" style="width: 480px;"/>
				</div>
				<div class="row">
					<div class="col-xs-6">{1}</div>
					<div class="col-xs-6">{2}</div>
				</div>
				<div class="row">
					<div class="col-xs-6">{3}</div>
					<div class="col-xs-6">{4}</div>
				</div>
				<div class="row">
					<div class="col-xs-6">{5}</div>
					<div class="col-xs-6">{6}</div>
				</div>
				'''.format(
					MEDIA_URL + obj_ph.chem_ph,
					tab_attr_ph['num_doss'],
					tab_attr_ph['num_ph'],
					tab_attr_ph['int_ph'],
					tab_attr_ph['descr_ph'],
					tab_attr_ph['int_ppv_ph'],
					tab_attr_ph['dt_pv_ph']
				)

			# Je traite le cas où je veux supprimer un dossier.
			if get_action == 'supprimer-dossier' :

				# Je prépare la réponse AJAX.
				contenu = aff_mess_suppr(reverse('supprimer_dossier', args = [obj_doss.id_doss]))

			# Je traite le cas où je veux délier un arrêté pour un dossier.
			if get_action == 'supprimer-arrete' and 'dossier' in request.GET and 'arrete' in request.GET :

				# Je prépare la réponse AJAX.
				contenu = aff_mess_suppr('{0}?dossier={1}&arrete={2}'.format(
					reverse('supprimer_arrete'), request.GET['dossier'], request.GET['arrete']
				))

			# Je récupère la réponse AJAX.
			reponse = HttpResponse(contenu)

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

			# J'initialise le nom du fichier uploadé ainsi que le chemin de destination.
			n_fich = crypt_val('{0}-{1}'.format(request.session['util']['id_util'], time.strftime('%d%m%Y%H%M%S')))
			v_chem_ph = 'dossiers/{0}/photos/{1}.jpg'.format(obj_doss.num_doss, n_fich)

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
			request.session['menu_doss'] = '#ong_photos'

		else :

			# J'affiche les erreurs du formulaire d'insertion d'une photo.
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
			request.session['menu_doss'] = '#ong_photos'

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
			n_fich = crypt_val('{0}-{1}'.format(request.session['util']['id_util'], time.strftime('%d%m%Y%H%M%S')))
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
			request.session['menu_doss'] = '#ong_reglementations'

		else :

			# J'affiche les erreurs du formulaire.
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
	from django.http import HttpResponse

	reponse = HttpResponse()

	if request.method == 'GET' :
		reponse = HttpResponse('TODO')
	else :
		reponse = HttpResponse('TODO')
			
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
			request.session['menu_doss'] = '#ong_reglementations'

	return reponse