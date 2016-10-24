from app.decorators import *
from app.forms import gestion_dossiers
from app.functions import *
from app.models import *
from datetime import date
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from styx.settings import MEDIA_ROOT, MEDIA_URL
import json
import os
#import shutil

@verif_acces
def ajouter_photo(request) :

	reponse = None

	if request.method == 'POST' :

		# Je déclare un objet "formulaire" permettant de traiter le formulaire d'ajout d'une photo.
		f1 = gestion_dossiers.GererPhoto(request.POST, request.FILES)

		if f1.is_valid() :

				# Je récupère et nettoie les données du formulaire valide.
				tab_donnees = f1.cleaned_data
				#v_chemin_photo = tab_donnees['zu_chem_ph']

				#shutil.copy2(v_chemin_photo, MEDIA_URL + 'pho.jpg')
		else :

			# J'affiche les erreurs du formulaire d'insertion d'une photo.
			reponse = HttpResponse(json.dumps(f1.errors), content_type = 'application/json')

	return reponse

'''
Cette vue permet d'afficher la page permettant de choisir un dossier pour consultation.
request : Objet requête
'''
@verif_acces
@nett_form
def choisir_dossier(request) :

	reponse = None

	if request.method == 'GET' :

		# Je déclare un objet "formulaire" permettant une future manipulation des champs.
		f1 = gestion_dossiers.ChoisirDossier()

		# Je stocke dans un tableau les dossiers référencés dans la base de données.
		les_dossiers = TDossier.objects.order_by('-dt_delib_moa_doss', 'num_doss')

		# Je créé un tableau de dossiers reprenant les colonnes du tableau HTML des dossiers.
		tab_dossiers = []
		for un_dossier in les_dossiers :
			tab_dossiers.append({
				'id_doss' : un_dossier.id_doss,
				'num_doss' : conv_none(un_dossier.num_doss),
				'int_doss' : conv_none(un_dossier.int_doss),
				'n_moa' : conv_none(un_dossier.id_org_moa.id_org_moa.n_org),
				'dt_delib_moa_doss' : conv_none(reecr_dt(un_dossier.dt_delib_moa_doss))
			})

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/choisir_dossier.html',
			{
				'f1' : init_form(f1),
				'les_dossiers' : tab_dossiers,
				'title' : 'Choisir un dossier'
			}
		)

	else :

		if 'action' in request.GET :

			# Je traite le cas où je veux filtrer les dossiers.
			if len(request.GET) == 1 and request.GET['action'] == 'filtrer-dossiers' :

				# Je stocke dans un tableau les dossiers trouvés après filtrage.
				les_dossiers_filtres = filtr_doss(request)

				# Je créé un tableau de dossiers filtrés reprenant les colonnes du tableau HTML des dossiers après
				# filtrage.
				tab_dossiers_filtres = []
				for un_dossier in les_dossiers_filtres :
					tab_dossiers_filtres.append([
						conv_none(un_dossier.num_doss),
						conv_none(un_dossier.int_doss),
						conv_none(un_dossier.id_org_moa.id_org_moa.n_org),
						conv_none(reecr_dt(un_dossier.dt_delib_moa_doss)),
						'<a href="{0}" class="bt-consulter pull-right"></a>'.format(
							reverse('consulter_dossier', args = [un_dossier.id_doss])
						)
					])

				# J'envoie la liste des dossiers filtrés.
				reponse = HttpResponse(json.dumps(
					{ 'success' : tab_dossiers_filtres }), content_type = 'application/json'
				)

		else :

			# J'alimente les listes déroulantes des axes, des sous-axes et des actions.
			reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

	return reponse

'''
Cette vue permet d'afficher la page de consultation d'un dossier.
request : Objet requête
p_dossier : Identifiant du dossier consulté
'''
@verif_acces
@nett_form
@csrf_exempt
def consulter_dossier(request, p_dossier) :

	reponse = None

	if request.method == 'GET' :

		# Je vérifie l'existence d'un objet TDossier.
		obj_dossier = get_object_or_404(TDossier, id_doss = p_dossier)

		# Je vérifie l'existence d'un objet TPgre.
		obj_dossier_pgre = None
		try :
			obj_dossier_pgre = TPgre.objects.get(id_pgre = obj_dossier.id_doss)
		except :
			pass

		# J'initialise la valeur de chaque champ PGRE.
		v_quantification_objectifs = None
		v_quantification_realisee = None
		v_unite = None
		v_rivieres = None
		v_portee = None

		if obj_dossier_pgre is not None :

			# J'attribue la valeur de chaque champ de saisie PGRE.
			v_quantification_objectifs = obj_dossier_pgre.quant_objs_pgre
			v_quantification_realisee = obj_dossier_pgre.quant_real_pgre

			# Je vérifie l'existence d'un objet TUnite.
			obj_unite_dossier_pgre = None
			try :
				obj_unite_dossier_pgre = obj_dossier_pgre.id_unit
			except :
				pass

			# J'attribue la valeur de l'unité si et seulement si l'objet TUnite existe.
			if obj_unite_dossier_pgre is not None :
				v_unite = obj_unite_dossier_pgre.int_unit

			# Je stocke dans un tableau les rivières d'un dossier PGRE.
			les_rivieres_dossier = TRivieresDossier.objects.filter(id_pgre = obj_dossier.id_doss).order_by(
				'id_riv__n_riv'
			)

			# Je créé un tableau de noms de rivières.
			tab_rivieres_dossier = []
			for une_riviere_dossier in les_rivieres_dossier :
				tab_rivieres_dossier.append(une_riviere_dossier.id_riv.n_riv)

			# J'attribue la valeur du champ PGRE des rivières impactées.
			v_rivieres = ', '.join(tab_rivieres_dossier)

			# Je vérifie l'existence d'un objet TPortee.
			obj_portee_dossier_pgre = None
			try :
				obj_portee_dossier_pgre = obj_dossier_pgre.id_port
			except :
				pass

			# J'attribue la valeur de la portée du dossier si et seulement si l'objet TPortee existe.
			if obj_portee_dossier_pgre is not None :
				v_portee = obj_portee_dossier_pgre.int_port	

		# Je définis les propriétés des attributs que l'on veut afficher pour consultation dans un tableau.
		tab_attributs_dossier = {
			'num_doss' : { 'label' : 'Numéro du dossier', 'value' : conv_none(obj_dossier.num_doss) },
			'int_doss' : { 'label' : 'Intitulé du dossier', 'value' : conv_none(obj_dossier.int_doss) },
			'n_org' : { 'label' : 'Maître d\'ouvrage', 'value' : conv_none(obj_dossier.id_org_moa.id_org_moa.n_org) },
			'int_progr' : { 'label' : 'Programme', 'value' : conv_none(obj_dossier.id_progr.int_progr) },
			'id_axe' : { 'label' : 'Axe', 'value' : conv_none(obj_dossier.id_axe) },
			'id_ss_axe' : { 'label' : 'Sous-axe', 'value' : conv_none(obj_dossier.id_ss_axe) },
			'id_act' : { 'label' : 'Action', 'value' : conv_none(obj_dossier.id_act) },
			'int_type_doss' :
			{
				'label' : 'Type du dossier', 'value' : conv_none(obj_dossier.id_type_doss.int_type_doss)
			},
			'int_nat_doss' :
			{
				'label' : 'Nature du dossier', 'value' : conv_none(obj_dossier.id_nat_doss.int_nat_doss)
			},
			'mont_ht_doss' :
			{
				'label' : 'Montant HT du dossier (en €)', 'value' : conv_none(float_to_int(obj_dossier.mont_ht_doss))
			},
			'mont_ttc_doss' :
			{
				'label' : 'Montant TTC du dossier (en €)', 'value' : conv_none(float_to_int(obj_dossier.mont_ttc_doss))
			},
			'techn' :
			{
				'label' : 'Technicien',
				'value' : conv_none(obj_dossier.id_techn.n_techn) + ' ' + conv_none(obj_dossier.id_techn.pren_techn)
			},
			'int_av' : { 'label' : 'État d\'avancement du dossier', 'value' : conv_none(obj_dossier.id_av.int_av) },
			'dt_delib_moa_doss' :
			{
				'label' : 'Date de délibération au maître d\'ouvrage',
				'value' : conv_none(reecr_dt(obj_dossier.dt_delib_moa_doss))
			},
			'int_av_cp' :
			{
				'label' : 'Avis du comité de programmation', 'value' : conv_none(obj_dossier.id_av_cp.int_av_cp)
			},
			'dt_av_cp_doss' :
			{
				'label' : 'Date de l\'avis du comité de programmation',
				'value' : conv_none(reecr_dt(obj_dossier.dt_av_cp_doss))
			},
			'descr_doss' : 
			{
				'label' : 'Description du dossier et de ses objectifs',
				'value' : conv_none(obj_dossier.descr_doss)
			},
			'comm_doss' : { 'label' : 'Commentaire', 'value' : conv_none(obj_dossier.comm_doss), 'textarea' : True },
			'quant_objs_pgre' : 
			{
				'label' : 'Quantification des objectifs', 
				'value' : conv_none(float_to_int(v_quantification_objectifs, 0))
			},
			'quant_real_pgre' : 
			{
				'label' : 'Réalisé', 'value' : conv_none(float_to_int(v_quantification_realisee, 0))
			},
			'int_unit' : { 'label' : 'Unité', 'value' : conv_none(v_unite) },
			'n_riv' : { 'label' : 'Rivières impactées', 'value' : conv_none(v_rivieres) },
			'int_port' : { 'label' : 'Portée du dossier', 'value' : conv_none(v_portee) }
		}

		# Je stocke dans un tableau les dossiers d'une famille de dossiers.
		les_dossiers_famille = TDossier.objects.filter(id_fam = obj_dossier.id_fam.id_fam).exclude(
			id_doss = obj_dossier.id_doss).order_by('-dt_delib_moa_doss', 'num_doss')

		# Je créé un tableau de dossiers d'une famille reprenant les colonnes du tableau HTML des dossiers associés.
		tab_dossiers_famille = []
		for un_dossier_famille in les_dossiers_famille :
			tab_dossiers_famille.append({
				'id_doss' : un_dossier_famille.id_doss,
				'num_doss' : conv_none(un_dossier_famille.num_doss),
				'int_doss' : conv_none(un_dossier_famille.int_doss),
				'n_moa' : conv_none(un_dossier_famille.id_org_moa.id_org_moa.n_org),
				'dt_delib_moa_doss' : conv_none(reecr_dt(un_dossier_famille.dt_delib_moa_doss)),
				'int_progr' : conv_none(un_dossier_famille.id_progr.int_progr),
				'int_nat_doss' : conv_none(un_dossier_famille.id_nat_doss.int_nat_doss)
			})

		# Je stocke dans un tableau les lignes constituant le plan de financement d'un dossier.
		les_financements = TFinancement.objects.filter(id_doss = obj_dossier.id_doss).order_by(
			'id_org_fin__id_org_fin__n_org'
		)

		# Je créé un tableau de financements reprenant les colonnes du tableau HTML du plan de financement d'un 
		# dossier.
		tab_financements = []
		for un_financement in les_financements :
			tab_financements.append({
				'id_fin' : un_financement.id_fin,
				'n_org' : conv_none(un_financement.id_org_fin.id_org_fin.n_org),
				'mont_subv' : conv_none(float_to_int(un_financement.mont_subv)),
				'pourc_elig' : conv_none(float_to_int(obt_pourcentage(un_financement.pourc_elig))),
				'dt_deb_elig' : conv_none(reecr_dt(un_financement.dt_deb_elig)),
				'dt_fin_elig' : conv_none(reecr_dt(un_financement.dt_fin_elig))
			})

		# Je stocke dans un tableau les prestations d'un dossier.
		les_prestations = TPrestationsDossier.objects.all().filter(id_doss = obj_dossier.id_doss).order_by(
			'id_prest__id_org_prest__id_org_prest__n_org'
		)

		# Je créé un tableau de prestations reprenant les colonnes du tableau HTML des prestations d'un dossier.
		tab_prestations = []
		for une_prestation in les_prestations :
			tab_prestations.append({
				'id_prest' : une_prestation.id_prest.id_prest,
				'n_org' : conv_none(une_prestation.id_prest.id_org_prest.id_org_prest.n_org),
				'mont_tot_prest' : conv_none(float_to_int(une_prestation.id_prest.mont_tot_prest)),
				'dt_notif_prest' : conv_none(reecr_dt(une_prestation.id_prest.dt_notif_prest)),
				'int_nat_prest' : conv_none(une_prestation.id_prest.id_nat_prest.int_nat_prest),
				'rap' : conv_none(None)
			})

		# Je stocke dans un tableau les factures d'une prestation.
		les_factures = TFacture.objects.filter(
			id_prest__tprestationsdossier__id_doss = obj_dossier.id_doss, id_doss = obj_dossier.id_doss
		)

		# Je créé un tableau de factures reprenant les colonnes du tableau HTML des factures d'une prestation.
		tab_factures = []
		for une_facture in les_factures :
			tab_factures.append({
				'id_fact' : une_facture.id_fact,
				'prest' : '{0} : {1}'.format(
					conv_none(une_facture.id_prest.id_org_prest.id_org_prest.n_org),
					conv_none(une_facture.id_prest.int_prest)
				),
				'dt_mep_fact' : conv_none(reecr_dt(une_facture.dt_mep_fact)),
				'mont_fact' : conv_none(float_to_int(une_facture.mont_fact)),
				'int_fact' : conv_none(une_facture.int_fact)
			})

		# Je stocke dans un tableau les photos d'un dossier.
		les_photos = TPhoto.objects.filter(id_doss = obj_dossier.id_doss).order_by('-dt_pv_ph')

		# Je créé un tableau de photos reprenant les colonnes du tableau HTML des photos d'un dossier.
		tab_photos = []
		for une_photo in les_photos :
			tab_photos.append({
				'id_ph' : une_photo.id_ph,
				'chem_ph' : MEDIA_URL + conv_none(une_photo.chem_ph),
				'int_ph' : conv_none(une_photo.int_ph),
				'int_ppv_ph' : conv_none(une_photo.id_ppv_ph.int_ppv_ph),
				'dt_pv_ph' : conv_none(reecr_dt(une_photo.dt_pv_ph))
			})

		# Je stocke dans un tableau les différents types d'arrêtés.
		les_arretes = TTypeDeclaration.objects.order_by('id_type_decl')

		# Je parcours le tableau des types d'arrêtés afin d'initialiser l'onglet "Réglementations".
		i = -1
		contenu_reglementations = ''
		for un_arrete in les_arretes :

			# J'incrémente le sommet.
			i += 1

			# Je stocke la valeur du modulo de l'indice courant.
			modulo = i % 2

			# J'initialise ou réinitialise le contenu d'un élément <div/> possédant la classe "row".
			if modulo == 0 :
				contenu_row = ''

			# Je vérifie l'existence d'un objet TArretesDossier.
			obj_arrete = None
			try :
				obj_arrete = TArretesDossier.objects.get(
					id_doss = obj_dossier.id_doss, id_type_decl = un_arrete.id_type_decl
				)
			except :
				pass

			# J'attribue la valeur de chaque champ de saisie si et seulement si l'objet TArretesDossier existe.
			if obj_arrete is not None :
				v_intitule_arrete = obj_arrete.id_type_av_arr.int_type_av_arr
				v_numero_arrete = obj_arrete.num_arr
				v_date_signature_arrete = obj_arrete.dt_sign_arr
				v_date_limite_enclenchement_travaux = obj_arrete.dt_lim_encl_trav_arr
			else :
				v_intitule_arrete = None
				v_numero_arrete = None
				v_date_signature_arrete = None
				v_date_limite_enclenchement_travaux = None

			# Je définis les propriétés des attributs que l'on veut afficher pour consultation dans un tableau.
			tab_attributs_arrete = {
				'int_type_av_arr' : { 
					'label' : 'Avancement', 'value' : conv_none(v_intitule_arrete)
				},
				'num_arr' : { 'label' : 'Numéro de l\'arrêté', 'value' : conv_none(v_numero_arrete) },
				'dt_sign_arr' : 
				{ 
					'label' : 'Date de signature de l\'arrêté', 'value' : conv_none(reecr_dt(v_date_signature_arrete))
				},
				'dt_lim_encl_trav_arr' :
				{
					'label' : 'Date limite d\'enclenchement des travaux',
					'value' : conv_none(reecr_dt(v_date_limite_enclenchement_travaux))
				}
			}

			# Je convertis le tableau des attributs des champs de chaque arrêté en un nombre de champs.
			tab_attributs_arrete = init_pg_cons(tab_attributs_arrete)

			# Je vérifie si je dois afficher ou non l'option "Consulter le fichier de l'arrêté".
			if obj_arrete is not None and obj_arrete.chem_pj_arr is not None :
				bouton_pdf = '''
				<div class="col-xs-6">
					<div class="icon-link">
						<div><span class="bt-pdf"></span></div>
						<div><a href="{0}" target="blank">Consulter le fichier de l'arrêté</a></div>
					</div>
				</div>
				'''.format(MEDIA_URL + obj_arrete.chem_pj_arr)
			else :
				bouton_pdf = ''
			
			# Je complète le contenu d'un élément <div/> possédant la classe "row".
			contenu_row += '''
			<div class="col-sm-6">
				<div class="alt-thumbnail">
					<p class="text-center b c-theme-fonce">{0}</p>
					<br />
					{1}
					{2}
					{3}
					{4}
					<div class="row">
						<div class="col-xs-3">
							<div class="icon-link">
								<div><span class="bt-modifier"></span></div>
								<div><a href="#">Modifier</a></div>
							</div>
						</div>
						<div class="col-xs-3">
							<div class="icon-link">
								<div><span class="bt-supprimer"></span></div>
								<div><span>Supprimer</span></div>
							</div>
						</div>
						{5}
					</div>
				</div>
			</div>
			'''.format(
				conv_none(un_arrete.int_type_decl),
				tab_attributs_arrete['int_type_av_arr'],
				tab_attributs_arrete['num_arr'],
				tab_attributs_arrete['dt_sign_arr'],
				tab_attributs_arrete['dt_lim_encl_trav_arr'],
				bouton_pdf
			)

			# Je vérifie si je dois terminer ou non l'élément <div/> possédant la classe "row".
			row_termine = False
			if modulo == 1 :
				row_termine = True
			if i + 1 == len(les_arretes) and modulo == 0 :
				row_termine = True

			# Je complète le contenu de l'onglet "Réglementations" avec le contenu d'un élément <div/> possédant la 
			# classe "row".
			if row_termine == True :
				contenu_reglementations += '''
				<div class="row">
					{0}
				</div>
				'''.format(contenu_row)

		# Je déclare un objet "formulaire" permettant une future manipulation des champs.
		f3 = gestion_dossiers.GererDossier_Reglementation(
			prefix = 'ModifierDossier', k_commentaire = obj_dossier.comm_regl_doss
		)

		# Je déclare des objets "formulaire" permettant une future manipulation des champs.
		f1 = gestion_dossiers.GererPhoto(prefix = 'AjouterPhoto', k_dossier = obj_dossier.id_doss)

		# J'initialise le gabarit d'affichage des champs de chaque formulaire de la page.
		tab_champs_f1 = init_form(f1)

		# J'initialise le tableau du contenu des différentes fenêtres modales.
		tab_contenus_fm = {
			'ajouter_photo' : '''
			<form name="form_ajouter_photo" method="post" action="{0}" class="c-theme" enctype="multipart/form-data">
				<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
				{2}
				{3}
				{4}
				{5}
				{6}
				<button type="submit" class="center-block btn bt-vert to-unfocus">Valider</button>
			</form>
			'''.format(
				reverse('ajouter_photo') + '?dossier=' + str(obj_dossier.id_doss),
				csrf(request)['csrf_token'],
				tab_champs_f1['za_doss'],
				tab_champs_f1['zl_ppv_ph'],
				tab_champs_f1['zs_int_ph'],
				tab_champs_f1['zd_dt_pv_ph'],
				tab_champs_f1['zu_chem_ph']
			)
		}

		# Je déclare un tableau de fenêtres modales.
		tab_fm = [
			init_fm('afficher_photo', 'Consulter une photo'),
			init_fm('ajouter_photo', 'Ajouter une photo', tab_contenus_fm['ajouter_photo']),
			init_fm('modifier_dossier', 'Modifier un dossier'),
			init_fm('supprimer_dossier', 'Êtes-vous certain de supprimer ce dossier ?'),
			init_fm('supprimer_photo', 'Êtes-vous certain de supprimer cette photo ?')
		]

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/consulter_dossier.html',
			{
				'contenu_reglementations' : contenu_reglementations,
				'f1' : init_form(f3),
				'le_dossier' : obj_dossier,
				'les_attributs_dossier' : init_pg_cons(tab_attributs_dossier),
				'les_dossiers_famille' : tab_dossiers_famille,
				'les_factures' : tab_factures,
				'les_financements' : tab_financements,
				'les_fm' : tab_fm,
				'les_photos' : tab_photos,
				'les_prestations' : tab_prestations,
				'nb_dossiers_famille' : len(tab_dossiers_famille),
				'title' : 'Consulter un dossier',
			}
		)

	else :

		# Je vérifie l'existence d'un objet TDossier
		try :
			obj_dossier = TDossier.objects.get(id_doss = p_dossier)
		except :
			return HttpResponse()

		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" "action".
			action = request.GET['action']

			# Je traite le cas où je dois afficher les données relatives à une photo.
			if action == 'afficher-photo' and 'photo' in request.GET :

				# Je récupère l'identifiant de la photo à afficher.
				v_photo = request.GET['photo']
				
				# Je verifie l'existence d'un objet TPhoto.
				try :
					obj_photo = TPhoto.objects.get(id_ph = v_photo)
				except :
					return HttpResponse()

				# Je définis les propriétés des attributs que l'on veut afficher pour consultation dans un tableau.
				tab_attributs_photo = {
					'int_ph' : { 'label' : 'Intitulé de la photo', 'value' : conv_none(obj_photo.int_ph) },
					'num_ph' : { 'label' : 'Numéro de la photo', 'value' : conv_none(obj_photo.num_ph) },
					'descr_ph' :
					{
						'label' : 'Description de la photo',
						'value' : conv_none(obj_photo.descr_ph),
						'textarea' : True
					},
					'int_ppv_ph' :
					{
						'label' : 'Période de la prise de vue de la photo',
						'value' : conv_none(obj_photo.id_ppv_ph.int_ppv_ph)
					},
					'dt_pv_ph' :
					{
						'label' : 'Date de la prise de vue de la photo',
						'value' : conv_none(reecr_dt(obj_photo.dt_pv_ph))
					}
				}

				# J'initialise le gabarit d'affichage des attributs de la photo.
				tab_attributs_photo = init_pg_cons(tab_attributs_photo)

				# Je prépare la réponse AJAX.
				contenu = '''
				<div class="attribute-wrapper text-center">
					<img src="{0}" style="width: 480px;"/>
				</div>
				<div class="row">
					<div class="col-xs-6">{1}</div>
					<div class="col-xs-6">{2}</div>
				</div>
				{3}
				<div class="row">
					<div class="col-xs-6">{4}</div>
					<div class="col-xs-6">{5}</div>
				</div>
				'''.format(
					MEDIA_URL + obj_photo.chem_ph,
					tab_attributs_photo['int_ph'],
					tab_attributs_photo['num_ph'],
					tab_attributs_photo['descr_ph'],
					tab_attributs_photo['int_ppv_ph'],
					tab_attributs_photo['dt_pv_ph']
				)

			# Je traite le cas où je dois supprimer une photo.
			if action == 'supprimer-photo' and 'photo' in request.GET :

				# Je récupère l'identifiant de la photo à supprimer.
				v_photo = request.GET['photo']

				# Je prépare la réponse AJAX.
				contenu = aff_mess_suppr(reverse('supprimer_photo') + '?photo=' + v_photo)

			# Je traite le cas où je dois supprimer un dossier.
			if action == 'supprimer-dossier' :

				# Je prépare la réponse AJAX.
				contenu = aff_mess_suppr(reverse('supprimer_dossier', args = [obj_dossier.id_doss]))

		# J'affiche la réponse AJAX correspondante à l'opération effectuée.
		reponse = HttpResponse(contenu)

	return reponse

'''
Cette vue permet soit d'afficher la page de création d'un dossier, soit de traiter l'un des formulaires de la page. 
request : Objet requête
'''
@verif_acces
@nett_form
def creer_dossier(request) :

	reponse = None

	if request.method == 'GET' :

		# Je déclare un objet "formulaire" permettant une future manipulation des champs.
		f1 = gestion_dossiers.GererDossier(prefix = 'CreerDossier')

		# J'initialise un tableau des contenus des différentes fenêtres modales.
		tab_contenus_fm = {
			'choisir_dossier_associe' : gen_tabl_chois_doss(request, reverse('creer_dossier'))
		}

		# J'instancie un tableau de fenêtres modales.
		tab_fm = [
			init_fm('creer_dossier', 'Créer un dossier'),
			init_fm(
				'choisir_dossier_associe', 'Ajouter un dossier associé', tab_contenus_fm['choisir_dossier_associe']
			)
		]

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/creer_dossier.html',
			{
				'f1' : init_form(f1),
				'les_fm' : tab_fm,
				'title' : 'Créer un dossier'
			}
		)

	else :

		# Je vérifie la longueur du tableau "GET" afin de router vers l'opération voulue.
		if len(request.GET) > 0 :

			if 'action' in request.GET :

				# Je traite le cas où je veux filtrer les dossiers dans la fenêtre de choix d'un dossier associé.
				if len(request.GET) == 1 and request.GET['action'] == 'filtrer-dossiers' :

					# Je stocke dans un tableau les dossiers filtrés.
					les_dossiers_filtres = filtr_doss(request)

					# Je créé un tableau de dossiers filtrés reprenant les colonnes du tableau HTML des dossiers 
					# filtrés.
					tab_dossiers_filtres = []
					for un_dossier in les_dossiers_filtres :
						tab_dossiers_filtres.append([
							conv_none(un_dossier.num_doss),
							conv_none(un_dossier.int_doss),
							conv_none(un_dossier.id_org_moa.id_org_moa.n_org),
							conv_none(reecr_dt(un_dossier.dt_delib_moa_doss)),
							'<span class="bt-choisir pointer pull-right" onclick="ajout_doss_ass(event)"></span>'
						])

					# J'affiche le tableau des dossiers filtrés.
					reponse = HttpResponse(json.dumps(
						{ 'success' : tab_dossiers_filtres }), content_type = 'application/json'
					)

			else :

				# J'alimente les listes déroulantes des axes, des sous-axes, des actions et des types de dossiers.
				reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

		else :

			# Je déclare un objet "formulaire" permettant de traiter le formulaire d'ajout d'un dossier.
			f1 = gestion_dossiers.GererDossier(request.POST)

			# Je rajoute un choix valide pour certaines listes déroulantes (prévention d'erreurs).
			v_programme = request.POST.get('zld_progr')
			v_axe = request.POST.get('zld_axe')
			v_sous_axe = request.POST.get('zld_ss_axe')
			v_action = request.POST.get('zld_act')
			v_type_dossier = request.POST.get('zld_type_doss')

			axe_valide = False
			try :
				TAxe.objects.get(id_progr = v_programme, id_axe = v_axe)
				axe_valide = True
			except :
				if v_axe == 'D' :
					axe_valide = True
				else :
					pass

			if axe_valide == True :
				f1.fields['zld_axe'].choices = [(
					v_axe, 
					v_axe
				)]

			sous_axe_valide = False
			try :
				TSousAxe.objects.get(id_progr = v_programme, id_axe = v_axe, id_ss_axe = v_sous_axe)
				sous_axe_valide = True
			except :
				if v_sous_axe == 'D' :
					sous_axe_valide = True
				else :
					pass

			if sous_axe_valide == True :
				f1.fields['zld_ss_axe'].choices = [(
					v_sous_axe, 
					v_sous_axe
				)]

			action_valide = False
			try :
				TAction.objects.get(id_progr = v_programme, id_axe = v_axe, id_ss_axe = v_sous_axe, id_act = v_action)
				action_valide = True
			except :
				if v_action == 'D' :
					action_valide = True
				else :
					pass

			if action_valide == True :
				f1.fields['zld_act'].choices = [(
					v_action, 
					v_action
				)]

			type_dossier_valide = False
			try :
				TTypeDossier.objects.get(id_progr = v_programme, id_type_doss = v_type_dossier)
				type_dossier_valide = True
			except :
				if v_type_dossier == 'D' :
					type_dossier_valide = True
				else :
					pass

			if type_dossier_valide == True :
				f1.fields['zld_type_doss'].choices = [(
					v_type_dossier, 
					v_type_dossier
				)]

			if f1.is_valid() :

				# Je récupère et nettoie les données du formulaire valide.
				tab_donnees = f1.cleaned_data
				v_intitule_dossier = nett_val(tab_donnees['zs_int_doss'])
				v_description_dossier = nett_val(tab_donnees['zs_descr_doss'])
				v_dossier_associe = nett_val(tab_donnees['za_doss_ass'])
				v_moa = nett_val(integer(tab_donnees['zl_moa']), True)
				v_programme = nett_val(integer(tab_donnees['zld_progr']), True)
				v_axe = nett_val(integer(tab_donnees['zld_axe']), True)
				v_sous_axe = nett_val(integer(tab_donnees['zld_ss_axe']), True)
				v_action = nett_val(integer(tab_donnees['zld_act']), True)
				v_type_dossier = nett_val(integer(tab_donnees['zld_type_doss']), True)
				v_nature_dossier = nett_val(integer(tab_donnees['zl_nat_doss']), True)
				v_technicien = nett_val(integer(tab_donnees['zl_techn']), True)
				v_montant_ht_dossier = nett_val(tab_donnees['zs_mont_ht_doss'])
				v_montant_ttc_dossier = nett_val(tab_donnees['zs_mont_ttc_doss'])
				v_avancement = nett_val(integer(tab_donnees['zl_av']), True)
				v_date_deliberation_moa_dossier = nett_val(tab_donnees['zd_dt_delib_moa_doss'])
				v_avis_cp = nett_val(integer(tab_donnees['zl_av_cp']), True)
				v_date_avis_cp_dossier = nett_val(tab_donnees['zd_dt_av_cp_doss'])
				v_commentaire_dossier = nett_val(tab_donnees['zs_comm_doss'])
				v_quantification_objectifs = nett_val(tab_donnees['zs_quant_objs_pgre'])
				v_quantification_realisee = nett_val(tab_donnees['zs_quant_real_pgre'])
				v_unite = nett_val(integer(tab_donnees['zl_unit']))
				tab_rivieres = request.POST.getlist('cbsm_riv')
				v_portee = nett_val(integer(tab_donnees['zl_port']))

				# Je stocke le diminutif du programme choisi.
				diminutif_programme = TProgramme.objects.get(id_progr = v_programme).dim_progr

				# Je stocke le diminutif du maître d'ouvrage choisi.
				diminutif_moa = TMoa.objects.get(id_org_moa = v_moa).dim_org_moa

				# Je stocke le séquentiel suivant du programme choisi.
				sequentiel = int(TProgramme.objects.get(id_progr = v_programme).seq_progr) + 1
				sequentiel = str(sequentiel).zfill(2)

				# Je désigne le numéro du dossier.
				v_numero_dossier = '{0}-{1}-{2}'.format(diminutif_programme, diminutif_moa, sequentiel)

				# Je vérifie l'existence d'un objet TDossier appartenant au dossier associé choisi.
				obj_dossier_associe = None
				try :
					obj_dossier_associe = TDossier.objects.get(num_doss = v_dossier_associe)
				except :
					pass

				# Je désigne la valeur de la famille.
				if obj_dossier_associe is None :

					# Je créé un nouvel objet TFamille dans la base de données.
					obj_nouvelle_famille = TFamille()
					obj_nouvelle_famille.save()

					# Je récupère l'identifiant du nouvel objet TFamille.
					v_famille = obj_nouvelle_famille.id_fam

				else :

					# J'inclus le dossier dans une famille existante.
					v_famille = TDossier.objects.get(id_doss = obj_dossier_associe.id_doss).id_fam.id_fam

				# Je remplis les données attributaires du nouvel objet TDossier.
				obj_nouveau_dossier = TDossier(
					comm_doss = v_commentaire_dossier,
					descr_doss = v_description_dossier,
					dt_av_cp_doss = v_date_avis_cp_dossier,
					dt_delib_moa_doss = v_date_deliberation_moa_dossier,
					dt_int_doss = date.today(),
					int_doss = v_intitule_dossier,
					mont_ht_doss = v_montant_ht_dossier,
					mont_ttc_doss = v_montant_ttc_dossier,
					num_doss = v_numero_dossier,
					id_act = v_action,
					id_ss_axe = v_sous_axe,
					id_axe = v_axe,
					id_progr = TProgramme.objects.get(id_progr = v_programme),
					id_av = TAvancement.objects.get(id_av = v_avancement),
					id_av_cp = TAvisCp.objects.get(id_av_cp = v_avis_cp),
					id_doss_ass = obj_dossier_associe,
					id_fam = TFamille.objects.get(id_fam = v_famille),
					id_nat_doss = TNatureDossier.objects.get(id_nat_doss = v_nature_dossier),
					id_org_moa = TMoa.objects.get(id_org_moa = v_moa),
					id_techn = TTechnicien.objects.get(id_techn = v_technicien),
					id_type_doss = TTypeDossier.objects.get(id_type_doss = v_type_dossier),				
				)

				# Je créé un nouvel objet TDossier dans la base de données.
				obj_nouveau_dossier.save()

				# Je tente d'incrémenter le séquentiel du programme choisi et j'enregistre la modification de l'objet 
				# TProgramme dans la base de données.
				try :
					obj_programme = TProgramme.objects.get(id_progr = v_programme)
					obj_programme.seq_progr = int(obj_programme.seq_progr) + 1
					obj_programme.save()
				except :
					pass

				# Je fais le lien avec la table t_pgre si et seulement si l'intitulé du programme choisi est "PGRE".
				if TProgramme.objects.get(id_progr = v_programme).int_progr == 'PGRE' :

					# Je vérifie l'existence d'un objet TUnite.
					obj_unite = None
					try :
						obj_unite = TUnite.objects.get(id_unit = v_unite)
					except :
						pass

					# Je vérifie l'existence d'un objet TPortee.
					obj_portee = None
					try :
						obj_portee = TPortee.objects.get(id_port = v_portee)
					except :
						pass

					# Je remplis les données attributaires du nouvel objet TPgre.
					obj_nouveau_dossier_pgre = TPgre(
						id_pgre = TDossier.objects.get(id_doss = obj_nouveau_dossier.id_doss),
						quant_objs_pgre = v_quantification_objectifs,
						quant_real_pgre = v_quantification_realisee,
						id_port = obj_portee,
						id_unit = obj_unite
					)

					# Je créé un nouvel objet TPgre dans la base de données.
					obj_nouveau_dossier_pgre.save()

					# Je parcours le tableau des rivières sélectionnées.
					for i in range(0, len(tab_rivieres)) :

						# Je tente de convertir en entier l'identifiant de la rivière courante, sinon sa valeur sera
						# -1.
						v_riviere = integer(tab_rivieres[i])

						# Je créé un nouvel objet TRivieresDossier si et seulement si l'identifiant converti de la
						# rivière courante existe dans la base de données.
						if v_riviere > 0 :

							obj_nouvelle_riviere_dossier = TRivieresDossier.objects.create(
								id_pgre = TPgre.objects.get(id_pgre = obj_nouveau_dossier_pgre),
								id_riv = TRiviere.objects.get(id_riv = v_riviere)
							)

				# Je stocke le chemin vers le répertoire "dossiers" (racine).
				chemin_racine = '{0}\{1}\\'.format(MEDIA_ROOT, 'dossiers')

				# Je stocke le chemin vers le répertoire destiné au nouveau dossier.
				chemin_dossier = chemin_racine + obj_nouveau_dossier.num_doss

				# J'initialise un tableau de dossiers à créer.
				tab_dossiers_repertoire = [
					chemin_dossier,
					chemin_dossier + '\\' + 'caracteristiques',
					chemin_dossier + '\\' + 'plan_de_financement',
					chemin_dossier + '\\' + 'prestations',
					chemin_dossier + '\\' + 'factures',
					chemin_dossier + '\\' + 'demandes_de_versement',
					chemin_dossier + '\\' + 'reglementations',
					chemin_dossier + '\\' + 'photos'
				]

				# Je créé chaque dossier.
				for i in range(0, len(tab_dossiers_repertoire)) :
					os.mkdir(tab_dossiers_repertoire[i])

				# Je mets à jour l'onglet actif après rechargement de la page.
				request.session['menu_dossier'] = '#ong_caracteristiques'

				# J'affiche le message de succès de la procédure de création d'un dossier.
				reponse = HttpResponse(
					json.dumps({
						'success' : 'Le dossier a été ajouté avec succès. Son numéro est {0}.'.format(
							obj_nouveau_dossier.num_doss
						),
						'redirect' : reverse('consulter_dossier', args = [obj_nouveau_dossier.id_doss])
					}),
					content_type = 'application/json'
				)

			else :

				# J'affiche les erreurs du formulaire de création d'un dossier.
				reponse = HttpResponse(json.dumps(f1.errors), content_type = 'application/json')

	return reponse

'''
Cette vue permet d'afficher le menu du module de gestion des dossiers.
request : Objet requête
'''
@verif_acces
def index(request) :

	# J'affiche le template.
	return render(
		request,
		'./gestion_dossiers/main.html',
		{ 'title' : 'Gestion des dossiers' }
	)

'''
Cette vue permet soit d'afficher la page de modification d'un dossier, soit de traiter l'un des formulaires de la page.
request : Objet requête
p_dossier : Identifiant du dossier à modifier
'''
@verif_acces
@nett_form
def modifier_dossier(request, p_dossier) :

	reponse = None

	if request.method == 'GET' :

		# Je vérifie l'existence d'un objet TDossier.
		obj_dossier = get_object_or_404(TDossier, id_doss = p_dossier)

		# Je vérifie l'existence d'un objet "TDossier" correspondant au dossier associé de l'objet TDossier principal.
		obj_dossier_associe = None
		try :
			obj_dossier_associe = TDossier.objects.get(id_doss = obj_dossier.id_doss_ass.id_doss)
		except :
			pass

		if obj_dossier_associe is not None :
			v_numero_dossier_associe = obj_dossier_associe.num_doss
		else :
			v_numero_dossier_associe = None

		kwargs = {
			'prefix' : 'ModifierDossier',
			'k_dossier' : obj_dossier.num_doss,
			'k_intitule_dossier' : obj_dossier.int_doss,
			'k_description_dossier' : obj_dossier.descr_doss,
			'k_dossier_associe' : v_numero_dossier_associe,
			'k_moa' : obj_dossier.id_org_moa.id_org_moa.id_org,
			'k_programme' : obj_dossier.id_progr.id_progr,
			'k_axe' : obj_dossier.id_axe,
			'k_sous_axe' : obj_dossier.id_ss_axe,
			'k_action' : obj_dossier.id_act,
			'k_type_dossier' : obj_dossier.id_type_doss.id_type_doss,
			'k_nature_dossier' : obj_dossier.id_nat_doss.id_nat_doss,
			'k_technicien' : obj_dossier.id_techn.id_techn,
			'k_montant_ht_dossier' : obj_dossier.mont_ht_doss,
			'k_montant_ttc_dossier' : obj_dossier.mont_ttc_doss,
			'k_avancement' : obj_dossier.id_av.id_av,
			'k_date_deliberation_moa_dossier' : obj_dossier.dt_delib_moa_doss,
			'k_avis_cp' : obj_dossier.id_av_cp.id_av_cp,
			'k_date_avis_cp_dossier' : obj_dossier.dt_av_cp_doss,
			'k_commentaire_dossier' : obj_dossier.comm_doss
		}

		if obj_dossier.id_progr.int_progr == 'PGRE' :
			obj_dossier_pgre = TPgre.objects.get(id_pgre = obj_dossier.id_doss)
			kwargs['k_quantification_objectifs'] = obj_dossier_pgre.quant_objs_pgre
			kwargs['k_quantification_realisee'] = obj_dossier_pgre.quant_real_pgre

			kwargs['k_unite'] = -1
			try :
				kwargs['k_unite'] = obj_dossier_pgre.id_unit.id_unit
			except :
				pass

			kwargs['k_portee'] = -1
			try :
				kwargs['k_portee'] = obj_dossier_pgre.id_port.id_port
			except :
				pass

		# Je déclare des objets "formulaire" permettant une future manipulation des champs.
		f1 = gestion_dossiers.GererDossier(**kwargs)

		# J'initialise un tableau des contenus des différentes fenêtres modales.
		tab_contenus_fm = {
			'choisir_dossier_associe' : gen_tabl_chois_doss(
				request, reverse('modifier_dossier', args = [obj_dossier.id_doss])
			)
		}

		# J'instancie un tableau de fenêtres modales.
		tab_fm = [
			init_fm('modifier_dossier', 'Modifier un dossier'),
			init_fm(
				'choisir_dossier_associe', 'Modifier un dossier associé', tab_contenus_fm['choisir_dossier_associe']
			)
		]

		# J'affiche le template.
		reponse = render(
			request,
			'./gestion_dossiers/modifier_dossier.html',
			{
				'f1' : init_form(f1),
				'le_dossier' : obj_dossier,
				'les_fm' : tab_fm,
				'title' : 'Modifier un dossier'
			}
		)

	else :

		# Je vérifie l'existence d'un objet TDossier.
		try :
			obj_dossier = TDossier.objects.get(id_doss = p_dossier)
		except :
			return HttpResponse()

		if 'action' in request.GET :

			action = request.GET['action']

			# Je traite le cas où je veux filtrer les dossiers dans la fenêtre de choix d'un dossier associé.
			if len(request.GET) == 1 and action == 'filtrer-dossiers' :

				# Je stocke dans un tableau les dossiers filtrés.
				les_dossiers_filtres = filtr_doss(request)

				# Je créé un tableau de dossiers filtrés reprenant les colonnes du tableau HTML des dossiers
				# filtrés.
				tab_dossiers_filtres = []
				for un_dossier in les_dossiers_filtres :
					tab_dossiers_filtres.append([
						conv_none(un_dossier.num_doss),
						conv_none(un_dossier.int_doss),
						conv_none(un_dossier.id_org_moa.id_org_moa.n_org),
						conv_none(reecr_dt(un_dossier.dt_delib_moa_doss)),
						'<span class="bt-choisir pointer pull-right" onclick="ajout_doss_ass(event)"></span>'
					])

				# J'envoie la liste des dossiers filtrés.
				reponse = HttpResponse(json.dumps(
					{ 'success' : tab_dossiers_filtres }), content_type = 'application/json'
				)

			# Je traite le cas où je veux modifier l'onglet "Caractéristiques".
			elif len(request.GET) == 1 and action == 'modifier-caracteristiques' :

				# Je déclare un objet "formulaire" permettant de traiter le formulaire de modification d'un dossier.
				f1 = gestion_dossiers.GererDossier(request.POST)

				# Je rajoute un choix valide pour certaines listes déroulantes (prévention d'erreurs).
				v_programme = request.POST.get('zld_progr')
				v_axe = request.POST.get('zld_axe')
				v_sous_axe = request.POST.get('zld_ss_axe')
				v_action = request.POST.get('zld_act')
				v_type_dossier = request.POST.get('zld_type_doss')
				
				f1.fields['zl_moa'].choices = [(
					request.POST.get('zl_moa'), 
					request.POST.get('zl_moa')
				)]

				axe_valide = False
				try :
					TAxe.objects.get(id_progr = v_programme, id_axe = v_axe)
					axe_valide = True
				except :
					if v_axe == 'D' :
						axe_valide = True
					else :
						pass

				if axe_valide == True :
					f1.fields['zld_axe'].choices = [(
						v_axe, 
						v_axe
					)]

				sous_axe_valide = False
				try :
					TSousAxe.objects.get(id_progr = v_programme, id_axe = v_axe, id_ss_axe = v_sous_axe)
					sous_axe_valide = True
				except :
					if v_sous_axe == 'D' :
						sous_axe_valide = True
					else :
						pass

				if sous_axe_valide == True :
					f1.fields['zld_ss_axe'].choices = [(
						v_sous_axe, 
						v_sous_axe
					)]

				action_valide = False
				try :
					TAction.objects.get(id_progr = v_programme, id_axe = v_axe, id_ss_axe = v_sous_axe, id_act = v_action)
					action_valide = True
				except :
					if v_action == 'D' :
						action_valide = True
					else :
						pass

				if action_valide == True :
					f1.fields['zld_act'].choices = [(
						v_action, 
						v_action
					)]

				type_dossier_valide = False
				try :
					TTypeDossier.objects.get(id_progr = v_programme, id_type_doss = v_type_dossier)
					type_dossier_valide = True
				except :
					if v_type_dossier == 'D' :
						type_dossier_valide = True
					else :
						pass

				if type_dossier_valide == True :
					f1.fields['zld_type_doss'].choices = [(
						v_type_dossier, 
						v_type_dossier
					)]

				if f1.is_valid() :

					# Je récupère et nettoie les données du formulaire valide.
					tab_donnees = f1.cleaned_data
					v_intitule_dossier = nett_val(tab_donnees['zs_int_doss'])
					v_description_dossier = nett_val(tab_donnees['zs_descr_doss'])
					v_dossier_associe = nett_val(tab_donnees['za_doss_ass'])
					v_moa = nett_val(integer(tab_donnees['zl_moa']))
					v_programme = nett_val(integer(tab_donnees['zld_progr']))
					v_axe = nett_val(integer(tab_donnees['zld_axe']), True)
					v_sous_axe = nett_val(integer(tab_donnees['zld_ss_axe']), True)
					v_action = nett_val(integer(tab_donnees['zld_act']), True)
					v_type_dossier = nett_val(integer(tab_donnees['zld_type_doss']), True)
					v_nature_dossier = nett_val(integer(tab_donnees['zl_nat_doss']), True)
					v_technicien = nett_val(integer(tab_donnees['zl_techn']), True)
					v_montant_ht_dossier = nett_val(tab_donnees['zs_mont_ht_doss'])
					v_montant_ttc_dossier = nett_val(tab_donnees['zs_mont_ttc_doss'])
					v_avancement = nett_val(integer(tab_donnees['zl_av']), True)
					v_date_deliberation_moa_dossier = nett_val(tab_donnees['zd_dt_delib_moa_doss'])
					v_avis_cp = nett_val(integer(tab_donnees['zl_av_cp']), True)
					v_date_avis_cp_dossier = nett_val(tab_donnees['zd_dt_av_cp_doss'])
					v_commentaire_dossier = nett_val(tab_donnees['zs_comm_doss'])
					v_quantification_objectifs = nett_val(tab_donnees['zs_quant_objs_pgre'])
					v_quantification_realisee = nett_val(tab_donnees['zs_quant_real_pgre'])
					v_unite = nett_val(integer(tab_donnees['zl_unit']))
					tab_rivieres = request.POST.getlist('cbsm_riv')
					v_portee = nett_val(integer(tab_donnees['zl_port']))

					# Je vérifie l'existence d'un objet TDossier correspondant au dossier associé.
					obj_nv_dossier_associe = None
					try :
						obj_nv_dossier_associe = TDossier.objects.get(num_doss = v_dossier_associe)
					except :
						pass

					# J'initialise la valeur de la famille selon deux paramètres : la valeur de l'ancien dossier associé et
					# la valeur du nouveau dossier associé.
					if obj_nv_dossier_associe is None :

						if obj_dossier.id_doss_ass is None :
							v_famille = obj_dossier.id_fam.id_fam
						else :

							# Je créé une nouvelle famille si et seulement si le dossier à modifier n'admet aucun dossier 
							# associé et qu'auparavant il était associé à un dossier.
							obj_nouvelle_famille = TFamille()
							obj_nouvelle_famille.save()

							# Je récupère l'identifiant de la nouvelle famille.
							v_famille = obj_nouvelle_famille.id_fam

					else :

						# Je renseigne l'identifiant de la famille du dossier associé (inclusion dans la famille de celui-
						# ci).
						v_famille = TDossier.objects.get(id_doss = obj_nv_dossier_associe.id_doss).id_fam.id_fam

						# Je mets à jour la famille de tous les dossiers qui sont associés au dossier à modifier.
						for un_dossier in TDossier.objects.filter(id_doss_ass = obj_dossier.id_doss) :
							un_dossier.id_fam = TFamille.objects.get(id_fam = v_famille)
							un_dossier.save()

					# Je remplis les données attributaires de l'objet TDossier à modifier.
					obj_dossier.comm_doss = v_commentaire_dossier
					obj_dossier.descr_doss = v_description_dossier
					obj_dossier.dt_av_cp_doss = v_date_avis_cp_dossier
					obj_dossier.dt_delib_moa_doss = v_date_deliberation_moa_dossier
					obj_dossier.int_doss = v_intitule_dossier
					obj_dossier.mont_ht_doss = v_montant_ht_dossier
					obj_dossier.mont_ttc_doss = v_montant_ttc_dossier
					obj_dossier.id_act = v_action
					obj_dossier.id_ss_axe = v_sous_axe
					obj_dossier.id_axe = v_axe
					obj_dossier.id_progr = TProgramme.objects.get(id_progr = v_programme)
					obj_dossier.id_av = TAvancement.objects.get(id_av = v_avancement)
					obj_dossier.id_av_cp = TAvisCp.objects.get(id_av_cp = v_avis_cp)
					obj_dossier.id_doss_ass = obj_nv_dossier_associe
					obj_dossier.id_fam = TFamille.objects.get(id_fam = v_famille)
					obj_dossier.id_nat_doss = TNatureDossier.objects.get(id_nat_doss = v_nature_dossier)
					obj_dossier.id_org_moa = TMoa.objects.get(id_org_moa = v_moa)
					obj_dossier.id_techn = TTechnicien.objects.get(id_techn = v_technicien)
					obj_dossier.id_type_doss = TTypeDossier.objects.get(id_type_doss = v_type_dossier)

					# Je mets à jour l'objet TDossier dans la base de données.
					obj_dossier.save()

					# Je supprime les familles vierges.
					for une_famille in TFamille.objects.all() :
						try :
							une_famille.delete()
						except :
							pass

					# Je mets à jour la table t_pgre si le programme du dossier est "PGRE".
					if TProgramme.objects.get(id_progr = v_programme).int_progr == 'PGRE' :

						# Je vérifie l'existence d'un objet TUnite.
						obj_unite = None
						try :
							obj_unite = TUnite.objects.get(id_unit = v_unite)
						except :
							pass

						# Je vérifie l'existence d'un objet TPortee.
						obj_portee = None
						try :
							obj_portee = TPortee.objects.get(id_port = v_portee)
						except :
							pass

						# Je remplis les données attributaires de l'objet TPgre à modifier.
						obj_dossier_pgre = TPgre.objects.get(id_pgre = obj_dossier.id_doss)
						obj_dossier_pgre.quant_objs_pgre = v_quantification_objectifs
						obj_dossier_pgre.quant_real_pgre = v_quantification_realisee
						obj_dossier_pgre.id_port = obj_portee
						obj_dossier_pgre.id_unit = obj_unite

						# Je mets à jour l'objet TPgre dans la base de données.
						obj_dossier_pgre.save()

						# Je supprime tous les objets TRivieresDossier dont l'identifiant du dossier PGRE est celui du 
						# dossier PGRE en cours de modification.
						TRivieresDossier.objects.filter(id_pgre = TPgre.objects.get(id_pgre = obj_dossier_pgre)).delete()

						# Je parcours le tableau des rivières sélectionnées.
						for i in range(0, len(tab_rivieres)) :

							# Je tente de convertir en entier l'identifiant de la rivière courante, sinon sa valeur sera
							# -1.
							v_riviere = integer(tab_rivieres[i])

							# Je créé un nouvel objet TRivieresDossier si et seulement si l'identifiant converti de la
							# rivière courante existe dans la base de données.
							if v_riviere > 0 :

								obj_nouvelle_riviere_dossier = TRivieresDossier.objects.create(
									id_pgre = TPgre.objects.get(id_pgre = obj_dossier_pgre),
									id_riv = TRiviere.objects.get(id_riv = v_riviere)
								)

					# Je mets à jour l'onglet actif après rechargement de la page.
					request.session['menu_dossier'] = '#ong_caracteristiques'

					# J'affiche le message de succès de la procédure de mise à jour d'un dossier.
					reponse = HttpResponse(
						json.dumps({
							'success' : 'Le dossier a été mis à jour avec succès.',
							'redirect' : reverse('consulter_dossier', args = [obj_dossier.id_doss])
						}),
						content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs du formulaire de modification d'un dossier.
					reponse = HttpResponse(json.dumps(f1.errors), content_type = 'application/json')

			# Je traite le cas où je veux modifier l'onglet "Réglementations".
			elif len(request.GET) == 1 and action == 'modifier-reglementations' :

				# Je déclare un objet "formulaire" permettant de traiter le formulaire de modification d'un dossier.
				f2 = gestion_dossiers.GererDossier_Reglementation(request.POST)

				if f2.is_valid() :

					# Je récupère et nettoie la donnée du formulaire valide.
					tab_donnees = f2.cleaned_data
					v_commentaire_reglementation = nett_val(tab_donnees['zs_comm_regl_doss'])

					# Je mets à jour l'objet TDossier.
					obj_dossier.comm_regl_doss = v_commentaire_reglementation
					obj_dossier.save()

					# Je mets à jour l'onglet actif après rechargement de la page.
					request.session['menu_dossier'] = '#ong_reglementations'

					# J'affiche le message de succès de la procédure de mise à jour d'un dossier.
					reponse = HttpResponse(
						json.dumps({
							'success' : 'Le dossier a été mis à jour avec succès.',
							'redirect' : reverse('consulter_dossier', args = [obj_dossier.id_doss])
						}),
						content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs du formulaire de modification d'un dossier.
					reponse = HttpResponse(json.dumps(f2.errors), content_type = 'application/json')

		else :

			# J'alimente les listes déroulantes des axes, des sous-axes, des actions et des types de dossiers.
			reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

	return reponse

'''
Cette vue permet de supprimer un dossier de la base de données.
request : Objet requête
p_dossier : Dossier à supprimer
'''
@verif_acces
@csrf_exempt
def supprimer_dossier(request, p_dossier) :

	reponse = None

	if request.method == 'POST' :

		'''
		# Je peux utiliser les données attributaires du dossier à supprimer.
		obj_dossier = TDossier.objects.get(id_doss = p_dossier)

		# Je supprime le dossier.
		obj_dossier.delete()
		'''

		# J'affiche le message de succès de la procédure de suppression d'une photo.
		reponse = HttpResponse(
			json.dumps({
				'success' : 'Le dossier a été supprimé avec succès.',
				'redirect' : reverse('choisir_dossier')
			}),
			content_type = 'application/json'
		)

	else :
		raise PermissionDenied

	return reponse

'''
Cette vue permet de supprimer une photo de la base de données ainsi que du serveur média.
request : Objet requête
'''
@verif_acces
@csrf_exempt
def supprimer_photo(request) :

	reponse = None

	if request.method == 'POST' :
		if len(request.GET) == 1 and 'photo' in request.GET :

			# Je vérifie l'existence d'un objet TPhoto.
			try :
				obj_photo = TPhoto.objects.get(id_ph = request.GET['photo'])
			except :
				return HttpResponse()

			# Je tente d'effacer la photo du serveur média.
			try :
				os.remove(MEDIA_ROOT + '\\' + obj_photo.chem_ph)
			except :
				pass

			# Je récupère l'identifiant du dossier rattaché à la photo en cours de suppression.
			id_dossier = obj_photo.id_doss.id_doss

			# Je supprime l'objet TPhoto de la base de données.
			obj_photo.delete()

			# J'affiche le message de succès de la procédure de suppression d'une photo.
			reponse = HttpResponse(
				json.dumps({
					'success' : 'La photo a été supprimée avec succès.',
					'redirect' : reverse('consulter_dossier', args = [id_dossier])
				}),
				content_type = 'application/json'
			)

	return reponse