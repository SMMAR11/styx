#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.constants import *
from datetime import date

'''
Cette fonction retourne un message de confirmation de suppression d'un élément.
p_vue : Vue supprimant un objet
p_mess : Message d'alerte
Retourne une chaîne de caractères
'''
def aff_mess_suppr(p_vue, p_mess = '') :

	# Je mets en forme les lignes du contenu de la fenêtre modale de demande de confirmation d'une suppression.
	row_princ = '''
	<div class="row">
		<div class="col-xs-6 text-center">
			<a href="{0}" class="btn bt-vert to-unfocus" onclick="suppr(event)">Oui</a>
		</div>
		<div class="col-xs-6 text-center">
			<button class="btn bt-vert to-unfocus" data-dismiss="modal">Non</button>
		</div>
	</div>
	'''.format(p_vue)

	row_sec = '''
	<div class="row">
		<div class="col-xs-12 text-center">
			<span class="b c-attention">
				<span class="u">Attention :</span> {0}
			</span>
		</div>
	</div>
	'''.format(p_mess)

	# J'initialise les élements du tableau des lignes.
	tab_rows = [row_princ]
	if p_mess != '' :
		tab_rows.append(row_sec)

	# J'inverse les éléments du tableau des lignes afin d'avoir le message d'alerte au début.
	tab_rows.reverse()

	return '<br />'.join(tab_rows)

'''
Cette fonction permet soit d'afficher le formulaire d'ajout d'un avenant, soit de traiter celui-ci.
request : Objet requête
p_type : "GET" ou "POST" ?
p_prest : Identifiant de la prestation
p_doss : Identifiant du dossier
p_act : URL traitant le formulaire
p_red : URL de redirection dès l'ajout de l'avenant
p_ong : Onglet actif après la redirection
Retourne soit une chaîne de caractères, soit un tableau au format JSON
'''
def ajout_aven(request, p_type, p_prest = None, p_doss = None, p_act = None, p_red = None, p_ong = None) :

	''' Imports '''
	from app.forms.gestion_dossiers import GererAvenant
	from app.functions import init_form, nett_val
	from app.models import TAvenant, TDossier, TPrestation
	from django.http import HttpResponse
	from django.template.context_processors import csrf
	import json

	reponse = None

	if p_type == 'GET' :

		# J'instancie un objet "formulaire".
		f = GererAvenant(prefix = 'AjouterAvenant', k_prest = p_prest, k_doss = p_doss)

		# J'initialise les champs du formulaire.
		tab = init_form(f)

		reponse = '''
		<form name="form_ajouter_avenant" method="post" action="{0}?action=ajouter-avenant" class="c-theme">
				<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
				<div class="row">
					<div class="col-xs-6">{2}</div>
					<div class="col-xs-6">
						{3}
						{4}
					</div>
				</div>
				{5}
				{6}
				<div class="row">
					<div class="col-sm-6">{7}</div>
					<div class="col-sm-6">{8}</div>
				</div>
				<button type="submit" class="bt-vert btn center-block to-unfocus">Valider</button>
			</form>
			'''.format(
				p_act,
				csrf(request)['csrf_token'],
				tab['za_num_doss'],
				tab['za_id_prest'],
				tab['za_prest'],
				tab['zs_int_aven'],
				tab['zd_dt_aven'],
				tab['zs_mont_ht_aven'],
				tab['zs_mont_ttc_aven']
			)

	else :

		# Je vérifie la validité du formulaire d'ajout d'un avenant.
		f = GererAvenant(request.POST)

		if f.is_valid() :

			# Je récupère et nettoie les données du formulaire valide.
			cleaned_data = f.cleaned_data
			v_num_doss = nett_val(cleaned_data['za_num_doss'])
			v_id_prest = nett_val(cleaned_data['za_id_prest'])
			v_dt_aven = nett_val(cleaned_data['zd_dt_aven'])
			v_int_aven = nett_val(cleaned_data['zs_int_aven'])
			v_mont_ht_aven = nett_val(cleaned_data['zs_mont_ht_aven'])
			v_mont_ttc_aven = nett_val(cleaned_data['zs_mont_ttc_aven'])

			# Je remplis les données attributaires du nouvel objet TAvenant.
			obj_nv_aven = TAvenant(
				dt_aven = v_dt_aven,
				int_aven = v_int_aven,
				mont_ht_aven = v_mont_ht_aven,
				mont_ttc_aven = v_mont_ttc_aven,
				id_doss = TDossier.objects.get(num_doss = v_num_doss),
				id_prest = TPrestation.objects.get(id_prest = v_id_prest)
			)

			# Je créé un nouvel objet TAvenant.
			obj_nv_aven.save()

			# J'affiche le message de succès.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'L\'avenant a été ajouté avec succès.',
					'redirect' : p_red
				}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['app-nav'] = p_ong

		else :

			# J'affiche les erreurs.
			reponse = HttpResponse(json.dumps(f.errors), content_type = 'application/json')

	return reponse

'''
Cette fonction permet de générer des données concernant les axes, les sous-axes, les actions et les types de dossiers.
request : Objet requête
Retourne un tableau associatif
'''
def alim_liste(request) :

	''' Imports '''
	from app.functions import index_alpha
	from app.models import TAction, TAxe, TProgramme, TSousAxe, TTypesProgrammesTypeDossier

	# J'initialise la valeur des paramètres "GET".
	v_progr = -1
	v_axe = -1
	v_ss_axe = -1

	# Je déclare des tableaux.
	tab_axes = []
	tab_ss_axes = []
	tab_act = []
	tab_types_doss = []

	if 'programme' in request.GET :
		
		# Je récupère la valeur du paramètre "GET".
		v_progr = request.GET['programme']

		# Je récupère la liste des axes relatifs à un programme.
		les_axes = TAxe.objects.filter(id_progr = v_progr)

		# J'empile le tableau des axes.
		for un_axe in les_axes :
			tab_axes.append([un_axe.num_axe, un_axe.num_axe])

		v_type_progr = -1
		try :
			v_type_progr = TProgramme.objects.get(id_progr = v_progr).id_type_progr.id_type_progr
		except :
			pass

		# Je récupère la liste des types de dossiers relatifs à un programme.
		les_types_doss = TTypesProgrammesTypeDossier.objects.filter(id_type_progr = v_type_progr).order_by(
			'id_type_doss__int_type_doss'
		)

		# J'empile le tableau des types de dossiers.
		for un_type_doss in les_types_doss :
			tab_types_doss.append([un_type_doss.id_type_doss.id_type_doss, un_type_doss.id_type_doss.int_type_doss])

	if 'axe' in request.GET :

		# Je récupère la valeur du paramètre "GET".
		v_axe = request.GET['axe']
		
		# Je récupère la liste des sous-axes relatifs à un programme et un axe.
		les_ss_axes = TSousAxe.objects.filter(id_axe = '{0}_{1}'.format(v_progr, v_axe))

		# J'empile le tableau des sous-axes.
		for un_ss_axe in les_ss_axes :
			tab_ss_axes.append([un_ss_axe.num_ss_axe, un_ss_axe.num_ss_axe])

	if 'sous_axe' in request.GET :

		# Je récupère la valeur du paramètre.
		v_ss_axe = request.GET['sous_axe']

		# Je récupère la liste des actions relatives à un programme, un axe et un sous-axe.
		les_act = TAction.objects.filter(id_ss_axe = '{0}_{1}_{2}'.format(v_progr, v_axe, v_ss_axe))

		# J'empile le tableau des actions.
		for une_act in les_act :
			tab_act.append([une_act.num_act, index_alpha(une_act.num_act)])

	return {
		'axe' : tab_axes,
		'ss_axe' : tab_ss_axes,
		'act' : tab_act,
		'type_doss' : tab_types_doss
	}

'''
Cette fonction permet de calculer des intervalles de valeurs afin de redistribuer correctement les montants d'une
prestation.
p_doss : Identifiant du dossier à traiter
p_prest : Identifiant de la prestation à traiter
Retourne un tableau associatif
'''
def calc_interv(p_doss, p_prest) :

	''' Imports '''
	from app.models import TPrestation
	from app.sql_views import VSuiviPrestationsDossier
	from app.sql_views import VSuiviDossier

	# Je pointe vers un objet VSuiviPrestationsDossier.
	obj_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(id_doss = p_doss, id_prest = p_prest)

	# Je pointe vers un objet VSuiviDossier.
	obj_suivi_doss = VSuiviDossier.objects.get(id_doss = p_doss)

	# Je définis un tableau de valeurs possibles pour chaque borne HT.
	tab_bornes_min_ht = sorted([
		obj_suivi_prest_doss.mont_ht_fact_sum - obj_suivi_prest_doss.mont_ht_aven_sum,
		obj_suivi_prest_doss.mont_ht_fact_sum
	])

	tab_bornes_max_ht = sorted([
		obj_suivi_prest_doss.mont_ht_prest + obj_suivi_doss.mont_ht_rau,
		TPrestation.objects.get(id_prest = p_prest).mont_ht_tot_prest
	])

	# Je définis les bornes HT.
	borne_min_ht = tab_bornes_min_ht[0]
	if borne_min_ht < 0 :
		borne_min_ht = 0

	borne_max_ht = tab_bornes_max_ht[0]

	# Je réalise le même travail pour le TTC.
	tab_bornes_min_ttc = sorted([
		obj_suivi_prest_doss.mont_ttc_fact_sum - obj_suivi_prest_doss.mont_ttc_aven_sum,
		obj_suivi_prest_doss.mont_ttc_fact_sum
	])

	tab_bornes_max_ttc = sorted([
		obj_suivi_prest_doss.mont_ttc_prest + obj_suivi_doss.mont_ttc_rau,
		TPrestation.objects.get(id_prest = p_prest).mont_ttc_tot_prest
	])

	borne_min_ttc = tab_bornes_min_ttc[0]
	if borne_min_ttc < 0 :
		borne_min_ttc = 0

	borne_max_ttc = tab_bornes_max_ttc[0]

	return {
		'ht' : { 'min' : borne_min_ht, 'max' : borne_max_ht },
		'ttc' : { 'min' : borne_min_ttc, 'max' : borne_max_ttc }
	}

'''
Cette fonction retourne une date sous un autre format.
p_valeur : Date dont le format doit être changé
p_format : Format à utiliser
Retourne une chaîne de caractères
'''
def chang_form_dt(p_valeur, p_format = 'AAAA-MM-JJ') :

	reponse = p_valeur

	if p_valeur is not None :

		# Je sépare les parties de la date.
		tab_dt = p_valeur.split('/')

		if p_format == 'AAAA-MM-JJ' :
			glue = '-'
			pieces = (tab_dt[2], tab_dt[1], tab_dt[0])

		# Je mets en forme la date.
		reponse = glue.join(pieces)

	return reponse

'''
Cette fonction convertit une valeur nulle en une chaîne vide.
p_valeur : Valeur à convertir
Retourne soit une chaîne vide, soit une valeur nulle
'''
def conv_none(p_valeur) :

	if p_valeur is None :
		p_valeur = ''

	return p_valeur

'''
Cette fonction crypte une valeur selon une méthode de hashage définie.
p_valeur : Valeur à crypter
Retourne une chaîne de caractères
'''
def crypt_val(p_valeur) :

	''' Imports '''
	import hashlib

	# Je crypte la valeur selon la méthode de hashage SHA1 si la valeur renseignée n'est pas nulle.
	if p_valeur is not None :
		p_valeur = hashlib.sha1(p_valeur.encode()).hexdigest()
	
	return p_valeur

'''
Cette fonction renvoie un ensemble de dossiers filtrés en vue d'actualiser une datatable.
request : Objet requête
'''
def filtr_doss(request) :

	''' Imports '''
	from app.forms.gestion_dossiers import ChoisirDossier
	from app.functions import integer
	from app.models import TAction, TAxe, TDossier, TRegroupementsMoa, TSousAxe
	from django.db.models import Q
	from functools import reduce
	import operator

	# Je vérifie la validité du formulaire de recherche d'un dossier.
	f = ChoisirDossier(request.POST)

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
		f.fields['zld_axe'].choices = [(post_axe, post_axe)]

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
		f.fields['zld_ss_axe'].choices = [(post_ss_axe, post_ss_axe)]

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
		f.fields['zld_act'].choices = [(post_act, post_act)]

	if f.is_valid() :

		# Je récupère et nettoie les données du formulaire valide.
		cleaned_data = f.cleaned_data
		v_org_moa = integer(cleaned_data['zl_org_moa'])
		v_progr = integer(cleaned_data['zld_progr'])
		v_axe = integer(cleaned_data['zld_axe'])
		v_ss_axe = integer(cleaned_data['zld_ss_axe'])
		v_act = integer(cleaned_data['zld_act'])
		v_nat_doss = integer(cleaned_data['zl_nat_doss'])
		v_ann_delib_moa_doss = integer(cleaned_data['zl_ann_delib_moa_doss'])

		# Je déclare des tableaux qui stockeront les conditions de la requête SQL.
		tab_or = []
		tab_and = {}

		# J'empile les tableaux des conditions.
		if v_org_moa > -1 :

			for un_couple_moa in TRegroupementsMoa.objects.filter(id_org_moa_fil = v_org_moa) :
				tab_or.append(Q(**{ 'id_org_moa' : un_couple_moa.id_org_moa_anc }))
			
			if len(tab_or) > 0 :
				tab_or.append(Q(**{ 'id_org_moa' : v_org_moa }))
			else :
				tab_and['id_org_moa'] = v_org_moa

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

		if v_ann_delib_moa_doss > -1 :
			tab_and['dt_delib_moa_doss__year'] = v_ann_delib_moa_doss

		# Je stocke dans un tableau les dossiers filtrés.
		if len(tab_or) > 0 :
			les_doss = TDossier.objects.filter(reduce(operator.or_, tab_or), **tab_and)
		else :
			les_doss = TDossier.objects.filter(**tab_and)

		reponse = { 'data' : les_doss, 'status' : True }
	else :
		reponse = { 'data' : f.errors, 'status' : False }

	return reponse

'''
Cette fonction convertit une chaîne représentant un nombre entier sous forme de décimal en une chaîne représentant un
nombre entier sous forme de nombre entier.
p_valeur : Chaîne à convertir
p_montant : Dois-je générer une chaîne de caractères prenant la forme d'un montant ?
Retourne une chaîne de caractères
'''
def float_to_int(p_valeur, p_montant = True) :

	reponse = p_valeur

	if p_valeur is not None :

		# Je transforme le nombre en chaîne de caractères.
		str_valeur = str(p_valeur)

		# Je vérifie si la chaîne de caractères se termine par ".0" afin de retirer la partie décimale inutile si 
		# besoin.
		if str_valeur.endswith('.0') :
			reponse = str_valeur[:-2]
		else :
			reponse = str_valeur

			# J'ajoute un zéro à la fin de la chaîne de caractères si la partie décimale ne comporte qu'un seul 
			# chiffre.
			if '.' in str_valeur[len(str_valeur) - 2] and p_montant == True :
				reponse = str_valeur + '0'
				
	return reponse

'''
Cette fonction retourne le tableau HTML des dossiers filtrés.
request : Objet requête
p_vue : Vue qui traite le formulaire de filtrage
'''
def gen_tabl_chois_doss(request, p_vue) :

	''' Imports '''
	from app.forms.gestion_dossiers import ChoisirDossier
	from app.functions import conv_none, init_form, reecr_dt
	from app.models import TDossier
	from django.template.context_processors import csrf

	# J'instancie un objet "formulaire".
	f = ChoisirDossier(prefix = 'ChoisirDossier')

	# J'initialise les champs du formulaire de filtrage des dossiers.
	tab_f = init_form(f) 

	# Je récupère dans un tableau l'ensemble des lignes du tableau HTML des dossiers filtrés.
	tab_lg = []
	for un_doss in TDossier.objects.all() :

		# J'initialise une ligne du tableau HTML des dossiers filtrés.
		lg = '''
		<tr>
			<td class="b">{0}</td>
			<td>{1}</td>
			<td>{2}</td>
			<td>
				<span class="bt-choisir pointer pull-right" title="Choisir le dossier"></span>
			</td>
		</tr>
		'''.format(
			conv_none(un_doss.num_doss),
			conv_none(un_doss.id_org_moa.id_org_moa.n_org),
			conv_none(reecr_dt(un_doss.dt_delib_moa_doss)) or 'En projet'
		)

		# J'ajoute la ligne du tableau HTML des dossiers filtrés.
		tab_lg.append(lg)

	return '''
	<form name="form_ajouter_dossier_associe" method="post" action="{0}?action=filtrer-dossiers" class="c-theme">
		<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
		<fieldset style="padding-bottom: 0;">
			<legend>Rechercher par</legend>
			<div class="form-content">
				<div class="row">
					<div class="col-xs-6">{2}</div>
					<div class="col-xs-6">{3}</div>
				</div>
				<div class="row">
					<div class="col-xs-6">{4}</div>
					<div class="col-xs-3">{5}</div>
					<div class="col-xs-3">{6}</div>
				</div>
				<div class="row">
					<div class="col-xs-6">{7}</div>
					<div class="col-xs-6">{8}</div>
				</div>
			</div>
		</fieldset>
	</form>				
	<br />
	<div style="overflow: auto;">
		<table class="display table" id="tab_ajouter_dossier_associe">
			<thead>
				<tr>
					<th>N° du dossier</th>
					<th>Maître d'ouvrage</th>
					<th>Date de délibération au maître d'ouvrage</th>
					<th></th>
				</tr>
			</thead>
			<tbody>{9}</tbody>
		</table>
	</div>
	'''.format(
		p_vue,
		(csrf(request)['csrf_token']),
		tab_f['zl_org_moa'],
		tab_f['zld_progr'],
		tab_f['zld_axe'],
		tab_f['zld_ss_axe'],
		tab_f['zld_act'],
		tab_f['zl_nat_doss'],
		tab_f['zl_ann_delib_moa_doss'],
		'\n'.join(tab_lg)
	)

'''
Cette fonction retourne une lettre de l'alphabet en fonction de son indice.
p_valeur : Nombre à convertir 
Retourne un caractère
'''
def index_alpha(p_valeur) :

	''' Imports '''
	import string

	# Je déclare le tableau relatif à l'alphabet.
	tab_alpha = list(string.ascii_lowercase)

	return tab_alpha[p_valeur - 1]

''' 
Cette fonction retourne une fenêtre modale.
p_suffixe : Suffixe utilisé pour reconnaître chaque élément de la fenêtre modale
p_header : En-tête de la fenêtre modale
p_body : Corps de la fenêtre modale
Retourne une fenêtre modale
'''
def init_fm(p_suffixe, p_header, p_body = '') :

	''' Imports '''
	from django.template.defaultfilters import safe

	# J'initialise le contenu HTML de la fenêtre modale.
	contenu = '''
	<div class="modal fade" id="fm_{suffixe}" tabindex="-1" role="dialog" aria-hidden="true" data-backdrop="static">
		<div class="modal-dialog modal-lg">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-hidden="true" id="bt_fm_{suffixe}">&times;</button>
					<p class="modal-title c-theme text-center">{header}</p>
				</div>
				<div class="modal-body">
					<span id="za_{suffixe}">
						{body}
					</span>
					<div class="modal-padding-bottom"></div>
				</div>
				<div class="modal-footer"></div>
			</div>
		</div>
	</div>
	'''.format(suffixe = p_suffixe, header = p_header, body = p_body)

	return safe(contenu)

''' 
Cette fonction retourne les champs d'un formulaire.
p_form : Formulaire à traiter
Retourne un tableau associatif
'''
def init_form(p_form) :

	''' Imports '''
	from django.template.defaultfilters import safe

	# Je déclare le tableau qui contiendra les champs d'un formulaire
	tab_champs = {}
	
	for un_champ in p_form :

		# J'initialise une variable booléenne me permettant de savoir si un autre gabarit d'affichage sera utilisé ou
		# non pour le champ en cours.
		autre_gabarit = False

		# Je traite le cas où le champ en cours est une zone d'upload.
		if un_champ.name.startswith('zu_') == True :
			autre_gabarit = True
			contenu = '''
			<div class="field-wrapper">
				<label>{0}</label>
				<div class="input-file-container">
					{1}
					<span class="input-file-trigger">Parcourir</span>
					<p class="file-return"></p>
				</div>
				<span class="za_erreur"></span>
			</div>
			'''.format(un_champ.label, un_champ)

		# Je traite le cas où le champ en cours est une case à cocher.
		if un_champ.name.startswith('cb_') == True :
			autre_gabarit = True
			contenu = '''
			<div>
				<div class="checkbox">
					<label>{0}{1}</label>
				</div>
				<span class="za_erreur"></span>
			</div>
			'''.format(un_champ, un_champ.label)

		# Je traite le cas où le champ en cours est une case à cocher multiple.
		if un_champ.name.startswith('cbsm_') == True :
			autre_gabarit = True

			# J'initialise l'indice de départ du sommet du tableau des options.
			sommet = -1

			# Je déclare deux tableaux qui s'empileront selon la valeur du sommet.
			tab_rng_g = []
			tab_rng_d = []

			# Je parcours chaque élément du tableau des options.
			for un_element in un_champ :

				# J'incrémente la valeur du sommet.
				sommet += 1

				contenu_option = '''
				<div class="checkbox c-police" style="margin-top: 0;">
					{0}
				</div>
				'''.format(un_element)

				# Je stocke l'option dans l'un des deux tableaux.
				if sommet % 2 == 0 :
					tab_rng_g.append(contenu_option)
				else :
					tab_rng_d.append(contenu_option)	

			contenu = '''
			<div class="field-wrapper">
				<label>{0}</label>
				<div class="row">
					<div class="col-xs-6">{1}</div>
					<div class="col-xs-6">{2}</div>
				</div>
				<span class="za_erreur"></span>
			</div>
			'''.format(un_champ.label, '\n'.join(tab_rng_g), '\n'.join(tab_rng_d))

		# Je traite le cas où le champ en cours est une zone de saisie avec autocomplétion.
		if un_champ.name.startswith('zsac_') == True :
			autre_gabarit = True
			contenu = '''
			<div class="field-wrapper">
				<div class="typeahead__container">
					<div class="typeahead__field">
						<span class="typeahead__query">
							<label>{0}</label>
							{1}
						</span>
					</div>
				</div>
				<span class="za_erreur"></span>
			</div>
			'''.format(un_champ.label, un_champ)

		# Je traite le cas classique si le champ en cours ne demande pas un gabarit d'affichage spécifique.
		if autre_gabarit == False :
			if un_champ.label != '' :
				contenu = '''
				<div class="field-wrapper">
					<label>{0}</label>
					{1}
					<span class="za_erreur"></span>
				</div>
				'''.format(un_champ.label, un_champ)
			else :
				contenu = '''
				<div class="field-wrapper" style="margin-bottom: 0;">
					{0}
					<span class="za_erreur"></span>
				</div>
				'''.format(un_champ)

		tab_champs[un_champ.name] = safe(contenu)

	return tab_champs

''' 
Cette fonction retourne les attributs de consultation.
p_tab : Tableau de données à traiter
Retourne un tableau associatif
'''
def init_pg_cons(p_tab) :

	''' Imports '''
	from django.template.defaultfilters import safe

	# Je déclare le tableau qui contiendra chaque attribut de consultation.
	tab_attr = {}

	for cle, valeur in p_tab.items() :

		# J'initialise l'attribut.
		if 'textarea' in valeur and valeur['textarea'] == True :
			contenu = '''
			<div class="attribute-wrapper">
				<label class="c-theme">{0}</label>
				<textarea class="form-control" rows="5" readonly>{1}</textarea>
			</div>
			'''.format(valeur['label'], valeur['value'])
		else :
			contenu = '''
			<div class="attribute-wrapper">
				<label class="c-theme">{0}</label>
				<input class="form-control" value="{1}" type="text" readonly>
			</div>
			'''.format(valeur['label'], valeur['value'])

		tab_attr[cle] = safe(contenu)

	return tab_attr

''' 
Cette fonction retourne une tranche d'années bornée.
p_borne_min : Borne minimale
p_borne_max : Borne maximale
Retourne une liste d'années
'''
def init_tab_annees(p_borne_min = 1999, p_borne_max = date.today().year + 1) :

	# Je déclare le tableau des années.
	tab_annees = []

	# J'empile la liste des années.
	for i in range(p_borne_min, p_borne_max) :
		tab_annees.append(i)

	return tab_annees

def init_val_aggr(p_valeur) :
	if p_valeur is None :
		p_valeur = 0
	return p_valeur

'''
Cette fonction essaie de convertir une valeur en un nombre. Si la valeur est une chaîne de caractères, alors le nombre
retourné sera -1.
p_valeur : Valeur à convertir
Retourne un nombre entier
'''
def integer(p_valeur) :

	reponse = -1

	# Je tente de convertir la valeur en un nombre entier.
	try :
		reponse = int(p_valeur)
	except :
		pass

	return reponse

''' 
Cette fonction nettoie la valeur d'une variable pour lui assigner une valeur nulle dans différents cas de figures.
p_valeur : Valeur à nettoyer
p_est_zl : La valeur à nettoyer est-elle issue d'une liste déroulante ?
Retourne soit une chaîne de caractères, soit un entier, soit une valeur nulle
'''
def nett_val(p_valeur, p_est_zl = False) :

	if p_est_zl == False :
		if p_valeur == '' :
			p_valeur = None
	else :
		if p_valeur < 0 :
			p_valeur = None

	return p_valeur

'''
Cette fonction transforme un nombre décimal en un pourcentage.
p_valeur : Nombre décimal à convertir
Retourne un pourcentage
'''
def obt_pourc(p_valeur) :

	reponse = p_valeur

	# Je transforme le nombre décimal en un pourcentage (arrondi à deux décimales) si celui-ci n'est pas une valeur
	# vide.
	if p_valeur is not None :
		reponse = round(float(p_valeur) * 100, 2)

	return reponse

''' 
Cette fonction met en forme une date au format français.
p_valeur : Date à mettre en forme
Retourne une chaîne de caractères
'''
def reecr_dt(p_valeur) :

	reponse = p_valeur

	if p_valeur is not None :

		# Je définis le séparateur ainsi que les données à concaténer avec le séparateur défini.
		glue = '/'
		pieces = (
			str(p_valeur.day).zfill(2),
			str(p_valeur.month).zfill(2),
			str(p_valeur.year).zfill(4)
		)

		# Je mets en forme la date.
		reponse = glue.join(pieces)

	return reponse

''' 
Cette fonction supprime les doublons d'une datatable lorsqu'on veut empiler des sélections.
p_tab : Tableau à épurer
Retourne le contenu d'une datatable (sans doublons) sous forme d'une liste
'''
def suppr_doubl_dtable(p_tab) :

	# Je déclare et j'empile le tableau des lignes de la datatable.
	tab_lg = []
	for i in range(0, len(p_tab)) :
		for j in range(0, len(p_tab[i])) :
			tab_lg.append(p_tab[i][j])

	# J'initialise un ensemble vide qui par la suite aidera à la recherche des tuples en doublons.
	tab_tuples = set()

	# Je déclare un tableau de tuples vierge.
	tab = []
	
	for une_lg in tab_lg :

		# Je stocke le tuple de la ligne courante.
		un_tuple = tuple(une_lg)

		if un_tuple not in tab_tuples :

			# J'empile le tableau des tuples sans doublons.
			tab.append(un_tuple)

			# J'informe pour la suite de la boucle que le tuple courant a été reconnu.
			tab_tuples.add(un_tuple)

	return tab

'''
Cette procédure permet d'uploader un fichier.
p_fich : Fichier à uploader
p_chem_fich : Destination du fichier à uploader
'''
def upload_fich(p_fich, p_chem_fich) :

	''' Imports '''
	from styx.settings import MEDIA_ROOT

	# Je stocke le chemin de destination du fichier à uploader.
	chem_fich = '{0}/{1}'.format(MEDIA_ROOT, p_chem_fich)

	# Je mets en forme le chemin de destination du fichier à uploader.
	chem_fich = chem_fich.replace('\\', '/')
	chem_fich = chem_fich.replace('//', '/')

	with open(chem_fich, 'wb+') as fich :
		for c in p_fich.chunks() :
			fich.write(c)

'''
Cette fonction renvoie faux si le montant saisi est incorrect, vrai sinon.
p_valeur : Montant saisi
p_etre_nul : Puis-je renseigner un montant nul ?
'''
def valid_mont(p_valeur, p_etre_nul = True) :

	# J'initialise la valeur de la variable de sortie de la fonction.
	erreur = False

	# Je prépare le processus de validation.
	str_valeur = str(p_valeur)
	tab_caract = []

	# J'empile le tableau des caractères non-numériques.
	for i in range(0, len(str_valeur)) :
		try :
			int(str_valeur[i])
		except :
			tab_caract.append(str_valeur[i])

	# J'initialise un indicateur booléen permettant de jauger la validité du montant saisi.
	valide = False

	# Je traite le cas où le montant saisi est un nombre décimal.
	if len(tab_caract) == 1 and '.' in tab_caract :

		valide = True

		# J'initialise deux variables, me permettant de calculer le nombre de décimales du montant saisi.
		sep_trouve = False
		cpt_dec = 0

		for i in range(0, len(str_valeur)) :

			# J'incrémente le compteur de décimales dès le moment où le séparateur a été trouvé.
			if sep_trouve == True :
				cpt_dec += 1

			# J'informe que le séparateur a été trouvé.
			if tab_caract[0] in str_valeur[i] :
				sep_trouve = True

			# Je renvoie une erreur si le montant saisi comporte plus de deux décimales.
			if cpt_dec > 2 :
				erreur = True

		# Je renvoie une erreur si le séparateur est le dernier caractère.
		if tab_caract[0] in str_valeur[len(str_valeur) - 1] :
			erreur = True

	# Je traite le cas où le montant saisi est un nombre entier.
	if len(tab_caract) == 0 and str_valeur != '' :
		valide = True

	if str_valeur == '0' :
		if p_etre_nul == False :
			erreur = True

	if valide == False :
		erreur = True

	return erreur

'''
Cette procédure renvoie une erreur si l'option par défaut d'une liste déroulante est choisie (dépendante ou non d'une 
autre liste déroulante).
p_form : Formulaire dont la liste déroulant est issue
p_cle_zl_dep : Nom de la liste déroulante de départ
p_valeur_zl_dep : Valeur de la liste déroulante de départ
p_cle_zl_arr : Valeur de la liste déroulante d'arrivée
p_valeur_zl_arr : Valeur de la liste déroulante d'arrivée
'''
def valid_zl(
	p_form,
	p_cle_zl_dep,
	p_valeur_zl_dep,
	p_cle_zl_arr = None,
	p_valeur_zl_arr = None
	) :
	
	# J'initialise la valeur entière de la liste déroulante.
	reponse = -1

	if p_cle_zl_arr is not None and p_valeur_zl_arr is not None:

		# Je traite le cas où une liste déroulante est dépendante d'une autre.
		if p_valeur_zl_dep != 'D' :
			if p_valeur_zl_arr == 'D' :
				p_form.add_error(p_cle_zl_arr, MESSAGES['required'])
			else :
				try :
					reponse = int(p_valeur_zl_arr)
				except :
					pass

	else :

		# Je traite le cas où une liste déroulante est indépendante.
		if p_valeur_zl_dep == 'D' :
			p_form.add_error(p_cle_zl_dep, MESSAGES['required'])
		else :
			try :
				reponse = int(p_valeur_zl_dep)
			except :
				pass

	return reponse