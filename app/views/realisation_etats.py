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
	from app.forms.realisation_etats import RechercherDossiers
	from app.functions import alim_ld
	from app.functions import gen_cdc
	from app.functions import init_f
	from app.functions import obt_doss_regr
	from app.functions import obt_mont
	from app.functions import suppr_doubl
	from app.models import TDossier
	from app.models import TFinancement
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
				output = HttpResponse(content_type = 'text/csv', charset = 'cp1252')
				output['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(gen_cdc())

				# Je m'autorise le droit d'écriture.
				writer = csv.writer(output, delimiter = ';')

				# J'initialise le tableau qui va aider à la conception du fichier CSV.
				t_lg = []
				if 'select_doss' in request.session :
					t_lg = request.session['select_doss']

				# Écriture de l'en-tête
				writer.writerow([
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
					'Mode de taxe du dossier',
					'État d\'avancement',
					'Date de délibération au maître d\'ouvrage',
					'Avis du comité de programmation - CD GEMAPI',
					'Date de l\'avis du comité de programmation',
					'Commentaire',
					'Organismes financiers'
				])

				for lg in t_lg :

					# Je pointe vers les objets TDossier et VSuiviDossier.
					o_doss = TDossier.objects.get(num_doss = lg[0])
					o_suivi_doss = VSuiviDossier.objects.get(pk = o_doss.pk)

					body = [
						o_doss,
						o_doss.get_int_doss(),
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
						'TTC' if o_doss.est_ttc_doss == True else 'HT',
						o_doss.id_av,
						o_doss.dt_delib_moa_doss,
						o_doss.id_av_cp,
						o_doss.dt_av_cp_doss,
						o_doss.comm_doss,
					]

					for f in TFinancement.objects.filter(id_doss = o_doss).order_by('id_org_fin') :
						body.append('{0} : {1} €'.format(f.id_org_fin, f.mont_part_fin))

					# Écriture d'une ligne
					writer.writerow(body)
		else :

			# J'initialise le tableau des dossiers sélectionnés.
			request.session['select_doss'] = []

			# J'instancie un objet "formulaire".
			f_select_doss = RechercherDossiers(prefix = 'RechercherDossiers')

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
			f_select_doss = RechercherDossiers(
				request.POST,
				prefix = 'RechercherDossiers',
				k_progr = request.POST.get('RechercherDossiers-zl_progr'),
				k_axe = request.POST.get('RechercherDossiers-zl_axe'),
				k_ss_axe = request.POST.get('RechercherDossiers-zl_ss_axe')
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
				v_dt_deb_av_cp_doss = cleaned_data.get('zd_dt_deb_av_cp_doss')
				v_dt_fin_av_cp_doss = cleaned_data.get('zd_dt_fin_av_cp_doss')
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
				if v_dt_deb_av_cp_doss :
					t_sql['and']['dt_av_cp_doss__gte'] = v_dt_deb_av_cp_doss
				if v_dt_fin_av_cp_doss :
					t_sql['and']['dt_av_cp_doss__lte'] = v_dt_fin_av_cp_doss
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
					d.get_int_doss(),
					str(d.id_org_moa),
					VSuiviDossier.objects.get(pk = d.pk).mont_tot_doss,
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

				# Je prépare le tableau de sortie.
				t_output = []
				for elem in request.session['select_doss'] :
					t_output.append([elem_2 for elem_2 in elem])

				# Je prépare le tableau relatif à la balise <tfoot/> de la datatable.
				tab_tfoot = ['Total', '', '', obt_mont(sum(elem[3] for elem in t_output)), '']

				# Je mets en forme le tableau de sortie.
				for elem in t_output :
					elem[3] = obt_mont(elem[3])

				# J'envoie le tableau des dossiers filtrés.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'datatable' : t_output, 'datatable_tfoot' : tab_tfoot
					}}), content_type = 'application/json'
				)

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_select_doss.errors.items() :
					t_err['RechercherDossiers-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher le formulaire de réalisation d'un état en sélectionnant des prestations ou de traiter l'une
des actions disponibles.
request : Objet requête
'''
@verif_acc
def regr_prest(request) :

	# Imports
	from app.forms.realisation_etats import RechercherPrestations
	from app.functions import alim_ld
	from app.functions import gen_cdc
	from app.functions import init_f
	from app.functions import obt_mont
	from app.functions import obt_pourc
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
				output = HttpResponse(content_type = 'text/csv', charset = 'cp1252')
				output['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(gen_cdc())

				# Je m'autorise le droit d'écriture.
				writer = csv.writer(output, delimiter = ';')

				# J'initialise le tableau qui va aider à la conception du fichier CSV.
				t_lg = []
				if 'regr_prest' in request.session :
					t_lg = request.session['regr_prest']

				writer.writerow([
					'Prestataire',
					'Nombre de prestations',
					'Montant cumulé des prestations (en €)',
					'Reste à facturer cumulé (en €)',
					'Nombre de prestations en cours',
					'Montant cumulé des prestations en cours (en €)',
					'Nombre de prestations clôturées',
					'Montant cumulé des prestations clôturées (en €)',
					'Indice de contractualisation (en %)'
				])

				mont_tot_prest = sum(elem[3] for elem in t_lg)
				for lg in t_lg :

					# Je récupère les prestations effectuées pour un prestataire.
					split = lg[0].split(';')

					mont_cumul_prest = [0, 0]
					nb_prest = [0, 0]
					for elem in split :

						# Je pointe vers l'objet TPrestation.
						o_prest = TPrestation.objects.get(pk = elem)

						# Je stocke le cumul des prestations ainsi que le cumul des restes à facturer lié à la
						# prestation courante.
						qs_aggr_prest_doss = VSuiviPrestationsDossier.objects.filter(id_prest = o_prest).aggregate(
							Sum('mont_prest_doss'), Sum('mont_raf')
						)

						# Je vérifie si la prestation courante est clôturée ou non.
						ind = 0
						if qs_aggr_prest_doss['mont_raf__sum'] == 0 :
							ind = 1
						mont_cumul_prest[ind] += qs_aggr_prest_doss['mont_prest_doss__sum']
						nb_prest[ind] += 1

					writer.writerow([
						lg[1],
						lg[2],
						lg[3],
						lg[4],
						nb_prest[0],
						mont_cumul_prest[0],
						nb_prest[1],
						mont_cumul_prest[1],
						obt_pourc((lg[3] / mont_tot_prest) * 100)
					])

		else :

			# J'initialise le tableau des dossiers sélectionnés.
			request.session['regr_prest'] = []

			# J'instancie un objet "formulaire".
			f_regr_prest = RechercherPrestations(prefix = 'RechercherPrestations')

			# J'affiche le template.
			output = render(request, './realisation_etats/regr_prest.html', {
				'f_regr_prest' : init_f(f_regr_prest),
				'title' : 'Réalisation d\'états en regroupant des prestations'
			})

	else :
		if 'action' in request.GET and request.GET['action'] == 'alimenter-listes' :

			# J'affiche ou je cache certaines listes déroulantes selon les données qu'elles contiennent.
			output = HttpResponse(json.dumps(alim_ld(request)), content_type = 'application/json')

		else :

			# Je soumets le formulaire.
			f_regr_prest = RechercherPrestations(
				request.POST,
				prefix = 'RechercherPrestations',
				k_progr = request.POST.get('RechercherPrestations-zl_progr'),
				k_axe = request.POST.get('RechercherPrestations-zl_axe'),
				k_ss_axe = request.POST.get('RechercherPrestations-zl_ss_axe')
			)

			if f_regr_prest.is_valid() :

				# Je récupère les données du formulaire valide.
				cleaned_data = f_regr_prest.cleaned_data
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

				# J'initialise, j'empile et j'épure le tableau des maîtres d'ouvrages concernés par la requête.
				t_org_moa = []
				for m in v_org_moa :
					qs_regr_moa = TRegroupementsMoa.objects.filter(id_org_moa_fil = m)
					for rm in qs_regr_moa :
						t_org_moa.append(str(rm.id_org_moa_anc.pk))
					t_org_moa.append(str(m))
				t_org_moa = list(set(t_org_moa))

				# Je débute l'initialisation de la requête en incluant.
				if len(t_org_moa) > 0 :
					if len(t_org_moa) == 1 :
						t_sql['and']['tprestationsdossier__id_doss__id_org_moa'] = t_org_moa[0]
					else :
						for m in t_org_moa :
							t_sql['or'].append(Q(**{ 'tprestationsdossier__id_doss__id_org_moa' : m }))
					if len(t_sql['or']) > 0 :
						qs_prest = TPrestation.objects.filter(reduce(operator.or_, t_sql['or']), **t_sql['and'])
					else :
						qs_prest = TPrestation.objects.filter(**t_sql['and'])
				else :
					qs_prest = TPrestation.objects.none()

				# Je termine l'initialisation de la requête en excluant.
				t_excl = [] 
				if v_mont_prest_min :
					t_excl[len(t_excl):] = [p.pk for p in VPrestation.objects.filter(
						mont_prest__lt = v_mont_prest_min
					)]
				if v_mont_prest_max :
					t_excl[len(t_excl):] = [p.pk for p in VPrestation.objects.filter(
						mont_prest__gt = v_mont_prest_max
					)]
				qs_prest = qs_prest.exclude(pk__in = t_excl).distinct().order_by('id_org_prest')

				# J'initialise et j'empile le tableau "group by".
				t_group_by = {}
				for p in qs_prest :
					v_id_org_prest = str(p.id_org_prest.pk)
					if v_id_org_prest not in t_group_by :
						t_group_by[v_id_org_prest] = TPrestation.objects.none()
					t_group_by[v_id_org_prest] = t_group_by[v_id_org_prest] | TPrestation.objects.filter(pk = p.pk)

				# J'empile le tableau des prestataires filtrés.
				t_org_prest = []

				for cle, val in t_group_by.items() :

					# Je cumule les montants des prestations ainsi que les restes à facturer pour le prestataire
					# courant.
					mont_cumul_prest = 0
					mont_cumul_raf = 0
					for p in val :
						qs_aggr = VSuiviPrestationsDossier.objects.filter(id_prest = p).aggregate(
							Sum('mont_prest_doss'), Sum('mont_raf')
						)
						mont_cumul_prest += qs_aggr['mont_prest_doss__sum']
						mont_cumul_raf += qs_aggr['mont_raf__sum']

					# J'empile le tableau des prestataires filtrés.
					t_org_prest.append((
						';'.join([str(p.pk) for p in val]),
						str(val[0].id_org_prest),
						len(val),
						mont_cumul_prest,
						mont_cumul_raf
					))

				# Je réinitialise le tableau des prestataires sélectionnés si l'option "Ajouter à la sélection 
				# existante" est cochée.
				if v_ajout_select_exist == False :
					request.session['regr_prest'] = []

				# J'empile le tableau des prestataires sélectionnés.
				for p in t_org_prest :
					request.session['regr_prest'].append(p)

				# Je supprime les doublons du tableau des prestataires sélectionnés.
				request.session['regr_prest'] = suppr_doubl(request.session['regr_prest'])

				# Je prépare le tableau de sortie.
				t_output = []
				mont_tot_prest = sum(elem[3] for elem in request.session['regr_prest'])
				for elem in request.session['regr_prest'] :
					t_output.append([
						elem[1],
						elem[2],
						elem[3],
						elem[4],
						(elem[3] / mont_tot_prest) * 100
					])

				# Je prépare le tableau relatif à la balise <tfoot/> de la datatable.
				t_tfoot = [
					'Total',
					sum(elem[1] for elem in t_output),
					obt_mont(sum(elem[2] for elem in t_output)),
					obt_mont(sum(elem[3] for elem in t_output)),
					obt_pourc(sum(elem[4] for elem in t_output))
				]

				# Je mets en forme le tableau de sortie.
				for elem in t_output :
					elem[2] = obt_mont(elem[2])
					elem[3] = obt_mont(elem[3])
					elem[4] = obt_pourc(elem[4])

				# J'envoie le tableau des prestataires filtrés.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'datatable' : t_output, 'datatable_tfoot' : t_tfoot
					}}), content_type = 'application/json'
				)

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_regr_prest.errors.items() :
					t_err['RechercherPrestations-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output