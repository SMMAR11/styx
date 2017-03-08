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

'''
Cette vue permet d'afficher le formulaire de réalisation d'un état en sélectionnant des dossiers ou de traiter l'une
des actions disponibles.
request : Objet requête
'''
@verif_acc
def select_doss(request) :

	# Imports
	from app.forms.realisation_etats import SelectionnerDossiers
	from app.functions import alim_ld
	from app.functions import dt_fr
	from app.functions import gen_cdc
	from app.functions import init_f
	from app.functions import obt_doss_regr
	from app.functions import suppr_doubl
	from app.models import TDossier
	from app.models import TFinancement
	from app.models import TPrestationsDossier
	from app.sql_views import VSuiviDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	from styx.settings import T_DONN_BDD_STR
	import csv
	import json

	output = HttpResponse()

	if request.method == 'GET' :
		if 'action' in request.GET :
			if request.GET['action'] == 'exporter-csv' :

				# Je génère le fichier CSV.
				output = HttpResponse(content_type = 'text/csv')
				output['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(gen_cdc())

				# Je m'autorise le droit d'écriture.
				writer = csv.writer(output, delimiter = ';')

				# J'initialise le tableau qui va aider à la conception du fichier CSV.
				t_lg = []
				if 'select_doss' in request.session :
					t_lg = request.session['select_doss']

				# Je commence à préparer la ligne "en-tête".
				header = [
					'Numéro du dossier',
					'Intitulé du dossier',
					'Dossier associé',
					'Maître d\'ouvrage',
					'Programme',
					'Axe',
					'Sous-axe',
					'Action',
					'Nature du dossier',
					'Type du dossier',
					'Agent responsable',
					'SAGE',
					'Montant du dossier présenté au CD GEMAPI (en €)',
					'Dépassement du dossier (en €)',
					'Montant total du dossier (en €)',
					'État d\'avancement',
					'Date de délibération au maître d\'ouvrage',
					'Avis du comité de programmation - CD GEMAPI',
					'Date de l\'avis du comité de programmation',
					'Commentaire'
				]

				# Je complète la ligne "en-tête" en cas d'utilisation du mode complet.
				if 'all' in request.GET and request.GET['all'] == 'true' :
					header.append('Organismes financiers')
					header.append('Prestataires')

				writer.writerow(header)

				for lg in t_lg :

					# Je pointe vers les objets TDossier et VSuiviDossier.
					o_doss = TDossier.objects.get(num_doss = lg[0])
					o_suivi_doss = VSuiviDossier.objects.get(pk = o_doss.pk)

					# Je commence à préparer la ligne courante.
					body = [
						o_doss,
						'{0} - {1} - {2} - {3}'.format(
							o_doss.id_nat_doss, o_doss.id_type_doss, o_doss.lib_1_doss, o_doss.lib_2_doss
						),
						o_doss.id_doss_ass,
						o_doss.id_org_moa,
						o_doss.id_progr,
						o_doss.num_axe,
						o_doss.num_ss_axe,
						o_doss.num_act,
						o_doss.id_nat_doss,
						o_doss.id_type_doss,
						o_doss.id_techn,
						o_doss.id_sage,
						o_doss.mont_doss,
						o_doss.mont_suppl_doss,
						o_suivi_doss.mont_tot_doss,
						o_doss.id_av,
						o_doss.dt_delib_moa_doss,
						o_doss.id_av_cp,
						o_doss.dt_av_cp_doss,
						o_doss.comm_doss
					]

					# Je complète la ligne courante en cas d'utilisation du mode complet.
					if 'all' in request.GET and request.GET['all'] == 'true' :
						qs_fin = TFinancement.objects.filter(id_doss = o_doss).order_by('id_org_fin')
						qs_prest = TPrestationsDossier.objects.filter(id_doss = o_doss).distinct(
							'id_prest__id_org_prest'
						)
						body.append(', '.join([str(f.id_org_fin) for f in qs_fin]))
						body.append(', '.join([str(p.id_prest.id_org_prest) for p in qs_prest]))

					writer.writerow(body)
		else :

			# J'initialise le tableau des dossiers sélectionnés.
			request.session['select_doss'] = []

			# J'instancie un objet "formulaire".
			f_select_doss = SelectionnerDossiers(prefix = 'SelectionnerDossiers')

			# J'affiche le template.
			output = render(request, './realisation_etats/select_doss.html', {
				'f_select_doss' : init_f(f_select_doss),
				'title' : 'Réalisation d\'états en sélectionnant des dossiers'
			})

	else :
		if 'action' in request.GET and request.GET['action'] == 'alimenter-listes' :

			# J'affiche ou je cache certaines listes déroulantes selon les données qu'elles contiennent.
			output = HttpResponse(json.dumps(alim_ld(request)), content_type = 'application/json')

		else :

			# Je soumets le formulaire.
			f_select_doss = SelectionnerDossiers(
				request.POST,
				prefix = 'SelectionnerDossiers',
				k_progr = request.POST.get('SelectionnerDossiers-zl_progr'),
				k_axe = request.POST.get('SelectionnerDossiers-zl_axe'),
				k_ss_axe = request.POST.get('SelectionnerDossiers-zl_ss_axe')
			)

			if f_select_doss.is_valid() :

				# Je récupère les données du formulaire valide.
				cleaned_data = f_select_doss.cleaned_data
				v_org_moa = cleaned_data.get('cbsm_org_moa')
				v_progr = cleaned_data.get('zl_progr')
				v_axe = cleaned_data.get('zl_axe')
				v_ss_axe = cleaned_data.get('zl_ss_axe')
				v_act = cleaned_data.get('zl_act')
				v_nat_doss = cleaned_data.get('zl_nat_doss')
				v_dt_deb_delib_moa_doss = cleaned_data.get('zd_dt_deb_delib_moa_doss')
				v_dt_fin_delib_moa_doss = cleaned_data.get('zd_dt_fin_delib_moa_doss')
				v_av_cp = cleaned_data.get('zl_av_cp')
				v_mont_doss_min = cleaned_data.get('zs_mont_doss_min')
				v_mont_doss_max = cleaned_data.get('zs_mont_doss_max')
				v_doss_dep_nn_sold = cleaned_data.get('cb_doss_dep_nn_sold')
				v_doss_ddv_nn_sold = cleaned_data.get('cb_doss_ddv_nn_sold')
				v_org_fin = cleaned_data.get('zl_org_fin')
				v_org_prest = cleaned_data.get('zl_org_prest')
				v_integr_doss_ass = cleaned_data.get('cb_integr_doss_ass')
				v_ajout_select_exist = cleaned_data.get('cb_ajout_select_exist')

				# J'initialise les conditions de la requête.
				t_sql = { 'and' : {}, 'or' : [] }
				if v_progr :
					t_sql['and']['id_progr'] = v_progr
					if v_axe :
						t_sql['and']['num_axe'] = v_axe.split('_')[-1]
						if v_ss_axe :
							t_sql['and']['num_ss_axe'] = v_ss_axe.split('_')[-1]
							if v_act :
								t_sql['and']['num_act'] = v_act.split('_')[-1]
				if v_nat_doss :
					t_sql['and']['id_nat_doss'] = v_nat_doss
				if v_dt_deb_delib_moa_doss :
					t_sql['and']['dt_delib_moa_doss__gte'] = v_dt_deb_delib_moa_doss
				if v_dt_fin_delib_moa_doss :
					t_sql['and']['dt_delib_moa_doss__lte'] = v_dt_fin_delib_moa_doss
				if v_av_cp :
					t_sql['and']['id_av_cp'] = v_av_cp
				if v_mont_doss_min :
					t_sql['and']['mont_doss__gte'] = v_mont_doss_min
				if v_mont_doss_max :
					t_sql['and']['mont_doss__lte'] = v_mont_doss_max
				if v_org_fin :
					t_sql['and']['tfinancement__id_org_fin'] = v_org_fin
				if v_org_prest :
					t_sql['and']['tprestationsdossier__id_prest__id_org_prest'] = v_org_prest

				# J'initialise le jeu de données des dossiers filtrés.
				qs_doss = TDossier.objects.none()
				for m in v_org_moa :
					qs_doss = qs_doss | obt_doss_regr(m).filter(**t_sql['and'])

				# Je complète le jeu de données des dossiers filtrés si je dois en plus ajouter les dossiers de chaque
				# famille.
				if v_integr_doss_ass == True :
					qs_doss_temp = TDossier.objects.none()
					for d in qs_doss :
						qs_doss_temp = qs_doss_temp | TDossier.objects.filter(id_fam = d.id_fam)
					qs_doss = qs_doss | qs_doss_temp

				# J'épure le jeu de données des dossiers filtrés en retirant les dossiers soldés.
				if v_doss_dep_nn_sold == True :
					qs_doss = qs_doss.exclude(id_av__int_av = T_DONN_BDD_STR['AV_SOLDE'])

				# Je prépare le tableau des dossiers filtrés.
				t_doss = [(
					str(d),
					'{0} - {1} - {2} - {3}'.format(d.id_nat_doss, d.id_type_doss, d.lib_1_doss, d.lib_2_doss),
					str(d.id_org_moa),
					dt_fr(d.dt_delib_moa_doss) or '-',
					'<a href="{0}" class="consult-icon pull-right" title="Consulter le dossier"></a>'.format(
						reverse('cons_doss', args = [d.pk])
					)
				) for d in qs_doss]

				# Je réinitialise le tableau des dossiers sélectionnés si l'option "Ajouter à la sélection existante"
				# est cochée.
				if v_ajout_select_exist == False :
					request.session['select_doss'] = []

				# J'empile le tableau des dossiers sélectionnés.
				for d in t_doss :
					request.session['select_doss'].append(d)

				# Je supprime les doublons du tableau des dossiers sélectionnés.
				request.session['select_doss'] = suppr_doubl(request.session['select_doss'])

				# J'envoie le tableau des dossiers filtrés.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'datatable' : request.session['select_doss']
					}}), content_type = 'application/json'
				)

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_select_doss.errors.items() :
					t_err['SelectionnerDossiers-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher le formulaire de réalisation d'un état en sélectionnant des prestations ou de traiter l'une
des actions disponibles.
request : Objet requête
'''
@verif_acc
def select_prest(request) :

	# Imports
	from app.forms.realisation_etats import SelectionnerPrestations
	from app.functions import alim_ld
	from app.functions import dt_fr
	from app.functions import gen_cdc
	from app.functions import init_f
	from app.functions import obt_mont
	from app.functions import suppr_doubl
	from app.models import TPrestation
	from app.models import TRegroupementsMoa
	from app.sql_views import VPrestation
	from app.sql_views import VSuiviPrestationsDossier
	from django.db.models import Count
	from django.db.models import Q
	from django.db.models import Sum
	from django.http import HttpResponse
	from django.shortcuts import render
	from functools import reduce
	import csv
	import json
	import operator

	output = HttpResponse()

	if request.method == 'GET' :
		if 'action' in request.GET :
			if request.GET['action'] == 'exporter-csv' :

				# Je génère le fichier CSV.
				output = HttpResponse(content_type = 'text/csv')
				output['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(gen_cdc())

				# Je m'autorise le droit d'écriture.
				writer = csv.writer(output, delimiter = ';')

				# J'initialise le tableau qui va aider à la conception du fichier CSV.
				t_lg = []
				if 'select_prest' in request.session :
					t_lg = request.session['select_prest']

				writer.writerow([
					'Prestataire',
					'Intitulé de la prestation',
					'Référence de la prestation',
					'Nombre de dossiers reliés à la prestation',
					'Dossier(s) relié(s) à la prestation',
					'Montant total de la prestation (en €)',
					'Reste à facturer total de la prestation (en €)',
					'Date de notification de la prestation',
					'Date de fin de la prestation',
					'Nature de la prestation',
					'Commentaire'
				])

				for lg in t_lg :

					# Je pointe vers l'objet TPrestation.
					o_prest = TPrestation.objects.get(pk = lg[0])

					qs_prest_doss = VSuiviPrestationsDossier.objects.filter(id_prest = o_prest)
					qs_aggr_prest_doss = qs_prest_doss.aggregate(Count('pk'), Sum('mont_prest_doss'), Sum('mont_raf'))

					writer.writerow([
						o_prest.id_org_prest,
						o_prest.int_prest,
						o_prest.ref_prest,
						qs_aggr_prest_doss['pk__count'],
						', '.join([str(pd.id_doss) for pd in qs_prest_doss]),
						qs_aggr_prest_doss['mont_prest_doss__sum'],
						qs_aggr_prest_doss['mont_raf__sum'],
						o_prest.dt_notif_prest,
						o_prest.dt_fin_prest,
						o_prest.id_nat_prest,
						o_prest.comm_prest
					])

		else :

			# J'initialise le tableau des dossiers sélectionnés.
			request.session['select_prest'] = []

			# J'instancie un objet "formulaire".
			f_select_prest = SelectionnerPrestations(prefix = 'SelectionnerPrestations')

			# J'affiche le template.
			output = render(request, './realisation_etats/select_prest.html', {
				'f_select_prest' : init_f(f_select_prest),
				'title' : 'Réalisation d\'états en sélectionnant des prestations'
			})

	else :
		if 'action' in request.GET and request.GET['action'] == 'alimenter-listes' :

			# J'affiche ou je cache certaines listes déroulantes selon les données qu'elles contiennent.
			output = HttpResponse(json.dumps(alim_ld(request)), content_type = 'application/json')

		else :

			# Je soumets le formulaire.
			f_select_prest = SelectionnerPrestations(
				request.POST,
				prefix = 'SelectionnerPrestations',
				k_progr = request.POST.get('SelectionnerPrestations-zl_progr'),
				k_axe = request.POST.get('SelectionnerPrestations-zl_axe'),
				k_ss_axe = request.POST.get('SelectionnerPrestations-zl_ss_axe')
			)

			if f_select_prest.is_valid() :

				# Je récupère les données du formulaire valide.
				cleaned_data = f_select_prest.cleaned_data
				v_org_prest = cleaned_data.get('zl_org_prest')
				v_org_moa = cleaned_data.get('cbsm_org_moa')
				v_progr = cleaned_data.get('zl_progr')
				v_axe = cleaned_data.get('zl_axe')
				v_ss_axe = cleaned_data.get('zl_ss_axe')
				v_act = cleaned_data.get('zl_act')
				v_dt_deb_notif_prest = cleaned_data.get('zd_dt_deb_notif_prest')
				v_dt_fin_notif_prest = cleaned_data.get('zd_dt_fin_notif_prest')
				v_nat_prest = cleaned_data.get('zl_nat_prest')
				v_mont_prest_min = cleaned_data.get('zs_mont_prest_min')
				v_mont_prest_max = cleaned_data.get('zs_mont_prest_max')
				v_mont_raf = cleaned_data.get('zs_mont_raf')
				v_dep = cleaned_data.get('zl_dep')
				v_ajout_select_exist = cleaned_data.get('cb_ajout_select_exist')

				# J'initialise les conditions de la requête.
				t_sql = { 'and' : {}, 'or' : [] }
				if v_org_prest :
					t_sql['and']['id_org_prest'] = v_org_prest
				if v_progr :
					t_sql['and']['tprestationsdossier__id_doss__id_progr'] = v_progr
					if v_axe :
						t_sql['and']['tprestationsdossier__id_doss__num_axe'] = v_axe.split('_')[-1]
						if v_ss_axe :
							t_sql['and']['tprestationsdossier__id_doss__num_ss_axe'] = v_ss_axe.split('_')[-1]
							if v_act :
								t_sql['and']['tprestationsdossier__id_doss__num_act'] = v_act.split('_')[-1]
				if v_dt_deb_notif_prest :
					t_sql['and']['dt_notif_prest__gte'] = v_dt_deb_notif_prest
				if v_dt_fin_notif_prest :
					t_sql['and']['dt_notif_prest__lte'] = v_dt_fin_notif_prest
				if v_nat_prest :
					t_sql['and']['id_nat_prest'] = v_nat_prest
				if v_dep :
					t_sql['and']['id_org_prest__num_dep'] = v_dep
				t_org_moa = []
				for m in v_org_moa :
					qs_regr_moa = TRegroupementsMoa.objects.filter(id_org_moa_fil = m)
					for rm in qs_regr_moa :
						t_org_moa.append(rm.id_org_moa_anc.pk)
					t_org_moa.append(m)
				if len(t_org_moa) > 0 :
					if len(t_org_moa) == 1 :
						t_sql['and']['tprestationsdossier__id_doss__id_org_moa'] = t_org_moa[0]
					else :
						for m in t_org_moa :
							t_sql['or'].append(Q(**{ 'tprestationsdossier__id_doss__id_org_moa' : m }))

				# Je débute l'initialisation de la requête.
				if len(t_sql['or']) > 0 :
					qs_prest = TPrestation.objects.filter(reduce(operator.or_, t_sql['or']), **t_sql['and'])
				else :
					qs_prest = TPrestation.objects.filter(**t_sql['and'])

				# Je termine l'initialisation de la requête.
				t_excl = [] 
				if v_mont_prest_min :
					t_excl[len(t_excl):] = [p.pk for p in VPrestation.objects.filter(
						mont_prest__lt = v_mont_prest_min
					)]
				if v_mont_prest_max :
					t_excl[len(t_excl):] = [p.pk for p in VPrestation.objects.filter(
						mont_prest__gt = v_mont_prest_max
					)]
				if v_mont_raf :
					for p in TPrestation.objects.all() :
						qs_aggr_prest_doss = VSuiviPrestationsDossier.objects.filter(id_prest = p).aggregate(
							Sum('mont_raf')
						)
						if qs_aggr_prest_doss['mont_raf__sum'] < v_mont_raf :
							t_excl.append(p.pk)
				qs_prest = qs_prest.exclude(pk__in = t_excl).order_by('id_org_prest', 'int_prest', 'dt_notif_prest')

				# Je prépare le tableau des prestations filtrées.
				t_prest = []
				for p in qs_prest :

					qs_aggr_prest_doss = VSuiviPrestationsDossier.objects.filter(id_prest = p).aggregate(
						Count('pk'), Sum('mont_prest_doss'), Sum('mont_raf')
					)

					t_prest.append((
						p.pk,
						str(p.id_org_prest),
						p.int_prest,
						dt_fr(p.dt_notif_prest),
						qs_aggr_prest_doss['pk__count'],
						obt_mont(qs_aggr_prest_doss['mont_prest_doss__sum']),
						obt_mont(qs_aggr_prest_doss['mont_raf__sum'])
					))

				# Je réinitialise le tableau des prestations sélectionnées si l'option "Ajouter à la sélection 
				# existante" est cochée.
				if v_ajout_select_exist == False :
					request.session['select_prest'] = []

				# J'empile le tableau des prestations sélectionnées.
				for p in t_prest :
					request.session['select_prest'].append(p)

				# Je supprime les doublons du tableau des prestations sélectionnées.
				request.session['select_prest'] = suppr_doubl(request.session['select_prest'])

				# Je "slice" le tableau de session afin de ne pas afficher l'identifiant de la prestation dans le
				# tableau HTML (utile pour la génération d'un fichier CSV).
				t_output = []
				for elem in request.session['select_prest'] :
					t_output.append(elem[1:])

				# J'envoie le tableau des prestations filtrées.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'datatable' : t_output
					}}), content_type = 'application/json'
				)

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_select_prest.errors.items() :
					t_err['SelectionnerPrestations-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output