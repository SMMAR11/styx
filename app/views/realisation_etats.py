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
	from app.functions import get_thumbnails_menu
	from django.http import HttpResponse
	from django.shortcuts import render

	output = HttpResponse()

	if request.method == 'GET' :

		# J'affiche le template.
		output = render(request, './realisation_etats/main.html', {
			'menu' : get_thumbnails_menu('real_etats', 2), 'title' : 'Réalisation d\'états' }
		)

	return output

'''
Affichage du formulaire de réalisation d'un état "dossier" ou traitement d'une requête quelconque
_req : Objet "requête"
_gby : Regroupement ou sélection de dossiers ?
'''
@verif_acc
def filtr_doss(_req, _gby) :

	# Imports
	from app.forms.realisation_etats import FiltrerDossiers
	from app.functions import alim_ld
	from app.functions import datatable_reset
	from app.functions import dt_fr
	from app.functions import gen_cdc
	from app.models import TDossier
	from app.models import TFinancement
	from app.models import TFinanceur
	from app.sql_views import VSuiviDossier
	from bs4 import BeautifulSoup
	from django.http import HttpResponse
	from django.shortcuts import render
	import csv
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_filtr_doss = 'FiltrerDossiers'

	if _req.method == 'GET' :
		if 'action' in _req.GET :
			if _req.GET['action'] == 'exporter-csv' and 'group-by' in _req.GET \
			and _req.GET['group-by'] in ['off', 'on'] :

				# Génération d'un fichier au format CSV
				output = HttpResponse(content_type = 'text/csv', charset = 'cp1252')
				output['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(gen_cdc())

				# Accès en écriture
				writer = csv.writer(output, delimiter = ';')

				# Initialisation des données "historique"
				donnees = _req.session.get('filtr_doss') if 'filtr_doss' in _req.session else []

				if _gby == False :

					# Définition de l'en-tête
					writer.writerow([
						'Numéro du dossier',
						'Intitulé du dossier',
						'Dossier associé et/ou contrepartie',
						'Maître d\'ouvrage',
						'Programme',
						'Axe',
						'Sous-axe',
						'Action',
						'Nature du dossier',
						'Type de dossier',
						'Agent responsable',
						'SAGE',
						'Montant du dossier présenté au CD GEMAPI (en €)',
						'Dépassement du dossier (en €)',
						'Montant total du dossier (en €)',
						'Mode de taxe du dossier',
						'État d\'avancement',
						'Date de délibération au maître d\'ouvrage',
						'Année prévisionnelle du dossier',
						'Avis du comité de programmation - CD GEMAPI',
						'Date de l\'avis du comité de programmation',
						'Commentaire',
						'Montant commandé (en €)',
						'Montant payé (en €)'
					] + [
						'Financement - {}'.format(elem) for elem in \
						['Autofinancement'] + [f for f in TFinanceur.objects.all()]
					])

					for d in TDossier.objects.filter(pk__in = donnees) :

						# Obtention d'une instance VSuiviDossier
						obj_sd = VSuiviDossier.objects.get(pk = d.pk)

						# Préparation des données des colonnes "Financement"
						fins = [obj_sd.mont_raf]
						for f in TFinanceur.objects.all() :
							if TFinancement.objects.filter(id_doss = d, id_org_fin = f).count() > 0 :
								mont_part_fin = TFinancement.objects.get(id_doss = d, id_org_fin = f).mont_part_fin
							else :
								mont_part_fin = 0
							fins.append(mont_part_fin)

						# Ajout d'une nouvelle ligne
						writer.writerow([
							d,
							d.get_int_doss(),
							d.id_doss_ass,
							d.id_org_moa,
							d.id_progr,
							d.num_axe,
							d.num_ss_axe,
							d.num_act,
							d.id_nat_doss,
							d.id_type_doss,
							d.id_techn,
							d.id_sage,
							d.mont_doss,
							d.mont_suppl_doss,
							obj_sd.mont_tot_doss,
							'TTC' if d.est_ttc_doss == True else 'HT',
							d.id_av,
							dt_fr(d.dt_delib_moa_doss),
							d.annee_prev_doss,
							d.id_av_cp,
							dt_fr(d.dt_av_cp_doss),
							d.comm_doss,
							obj_sd.mont_tot_prest_doss,
							obj_sd.mont_fact_sum
						] + fins)

				else :
					for elem in donnees : writer.writerow(elem)
		else :

			# Initialisation de la variable "historique"
			_req.session['filtr_doss'] = []

			# Initialisation du formulaire et de ses attributs
			form_filtr_doss = FiltrerDossiers(prefix = pref_filtr_doss, kw_gby = _gby)

			# Définition de l'attribut <title/>
			if _gby == False :
				title = 'Réalisation d\'états en sélectionnant des dossiers'
			else :
				title = 'Réalisation d\'états en regroupant des dossiers'

			# Affichage du template
			output = render(_req, './realisation_etats/filtr_doss.html', {
				'dtab_filtr_doss' : form_filtr_doss.get_datatable(_req),
				'form_filtr_doss' : form_filtr_doss.get_form(_req),
				'gby' : 'off' if _gby == False else 'on',
				'title' : title
			})

	else :
		if 'action' in _req.GET and _req.GET['action'] == 'alimenter-listes' :

			# Gestion d'affichage des listes déroulantes des axes, des sous-axes et des actions
			output = HttpResponse(json.dumps(alim_ld(_req)), content_type = 'application/json')

		else :

			# Soumission du formulaire
			form_filtr_doss = FiltrerDossiers(
				_req.POST,
				prefix = pref_filtr_doss,
				kw_gby = _gby,
				kw_progr = _req.POST.get('FiltrerDossiers-id_progr'),
				kw_axe = _req.POST.get('FiltrerDossiers-zl_axe'),
				kw_ss_axe = _req.POST.get('FiltrerDossiers-zl_ss_axe')
			)

			# Rafraîchissement de la datatable ou affichage des erreurs
			if form_filtr_doss.is_valid() :

				# Préparation des paramètres de la fonction datatable_reset
				dtab = form_filtr_doss.get_datatable(_req)
				bs = BeautifulSoup(dtab)
				if _gby == True :
					dico = {
						'elements' : [['#za_tfoot_regr_doss', str(bs.find('tfoot', id = 'za_tfoot_regr_doss'))]],
						'replace' : ['#za_regr_doss_0', bs.find('th', id = 'za_regr_doss_0').contents]
					}
				else :
					dico = {
						'elements' : [['#za_tfoot_select_doss', str(bs.find('tfoot', id = 'za_tfoot_select_doss'))]]
					}
				output = datatable_reset(dtab, dico)
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

	# Imports
	from app.forms.realisation_etats import FiltrerPrestations
	from app.functions import alim_ld
	from app.functions import datatable_reset
	from app.functions import dt_fr
	from app.functions import gen_cdc
	from app.models import TPrestationsDossier
	from app.sql_views import VSuiviPrestationsDossier
	from bs4 import BeautifulSoup
	from django.http import HttpResponse
	from django.shortcuts import render
	import csv
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	pref_filtr_prest = 'FiltrerPrestations'

	if _req.method == 'GET' :
		if 'action' in _req.GET :
			if _req.GET['action'] == 'exporter-csv' and 'group-by' in _req.GET \
			and _req.GET['group-by'] in ['off', 'on'] :

				# Génération d'un fichier au format CSV
				output = HttpResponse(content_type = 'text/csv', charset = 'cp1252')
				output['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(gen_cdc())

				# Accès en écriture
				writer = csv.writer(output, delimiter = ';')

				# Initialisation des données "historique"
				donnees = _req.session.get('filtr_prest') if 'filtr_prest' in _req.session else []

				if _gby == False :

					# Définition de l'en-tête
					writer.writerow([
						'Numéro du dossier',
						'Intitulé du dossier',
						'Intitulé de la prestation',
						'Référence de la prestation',
						'Nature de la prestation',
						'Prestataire',
						'Montant de la prestation (en €)',
						'Nombre d\'avenants',
						'Somme des avenants (en €)',
						'Montant total de la prestation (en €)',
						'Somme HT des factures émises (en €)',
						'Somme TTC des factures émises (en €)',
						'Reste à facturer (en €)',
						'Mode de taxe',
						'Date de notification de la prestation',
						'Date de fin de la prestation',
						'Commentaire'
					])

					for pd in TPrestationsDossier.objects.filter(pk__in = donnees) :

						# Obtention d'une instance VSuiviPrestationsDossier
						obj_spd = VSuiviPrestationsDossier.objects.get(pk = pd.pk)

						# Ajout d'une nouvelle ligne
						writer.writerow([
							pd.id_doss,
							pd.id_doss.get_int_doss(),
							pd.id_prest.int_prest,
							pd.id_prest.ref_prest,
							pd.id_prest.id_nat_prest,
							pd.id_prest.id_org_prest,
							pd.mont_prest_doss,
							obj_spd.nb_aven,
							obj_spd.mont_aven_sum,
							obj_spd.mont_tot_prest_doss,
							obj_spd.mont_ht_fact_sum,
							obj_spd.mont_ttc_fact_sum,
							obj_spd.mont_raf,
							'TTC' if pd.id_doss.est_ttc_doss == True else 'HT',
							dt_fr(pd.id_prest.dt_notif_prest),
							dt_fr(pd.id_prest.dt_fin_prest),
							pd.id_prest.comm_prest
						])

				else :
					for elem in donnees : writer.writerow(elem)
		else :

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
				'gby' : 'off' if _gby == False else 'on',
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
