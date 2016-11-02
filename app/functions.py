#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.constants import *
from datetime import date

'''
Cette fonction retourne un message de confirmation de suppression d'un élément.
p_vue : Vue supprimant un objet
Retourne une chaîne de caractères
'''
def aff_mess_suppr(p_vue) :

	return '''
	<div class="row">
		<div class="col-xs-6 text-center">
			<a href="{0}" class="btn bt-vert to-unfocus" onclick="suppr(event)">Oui</a>
		</div>
		<div class="col-xs-6 text-center">
			<button class="btn bt-vert to-unfocus" data-dismiss="modal">Non</button>
		</div>
	</div>
	'''.format(p_vue)

'''
Cette fonction permet de générer des données concernant les axes, les sous-axes, les actions et les types de dossiers.
request : Objet requête
'''
def alim_liste(request) :

	''' Imports '''
	from app.functions import index_alpha
	from app.models import TAction, TAxe, TSousAxe, TTypeDossier

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
			tab_axes.append([un_axe.id_axe, un_axe.id_axe])

		# Je récupère la liste des types de dossiers relatifs à un programme.
		les_types_doss = TTypeDossier.objects.filter(id_progr = v_progr)

		# J'empile le tableau des types de dossiers.
		for un_type_doss in les_types_doss :
			tab_types_doss.append([un_type_doss.id_type_doss, un_type_doss.int_type_doss])

	if 'axe' in request.GET :

		# Je récupère la valeur du paramètre "GET".
		v_axe = request.GET['axe']
		
		# Je récupère la liste des sous-axes relatifs à un programme et un axe.
		les_ss_axes = TSousAxe.objects.filter(id_progr = v_progr, id_axe = v_axe)

		# J'empile le tableau des sous-axes.
		for un_ss_axe in les_ss_axes :
			tab_ss_axes.append([un_ss_axe.id_ss_axe, un_ss_axe.id_ss_axe])

	if 'sous_axe' in request.GET :

		# Je récupère la valeur du paramètre.
		v_ss_axe = request.GET['sous_axe']

		# Je récupère la liste des actions relatives à un programme, un axe et un sous-axe.
		les_act = TAction.objects.filter(id_progr = v_progr, id_axe = v_axe, id_ss_axe = v_ss_axe)

		# J'empile le tableau des actions.
		for une_act in les_act :
			tab_act.append([une_act.id_act, index_alpha(une_act.id_act)])

	return {
		'axe' : tab_axes,
		'ss_axe' : tab_ss_axes,
		'act' : tab_act,
		'type_doss' : tab_types_doss
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
	from app.functions import init_post, integer
	from app.models import TDossier, TRegroupementMoa
	from django.db.models import Q
	from functools import reduce
	import operator

	# Je récupère les données du formulaire.
	v_org_moa = integer(init_post(request.POST, 'zl_org_moa'))
	v_progr = integer(init_post(request.POST, 'zld_progr'))
	v_axe = integer(init_post(request.POST, 'zld_axe'))
	v_ss_axe = integer(init_post(request.POST, 'zld_ss_axe'))
	v_act = integer(init_post(request.POST, 'zld_act'))
	v_nat_doss = integer(init_post(request.POST, 'zl_nat_doss'))
	v_ann_delib_moa_doss = integer(init_post(request.POST, 'zl_ann_delib_moa_doss'))

	# Je déclare des tableaux qui stockeront les conditions de la requête SQL.
	tab_or = []
	tab_and = {}

	# J'empile les tableaux des conditions.
	if v_org_moa > -1 :

		for un_couple_moa in TRegroupementMoa.objects.filter(id_org_moa_fil = v_org_moa) :
			tab_or.append(Q(**{ 'id_org_moa' : un_couple_moa.id_org_moa_anc }))
		
		if len(tab_or) > 0 :
			tab_or.append(Q(**{ 'id_org_moa' : v_org_moa }))
		else :
			tab_and['id_org_moa'] = v_org_moa

	if v_progr > -1 :
		tab_and['id_progr'] = v_progr

	if v_axe > -1 :
		tab_and['id_axe'] = v_axe

	if v_ss_axe > -1 :
		tab_and['id_ss_axe'] = v_ss_axe

	if v_act > -1 :
		tab_and['id_act'] = v_act

	if v_nat_doss > -1 :
		tab_and['id_nat_doss'] = v_nat_doss

	if v_ann_delib_moa_doss > -1 :
		tab_and['dt_delib_moa_doss__year'] = v_ann_delib_moa_doss

	# Je stocke dans un tableau les dossiers filtrés.
	if len(tab_or) > 0 :
		les_doss = TDossier.objects.filter(reduce(operator.or_, tab_or), **tab_and)
	else :
		les_doss = TDossier.objects.filter(**tab_and)

	# Je trie les dossiers filtrés.
	les_doss = les_doss.order_by('-dt_delib_moa_doss', 'num_doss')

	return les_doss

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
	for un_doss in TDossier.objects.order_by('num_doss') :

		# J'initialise une ligne du tableau HTML des dossiers filtrés.
		lg = '''
		<tr>
			<td class="b">{0}</td>
			<td>{1}</td>
			<td>{2}</td>
			<td>{3}</td>
			<td>
				<span class="bt-choisir pointer pull-right" onclick="ajout_doss_ass(event)" title="Choisir le dossier"></span>
			</td>
		</tr>
		'''.format(
			conv_none(un_doss.num_doss),
			conv_none(un_doss.int_doss),
			conv_none(un_doss.id_org_moa.id_org_moa.n_org),
			conv_none(reecr_dt(un_doss.dt_delib_moa_doss))
		)

		# J'ajoute la ligne du tableau HTML des dossiers filtrés.
		tab_lg.append(lg)

	return '''
	<form name="form_ajouter_dossier_associe" method="post" action="{0}" class="c-theme">
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
					<th>Intitulé</th>
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
			tab_rng_d = ['']

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
				<div class="field-wrapper">
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
Cette fonction renvoie la valeur d'un élément d'un tableau "POST" selon l'existence ou non de cet élément dans le
tableau "POST".
p_tab : Tableau "POST"
p_cle : Clé de l'élément
Retourne un nombre
'''
def init_post(p_tab, p_cle) :

	reponse = -1

	if p_cle in p_tab :
		reponse = p_tab[p_cle]

	return reponse

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
def obt_pourcentage(p_valeur) :

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
	chem_fich = '{0}\{1}'.format(MEDIA_ROOT, p_chem_fich)

	with open(chem_fich, 'wb+') as fich :
		for c in p_fich.chunks() :
			fich.write(c)

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