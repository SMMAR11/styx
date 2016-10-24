from app.constants import *
from app.forms import gestion_dossiers
from app.models import *
from datetime import date
from django.db.models import Q, Sum
from django.template.context_processors import csrf
from django.template.defaultfilters import safe
from functools import reduce
import hashlib
import operator
import string

'''
Cette fonction retourne le gabarit d'affichage d'un message de confirmation de suppression d'un élément de la base de
données.
p_url : URL de la vue permettant la suppression d'un élément de la base de données.
Retourne une chaîne de caractères
'''
def aff_mess_suppr(p_url) :
	return '''
	<div class="row">
		<div class="col-xs-6 text-center">
			<a href="{0}" class="btn bt-vert to-unfocus" onclick="suppr(event)">Oui</a>
		</div>
		<div class="col-xs-6 text-center">
			<button class="btn bt-vert to-unfocus" data-dismiss="modal">Non</button>
		</div>
	</div>
	'''.format(p_url)

'''
Cette fonction permet de générer des données concernant les axes, les sous-axes, les actions et les types de dossiers.
request : Objet requête
'''
def alim_liste(request) :

	# J'initialise la valeur des paramètres "GET".
	v_programme = -1
	v_axe = -1
	v_sous_axe = -1

	# Je déclare des tableaux.
	tab_axes = []
	tab_sous_axes = []
	tab_actions = []
	tab_types = []

	# Je vérifie le renseignement du paramètre "programme".
	if 'programme' in request.GET :
		
		# Je récupère la valeur du paramètre.
		v_programme = request.GET['programme']

		# Je récupère la liste des axes relatifs à un programme.
		les_axes = TAxe.objects.filter(id_progr = v_programme)

		# J'empile le tableau des axes.
		for un_axe in les_axes :
			tab_axes.append([un_axe.id_axe, un_axe.id_axe])

		# Je récupère la liste des types de dossiers relatifs à un programme.
		les_types = TTypeDossier.objects.filter(id_progr = v_programme)

		# J'empile le tableau des types de dossiers.
		for un_type in les_types :
			tab_types.append([un_type.id_type_doss, un_type.int_type_doss])

	# Je vérifie le renseignement du paramètre "axe".
	if 'axe' in request.GET :

		# Je récupère la valeur du paramètre.
		v_axe = request.GET['axe']
		
		# Je récupère la liste des sous-axes relatifs à un programme et un axe.
		les_sous_axes = TSousAxe.objects.filter(id_progr = v_programme, id_axe = v_axe)

		# J'empile le tableau des sous-axes.
		for un_sous_axe in les_sous_axes :
			tab_sous_axes.append([un_sous_axe.id_ss_axe, un_sous_axe.id_ss_axe])

	# Je vérifie le renseignement du paramètre "sous_axe".
	if 'sous_axe' in request.GET :

		# Je récupère la valeur du paramètre.
		v_sous_axe = request.GET['sous_axe']

		# Je récupère la liste des actions relatives à un programme, un axe et un sous-axe.
		les_actions = TAction.objects.filter(
			id_progr = v_programme, 
			id_axe = v_axe, 
			id_ss_axe = v_sous_axe
		)

		# J'empile le tableau des actions.
		for une_action in les_actions :
			tab_actions.append([une_action.id_act, index_alpha(une_action.id_act)])

	# J'initialise les données retournées par la requête "GET" dans un tableau.
	tab_get = {
		'axe' : tab_axes,
		'ss_axe' : tab_sous_axes,
		'act' : tab_actions,
		'type_doss' : tab_types
	}

	return tab_get

'''
Cette fonction retourne une date sous un autre format.
p_valeur : Date dont le format doit être changé
p_format : Format à utiliser
Retourne une chaîne de caractères
'''
def chang_form_dt(p_valeur, p_format = 'AAAA-MM-JJ') :

	reponse = p_valeur

	if p_valeur is not None :

		# J'initialise un tableau contenant les informations de la date.
		tab_date = p_valeur.split('/')

		if p_format == 'AAAA-MM-JJ' :

			# Je définis le séparateur ainsi que les données à concaténer avec le séparateur défini.
			glue = '-'
			pieces = (
				tab_date[2],
				tab_date[1],
				tab_date[0]
			)

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

	# Je crypte la valeur selon la méthode de hashage SHA1 si la valeur renseignée n'est pas nulle.
	if p_valeur is not None :
		p_valeur = hashlib.sha1(p_valeur.encode()).hexdigest()
	
	return p_valeur

'''
Cette fonction renvoie une liste de dossiers filtrés afin d'actualiser une datatable.
request : Objet requête
'''
def filtr_doss(request) :

	# Je récupère les données du formulaire.
	v_moa = integer(init_post(request.POST, 'zl_moa'))
	v_programme = integer(init_post(request.POST, 'zld_progr'))
	v_axe = integer(init_post(request.POST, 'zld_axe'))
	v_sous_axe = integer(init_post(request.POST, 'zld_ss_axe'))
	v_action = integer(init_post(request.POST, 'zld_act'))
	v_nature_dossier = integer(init_post(request.POST, 'zl_nat_doss'))
	v_annee_deliberation_moa_dossier = integer(init_post(request.POST, 'zl_annee_delib_moa_doss'))

	# Je déclare des tableaux d'arguments.
	args = []
	kwargs = {}

	# J'empile les tableaux d'arguments.
	if v_moa > -1 :

		# J'empile le tableau des arguments ayant la clause "OR". Lorsque je choisis un maître d'ouvrage, je regarde
		# dans la table t_regroupement_moa si le maître d'ouvrage choisi correspond à une filiation avec des anciens
		# maîtres d'ouvrages. Dans le cas positif, je cherche les dossiers du groupe de maîtres d'ouvrages.
		les_moa_anciens = TRegroupementMoa.objects.filter(id_org_moa_fil = v_moa)
		for un_moa_ancien in les_moa_anciens :
			args.append(Q(**{ 'id_org_moa' : un_moa_ancien.id_org_moa_anc }))
		
		if len(args) > 0 :
			args.append(Q(**{ 'id_org_moa' : v_moa }))
		else :
			kwargs['id_org_moa'] = v_moa

	if v_programme > -1 :
		kwargs['id_progr'] = v_programme

	if v_axe > -1 :
		kwargs['id_axe'] = v_axe

	if v_sous_axe > -1 :
		kwargs['id_ss_axe'] = v_sous_axe

	if v_action > -1 :
		kwargs['id_act'] = v_action

	if v_nature_dossier > -1 :
		kwargs['id_nat_doss'] = v_nature_dossier

	if v_annee_deliberation_moa_dossier > -1 :
		kwargs['dt_delib_moa_doss__year'] = v_annee_deliberation_moa_dossier

	# Je stocke dans un tableau les dossiers filtrés.
	if len(args) > 0 :
		les_dossiers = TDossier.objects.filter(reduce(operator.or_, args), **kwargs)
	else :
		les_dossiers = TDossier.objects.filter(**kwargs)

	# Je trie les dossiers filtrés.
	les_dossiers = les_dossiers.order_by('-dt_delib_moa_doss', 'num_doss')

	return les_dossiers

'''
Cette fonction convertit une chaîne représentant un nombre entier sous forme de décimal en une chaîne représentant un 
nombre entier sous forme de nombre entier.
p_valeur : Chaîne à convertir
p_zeros_ns : Nombre de zéros significatifs à rajouter
Retourne une chaîne de caractères
'''
def float_to_int(p_valeur, p_zeros_ns = 1) :

	reponse = p_valeur

	if p_valeur is not None :

		# Je transforme le nombre en chaîne de caractères.
		str_valeur = str(p_valeur)

		# Je vérifie si la chaîne de caractères se termine par ".0" afin de retirer la partie décimale inutile.
		if str_valeur.endswith('.0') :
			reponse = str_valeur[:-2]
		else :

			# J'ajoute un zéro à la fin du montant si la partie décimale ne comporte qu'un seul chiffre.
			if '.' in str_valeur[len(str_valeur) - 2] :
				reponse = str_valeur + '0' * p_zeros_ns
			else :
				reponse = str_valeur
				
	return reponse

'''
Cette fonction retourne le gabarit d'affichage de la procédure de choix d'un dossier associé.
request : Objet requête
p_url : URL qui traite le formulaire de filtrage
'''
def gen_tabl_chois_doss(request, p_url) :

	# Je déclare un objet "formulaire" permettant une future manipulation des champs.
	f = gestion_dossiers.ChoisirDossier(prefix = 'ChoisirDossier')

	# J'initialise l'affichage des champs du formulaire de choix d'un dossier associé.
	tab_champs_f = init_form(f)

	# Je stocke dans un tableau tous les dossiers référencés dans la base de données.
	les_dossiers = TDossier.objects.all().order_by('num_doss')

	# Je parcours chaque dossier afin de générer pour chacun d'entre eux une ligne du futur tableau HTML des
	# dossiers.
	contenu_tab_html_dossiers = ''
	for un_dossier in les_dossiers :

		# Je créé une ligne du futur tableau HTML des dossiers.
		contenu_tab_html_dossiers += '''
		<tr>
			<td class="b">{0}</td>
			<td>{1}</td>
			<td>{2}</td>
			<td>{3}</td>
			<td>
				<span class="bt-choisir pointer pull-right" onclick="ajout_doss_ass(event)"></span>
			</td>
		</tr>
		'''.format(
			conv_none(un_dossier.num_doss),
			conv_none(un_dossier.int_doss),
			conv_none(un_dossier.id_org_moa.id_org_moa.n_org),
			conv_none(reecr_dt(un_dossier.dt_delib_moa_doss))
		)

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
		<table class="table display" id="tab_ajouter_dossier_associe">
			<thead>
				<tr>
					<th>Numéro du dossier</th>
					<th>Intitulé du dossier</th>
					<th>MOA</th>
					<th>Date de délibération au MOA</th>
					<th></th>
				</tr>
			</thead>
			<tbody>{9}</tbody>
		</table>
	</div>
	'''.format(
		p_url,
		(csrf(request)['csrf_token']),
		tab_champs_f['zl_moa'],
		tab_champs_f['zld_progr'],
		tab_champs_f['zld_axe'],
		tab_champs_f['zld_ss_axe'],
		tab_champs_f['zld_act'],
		tab_champs_f['zl_nat_doss'],
		tab_champs_f['zl_annee_delib_moa_doss'],
		contenu_tab_html_dossiers
	)

'''
Cette fonction retourne une lettre de l'alphabet en fonction de son indice.
p_valeur : Nombre à convertir 
Retourne un caractère
'''
def index_alpha(p_valeur) :

	# Je déclare le tableau relatif à l'alphabet.
	tab_alphabet = list(string.ascii_lowercase)

	return tab_alphabet[p_valeur - 1]

''' 
Cette fonction retourne le gabarit d'affichage d'une fenêtre modale.
p_suffixe : Suffixe utilisé pour reconnaître chaque élément de la fenêtre modale
p_header : En-tête de la fenêtre modale
p_body : Corps de la fenêtre modale
Retourne la fenêtre modale
'''
def init_fm(p_suffixe, p_header, p_body = '') :

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
Cette fonction retourne le gabarit d'affichage de chaque champ d'un formulaire.
p_form : Formulaire à traiter
Retourne un tableau associatif
'''
def init_form(p_form) :

	# Je déclare le tableau qui contiendra le gabarit d'affichage de chaque champ du formulaire traité.
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
				<label>{label}</label>
				<div class="input-file-container">
					{champ}
					<span class="input-file-trigger">Parcourir</span>
					<p class="file-return"></p>
				</div>
				<span class="za_erreur"></span>
			</div>
			'''.format(label = un_champ.label, champ = un_champ)

		# Je traite le cas où le champ en cours est une case à cocher.
		if un_champ.name.startswith('cb_') == True :
			autre_gabarit = True
			contenu = '''
			<div>
				<div class="checkbox">
					<label>{champ}{label}</label>
				</div>
				<span class="za_erreur"></span>
			</div>
			'''.format(champ = un_champ, label = un_champ.label)

		# Je traite le cas où le champ en cours est une case à cocher multiple.
		if un_champ.name.startswith('cbsm_') == True :
			autre_gabarit = True

			# J'initialise l'indice de départ du sommet du tableau des options.
			sommet = -1

			# Je déclare deux chaînes de caractères vides qui s'implémenteront selon la valeur du sommet.
			rangee_gauche = ''
			rangee_droite = ''

			# Je parcours chaque élément du tableau des options.
			for un_element in un_champ :

				# J'incrémente la valeur du sommet.
				sommet += 1

				contenu_option = '''
				<div class="checkbox c-police" style="margin-top: 0;">
					{champ}
				</div>
				'''.format(champ = un_element)

				# Je stocke l'option dans l'une des deux rangées (selon la valeur du modulo du sommet).
				if sommet % 2 == 0 :
					rangee_gauche += contenu_option
				else :
					rangee_droite += contenu_option		

			contenu = '''
			<div class="field-wrapper">
				<label>{label}</label>
				<div class="row">
					<div class="col-xs-6">{gauche}</div>
					<div class="col-xs-6">{droite}</div>
				</div>
				<span class="za_erreur"></span>
			</div>
			'''.format(label = un_champ.label, gauche = rangee_gauche, droite = rangee_droite)

		# Je traite le cas classique si le champ en cours ne demande pas un gabarit d'affichage spécifique.
		if autre_gabarit == False :
			if un_champ.label != '' :
				contenu = '''
				<div class="field-wrapper">
					<label>{label}</label>
					{champ}
					<span class="za_erreur"></span>
				</div>
				'''.format(label = un_champ.label, champ = un_champ)
			else :
				contenu = '''
				<div class="field-wrapper">
					{champ}
					<span class="za_erreur"></span>
				</div>
				'''.format(champ = un_champ)

		# J'affecte le contenu HTML du champ au tableau des gabarits d'affichage des champs du formulaire.
		tab_champs[un_champ.name] = safe(contenu)

	return tab_champs

''' 
Cette fonction retourne le gabarit d'affichage de chaque attribut de consultation.
p_tab : Tableau de données à traiter
Retourne un tableau associatif
'''
def init_pg_cons(p_tab) :

	# Je déclare le tableau qui contiendra le gabarit d'affichage de chaque attribut.
	tab_attributs = {}

	for cle, valeur in p_tab.items() :

		# J'initialise le gabarit d'affichage.
		if 'textarea' in valeur and valeur['textarea'] == True :
			contenu = '''
			<div class="attribute-wrapper">
				<label class="c-theme">{label}</label>
				<textarea class="form-control" rows="5" readonly>{valeur}</textarea>
			</div>
			'''.format(label = valeur['label'], valeur = valeur['value'])
		else :
			contenu = '''
			<div class="attribute-wrapper">
				<label class="c-theme">{label}</label>
				<input class="form-control" value="{valeur}" type="text" readonly>
			</div>
			'''.format(label = valeur['label'], valeur = valeur['value'])

		# J'affecte le contenu HTML du champ au tableau des gabarits d'affichage des champs du formulaire.
		tab_attributs[cle] = safe(contenu)

	return tab_attributs

'''
Cette fonction renvoie la valeur d'un élément d'un tableau "POST" selon l'existence ou non de cet élément dans le
tableau "POST".
p_tab : Tableau "POST"
p_cle : Clé de l'élément existant ou non du tableau "POST"
Retourne un nombre
'''
def init_post(p_tab, p_cle) :

	reponse = -1

	# Je vérifie l'existence de la clé dans le tableau "POST" afin de mettre à jour la valeur de l'élément du tableau
	# "POST" à une clé donnée.
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

'''
Cette fonction essaie de convertir une valeur en un nombre. Si la valeur est une chaîne de caractères, alors le nombre
retourné sera -1.
p_valeur : Valeur à convertir
Retourne un nombre entier
'''
def integer(p_valeur) :

	# J'initialise la valeur qui sera retournée par la fonction.
	reponse = -1

	# Je tente de convertir la valeur en un nombre entier.
	try :
		reponse = int(p_valeur)
	except :
		pass

	return reponse

''' 
Cette fonction nettoie la valeur d'une variable pour lui assigner une valeur nulle dans différents cas de figure.
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
	tab_lignes = []
	for i in range(0, len(p_tab)) :
		for j in range(0, len(p_tab[i])) :
			tab_lignes.append(p_tab[i][j])

	# J'initialise un ensemble vide qui par la suite aidera à la recherche des tuples en doublons.
	tab_tuples = set()

	# Je déclare un tableau de tuples vide.
	tab = []
	
	for une_ligne in tab_lignes :

		# J'initialise le tuple de la ligne courante.
		un_tuple = tuple(une_ligne)

		if un_tuple not in tab_tuples :

			# J'empile le tableau des tuples sans doublons.
			tab.append(un_tuple)

			# J'informe pour la suite de la boucle que le tuple courant a été reconnu.
			tab_tuples.add(un_tuple)

	return tab

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