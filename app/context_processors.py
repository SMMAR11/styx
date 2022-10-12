#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from django.conf import settings

'''
Cette fonction permet d'obtenir les différentes constantes paramétrées dans le fichier settings.py.
request : Objet "requête"
Retourne un tableau associatif
'''
def get_settings(request) :
	return {
		'consts_str' : [(cle, val) for cle, val in settings.T_DONN_BDD_STR.items()],
		'consts_int' : [(cle, val) for cle, val in settings.T_DONN_BDD_INT.items()],
		'IGN_KEY' : settings.IGN_KEY
	}

'''
Obtention du menu dans le template
_req : Objet requête
Retourne un tableau associatlf
'''
def set_menus(_req) :

	# Import
	from app.functions import get_menu

	# Initialisation du menu
	menu = get_menu(_req) if _req.user.is_authenticated else {}

	# Préparation du menu principal
	elems = []
	for elem in menu.values() :

		# Mise en forme de l'élément
		if len(elem['mod_items']) > 0 :
			li = '''
			<li class="dropdown">
				<a class="dropdown-toggle" data-toggle="dropdown" href="#">
					{}
					<span class="caret"></span>
				</a>
				<ul class="dropdown-menu">{}</ul>
			</li>
			'''.format(
				elem['mod_name'],
				''.join(['<li><a href="{}">{}</a></li>'.format(
					elem_2['item_href'], elem_2['item_name']
				) for elem_2 in elem['mod_items']])
			)
		else :
			li = '<li><a href="{}" target="{}">{}</a></li>'.format(
				elem['mod_href'], elem['mod_href_blank'], elem['mod_name']
			)

		elems.append(li)

	return { 'navbar' : '<ul class="nav navbar-nav">{}</ul>'.format(''.join(elems)) }

def set_alerts(request) :

	# Imports
	from app.functions import obt_mont
	from app.models import TDemandeVersement
	from app.models import TDroit
	from app.models import TMoa
	from app.models import TRegroupementsMoa
	from app.models import TTypeProgramme
	from app.models import TUtilisateur
	from app.models import VFinancement
	from django.urls import reverse
	from django.shortcuts import render
	from styx.settings import T_DONN_BDD_STR
	import datetime
	import json

	# J'initialise le tableau des alertes ainsi que le tableau des couleurs disponibles pour une alerte.
	t_alert = []
	t_pr_alert = {
		1 : 'background-color: #F8B862;',
		2 : 'background-color: #FF0921;',
		3 : 'background-color: #000;'
	}

	# Obtention de l'utilisateur connecté
	usr = TUtilisateur.objects.get_authenticated_user(req = request)

	if usr :

		# Obtention des permissions
		t_coupl_uniq = usr.get_permissions(read_or_write = 'W')

		# Je stocke la date du jour.
		today = datetime.date.today()

		for t in t_coupl_uniq :

			# Je stocke les financements du couple courant avec exclusion si le dossier est soldé.
			qs_fin = VFinancement.objects.filter(
				id_doss__id_org_moa = t[0], id_doss__id_progr__id_type_progr = t[1]
			).exclude(
				id_doss__id_av__int_av = T_DONN_BDD_STR['AV_SOLDE']
			).exclude(
				id_doss__id_av__int_av=T_DONN_BDD_STR['AV_ABAND']
			).exclude(
				id_doss__id_av__int_av=T_DONN_BDD_STR['AV_ARCHI']
			)

			# Pour chaque financement...
			for f in qs_fin :
				# Ne correspondant pas à de l'autofinancement !
				if f.id_fin :

					# Je vérifie l'alerte relative à la date de fin d'éligibilité d'un financement.
					if f.dt_fin_elig_fin :

						# Je vérifie dans un premier temps si le montant restant à demander est inférieur à un
						# pourcentage par rapport au montant de participation.
						if float(f.mont_rad) > float(f.mont_part_fin) * 0.1 :

							# Je vérifie dans un second temps si la date de fin d'éligibilité est proche.
							diff = (f.dt_fin_elig_fin - today).days
							if diff <= 60 :
								alert = {
									'etat_alert' : [1, t_pr_alert[1]],
									'int_alert' : 'Fin d\'éligibilité',
									'descr_alert' : '''
									Il reste {0} jour(s) avant la date de fin d'éligibilité du financeur « {1} » pour
									le dossier {2}. Attention, {3} € n'ont pas encore été demandés.
									'''.format(diff, f.id_org_fin, f.id_doss, obt_mont(f.mont_rad)),
									'lien_alert' : reverse('cons_doss', args = [f.id_doss.pk])
								}
								if diff <= 30 :
									alert['etat_alert'] = [2, t_pr_alert[2]]
								if diff <= 15 :
									alert['etat_alert'] = [3, t_pr_alert[3]]

								# J'empile le tableau des alertes.
								t_alert.append(alert)

					# Je vérifie l'alerte relative à la date limite du début de l'opération.
					if f.id_fin.dt_lim_deb_oper_fin and f.id_fin.a_inf_fin == 'Non' :

						# Je vérifie si la date limite du début de l'opération est proche.
						diff = (f.id_fin.dt_lim_deb_oper_fin - today).days
						if diff <= 60 :
							alert = {
								'etat_alert' : [1, t_pr_alert[1]],
								'int_alert' : 'Début de l\'opération',
								'descr_alert' : '''
								Il reste {0} jour(s) avant la date limite du début de l'opération. Attention, veuillez
								informer le financeur « {1} » du début de l'opération pour le dossier {2}.
								'''.format(diff, f.id_org_fin, f.id_doss),
								'lien_alert' : reverse('modif_fin', args = [f.id_fin.pk])
							}
							if diff <= 30 :
								alert['etat_alert'] = [2, t_pr_alert[2]]
							if diff <= 15 :
								alert['etat_alert'] = [3, t_pr_alert[3]]

							# J'empile le tableau des alertes.
							t_alert.append(alert)

					# Je vérifie l'alerte relative à la date limite du premier acompte.
					# if f.id_fin.dt_lim_prem_ac_fin and len(TDemandeVersement.objects.filter(id_fin = f.id_fin)) == 0 :
					if f.id_fin.dt_lim_prem_ac_fin and not TDemandeVersement.objects.filter(id_fin = f.id_fin).exists():

						# Je vérifie si la date limite du premier acompte est proche.
						diff = (f.id_fin.dt_lim_prem_ac_fin - today).days
						if diff <= 60 :
							alert = {
								'etat_alert' : [1, t_pr_alert[1]],
								'int_alert' : 'Premier acompte',
								'descr_alert' : '''
								Il reste {0} jour(s) avant la date limite du premier acompte. Attention, veuillez
								effectuer une demande de versement pour le financeur « {1} » du dossier {2}.
								'''.format(diff, f.id_org_fin, f.id_doss),
								'lien_alert' : reverse('cons_doss', args = [f.id_doss.pk])
							}
							if diff <= 30 :
								alert['etat_alert'] = [2, t_pr_alert[2]]
							if diff <= 15 :
								alert['etat_alert'] = [3, t_pr_alert[3]]

							# J'empile le tableau des alertes.
							t_alert.append(alert)

	return {
		'alerts_list' : sorted(t_alert, key = lambda l : (-l['etat_alert'][0], l['int_alert'])),
		'badge_color' : '#FF0921' if len(t_alert) > 0 else '#82C46C'
	}
