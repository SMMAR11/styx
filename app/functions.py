#!/usr/bin/env python
#-*- coding: utf-8

'''
Cette fonction retourne un tableau de données.
request : Objet requête
Retourne un tableau associatif
'''
def alim_ld(request) :

	# Imports
	from app.models import TAction
	from app.models import TAxe
	from app.models import TProgramme
	from app.models import TSousAxe
	from app.models import TTypesProgrammesTypeDossier

	# J'initialise certaines valeurs du formulaire non-soumis.
	v_type_progr = ''
	v_progr = ''
	v_axe = ''
	v_ss_axe = ''
	try :
		v_progr = request.POST['id_progr']
	except :
		pass
	try :
		v_axe = request.POST['num_axe']
	except :
		pass
	try :
		v_ss_axe = request.POST['num_ss_axe']
	except :
		pass

	# Je déclare les tableaux de sortie.
	t_axes = []
	t_ss_axes = []
	t_act = []
	t_types_doss = []

	# Je prépare et mets en forme les données des tableaux de sortie.
	if v_progr :
		qs_axes = TAxe.objects.filter(id_progr = v_progr)
		for a in qs_axes :
			t_axes.append([a.pk, a.num_axe])
		try :
			v_type_progr = TProgramme.objects.get(pk = v_progr).id_type_progr
		except :
			pass
		qs_types_doss = TTypesProgrammesTypeDossier.objects.filter(id_type_progr = v_type_progr).order_by(
			'id_type_doss'
		)
		for td in qs_types_doss :
			t_types_doss.append([td.id_type_doss.pk, td.id_type_doss.int_type_doss])
		if v_axe :
			qs_ss_axes = TSousAxe.objects.filter(id_axe = v_axe)
			for sa in qs_ss_axes :
				t_ss_axes.append([sa.pk, sa.num_ss_axe])
			if v_ss_axe :
				qs_act = TAction.objects.filter(id_ss_axe = v_ss_axe)
				for a in qs_act :
					t_act.append([a.pk, a.num_act])

	return {
		'axe' : t_axes,
		'ss_axe' : t_ss_axes,
		'act' : t_act,
		'type_doss' : t_types_doss
	}

'''
Réinitialisation d'une datatable
_html : Code HTML
_datas : Données de sortie sous forme de tableau associatif
Retourne une réponse HTTP
'''
def datatable_reset(_html, _datas = {}) :

	# Imports
	from bs4 import BeautifulSoup
	from django.http import HttpResponse
	import json

	# Possibilité de manier le code HTML
	html = BeautifulSoup(_html)

	# Initialisation des données de sortie
	success = { cle : val for cle, val in _datas.items() }
	success['datatable'] = [[''.join(str(elem) for elem in td.contents if elem != '\n') for td in tr.find_all('td')] \
	for tr in html.find_all('tbody')[0].find_all('tr')]
	success['datatable_name'] = html.find_all('div', { 'class' : 'my-table'})[0]['id'][2:]

	return HttpResponse(json.dumps({ 'success' : success }), content_type = 'application/json')

'''
Cette fonction retourne une date au format français.
_d : Date convertie
Retourne une chaîne de caractères
'''
def dt_fr(_d) :

	# Imports
	from datetime import datetime

	output = _d

	if _d :
		d = datetime.strptime(str(_d), '%Y-%m-%d')
		output = d.strftime('%d/%m/%Y')

	return output

'''
Cette fonction retourne un tableau de dossiers filtrés.
request : Objet requête
_d_excl : Dossier exclu du résultat de la requête.
Retourne un jeu de données
'''
def filtr_doss(request, _d_excl = None) :

	# Imports
	from app.forms.gestion_dossiers import ChoisirDossier
	from app.functions import obt_doss_regr
	from app.models import TAction
	from app.models import TAxe
	from app.models import TDossier
	from app.models import TSousAxe

	# Je soumets le formulaire.
	f_chois_doss = ChoisirDossier(request.POST, prefix = 'ChoisirDossier')

	# Je rajoute des choix valides pour certaines listes déroulantes (prévention d'erreurs).
	post_progr = request.POST['ChoisirDossier-zl_progr']
	post_axe = request.POST['ChoisirDossier-zl_axe']
	post_ss_axe = request.POST['ChoisirDossier-zl_ss_axe']
	if post_progr :
		t_axes = [(a.pk, a.pk) for a in TAxe.objects.filter(id_progr = post_progr)]
		f_chois_doss.fields['zl_axe'].choices = t_axes
		t_ss_axes = [(sa.pk, sa.pk) for sa in TSousAxe.objects.filter(id_axe = post_axe)]
		f_chois_doss.fields['zl_ss_axe'].choices = t_ss_axes
		t_act = [(a.pk, a.pk) for a in TAction.objects.filter(id_ss_axe = post_ss_axe)]
		f_chois_doss.fields['zl_act'].choices = t_act

	if f_chois_doss.is_valid() :

		# Je récupère les données du formulaire valide.
		cleaned_data = f_chois_doss.cleaned_data
		v_org_moa = cleaned_data.get('zl_org_moa')
		v_progr = cleaned_data.get('zl_progr')
		v_axe = cleaned_data.get('zl_axe')
		v_ss_axe = cleaned_data.get('zl_ss_axe')
		v_act = cleaned_data.get('zl_act')
		v_nat_doss = cleaned_data.get('zl_nat_doss')
		v_ann_delib_moa_doss = cleaned_data.get('zl_ann_delib_moa_doss')

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
		if v_ann_delib_moa_doss :
			t_sql['and']['dt_delib_moa_doss__year'] = v_ann_delib_moa_doss

		# J'initialise la requête.
		if v_org_moa :
			qs_doss = obt_doss_regr(v_org_moa).filter(**t_sql['and'])
		else :
			qs_doss = TDossier.objects.filter(**t_sql['and'])
		if _d_excl :
			qs_doss = qs_doss.exclude(pk = _d_excl)

	else :
		qs_doss = []

	return qs_doss

'''
Cette fonction génère une chaîne de caractères selon le datetime courant.
Retourne une chaîne de caractères
'''
def gen_cdc() :

	# Imports
	import hashlib
	import time

	# Je récupère le "datetime" courant.
	dt = time.strftime('%d%m%Y%H%M%S')

	# Je crypte le "datetime" courant selon la méthode de hashage "SHA1".
	dt_crypt = hashlib.sha1(dt.encode()).hexdigest()

	return dt_crypt

'''
Cette fonction retourne le formulaire d'ajout d'un avenant.
request : Objet requête
_pd : Objet TPrestationsDossier
_u : URL traitant le formulaire
Retourne une chaîne de caractères
'''
def gen_f_ajout_aven(request, _pd, _u) :

	# Imports
	from app.forms.gestion_dossiers import GererAvenant
	from app.functions import init_f
	from django.template.context_processors import csrf

	# J'instancie un objet "formulaire".
	f = GererAvenant(prefix = 'GererAvenant', k_prest_doss = _pd)

	# J'initialise le gabarit de chaque champ du formulaire.
	t = init_f(f)

	return '''
	<form action="{0}" enctype="multipart/form-data" name="f_ajout_aven" method="post" onsubmit="soum_f(event)">
		<input name="csrfmiddlewaretoken" type="hidden" value="{1}">
		<div class="row">
			<div class="col-sm-6">{2}</div>
			<div class="col-sm-6">{3}</div>
		</div>
		{4}
		{5}
		{6}
		{7}
		{8}
		<button class="center-block green-btn my-btn" type="submit">Valider</button>
	</form>
	'''.format(
		_u,
		csrf(request)['csrf_token'],
		t['za_num_doss'],
		t['zl_prest'],
		t['int_aven'],
		t['dt_aven'],
		t['mont_aven'],
		t['chem_pj_aven'],
		t['comm_aven']
	)

'''
Cette fonction retourne un tableau HTML de dossiers.
request : Objet requête
_d_excl : Dossier exclu du résultat de la requête.
Retourne un tableau HTML
'''
def gen_t_ch_doss(request, _d_excl = None) :

	# Imports
	from app.forms.gestion_dossiers import ChoisirDossier
	from app.functions import dt_fr
	from app.functions import init_f
	from app.functions import obt_doss_regr
	from app.models import TDossier
	from app.models import TMoa
	from app.models import TUtilisateur
	from django.template.context_processors import csrf

	# J'initialise la valeur de l'argument "k_org_moa".
	try :
		v_org_moa = TMoa.objects.get(
			pk = TUtilisateur.objects.get(pk = request.user.pk).id_org,
			peu_doss = True,
			en_act_doss = True
		).pk
	except :
		v_org_moa = None

	# J'instancie un objet "formulaire".
	f_ch_doss = ChoisirDossier(prefix = 'ChoisirDossier', k_org_moa = v_org_moa)

	# J'initialise le gabarit de chaque champ du formulaire.
	t_ch_doss = init_f(f_ch_doss)

	# J'initialise la requête.
	if v_org_moa :
		qs_doss = obt_doss_regr(v_org_moa)
	else :
		qs_doss = TDossier.objects.all()
	if _d_excl :
		qs_doss = qs_doss.exclude(pk = _d_excl)

	# J'empile le tableau des lignes du tableau HTML.
	t_lg = []
	for d in qs_doss :
		lg = '''
		<tr>
			<td class="b">{0}</td>
			<td>{1}</td>
			<td>{2}</td>
			<td>{3}</td>
			<td><span class="choose-icon pointer pull-right" title="Choisir le dossier"></span></td>
		</tr>
		'''.format(
			d,
			d.get_int_doss(),
			d.id_org_moa,
			dt_fr(d.dt_delib_moa_doss) or '-'
		)
		t_lg.append(lg)

	return '''
	<form action="?action=filtrer-dossiers" method="post" name="f_ch_doss">
		<input name="csrfmiddlewaretoken" type="hidden" value="{0}">
		<fieldset class="my-fieldset" style="padding-bottom: 0;">
			<legend>Rechercher par</legend>
			<div>
				<div class="row">
					<div class="col-xs-6">{1}</div>
					<div class="col-xs-6">{2}</div>
				</div>
				<div class="row">
					<div class="col-xs-6">{3}</div>
					<div class="col-xs-3">{4}</div>
					<div class="col-xs-3">{5}</div>
				</div>
				<div class="row">
					<div class="col-xs-6">{6}</div>
					<div class="col-xs-6">{7}</div>
				</div>
			</div>
		</fieldset>
	</form>
	<div class="br"></div>
	<div class="my-table" id="t_ch_doss">
		<table>
			<thead>
				<tr>
					<th>N° du dossier</th>
					<th>Intitulé du dossier</th>
					<th>Maître d'ouvrage</th>
					<th>Date de délibération au maître d'ouvrage</th>
					<th></th>
				</tr>
			</thead>
			<tbody>{8}</tbody>
		</table>
	</div>
	'''.format(
		(csrf(request)['csrf_token']),
		t_ch_doss['zl_org_moa'],
		t_ch_doss['zl_progr'],
		t_ch_doss['zl_axe'],
		t_ch_doss['zl_ss_axe'],
		t_ch_doss['zl_act'],
		t_ch_doss['zl_nat_doss'],
		t_ch_doss['zl_ann_delib_moa_doss'],
		'\n'.join(t_lg)
	)

'''
Cette procédure (ou fonction) permet de savoir si un utilisateur peut accéder ou non à une vue.
request : Objet requête
Retourne un booléen si le paramètre "_h" vaut False
_u : Utilisateur en cours
_d : Dossier cible (objet TDossier ou tableau)
_g : Dois-je vérifier l'accès en lecture ou en écriture ?
_h : Dois-je déclencher une erreur 403 en cas de non-permission ?
'''
def ger_droits(_u, _d, _g = True, _h = True) :

	# Imports
	from app.models import TDroit
	from app.models import TMoa
	from app.models import TRegroupementsMoa
	from app.models import TTypeProgramme
	from django.core.exceptions import PermissionDenied

	t_coupl = []
	for d in TDroit.objects.filter(id_util = _u).order_by('id') :

		# J'initialise le tableau des maîtres d'ouvrages (identifiants).
		if d.id_org_moa :
			t_org_moa = [rm.id_org_moa_anc.pk for rm in TRegroupementsMoa.objects.filter(id_org_moa_fil = d.id_org_moa)]
			t_org_moa.append(d.id_org_moa.pk)
		else :
			t_org_moa = [m.pk for m in TMoa.objects.all()]

		# J'initialise le tableau des types de programmes (identifiants).
		if d.id_type_progr :
			t_type_progr = [d.id_type_progr.pk]
		else :
			t_type_progr = [tp.pk for tp in TTypeProgramme.objects.all()]

		# Je définis si je dois vérifier le droit en écriture ou en lecture.
		attr = d.en_lect
		if _g == False :
			attr = d.en_ecr

		# Je prépare le tableau des couples valides.
		for i in t_org_moa :
			for j in t_type_progr :
				coupl = (i, j)
				if attr == True :
					t_coupl.append(coupl)
				else :
					if coupl in t_coupl :
						t_coupl.remove(coupl)

	# Je retire les doublons.
	t_coupl_uniq = set(t_coupl)

	# Je vérifie si l'utilisateur peut accéder à la vue.
	trouve = False
	if isinstance(_d, list) == True :
		for e in _d :
			tupl = tuple(e)
			if tupl in t_coupl_uniq :
				trouve = True
	else :
		if (_d.id_org_moa.pk, _d.id_progr.id_type_progr.pk) in t_coupl_uniq :
			trouve = True

	if _h == True :
		if trouve == False :
			raise PermissionDenied
	else :
		return trouve

'''
Obtention du menu
Retourne un tableau associatif
'''
def get_menu() :

	# Imports
	from collections import OrderedDict
	from django.core.urlresolvers import reverse

	output = {
		'port_cart' : {
			'mod_name' : 'Portail cartographique',
			'mod_img' : 'pics/thumbnails/portail_cartographique/main.jpg',
			'mod_href' : 'http://carto.smmar.fr/styx',
			'mod_href_blank' : 'target',
			'mod_items' : [],
			'mod_rank' : 1
		},
		'gest_doss' : {
			'mod_name' : 'Gestion des dossiers',
			'mod_img' : 'pics/thumbnails/gestion_dossiers/main.png',
			'mod_href' : reverse('gest_doss'),
			'mod_href_blank' : '',
			'mod_items' : [
				{
					'item_name' : 'Créer un dossier',
					'item_img' : 'pics/thumbnails/gestion_dossiers/add.png',
					'item_href' : reverse('cr_doss')
				},
				{
					'item_name' : 'Consulter un dossier',
					'item_img' : 'pics/thumbnails/gestion_dossiers/consult.png',
					'item_href' : reverse('ch_doss')
				}
			],
			'mod_rank' : 2
		},
		'real_etats' : {
			'mod_name' : 'Réalisation d\'états',
			'mod_img' : 'pics/thumbnails/realisation_etats/main.png',
			'mod_href' : reverse('real_etats'),
			'mod_href_blank' : '',
			'mod_items' : [
				{
					'item_name' : 'En sélectionnant des dossiers',
					'item_img' : 'pics/thumbnails/realisation_etats/main.png',
					'item_href' : reverse('select_doss')
				},
				{
					'item_name' : 'En regroupant des dossiers',
					'item_img' : 'pics/thumbnails/realisation_etats/main.png',
					'item_href' : reverse('regroup_doss')
				},
				{
					'item_name' : 'En sélectionnant des prestations',
					'item_img' : 'pics/thumbnails/realisation_etats/main.png',
					'item_href' : reverse('select_prest')
				},
				{
					'item_name' : 'En regroupant des prestations',
					'item_img' : 'pics/thumbnails/realisation_etats/main.png',
					'item_href' : reverse('regroup_prest')
				},
				{
					'item_name' : "État d'avancement d'un programme",
					'item_img' : 'pics/thumbnails/realisation_etats/main.png',
					'item_href' : reverse('avancement_programme')
				},
			],
			'mod_rank' : 3
		},
		'pgre' : {
			'mod_name' : 'PGRE',
			'mod_img' : 'pics/thumbnails/pgre/main.jpg',
			'mod_href' : reverse('pgre'),
			'mod_href_blank' : '',
			'mod_items' : [
				{
					'item_name' : 'Créer une action PGRE',
					'item_img' : 'pics/thumbnails/pgre/add.jpg',
					'item_href' : reverse('cr_act_pgre')
				},
				{
					'item_name' : 'Consulter une action PGRE',
					'item_img' : 'pics/thumbnails/pgre/consult.jpg',
					'item_href' : reverse('ch_act_pgre')
				},
				{
					'item_name' : 'Réalisation d\'états PGRE',
					'item_img' : 'pics/thumbnails/pgre/realisation_etats.png',
					'item_href' : reverse('select_act_pgre')
				}
			],
			'mod_rank' : 4
		}
	}

	return OrderedDict(sorted(output.items(), key = lambda x : x[1]['mod_rank']))

'''
Mise en forme d'un menu à vignettes
_module : Module source (ou __ALL__)
_lim : Limite de vignettes
Retourne une chaîne de caractères
'''
def get_thumbnails_menu(_module, _lim) :

	# Imports
	from app.functions import get_menu
	from django.conf import settings
	from django.core.urlresolvers import reverse
	from django.template.defaultfilters import safe

	# Gestion des erreurs
	if type(_lim) is int :
		if not 0 < _lim < 5 :
			raise ValueError('La valeur du paramètre _lim doit être comprise dans l\'intervalle ]0; 4].')
	else :
		raise ValueError('La valeur du paramètre _lim doit être un nombre entier.')

	# Stockage du menu
	menu = get_menu()

	# Mise en forme d'une vignette
	thumbnail = '''
	<a class="custom-thumbnail" href="{}" target="{}">
		<img src="{}">
		<div>{}</div>
	</a>
	'''

	# Initialisation des vignettes
	if _module in menu.keys() :
		thumbnails = [thumbnail.format(
			elem['item_href'],
			'',
			settings.STATIC_URL + elem['item_img'],
			elem['item_name']
		) for elem in menu[_module]['mod_items']]
	else :
		if _module == '__ALL__' :
			thumbnails = [thumbnail.format(
				val['mod_href'],
				val['mod_href_blank'],
				settings.STATIC_URL + val['mod_img'],
				val['mod_name']
			) for key, val in menu.items()]
		else :
			thumbnails = []

	'''
	Création d'une ligne
	_array : Tableau source
	_start : Indice de départ
	_lim : Limite de vignettes
	Retourne une chaîne de caractères
	'''
	def create_row(_array, _start, _lim) :
		return '<div class="row">{}</div>'.format(
			''.join(['<div class="col-sm-{}">{}</div>'.format(
				'{0:g}'.format(12 / _lim), _array[_start + i]
			) for i in range(_lim)])
		)

	# Stockage du nombre de vignettes ainsi que du nombre de vignettes non-assignées à une ligne complète
	thumbnails__length = len(thumbnails)
	missing_thumbnails__length = thumbnails__length % _lim

	# Initialisation des lignes
	rows = []
	for i in range(thumbnails__length // _lim) : rows.append(create_row(thumbnails, i * _lim, _lim))
	if missing_thumbnails__length > 0 :
		rows.append(
			create_row(thumbnails, thumbnails__length - missing_thumbnails__length, missing_thumbnails__length)
		)

	return safe('<div class="thumbnails-row">{}</div>'.format(''.join(rows)) if len(rows) > 0 else '')

'''
Obtention d'un gabarit normé pour chaque champ d'un formulaire
_form : Objet "formulaire"
Retourne un tableau associatif
'''
def init_f(_form) :

	# Imports
	from bs4 import BeautifulSoup
	from django.template.defaultfilters import safe

	output = {}

	# Mise en forme du gabarit par défaut
	gab_defaut = '''
	<div class="field-wrapper" id="fw_{0}">
		<span class="field-label">{1}</span>
		<span class="field-control">{2}</span>
		<span class="field-error"></span>
	</div>
	'''

	for champ in _form :
		gab = None

		# Conversion du champ en code HTML
		champ_html = '{0}'.format(champ)

		# Définition du nom du champ (valeur de l'attribut "name")
		if _form.prefix :
			set_name = '{0}-{1}'.format(_form.prefix, champ.name)
		else :
			set_name = champ.name

		# Stockage du type de champ
		bs_champ = BeautifulSoup(champ_html, 'html.parser')
		balise_init = bs_champ.find_all()[0].name

		if balise_init == 'a' :

			bs = BeautifulSoup(champ_html, 'html.parser')
			tab_input = bs.find_all('input')

			if len(tab_input) > 1 :
				span = '''
				<span class="delete-file">
					{0}
					{1}
				</span>
				'''.format(tab_input[0], bs.find_all('label')[0])
			else :
				span = ''

			gab = '''
			<div class="field-wrapper" id="fw_{0}">
				<span class="field-label">{1}</span>
				<div class="input-file-container">
					<span class="field-control">{2}</span>
					<span class="input-file-trigger">Parcourir</span>
					<div class="input-file-return">
						<span class="file-infos">
							{3}
						</span>
						{4}
					</div>
				</div>
				<span class="field-error"></span>
			</div>
			'''.format(
				set_name,
				champ.label,
				tab_input[len(tab_input) - 1],
				bs.find_all('a')[0]['href'],
				span
			)

		if balise_init == 'input' :

			# Mise en forme d'une zone de saisie de type "checkbox"
			if 'type="checkbox"' in champ_html :
				gab = '''
				<div class="field-wrapper" id="fw_{0}">
					<span class="field-control">{1}</span>
					<span class="field-label">{2}</span>
					<span class="field-error"></span>
				</div>
				'''.format(set_name, champ, champ.label)

			# Mise en forme d'une zone de saisie de type "file"
			if 'type="file"' in champ_html :
				gab = '''
				<div class="field-wrapper" id="fw_{0}">
					<span class="field-label">{1}</span>
					<div class="input-file-container">
						<span class="field-control">{2}</span>
						<span class="input-file-trigger">Parcourir</span>
					</div>
					<span class="field-error"></span>
				</div>
				'''.format(set_name, champ.label, champ)

			# Mise en forme d'une zone de saisie de type "number"
			if 'type="number"' in champ_html :
				champ_html_modif = champ_html.replace('type="number"', 'type="text"')
				champ_html_modif = champ_html_modif.replace('step="any"', '')
				if 'input-group-addon="euro"' in champ_html :
					gab = '''
					<div class="field-wrapper" id="fw_{0}">
						<span class="field-label">{1}</span>
						<div class="form-group">
							<span class="field-control">
								<div class="input-group">
									{2}
									<span class="input-group-addon">
										<span class="fa fa-eur"></span>
									</span>
								</div>
							</span>
						</div>
						<span class="field-error"></span>
					</div>
					'''.format(set_name, champ.label, champ_html_modif)
				else :
					gab = gab_defaut.format(set_name, champ.label, champ_html_modif)

			# Mise en forme d'une zone de saisie de type "password"
			if 'type="password"' in champ_html :
				gab = gab_defaut.format(set_name, champ.label, champ)

			# Mise en forme d'une zone de saisie de type "text"
			if 'type="text"' in champ_html :
				if 'input-group-addon="date"' in champ_html :
					gab = '''
					<div class="field-wrapper" id="fw_{0}">
						<span class="field-label">{1}</span>
						<div class="form-group">
							<span class="field-control">
								<div class="input-group">
									{2}
									<span class="date input-group-addon">
										<input name="{3}__datepicker" type="hidden">
										<span class="glyphicon glyphicon-calendar"></span>
									</span>
								</div>
							</span>
						</div>
						<span class="field-error"></span>
					</div>
					'''.format(set_name, champ.label, champ, set_name)
				elif 'input-group-addon="email"' in champ_html :
					gab = '''
					<div class="field-wrapper" id="fw_{0}">
						<span class="field-label">{1}</span>
						<div class="form-group">
							<span class="field-control">
								<div class="input-group">
									{2}
									<span class="input-group-addon">
										<span class="fa fa-at"></span>
									</span>
								</div>
							</span>
						</div>
						<span class="field-error"></span>
					</div>
					'''.format(set_name, champ.label, champ)
				elif 'typeahead="on"' in champ_html :
					gab = '''
					<div class="field-wrapper" id="fw_{0}">
						<span class="field-label">{1}</span>
						<div class="typeahead__container">
							<div class="typeahead__field">
								<span class="typeahead__query">
									<div class="form-group">
										<span class="field-control">
											<div class="input-group">
												{2}
												<span class="input-group-addon pointer" id="btn_rech_siret"
												title="Rechercher sur www.societe.com/">
													<span class="siret-search-icon" style="display: block;"></span>
												</span>
											</div>
										</span>
									</div>
								</span>
							</div>
						</div>
						<span class="field-error"></span>
					</div>
					'''.format(set_name, champ.label, champ)
				else :
					gab = gab_defaut.format(set_name, champ.label, champ)

		# Mise en forme d'une zone de liste
		if balise_init == 'select' :
			if 'multiple="multiple"' in champ_html :
				if 'm2m="on"' in champ_html :

					# Initialisation des colonnes de la balise <thead/>
					tab_elem = [
						champ.label.split('|')[1],
						'<input type="checkbox" id="id_{0}__all" value="__all__">'.format(set_name)
					]
					tab_thead = ['<th>{0}</th>'.format(elem) for elem in tab_elem]

					# Initialisation des lignes de la balise <tbody/>
					bs = BeautifulSoup(champ_html, 'html.parser')
					tab_tbody = []
					for index, elem in enumerate(bs.find_all('option')) :
						tab_elem = [elem.text, '<input type="checkbox" id="id_{0}_{1}" name="{2}" value="{3}" {4}>'.format(
							set_name,
							index,
							set_name,
							elem['value'],
							'checked' if elem.has_attr('selected') else ''
						)]
						tab_td = ['<td>{0}</td>'.format(elem) for elem in tab_elem]
						tab_tbody.append('<tr>{0}</tr>'.format(''.join(tab_td)))

				else :

					# Initialisation des colonnes de la balise <thead/>
					tab_thead = []
					for elem in champ.label.split('|')[1:] :
						if elem == '__zcc__' :
							elem = '<input type="checkbox" id="id_{0}__all" value="__all__">'.format(set_name)
						tab_thead.append('<th>{0}</th>'.format(elem))

					# Initialisation des lignes de la balise <tbody/>
					bs = BeautifulSoup(champ_html, 'html.parser')
					tab_tbody = []
					for index, elem in enumerate(bs.find_all('option')) :
						tab_td = []
						for elem_2 in elem.text.split('|') :
							if '__zcc__' in elem_2 :

								# Détermination d'attributs
								attrs = elem_2.split('$')[1:]
								attrs_html = ['{}="{}"'.format(*attr.split(':')) for attr in attrs]
								if elem.has_attr('selected') : attrs_html.append('checked=""')

								elem_2 = '<input type="checkbox" id="id_{0}_{1}" name="{2}" value="{3}" {4}>'.format(
									set_name,
									index,
									set_name,
									elem['value'],
									' '.join(attrs_html)
								)
							tab_td.append('<td>{0}</td>'.format(elem_2))
						tab_tbody.append('<tr>{0}</tr>'.format(''.join(tab_td)))

				gab = '''
				<div class="field-wrapper" id="fw_{0}">
					<span class="field-label">{1}</span>
					<div class="my-table" id="dtab_{2}">
						<table id="id_{3}">
							<thead><tr>{4}</tr></thead>
							<tbody>{5}</tbody>
						</table>
					</div>
					<span class="field-error"></span>
				</div>
				'''.format(
					set_name,
					champ.label.split('|')[0],
					set_name,
					set_name,
					''.join(tab_thead),
					''.join(tab_tbody)
				)
			else :
				gab = gab_defaut.format(set_name, champ.label, champ)

		# Mise en forme d'une zone de texte
		if balise_init == 'textarea' :
			gab = gab_defaut.format(set_name, champ.label, champ)

		# Mise en forme d'une zone de boutons radio
		if balise_init == 'ul' :
			gab = gab_defaut.format(set_name, champ.label, champ)

		# Tentative d'empilage du tableau associatif de sortie
		if gab :
			output[champ.name] = safe(gab)
		else :
			raise ValueError('Aucun gabarit n\'est disponible pour le champ « {0} ».'.format(set_name))

	return output

'''
Cette fonction retourne une fenêtre modale.
_s : Suffixe de reconnaissance pour chaque élément de la fenêtre modale
_h : En-tête de la fenêtre modale
_b : Corps de la fenêtre modale
Retourne une fenêtre modale
'''
def init_fm(_s, _h, _b = '') :

	# Imports
	from django.template.defaultfilters import safe

	fm = '''
	<div class="fade modal my-modal" data-backdrop="static" id="fm_{s}" role="dialog" tabindex="-1">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button class="close" data-dismiss="modal" type="button">&times;</button>
					<p class="modal-title">{h}</p>
				</div>
				<div class="modal-body">
					<span id="za_{s}" class="form-root">
						{b}
					</span>
					<div class="modal-padding-bottom"></div>
				</div>
			</div>
		</div>
	</div>
	'''.format(s = _s, h = _h, b = _b)

	return safe(fm)

'''
Initialisation des messages d'erreur
_form : Formulaire source
_sv : Dois-je ajouter un style visuel ?
'''
def init_mess_err(_form, _sv = True) :

	# Import
	from app.constants import ERROR_MESSAGES

	for elem in _form.fields.keys() :
		for cle, val in ERROR_MESSAGES.items() :
			_form.fields[elem].error_messages[cle] = val

		# Ajout d'un style visuel si le champ est requis
		if _sv == True and _form.fields[elem].required == True :
			spl = _form.fields[elem].label.split('|')
			spl[0] = spl[0] + '<span class="required-field"></span>'
			_form.fields[elem].label = '|'.join(spl)

'''
Cette fonction retourne le gabarit de chaque attribut d'une instance.
_t : Tableau d'attributs
_pdf : La sortie est-elle au format PDF ?
Retourne un tableau associatif
'''
def init_pg_cons(_t, _pdf = False) :

	# Imports
	from django.template.defaultfilters import safe
	from styx.settings import MEDIA_URL

	# Je déclare le tableau de sortie.
	t_attrs = {}

	for c, v in _t.items() :

		err = False

		if 'label' in v and 'value' in v :

			# Stockage du label et de la valeur attributaire
			get_label = v['label']
			get_value = v['value'] if v['value'] else ''

			if _pdf == False :

				# J'initialise le contenu du conteneur.
				contr = '''
				<span class="attribute-label">{0}</span>
				<div class="attribute-control">{1}</div>
				'''.format(get_label, get_value)

				# Je surcharge le contenu du conteneur dans le cas d'un fichier PDF.
				if 'pdf' in v :
					if v['pdf'] == True :
						if get_value :
							contr = '''
							<a href="{0}{1}" target="blank" class="icon-link pdf-icon">{2}</a>
							'''.format(MEDIA_URL, get_value, get_label)
						else :
							contr = None
					else :
						err = True

				# Je complète le contenu du conteneur si besoin.
				if 'help-text' in v and contr != '' :
					contr += '''
					<span class="attribute-help-text">{0}</span>
					'''.format(v['help-text'])

				# Je surcharge le contenu du conteneur dans le cas d'un champs commentaire.
				is_text_area = v.get('text_area', False)
				if is_text_area :
					contr = '''
					<span class="attribute-label">{0}</span>
					<div class="attribute-control-com">{1}</div>
					'''.format(get_label, get_value)

				# J'initialise le gabarit.
				if contr :
					# Je change le conteneur si attribut de champs commentaire (pardon)
					wrapper = "attribute-wrapper-com" if is_text_area else "attribute-wrapper"
					cont = '''
					<div class={0}>
						{1}
					</div>
					'''.format(wrapper, contr)
				else :
					cont = ''

			else :

				# J'initialise le contenu du conteneur.
				contr = '''
				<span class="pdf-attribute-label">{0}</span>
				<span class="pdf-attribute-value">{1}</span>
				'''.format(get_label, get_value)

				# Je surcharge le contenu du conteneur dans le cas d'un fichier PDF.
				if 'pdf' in v :
					if v['pdf'] == True :
						if get_value :
							contr = '''
							<span class="pdf-attribute-label">{label}</span>
							<span class="pdf-attribute-value">{value}</span>
							'''.format(label = get_label, value = get_value)
						else :
							contr = None
					else :
						err = True

				# J'initialise le gabarit.
				if contr :
					cont = '''
					<div class="pdf-attribute-wrapper">
						{0}
					</div>
					'''.format(contr)
				else :
					cont = ''

		else :
			err = True

		# J'empile le tableau de sortie s'il n'y a pas d'erreurs.
		if err == False :
			t_attrs[c] = safe(cont)
		else :
			raise ValueError('Aucun gabarit n\'est disponible pour l\'attribut « {0} ».'.format(c))

	return t_attrs

'''
Cette fonction permet d'obtenir les actions PGRE d'un maître d'ouvrage ainsi que les actions PGRE des maîtres
d'ouvrages reliés au maître d'ouvrage.
_m : Identifiant du maître d'ouvrage
Retourne un jeu de données
'''
def obt_act_pgre_regr(_m) :

	# Imports
	from app.models import TDossierPgre
	from app.models import TRegroupementsMoa
	from django.db.models import Q
	from functools import reduce
	import operator

	# J'initialise les conditions de la requête.
	qs_regr_moa = TRegroupementsMoa.objects.filter(id_org_moa_fil = _m)
	if len(qs_regr_moa) > 0 :
		t_sql = [Q(**{ 'moa__id_org_moa' : rm.id_org_moa_anc }) for rm in qs_regr_moa]
		t_sql.append(Q(**{ 'moa__id_org_moa' : _m }))
	else :
		t_sql = { 'moa__id_org_moa' : _m }

	# J'initialise la requête.
	if len(t_sql) == 1 :
		qs_act_pgre = TDossierPgre.objects.filter(**t_sql)
	else :
		qs_act_pgre = TDossierPgre.objects.filter(reduce(operator.or_, t_sql))

	return qs_act_pgre

'''
Cette fonction permet d'obtenir les dossiers d'un maître d'ouvrage ainsi que les dossiers des maîtres d'ouvrages reliés
au maître d'ouvrage.
_m : Identifiant du maître d'ouvrage
Retourne un jeu de données
'''
def obt_doss_regr(_m) :

	# Imports
	from app.models import TDossier
	from app.models import TRegroupementsMoa
	from django.db.models import Q
	from functools import reduce
	import operator

	# J'initialise les conditions de la requête.
	qs_regr_moa = TRegroupementsMoa.objects.filter(id_org_moa_fil = _m)
	if len(qs_regr_moa) > 0 :
		t_sql = [Q(**{ 'id_org_moa' : rm.id_org_moa_anc }) for rm in qs_regr_moa]
		t_sql.append(Q(**{ 'id_org_moa' : _m }))
	else :
		t_sql = { 'id_org_moa' : _m }

	# J'initialise la requête.
	if len(t_sql) == 1 :
		qs_doss = TDossier.objects.filter(**t_sql)
	else :
		qs_doss = TDossier.objects.filter(reduce(operator.or_, t_sql))

	return qs_doss

'''
Cette fonction retourne un entier ou un nombre décimal sous forme de montant.
_v : Valeur dont on veux avoir le montant
Retourne un entier ou un nombre décimal
'''
def obt_mont(_v) :

	output = _v

	if _v is not None :

		# Je convertis l'entier ou le nombre décimal sous forme de montant.
		output = '{:,.2f}'.format(_v)

		# Je retire les virgules.
		output = output.replace(',', ' ')

		# Je retire les zéros non-significatifs si besoin.
		if output.endswith('.00') :
			output = output[:-3]

	return output

'''
Cette fonction retourne un entier ou un nombre décimal sous forme de pourcentage.
_v : Valeur dont on veux avoir le pourcentage
Retourne un entier ou un nombre décimal
'''
def obt_pourc(_v) :

	output = _v

	if _v is not None :

		# Je convertis l'entier ou le nombre décimal sous forme de pourcentage.
		output = '{0:.2f}'.format(_v)

		# Je retire les zéros non-significatifs si besoin.
		if output.endswith('.00') :
			output = output[:-3]
		if '.' in output and output.endswith('0') :
			output = output[:-1]

	return output

'''
Cette procédure permet de mettre à jour un fichier log.
_t : Tableau de données à renseigner dans le fichier log
'''
def rempl_fich_log(_t) :

	# Imports
	from styx.settings import MEDIA_ROOT
	import csv
	import time

	try :

		# Je mets en forme le chemin du fichier log.
		chem_fich = '{0}/log.csv'.format(MEDIA_ROOT)
		chem_fich = chem_fich.replace('\\', '/')
		chem_fich = chem_fich.replace('//', '/')

		# J'ouvre (ou je créé) le fichier log.
		with open(chem_fich, 'a', newline = '') as fich :

			# Je définis le délimiteur.
			writer = csv.writer(fich, delimiter = ';')

			# J'ajoute en fin de tableau la date et l'heure de l'opération.
			_t.append(time.strftime('%d/%m/%Y %H:%M:%S'))

			# J'ajoute une ligne au fichier log.
			writer.writerow(_t)

			# Je ferme le fichier log.
			fich.close()

	except :
		pass

'''
Cette fonction retourne une demande de confirmation de suppression d'un élément.
_v : Vue permettant la suppression
_m: Message d'alerte
Retourne une chaîne de caractères
'''
def suppr(_v, _m = '') :

	# Je mets en forme les lignes de la fenêtre modale.
	lg_princ = '''
	<div class="row">
		<div class="col-xs-6 text-center">
			<a href="{0}" class="green-btn my-btn" onclick="suppr(event);" style="display: inline-block;">Oui</a>
		</div>
		<div class="col-xs-6 text-center">
			<button class="green-btn my-btn" data-dismiss="modal" style="display: inline-block;">Non</button>
		</div>
	</div>
	'''.format(_v)

	lg_sec = '''
	<div class="row">
		<div class="col-xs-12 text-center">
			<span class="b red-color">
				<span class="u">Attention :</span> {0}
			</span>
		</div>
	</div>
	'''.format(_m)

	# J'initialise le tableau des lignes de la fenêtre modale.
	t_lg = [lg_princ]
	if _m != '' :
		t_lg.append(lg_sec)

	# J'inverse l'ordre du tableau des lignes de la fenêtre modale afin d'avoir le message d'alerte au début.
	t_lg.reverse()

	return '<div class="br"></div>'.join(t_lg)

'''
Cette fonction vérifie si l'extension d'un fichier uploadé est autorisée.
_v : Fichier uploadé
_e : Extension(s) autorisée(s)
Retourne un booléen
'''
def verif_ext_fich(_v, _e) :

	# Imports
	import os

	err = False

	# Je récupère l'extension du fichier.
	ext = os.path.splitext(_v.name)[1]

	if ext.lower() not in _e :
		err = True

	return err

'''
Cette fonction vérifie une valeur numérique saisie.
_v : Valeur saisie
_null : La valeur peut-elle être nulle ?
'''
def verif_mont(_v, _null) :

	err = False

	# Je vérifie que la valeur ne soit pas strictement négative.
	if _null == True and _v < 0 :
		err = True
	if _null == False and _v <= 0 :
		err = True

	# Je calcule le nombre de décimales.
	v_str = str(_v)
	i = v_str.index('.') + 1
	nb_dec = len(v_str) - i

	if nb_dec > 2 :
		err = True

	return err
