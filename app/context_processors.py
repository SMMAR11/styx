#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from django.conf import settings

'''
Cette fonction permet d'obtenir les différentes constantes paramétrées via la base de données.
request : Objet "requête"
Retourne un tableau associatif
'''
def get_bdd_settings(request) :
	return {
		'consts_str' : [(cle, val) for cle, val in settings.T_DONN_BDD_STR.items()],
		'consts_int' : [(cle, val) for cle, val in settings.T_DONN_BDD_INT.items()]
	}

'''
Cette fonction permet d'obtenir les différents menus de l'application.
request : Objet "requête"
Retourne un tableau associatif
'''
def get_menu(request) :

	# Imports
	from app.functions import get_menu_vign
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.template.defaultfilters import safe
	from styx.settings import STATIC_URL

	output = {}

	# Je mets en forme le gabarit d'une vignette.
	gab_vign = '''
	<a class="custom-thumbnail" href="{0}" target="{1}">
		<img src="{2}">
		<div>{3}</div>
	</a>
	'''

	# J'initialise le tableau relatif au menu de l'application.
	t_menu = {
		'gest_doss' : {
			'mod_name' : 'Gestion des dossiers',
			'mod_img' : STATIC_URL + 'pics/thumbnails/gestion_dossiers/main.png',
			'mod_href' : reverse('gest_doss'),
			'mod_href_blank' : '',
			'mod_items' : [
				{
					'item_name' : 'Créer un dossier',
					'item_img' : STATIC_URL + 'pics/thumbnails/gestion_dossiers/add.png',
					'item_href' : reverse('cr_doss')
				},
				{
					'item_name' : 'Consulter un dossier',
					'item_img' : STATIC_URL + 'pics/thumbnails/gestion_dossiers/consult.png',
					'item_href' : reverse('ch_doss')
				}
			],
			'mod_rank' : 2
		},
		'pgre' : {
			'mod_name' : 'PGRE',
			'mod_img' : STATIC_URL + 'pics/thumbnails/pgre/main.jpg',
			'mod_href' : reverse('pgre'),
			'mod_href_blank' : '',
			'mod_items' : [
				{
					'item_name' : 'Créer une action PGRE',
					'item_img' : STATIC_URL + 'pics/thumbnails/pgre/add.jpg',
					'item_href' : reverse('cr_act_pgre')
				},
				{
					'item_name' : 'Consulter une action PGRE',
					'item_img' : STATIC_URL + 'pics/thumbnails/pgre/consult.jpg',
					'item_href' : reverse('ch_act_pgre')
				},
				{
					'item_name' : 'Réalisation d\'états PGRE',
					'item_img' : STATIC_URL + 'pics/thumbnails/pgre/realisation_etats.png',
					'item_href' : '#'
				}
			],
			'mod_rank' : 4
		},
		'port_cart' : {
			'mod_name' : 'Portail cartographique',
			'mod_img' : STATIC_URL + 'pics/thumbnails/portail_cartographique/main.jpg',
			'mod_href' : 'http://carto.smmar.fr/styx',
			'mod_href_blank' : 'target',
			'mod_items' : [],
			'mod_rank' : 1
		},
		'real_etats' : {
			'mod_name' : 'Réalisation d\'états',
			'mod_img' : STATIC_URL + 'pics/thumbnails/realisation_etats/main.png',
			'mod_href' : reverse('real_etats'),
			'mod_href_blank' : '',
			'mod_items' : [
				{
					'item_name' : 'En sélectionnant des dossiers',
					'item_img' : STATIC_URL + 'pics/thumbnails/realisation_etats/select_doss.png',
					'item_href' : reverse('select_doss')
				},
				{
					'item_name' : 'En cumulant des dossiers',
					'item_img' : STATIC_URL + 'pics/thumbnails/realisation_etats/cumul_doss.jpg',
					'item_href' : '#'
				},
				{ 
					'item_name' : 'En sélectionnant des prestations',
					'item_img' : STATIC_URL + 'pics/thumbnails/realisation_etats/select_prest.jpg',
					'item_href' : reverse('select_prest')
				}
			],
			'mod_rank' : 3
		}
	}

	# Je trie le tableau par ordre d'affichage.
	t_menu = sorted(t_menu.items(), key = lambda l : l[1]['mod_rank'])

	# J'initialise le menu principal à vignettes.
	t_vign = []
	
	for cle, val in t_menu :

		# Je prépare la vignette courante.
		vign = gab_vign.format(val['mod_href'], val['mod_href_blank'], val['mod_img'], val['mod_name'])

		# J'empile le tableau des vignettes.
		t_vign.append(vign)

	# J'empile le tableau de sortie.
	output['main_thumbnails'] = get_menu_vign(t_vign, 3)

	# J'initialise le tableau des éléments du navigateur.
	t_elem_nav = []

	for cle, val in t_menu :

		# J'initialise chaque élément du navigateur selon le nombre de sous-éléments de celui-ci.
		if len(val['mod_items']) > 0 :

			# J'initialise et j'empile le tableau des sous-éléments de l'élément courant du navigateur.
			t_li_ddown = ['<li><a href="{0}">{1}</a></li>'.format(
				elem['item_href'], elem['item_name']
			) for elem in val['mod_items']]

			# Je prépare l'élément courant du navigateur.
			li = '''
			<li class="dropdown">
				<a class="dropdown-toggle" data-toggle="dropdown" href="#">
					{0}
					<span class="caret"></span>
				</a>
				<ul class="dropdown-menu">{1}</ul>
			</li>
			'''.format(val['mod_name'], ''.join(t_li_ddown))

		else :

			# Je prépare l'élément courant du navigateur.
			li = '<li><a href="{0}" target="{1}">{2}</a></li>'.format(
				val['mod_href'], val['mod_href_blank'], val['mod_name']
			)

		# J'empile le tableau des éléments du navigateur.
		t_elem_nav.append(li)

	# J'empile le tableau de sortie.
	nav = '<ul class="nav navbar-nav">{0}</ul>'.format(''.join(t_elem_nav))
	output['navbar'] = safe(nav)

	# J'initialise le menu à vignettes du module de gestion des dossiers.
	t_vign = []

	for elem in dict(t_menu)['gest_doss']['mod_items'] :

		# Je prépare la vignette courante.
		vign = gab_vign.format(elem['item_href'], '', elem['item_img'], elem['item_name'])

		# J'empile le tableau des vignettes.
		t_vign.append(vign)

	# J'empile le tableau de sortie.
	output['gest_doss_thumbnails'] = get_menu_vign(t_vign, 3)

	# J'initialise le menu à vignettes du module de réalisation d'états.
	t_vign = []

	for elem in dict(t_menu)['real_etats']['mod_items'] :

		# Je prépare la vignette courante.
		vign = gab_vign.format(elem['item_href'], '', elem['item_img'], elem['item_name'])

		# J'empile le tableau des vignettes.
		t_vign.append(vign)

	# J'empile le tableau de sortie.
	output['real_etats_thumbnails'] = get_menu_vign(t_vign, 3)

	# J'initialise le menu à vignettes du module PGRE.
	t_vign = []

	for elem in dict(t_menu)['pgre']['mod_items'] :

		# Je prépare la vignette courante.
		vign = gab_vign.format(elem['item_href'], '', elem['item_img'], elem['item_name'])

		# J'empile le tableau des vignettes.
		t_vign.append(vign)

	# J'empile le tableau de sortie.
	output['pgre_thumbnails'] = get_menu_vign(t_vign, 3)

	return output