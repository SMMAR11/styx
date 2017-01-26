#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.decorators import *
from django.views.decorators.csrf import csrf_exempt

'''
Cette vue permet d'afficher le menu principal du module de gestion des dossiers.
request : Objet requête
'''
@verif_acc
def index(request) :

	''' Imports '''
	from django.http import HttpResponse
	from django.shortcuts import render

	output = HttpResponse()

	if request.method == 'GET' :

		# J'affiche le template.
		output = render(request, './gestion_dossiers/main.html', { 'title' : 'Gestion des dossiers' })

	return output

'''
Cette vue permet d'afficher la page de création d'un dossier ou de traiter une action.
request : Objet requête
'''
@verif_acc
@nett_f
def cr_doss(request) :

	# Imports
	from app.forms.gestion_dossiers import GererDossier
	from app.functions import alim_ld
	from app.functions import dt_fr
	from app.functions import filtr_doss
	from app.functions import gen_t_ch_doss
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import rempl_fich_log
	from app.models import TAction
	from app.models import TAxe
	from app.models import TDossier
	from app.models import TFamille
	from app.models import TMoa
	from app.models import TProgramme
	from app.models import TSousAxe
	from app.models import TTypesProgrammesTypeDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = HttpResponse()

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_cr_doss = GererDossier(prefix = 'GererDossier', k_util = request.user)

		# Je déclare un tableau qui stocke le contenu de certaines fenêtres modales.
		t_cont_fm = {
			'ch_doss' : gen_t_ch_doss(request)
		}

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('ch_doss', 'Choisir un dossier associé', t_cont_fm['ch_doss']),
			init_fm('cr_doss', 'Créer un dossier')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/cr_doss.html',
			{ 'f_cr_doss' : init_f(f_cr_doss), 't_fm' : t_fm, 'title' : 'Créer un dossier' }
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois alimenter les listes déroulantes des axes, des sous-axes, des actions et des
			# types de dossiers.
			if get_action == 'alimenter-listes' :

				# J'affiche ou je cache certaines listes déroulantes selon les données qu'elles contiennent.
				output = HttpResponse(json.dumps(alim_ld(request)), content_type = 'application/json')

			# Je traite le cas où je dois filtrer les dossiers selon certains critères.
			if get_action == 'filtrer-dossiers' :

				# Je prépare le tableau des dossiers filtrés.
				t_doss = [(
					d.num_doss,
					'{0} - {1} - {2} - {3}'.format(d.id_nat_doss, d.id_type_doss, d.lib_1_doss, d.lib_2_doss),
					d.id_org_moa.n_org,
					dt_fr(d.dt_delib_moa_doss) or '-',
					'<span class="choose-icon pointer pull-right" title="Choisir le dossier"></span>'
				) for d in filtr_doss(request)]

				# J'envoie le tableau des dossiers filtrés.
				output = HttpResponse(
					json.dumps({ 'success' : { 'datatable' : t_doss }}), content_type = 'application/json'
				)

		else :

			# Je soumets le formulaire.
			f_cr_doss = GererDossier(request.POST, request.FILES, prefix = 'GererDossier', k_util = request.user)

			# Je rajoute des choix valides pour certaines listes déroulantes (prévention d'erreurs).
			post_progr = request.POST['GererDossier-id_progr']
			post_axe = request.POST['GererDossier-zl_axe']
			post_ss_axe = request.POST['GererDossier-zl_ss_axe']
			if post_progr :
				t_axes = [(a.pk, a.pk) for a in TAxe.objects.filter(id_progr = post_progr)]
				f_cr_doss.fields['zl_axe'].choices = t_axes
				t_types_doss = [
					(td.id_type_doss.pk, td.id_type_doss.pk) for td in TTypesProgrammesTypeDossier.objects.filter(
						id_type_progr = TProgramme.objects.get(pk = post_progr).id_type_progr.pk
					)
				]
				f_cr_doss.fields['zl_type_doss'].choices = t_types_doss
				t_ss_axes = [(sa.pk, sa.pk) for sa in TSousAxe.objects.filter(id_axe = post_axe)]
				f_cr_doss.fields['zl_ss_axe'].choices = t_ss_axes
				t_act = [(a.pk, a.pk) for a in TAction.objects.filter(id_ss_axe = post_ss_axe)]
				f_cr_doss.fields['zl_act'].choices = t_act

			if f_cr_doss.is_valid() :

				# Je récupère les données du formulaire valide.
				cleaned_data = f_cr_doss.cleaned_data
				v_doss_ass = cleaned_data.get('za_doss_ass')
				v_org_moa = cleaned_data.get('zl_org_moa')
				v_progr = cleaned_data.get('id_progr')

				# Je pointe vers l'objet TMoa.
				o_org_moa = TMoa.objects.get(pk = v_org_moa)

				# J'initialise la valeur de la famille (valeur existante ou nouvelle instance).
				if v_doss_ass :
					o_fam = TDossier.objects.get(num_doss = v_doss_ass).id_fam
				else :
					o_fam = TFamille()
					o_fam.save()

				# Je prépare la valeur de chaque constituant du numéro de dossier.
				dim_progr = v_progr.dim_progr
				if o_org_moa.dim_org_moa :
					dim_org_moa = o_org_moa.dim_org_moa
				else :
					dim_org_moa = 'X'
				seq_progr = str(v_progr.seq_progr).zfill(2)

				# Je créé la nouvelle instance TDossier.
				o_nv_doss = f_cr_doss.save(commit = False)
				o_nv_doss.num_doss = '{0}-{1}-{2}'.format(dim_progr, dim_org_moa, seq_progr)
				o_nv_doss.id_fam = o_fam
				o_nv_doss.save()

				# Je mets à jour le séquentiel.
				v_progr.seq_progr = int(v_progr.seq_progr) + 1
				v_progr.save()

				# J'affiche le message de succès.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le dossier {0} a été créé avec succès.'.format(o_nv_doss),
						'redirect' : reverse('cons_doss', args = [o_nv_doss.id_doss])
					}}), 
					content_type = 'application/json'
				)

				# Je complète le fichier log.
				rempl_fich_log([request.user.pk, request.user, 'C', 'Dossier', o_nv_doss.pk])

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_cr_doss.errors.items() :
					t_err['GererDossier-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'un dossier ou de traiter le formulaire de mise à jour d'un
dossier.
request : Objet requête
_d : Identifiant d'un dossier
'''
@verif_acc
@nett_f
def modif_doss(request, _d) :

	# Imports
	from app.forms.gestion_dossiers import GererDossier
	from app.functions import alim_ld
	from app.functions import dt_fr
	from app.functions import filtr_doss
	from app.functions import gen_t_ch_doss
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import rempl_fich_log
	from app.models import TAction
	from app.models import TAxe
	from app.models import TDossier
	from app.models import TDossierGeom
	from app.models import TFamille
	from app.models import TFinancement
	from app.models import TPrestationsDossier
	from app.models import TSousAxe
	from django.contrib.gis import geos
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TDossier.
	o_doss = get_object_or_404(TDossier, pk = _d)

	# Je vérifie le droit d'écriture.
	ger_droits(request.user, o_doss, False)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_doss = GererDossier(instance = o_doss, prefix = 'GererDossier')

		# Je déclare un tableau qui stocke le contenu de certaines fenêtres modales.
		t_cont_fm = {
			'ch_doss' : gen_t_ch_doss(request, o_doss.pk)
		}

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('ch_doss', 'Choisir un dossier associé', t_cont_fm['ch_doss']),
			init_fm('modif_doss', 'Modifier un dossier')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/modif_doss.html',
			{
				'd' : o_doss,
				'f_modif_doss' : init_f(f_modif_doss),
				't_fm' : t_fm,
				't_fin_length' : len(TFinancement.objects.filter(id_doss = o_doss)),
				't_prest_doss_length' : len(TPrestationsDossier.objects.filter(id_doss = o_doss)),
				'title' : 'Modifier un dossier'
			}
		)
	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois alimenter les listes déroulantes des axes, des sous-axes, des actions et des
			# types de dossiers.
			if get_action == 'alimenter-listes' :

				# J'affiche ou je cache certaines listes déroulantes selon les données qu'elles contiennent.
				output = HttpResponse(json.dumps(alim_ld(request)), content_type = 'application/json')

			# Je traite le cas où je dois filtrer les dossiers selon certains critères.
			if get_action == 'filtrer-dossiers' :

				# Je prépare le tableau des dossiers filtrés.
				t_doss = [(
					d.num_doss,
					'{0} - {1} - {2} - {3}'.format(d.id_nat_doss, d.id_type_doss, d.lib_1_doss, d.lib_2_doss),
					d.id_org_moa.n_org,
					dt_fr(d.dt_delib_moa_doss) or '-',
					'<span class="choose-icon pointer pull-right" title="Choisir le dossier"></span>'
				) for d in filtr_doss(request, o_doss.pk)]

				# J'envoie le tableau des dossiers filtrés.
				output = HttpResponse(
					json.dumps({ 'success' : { 'datatable' : t_doss }}), content_type = 'application/json'
				)

			# Je traite le cas où je dois modifier la géométrie de l'objet TDossier.
			if get_action == 'modifier-geom' :

				# Je supprime les géométries existantes du dossier.
				TDossierGeom.objects.filter(id_doss = o_doss).delete()

				if request.POST['edit-geom'] :
					
					# Je récupère les objets créés.
					editgeom = request.POST['edit-geom'].split(';')

					# Je créé la nouvelle instance TDossierGeom.
					for g in editgeom :
						geom = geos.GEOSGeometry(g)
						geom_doss = TDossierGeom(id_doss = o_doss)
						if geom and isinstance(geom, geos.Polygon):
							geom_doss.geom_pol = geom
						if geom and isinstance(geom, geos.LineString):
							geom_doss.geom_lin = geom
						if geom and isinstance(geom, geos.Point):
							geom_doss.geom_pct = geom
						geom_doss.save()

				# J'affiche le message de succès.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'La géométrie du dossier {0} a été mise à jour avec succès.'.format(o_doss),
						'redirect' : reverse('cons_doss', args = [o_doss.pk])
					}}), 
					content_type = 'application/json'
				)

				# Je complète le fichier log.
				rempl_fich_log([request.user.pk, request.user, 'U', 'Géométrie d\'un dossier', o_doss.pk])

		else :

			# Je soumets le formulaire.
			f_modif_doss = GererDossier(request.POST, request.FILES, instance = o_doss, prefix = 'GererDossier')

			# Je rajoute des choix valides pour certaines listes déroulantes (prévention d'erreurs).
			post_progr = request.POST['GererDossier-id_progr']
			post_axe = request.POST['GererDossier-zl_axe']
			post_ss_axe = request.POST['GererDossier-zl_ss_axe']
			if post_progr :
				t_axes = [(a.pk, a.pk) for a in TAxe.objects.filter(id_progr = post_progr)]
				f_modif_doss.fields['zl_axe'].choices = t_axes
				f_modif_doss.fields['zl_type_doss'].choices = [(o_doss.id_type_doss.pk, o_doss.id_type_doss)]
				t_ss_axes = [(sa.pk, sa.pk) for sa in TSousAxe.objects.filter(id_axe = post_axe)]
				f_modif_doss.fields['zl_ss_axe'].choices = t_ss_axes
				t_act = [(a.pk, a.pk) for a in TAction.objects.filter(id_ss_axe = post_ss_axe)]
				f_modif_doss.fields['zl_act'].choices = t_act

			if f_modif_doss.is_valid() :

				# Je récupère les données du formulaire valide.
				cleaned_data = f_modif_doss.cleaned_data
				v_doss_ass = cleaned_data.get('za_doss_ass')

				# Je pointe vers l'objet TDossier relatif au dossier associé.
				o_doss_ass = TDossier.objects.get(pk = o_doss.pk).id_doss_ass

				# J'initialise la valeur de la famille (valeur existante ou nouvelle instance).
				if v_doss_ass :
					v_fam = TDossier.objects.get(num_doss = v_doss_ass).id_fam
					TDossier.objects.filter(id_doss_ass = o_doss.pk).update(id_fam = v_fam)
				else :
					if o_doss_ass :
						v_fam = TFamille()
						v_fam.save()
					else :
						v_fam = o_doss.id_fam

				# Je modifie l'instance TDossier.
				o_doss_modif = f_modif_doss.save(commit = False)
				o_doss_modif.id_fam = v_fam
				o_doss_modif.save()

				# J'affiche le message de succès.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le dossier {0} a été mis à jour avec succès.'.format(o_doss_modif),
						'redirect' : reverse('cons_doss', args = [o_doss_modif.pk])
					}}), 
					content_type = 'application/json'
				)

				# Je complète le fichier log.
				rempl_fich_log([request.user.pk, request.user, 'U', 'Dossier', o_doss_modif.pk])

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_modif_doss.errors.items() :
					t_err['GererDossier-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de choix d'un dossier ou de traiter une action.
request : Objet requête
'''
@verif_acc
@nett_f
def ch_doss(request) :

	# Imports
	from app.forms.gestion_dossiers import ChoisirDossier
	from app.functions import alim_ld
	from app.functions import dt_fr
	from app.functions import filtr_doss
	from app.functions import init_f
	from app.models import TDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = HttpResponse()

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_ch_doss = ChoisirDossier(prefix = 'ChoisirDossier')

		# Je prépare le tableau des dossiers.
		t_doss = [{
			'pk' : d.pk,
			'num_doss' : d,
			'int_doss' : '{0} - {1} - {2} - {3}'.format(d.id_nat_doss, d.id_type_doss, d.lib_1_doss, d.lib_2_doss),
			'n_org' : d.id_org_moa,
			'dt_delib_moa_doss' : dt_fr(d.dt_delib_moa_doss) or '-'
		} for d in TDossier.objects.all()]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/ch_doss.html',
			{ 'f_ch_doss' : init_f(f_ch_doss), 't_doss' : t_doss, 'title' : 'Choisir un dossier' }
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois alimenter les listes déroulantes des axes, des sous-axes, des actions et des
			# types de dossiers.
			if get_action == 'alimenter-listes' :

				# J'affiche ou je cache certaines listes déroulantes selon les données qu'elles contiennent.
				output = HttpResponse(json.dumps(alim_ld(request)), content_type = 'application/json')

			# Je traite le cas où je dois filtrer les dossiers selon certains critères.
			if get_action == 'filtrer-dossiers' :

				# Je prépare le tableau des dossiers filtrés.
				t_doss = [(
					d.num_doss,
					'{0} - {1} - {2} - {3}'.format(d.id_nat_doss, d.id_type_doss, d.lib_1_doss, d.lib_2_doss),
					d.id_org_moa.n_org,
					dt_fr(d.dt_delib_moa_doss) or '-',
					'<a href="{0}" class="consult-icon pull-right" title="Consulter le dossier"></a>'.format(
						reverse('cons_doss', args = [d.pk])
					)
				) for d in filtr_doss(request)]

				# J'envoie le tableau des dossiers filtrés.
				output = HttpResponse(
					json.dumps({ 'success' : { 'datatable' : t_doss}}), content_type = 'application/json'
				)

	return output

'''
Cette vue permet d'afficher la page de consultation d'un dossier ou de traiter une action.
request : Objet requête
'''
@verif_acc
@nett_f
@csrf_exempt
def cons_doss(request, _d) :

	# Imports
	from app.forms.gestion_dossiers import AjouterPrestataire
	from app.forms.gestion_dossiers import ChoisirPrestation
	from app.forms.gestion_dossiers import GererArrete
	from app.forms.gestion_dossiers import GererDemandeVersement
	from app.forms.gestion_dossiers import GererDossier_Reglementations
	from app.forms.gestion_dossiers import GererFacture
	from app.forms.gestion_dossiers import GererFinancement
	from app.forms.gestion_dossiers import GererPrestation
	from app.forms.gestion_dossiers import GererPhoto
	from app.forms.gestion_dossiers import RedistribuerPrestation
	from app.functions import dt_fr
	from app.functions import gen_f_ajout_aven
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import init_pg_cons
	from app.functions import obt_mont
	from app.functions import obt_pourc
	from app.functions import rempl_fich_log
	from app.functions import suppr
	from app.models import TArretesDossier
	from app.models import TDossier
	from app.models import TDossierGeom
	from app.models import TFacture
	from app.models import TPhoto
	from app.models import TPrestation
	from app.models import TPrestationsDossier
	from app.models import TTypesGeomTypeDossier
	from app.sql_views import VDemandeVersement
	from app.sql_views import VFinancement
	from app.sql_views import VSuiviDossier
	from app.sql_views import VSuiviPrestationsDossier
	from django.contrib.gis import geos
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from django.template.context_processors import csrf
	from styx.settings import MEDIA_URL
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TDossier.
	o_doss = get_object_or_404(TDossier, pk = _d)

	if request.method == 'GET' :

		# Je vérifie le droit de lecture.
		ger_droits(request.user, o_doss)

		# Je désigne l'onglet actif du navigateur à onglets relatif à un dossier.
		if 'tab_doss' not in request.session :
			request.session['tab_doss'] = ['#ong_doss', -1]
		request.session['tab_doss'][1] += 1
		if request.session['tab_doss'][1] > 0 :
			del request.session['tab_doss']

		# Je définis si le montant du dossier est en HT ou en TTC.
		ht_ou_ttc = 'HT'
		if o_doss.est_ttc_doss == True :
			ht_ou_ttc = 'TTC'

		# Je pointe vers l'objet VSuiviDossier.
		o_suivi_doss = VSuiviDossier.objects.get(id_doss = o_doss.pk)

		# Je prépare l'onglet "Caractéristiques".
		t_attrs_doss = {
			'num_doss' : { 'label' : 'Numéro du dossier', 'value' : o_doss },
			'int_doss' : {
				'label' : 'Intitulé du dossier',
				'value' : '''
				<div class="row">
					<div class="col-xs-6">
						<span class="red-color small u">Nature du dossier :</span>
						{0}
						<br/>
						<span class="red-color small u">Type de dossier :</span>
						{1}
					</div>
					<div class="col-xs-6">
						<span class="red-color small u">Territoire ou caractéristique :</span>
						{2}
						<br/>
						<span class="red-color small u">Territoire ou lieu-dit précis :</span>
						{3}
					</div>
				</div>
				'''.format(
					o_doss.id_nat_doss, o_doss.id_type_doss, o_doss.lib_1_doss, o_doss.lib_2_doss
				)
			},
			'id_org_moa' : { 'label' : 'Maître d\'ouvrage', 'value' : o_doss.id_org_moa },
			'id_progr' : { 'label' : 'Programme', 'value' : o_doss.id_progr },
			'num_axe' : { 'label' : 'Axe', 'value' : o_doss.num_axe or '' },
			'num_ss_axe' : { 'label' : 'Sous-axe', 'value' : o_doss.num_ss_axe or '' },
			'num_act' : { 'label' : 'Action', 'value' : o_doss.num_act or '' },
			'id_nat_doss' : { 'label' : 'Nature du dossier', 'value' : o_doss.id_nat_doss },
			'id_type_doss' : { 'label' : 'Type de dossier', 'value' : o_doss.id_type_doss },
			'id_techn' : { 'label' : 'Agent responsable', 'value' : o_doss.id_techn },
			'id_sage' : { 'label' : 'SAGE', 'value' : o_doss.id_sage or '' },
			'mont_doss' : {
				'label' : 'Montant {0} du dossier présenté au CD GEMAPI (en €)'.format(ht_ou_ttc),
				'value' : obt_mont(o_doss.mont_doss)
			},
			'mont_suppl_doss' : {
				'label' : 'Dépassement {0} du dossier (en €)'.format(ht_ou_ttc),
				'value' : obt_mont(o_doss.mont_suppl_doss)
			},
			'mont_tot_doss' : {
				'label' : 'Montant {0} total du dossier (en €)'.format(ht_ou_ttc),
				'value' : obt_mont(o_suivi_doss.mont_tot_doss)
			},
			'id_av' : { 'label' : 'État d\'avancement', 'value' : o_doss.id_av },
			'dt_delib_moa_doss' : { 
				'label' : 'Date de délibération au maître d\'ouvrage', 'value' : dt_fr(o_doss.dt_delib_moa_doss) or ''
			},
			'id_av_cp' : { 'label' : 'Avis du comité de programmation - CD GEMAPI', 'value' : o_doss.id_av_cp },
			'dt_av_cp_doss' : { 
				'label' : 'Date de l\'avis du comité de programmation', 'value' : dt_fr(o_doss.dt_av_cp_doss) or ''
			},
			'chem_pj_doss' : {
				'label' : 'Consulter le fichier scanné du mémoire technique',
				'value' : o_doss.chem_pj_doss,
				'pdf' : True 
			},
			'comm_doss' : { 'label' : 'Commentaire', 'value' : o_doss.comm_doss or '' }
		}

		# J'initialise le tableau des dossiers de la famille.
		t_doss_fam = [{
			'num_doss' : d,
			'int_doss' : '{0} - {1} - {2} - {3}'.format(d.id_nat_doss, d.id_type_doss, d.lib_1_doss, d.lib_2_doss),
			'id_org_moa' : d.id_org_moa,
			'dt_delib_moa_doss' : dt_fr(d.dt_delib_moa_doss) or '-',
			'pk' : d.pk
		} for d in TDossier.objects.filter(id_fam = o_doss.id_fam).exclude(pk = o_doss.pk)]
		
		# J'initialise le tableau des financements du dossier.
		t_fin = [{
			'n_org' : f.id_org_fin.n_org,
			'mont_elig_fin' : obt_mont(f.mont_elig_fin) or '-',
			'pourc_elig_fin' : obt_pourc(f.pourc_elig_fin) or '-',
			'mont_part_fin' : obt_mont(f.mont_part_fin),
			'pourc_glob_fin' : obt_pourc(f.pourc_glob_fin),
			'dt_deb_elig_fin' : dt_fr(f.dt_deb_elig_fin) or '-',
			'dt_fin_elig_fin' : dt_fr(f.dt_fin_elig_fin) or '-',
			'mont_rad' : obt_mont(f.mont_rad),
			'pk' : f.pk
		} for f in VFinancement.objects.filter(id_doss = o_doss)]

		# Je complète le tableau des financements du dossier si besoin.
		if o_suivi_doss.mont_raf > 0 :
			t_fin.append({
				'n_org' : 'Autofinancement - {0}'.format(o_doss.id_org_moa),
				'mont_elig_fin' : '-',
				'pourc_elig_fin' : '-',
				'mont_part_fin' : obt_mont(o_suivi_doss.mont_raf),
				'pourc_glob_fin' : obt_pourc(o_suivi_doss.mont_raf / o_suivi_doss.mont_doss * 100),
				'dt_deb_elig_fin' : '-',
				'dt_fin_elig_fin' : '-',
				'mont_rad' : '-',
			})

		# Je trie le tableau des financements par financeurs.
		t_fin = sorted(t_fin, key = lambda l : l['n_org'])

		# J'initialise le tableau des prestations.
		t_prest = []
		t_prest_sum = [0, 0, 0, 0, 0]
		for p in VSuiviPrestationsDossier.objects.filter(id_doss = o_doss) :

			if ht_ou_ttc == 'TTC' :
				mont_fact_sum = p.mont_ttc_fact_sum
			else :
				mont_fact_sum = p.mont_ht_fact_sum

			t_prest.append({
				'n_org' : p.id_prest.id_org_prest,
				'mont_prest_doss' : obt_mont(p.mont_prest_doss),
				'nb_aven' : p.nb_aven,
				'mont_aven_sum' : obt_mont(p.mont_aven_sum),
				'mont_fact_sum' :  obt_mont(mont_fact_sum),
				'mont_raf' : obt_mont(p.mont_raf),
				'pk' : p.pk
			})

			t_prest_sum[0] += p.mont_prest_doss
			t_prest_sum[1] += p.nb_aven
			t_prest_sum[2] += p.mont_aven_sum
			t_prest_sum[3] += mont_fact_sum
			t_prest_sum[4] += p.mont_raf

		for i in range(0, len(t_prest_sum)) :
			if i != 1 :
				t_prest_sum[i] = obt_mont(t_prest_sum[i])

		# Je stocke le jeu de données des prestations du maître d'ouvrage du dossier.
		qs_prest_moa_doss = TPrestation.objects.filter(
			tprestationsdossier__id_doss__id_org_moa = o_doss.id_org_moa
		).exclude(tprestationsdossier__id_doss = o_doss).distinct()
		
		# J'initialise le tableau des prestations du maître d'ouvrage du dossier.
		t_prest_moa_doss = []
		for pmd in qs_prest_moa_doss :

			# Je vérifie si je peux choisir la prestation courante pour une redistribution.
			peut_ch = True
			for dp in TPrestationsDossier.objects.filter(id_prest = pmd.pk) :
				ht_ou_ttc_dp = 'HT'
				if dp.id_doss.est_ttc_doss == True :
					ht_ou_ttc_dp = 'TTC'
				if ht_ou_ttc != ht_ou_ttc_dp :
					peut_ch = False

			# J'initialise le contenu de la dernière balise <td/>.
			dern_td = ''
			if peut_ch == True :
				dern_td = '''
				<span action="?action=afficher-form-redistribution-prestation&prestation={0}" 
				class="choose-icon pointer pull-right" title="Choisir la prestation"></span>
				'''.format(pmd.pk)

			lg = '''
			<tr>
				<td>{0}</td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
				<td>{4}</td>
				<td>{5}</td>
			</tr>
			'''.format(
				pmd.id_org_prest.n_org, 
				pmd.int_prest, 
				dt_fr(pmd.dt_notif_prest), 
				obt_mont(pmd.mont_prest), 
				', '.join([(dp.id_doss.num_doss) for dp in TPrestationsDossier.objects.filter(id_prest = pmd).order_by(
					'id_doss'
				)]),
				dern_td
			)
			t_prest_moa_doss.append(lg)

		# J'initialise le tableau des factures.
		t_fact = []
		mont_fact_sum = 0
		for f in TFacture.objects.filter(id_doss = o_doss) :

			if ht_ou_ttc == 'TTC' :
				mont_fact = f.mont_ttc_fact
			else :
				mont_fact = f.mont_ht_fact

			t_fact.append({
				'id_prest' : f.id_prest,
				'num_fact' : f.num_fact,
				'dt_mand_moa_fact' : dt_fr(f.dt_mand_moa_fact),
				'mont_fact' : obt_mont(mont_fact),
				'num_mandat_fact' : f.num_mandat_fact,
				'num_bord_fact' : f.num_bord_fact,
				'suivi_fact' : f.suivi_fact,
				'pk' : f.pk
			})

			mont_fact_sum += mont_fact

		# J'initialise le tableau des demandes de versements.
		t_ddv = []
		mont_ddv_sum = 0
		for d in VDemandeVersement.objects.filter(id_doss = o_doss) :

			if ht_ou_ttc == 'TTC' :
				mont_ddv = d.mont_ttc_ddv
				map_ddv = d.map_ttc_ddv
			else :
				mont_ddv = d.mont_ht_ddv
				map_ddv = d.map_ht_ddv

			t_ddv.append({
				'id_org_fin' : d.id_org_fin,
				'mont_ddv' : obt_mont(mont_ddv),
				'dt_ddv' : dt_fr(d.dt_ddv),
				'dt_vers_ddv' : dt_fr(d.dt_vers_ddv) or '-',
				'map_ddv' : obt_mont(map_ddv),
				'id_type_vers' : d.id_type_vers,
				'pk' : d.pk
			})

			mont_ddv_sum += mont_ddv

		# J'initialise le tableau des arrêtés du dossier.
		t_arr = [{
			'id_type_decl' : a.id_type_decl,
			'id_type_av_arr' : a.id_type_av_arr,
			'num_arr' : a.num_arr or '-',
			'dt_sign_arr' : dt_fr(a.dt_sign_arr) or '-',
			'dt_lim_encl_trav_arr' : dt_fr(a.dt_lim_encl_trav_arr) or '-',
			'pk' : a.pk
		} for a in TArretesDossier.objects.filter(id_doss = o_doss).order_by('id_type_decl')]

		# J'initialise le tableau des photos du dossier.
		t_ph = [{
			'id_doss' : p.id_doss.pk,
			'chem_ph' : p.chem_ph,
			'int_ph' : p.int_ph,
			'int_ppv_ph' : p.id_ppv_ph,
			'dt_pv_ph' : dt_fr(p.dt_pv_ph),
			'pk' : p.pk
		} for p in TPhoto.objects.filter(id_doss = o_doss).order_by('-dt_pv_ph')]

		# J'initialise le tableau des géométries du dossier.
		qs_geom_doss = TDossierGeom.objects.filter(id_doss = o_doss)
		t_geom_doss = []
		for g in qs_geom_doss :
			if g.geom_pol :
				la_geom = geos.GEOSGeometry(g.geom_pol)
			if g.geom_lin :
				la_geom = geos.GEOSGeometry(g.geom_lin)
			if g.geom_pct :
				la_geom = geos.GEOSGeometry(g.geom_pct)
			t_geom_doss.append(la_geom.geojson)
			
		# J'initialise les types de géométries autorisés.
		qs_type_geom_doss = TTypesGeomTypeDossier.objects.filter(id_type_doss = o_doss.id_type_doss)
		t_types_geom_doss = [tg.id_type_geom.int_type_geom for tg in qs_type_geom_doss]

		# J'instancie des objets "formulaire".
		f_ajout_fin = GererFinancement(prefix = 'GererFinancement', k_doss = o_doss)
		f_ajout_prest = GererPrestation(prefix = 'GererPrestation', k_doss = o_doss)
		f_ch_prest = ChoisirPrestation(prefix = 'ChoisirPrestation', k_org_moa = o_doss.id_org_moa)
		f_ajout_fact = GererFacture(prefix = 'GererFacture', k_doss = o_doss)
		f_ajout_ddv = GererDemandeVersement(prefix = 'GererDemandeVersement', k_doss = o_doss)
		f_ajout_arr = GererArrete(prefix = 'GererArrete', k_doss = o_doss)
		f_modif_doss_regl = GererDossier_Reglementations(prefix = 'GererDossier', instance = o_doss)
		f_ajout_ph = GererPhoto(prefix = 'GererPhoto', k_doss = o_doss)
		f_ajout_org_prest = AjouterPrestataire(prefix = 'AjouterPrestataire')

		# J'initialise le gabarit de chaque champ de chaque formulaire.
		t_ajout_fin = init_f(f_ajout_fin)
		t_ajout_prest = init_f(f_ajout_prest)
		t_ch_prest = init_f(f_ch_prest)
		t_ajout_fact = init_f(f_ajout_fact)
		t_ajout_ddv = init_f(f_ajout_ddv)
		t_ajout_arr = init_f(f_ajout_arr)
		t_ajout_ph = init_f(f_ajout_ph)
		t_ajout_org_prest = init_f(f_ajout_org_prest)

		# Je déclare un tableau qui stocke le contenu de certaines fenêtres modales.
		t_cont_fm = {
			'ajout_arr' : '''
			<form action="{0}" enctype="multipart/form-data" name="f_ajout_arr" method="post" onsubmit="soum_f(event)">
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
				{9}
				<button class="center-block green-btn my-btn" type="submit">Valider</button>
				<div class="form-remark">
					**
					<br/>
					Le numéro de l'arrêté, la date de signature de l'arrêté, la date limite d'enclenchement des travaux
					et le fichier scanné de l'arrêté sont obligatoires si et seulement si l'avancement de l'arrêté est
					« Validé ».
				</div>
			</form>
			'''.format(
				reverse('ajout_arr'),
				csrf(request)['csrf_token'],
				t_ajout_arr['za_num_doss'],
				t_ajout_arr['zl_type_decl'],
				t_ajout_arr['id_type_av_arr'],
				t_ajout_arr['num_arr'],
				t_ajout_arr['dt_sign_arr'],
				t_ajout_arr['dt_lim_encl_trav_arr'],
				t_ajout_arr['chem_pj_arr'],
				t_ajout_arr['comm_arr']
			),
			'ajout_ddv' : '''
			<form action="{0}" enctype="multipart/form-data" name="f_ger_ddv" method="post" onsubmit="soum_f(event)">
				<input name="csrfmiddlewaretoken" type="hidden" value="{1}">
				{2}
				{3}
				{4}
				{5}
				<div class="row">
					<div class="col-sm-6">{6}</div>
					<div class="col-sm-6">{7}</div>
				</div>
				<div class="row">
					<div class="col-sm-6">{8}</div>
					<div class="col-sm-6">{9}</div>
				</div>
				<div class="row">
					<div class="col-sm-6">{10}</div>
					<div class="col-sm-6">{11}</div>
				</div>
				{12}
				{13}
				<button class="center-block green-btn my-btn" type="submit">Valider</button>
			</form>
			'''.format(
				reverse('ajout_ddv'),
				csrf(request)['csrf_token'],
				t_ajout_ddv['za_num_doss'],
				t_ajout_ddv['zl_fin'],
				t_ajout_ddv['id_type_vers'],
				t_ajout_ddv['int_ddv'],
				t_ajout_ddv['mont_ht_ddv'],
				t_ajout_ddv['mont_ttc_ddv'],
				t_ajout_ddv['dt_ddv'],
				t_ajout_ddv['dt_vers_ddv'],
				t_ajout_ddv['mont_ht_verse_ddv'],
				t_ajout_ddv['mont_ttc_verse_ddv'],
				t_ajout_ddv['chem_pj_ddv'],
				t_ajout_ddv['comm_ddv'],
			),
			'ajout_fact' : '''
			<form action="{0}" enctype="multipart/form-data" name="f_ajout_fact" method="post" onsubmit="soum_f(event)">
				<input name="csrfmiddlewaretoken" type="hidden" value="{1}">
				{2}
				{3}
				{4}
				{5}
				<div class="row">
					<div class="col-sm-6">{6}</div>
					<div class="col-sm-6">{7}</div>
				</div>
				{8}
				<div class="row">
					<div class="col-sm-6">{9}</div>
					<div class="col-sm-6">{10}</div>
				</div>
				{11}
				{12}
				{13}
				<button class="center-block green-btn my-btn" type="submit">Valider</button>
			</form>
			'''.format(
				reverse('ajout_fact'),
				csrf(request)['csrf_token'],
				t_ajout_fact['za_num_doss'],
				t_ajout_fact['zl_prest'],
				t_ajout_fact['num_fact'],
				t_ajout_fact['dt_mand_moa_fact'],
				t_ajout_fact['mont_ht_fact'],
				t_ajout_fact['mont_ttc_fact'],
				t_ajout_fact['dt_rec_fact'],
				t_ajout_fact['num_mandat_fact'],
				t_ajout_fact['num_bord_fact'],
				t_ajout_fact['zl_suivi_fact'],
				t_ajout_fact['chem_pj_fact'],
				t_ajout_fact['comm_fact']
			),
			'ajout_fin' : '''
			<form action="{0}" enctype="multipart/form-data" name="f_ajout_fin" method="post" onsubmit="soum_f(event)">
				<input name="csrfmiddlewaretoken" type="hidden" value="{1}">
				{2}
				{3}
				{4}
				<div class="row">
					<div class="col-sm-6">{5}</div>
					<div class="col-sm-6">{6}</div>
				</div>
				{7}
				{8}
				<div class="row">
					<div class="col-sm-6">{9}</div>
					<div class="col-sm-6">{10}</div>
				</div>
				{11}
				<div class="row">
					<div class="col-sm-6">{12}</div>
					<div class="col-sm-6">{13}</div>
				</div>
				{14}
				{15}
				{16}
				<button class="center-block green-btn my-btn" type="submit">Valider</button>
				<div class="form-remark">
					**
					<br/>
					Le montant de l'assiette éligible de la subvention et le pourcentage de l'assiette éligible peuvent
					ne pas être renseignés, mais si l'un d'entre eux est renseigné, l'autre doit l'être également.
					<br/>
					La date de début d'éligibilité doit être renseignée si et seulement si la durée de validité de l'
					aide et/ou la durée de prorogation est/sont supérieure(s) à 0 mois.
					<br/>
					Il est impossible de renseigner un pourcentage de réalisation des travaux tant que le premier 
					acompte n'est pas payé en fonction de celui-ci.
				</div>
			</form>
			'''.format(
				reverse('ajout_fin'),
				csrf(request)['csrf_token'],
				t_ajout_fin['za_num_doss'],
				t_ajout_fin['id_org_fin'],
				t_ajout_fin['num_arr_fin'],
				t_ajout_fin['mont_elig_fin'],
				t_ajout_fin['pourc_elig_fin'],
				t_ajout_fin['mont_part_fin'],
				t_ajout_fin['dt_deb_elig_fin'],
				t_ajout_fin['duree_valid_fin'],
				t_ajout_fin['duree_pror_fin'],
				t_ajout_fin['dt_lim_deb_oper_fin'],
				t_ajout_fin['dt_lim_prem_ac_fin'],
				t_ajout_fin['id_paiem_prem_ac'],
				t_ajout_fin['pourc_real_fin'],
				t_ajout_fin['chem_pj_fin'],
				t_ajout_fin['comm_fin']
			),
			'ajout_org_prest' : '''
			<form action="{0}" name="f_ajout_org_prest" method="post" onsubmit="soum_f(event)">
				<input name="csrfmiddlewaretoken" type="hidden" value="{1}">
				<div class="row">
					<div class="col-sm-6">{2}</div>
					<div class="col-sm-6">{3}</div>
				</div>
				{4}
				{5}
				<button class="center-block green-btn my-btn" type="submit">Valider</button>
			</form>
			'''.format(
				reverse('ajout_org_prest'),
				csrf(request)['csrf_token'],
				t_ajout_org_prest['n_org'],
				t_ajout_org_prest['siret_org_prest'],
				t_ajout_org_prest['num_dep'],
				t_ajout_org_prest['comm_org']
			),
			'ajout_prest' : '''
			{0}
			<div id="za_nvelle_prest">
				<form action="{1}" enctype="multipart/form-data" name="f_ajout_prest" method="post" onsubmit="soum_f(event)">
					<input name="csrfmiddlewaretoken" type="hidden" value="{2}">
					{3}
					<div class="row">
						<div class="col-xs-6">{4}</div>
						<div class="col-xs-6" style="margin-top: 20px;">
							<span class="add-company-icon icon-link" id="bt_ajout_org_prest">Ajouter un prestataire</span>
						</div>
					</div>
					{5}
					{6}
					{7}
					<div class="row">
						<div class="col-sm-6">{8}</div>
						<div class="col-sm-6">{9}</div>
					</div>
					{10}
					{11}
					{12}
					<button class="center-block green-btn my-btn" type="submit">Valider</button>
				</form>
			</div>
			<div id="za_red_prest_etape_1" style="display: none;">
				<form action="?action=filtrer-prestations" name="f_ch_prest" method="post">
					<input name="csrfmiddlewaretoken" type="hidden" value="{13}">
					<fieldset class="my-fieldset" style="padding-bottom: 0;">
						<legend>Rechercher par</legend>
						<div>
							{14}
							{15}
							{16}
						</div>
					</fieldset>
				</form>
				<div class="br"></div>
				<span class="my-label">
					<span class="u">Étape 1 :</span> Choisir une prestation dont le montant total est en {17}
				</span>
				<div class="my-table" id="t_ch_prest">
					<table>
						<thead>
							<tr>
								<th>Prestataire</th>
								<th>Intitulé</th>
								<th>Date de notification</th>
								<th>Montant (en €)</th>
								<th>Dossier(s)</th>
								<th></th>
							</tr>
						</thead>
						<tbody>{18}</tbody>
					</table>
				</div>
			</div>
			'''.format(
				t_ajout_prest['rb_prest_exist'],
				reverse('ajout_prest'),
				csrf(request)['csrf_token'],
				t_ajout_prest['za_num_doss'],
				t_ajout_prest['zsac_siret_org_prest'],
				t_ajout_prest['int_prest'],
				t_ajout_prest['ref_prest'],
				t_ajout_prest['mont_prest'],
				t_ajout_prest['dt_notif_prest'],
				t_ajout_prest['dt_fin_prest'],
				t_ajout_prest['id_nat_prest'],
				t_ajout_prest['chem_pj_prest'],
				t_ajout_prest['comm_prest'],
				csrf(request)['csrf_token'],
				t_ch_prest['zl_progr'],
				t_ch_prest['za_org_moa'],
				t_ch_prest['zl_org_prest'],
				ht_ou_ttc,
				'\n'.join(t_prest_moa_doss)
			),
			'ajout_ph' : '''
			<form action="{0}" enctype="multipart/form-data" name="f_ajout_ph" method="post" onsubmit="soum_f(event)">
				<input name="csrfmiddlewaretoken" type="hidden" value="{1}">
				{2}
				<div class="row">
					<div class="col-sm-6">{3}</div>
					<div class="col-sm-6">{4}</div>
				</div>
				{5}
				{6}
				{7}
				<button class="center-block green-btn my-btn" type="submit">Valider</button>
			</form>
			'''.format(
				reverse('ajout_ph'),
				csrf(request)['csrf_token'],
				t_ajout_ph['za_num_doss'],
				t_ajout_ph['int_ph'],
				t_ajout_ph['descr_ph'],
				t_ajout_ph['id_ppv_ph'],
				t_ajout_ph['dt_pv_ph'],
				t_ajout_ph['chem_ph']
			)
		}

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('ajout_arr', 'Ajouter un arrêté', t_cont_fm['ajout_arr']),
			init_fm('ajout_aven', 'Ajouter un avenant'),
			init_fm('ajout_fact', 'Ajouter une facture', t_cont_fm['ajout_fact']),
			init_fm('ajout_fin', 'Ajouter un organisme financier', t_cont_fm['ajout_fin']),
			init_fm('ajout_org_prest', 'Ajouter un prestataire', t_cont_fm['ajout_org_prest']),
			init_fm('ajout_ph', 'Ajouter une photo', t_cont_fm['ajout_ph']),
			init_fm('ajout_prest', 'Ajouter/relier une prestation', t_cont_fm['ajout_prest']),
			init_fm('cons_ph', 'Consulter une photo'),
			init_fm('ger_ddv', 'Ajouter une demande de versement', t_cont_fm['ajout_ddv']),
			init_fm('modif_carto', 'Modifier un dossier'),
			init_fm('modif_doss_regl', 'Modifier un dossier'),
			init_fm('suppr_ph', 'Supprimer une photo')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/cons_doss.html',
			{
				'd' : o_doss,
				'f_modif_doss_regl' : init_f(f_modif_doss_regl),
				'forbidden' : ger_droits(request.user, o_doss, False, False),
				'ht_ou_ttc' : ht_ou_ttc,
				'mont_ddv_sum' : mont_ddv_sum,
				'mont_ddv_sum_str' : obt_mont(mont_ddv_sum),
				'mont_doss' : obt_mont(o_doss.mont_doss),
				'mont_fact_sum' : mont_fact_sum,
				'mont_fact_sum_str' : obt_mont(mont_fact_sum),
				'mont_rae' : obt_mont(o_suivi_doss.mont_rae),
				'mont_suppl_doss' : obt_mont(o_doss.mont_suppl_doss),
				't_arr' : t_arr,
				't_attrs_doss' : init_pg_cons(t_attrs_doss),
				't_ddv' : t_ddv,
				't_doss_fam' : t_doss_fam,
				't_fact' : t_fact,
				't_fin' : t_fin,
				't_fm' : t_fm,
				't_geom_doss' : t_geom_doss,
				't_ph' : t_ph,
				't_prest' : t_prest,
				't_prest_length' : len(t_prest),
				't_prest_sum' : t_prest_sum,
				't_types_geom_doss' : t_types_geom_doss,
				'title' : 'Consulter un dossier'
			}
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois supprimer une photo.
			if get_action == 'supprimer-photo' :
				if request.GET['photo'] :
					output = HttpResponse(suppr(reverse('suppr_ph', args = [request.GET['photo']])))

			# Je traite le cas où je dois consulter une photo.
			if get_action == 'consulter-photo' :
				if request.GET['photo'] :

					# Je vérifie l'existence d'un objet TPhoto.
					o_ph = get_object_or_404(TPhoto, pk = request.GET['photo'])

					# Je vérifie le droit de lecture.
					ger_droits(request.user, o_ph.id_doss)

					# Je prépare le volet de consultation de la photo.
					t_attrs_ph = {
						'id_doss' : { 'label' : 'Numéro du dossier', 'value' : o_ph.id_doss },
						'int_ph' : { 'label' : 'Intitulé de la photo', 'value' : o_ph.int_ph },
						'descr_ph' : { 'label' : 'Description', 'value' : o_ph.descr_ph or '' },
						'id_ppv_ph' : { 'label' : 'Période de prise de vue', 'value' : o_ph.id_ppv_ph },
						'dt_pv_ph' : { 'label' : 'Date de prise de vue', 'value' : dt_fr(o_ph.dt_pv_ph) }
					}
					
					t_attrs_ph = init_pg_cons(t_attrs_ph)

					output = HttpResponse(
					'''
					<div style="margin-bottom: -20px;">
						<div class="attribute-wrapper">
							<span class="attribute-label">Visualisation</span>
							<img src="{0}{1}" width="100%">
						</div>
						{2}
						<div class="row">
							<div class="col-sm-6">{3}</div>
							<div class="col-sm-6">{4}</div>
						</div>
						<div class="row">
							<div class="col-sm-6">{5}</div>
							<div class="col-sm-6">{6}</div>
						</div>
					</div>
					'''.format(
						MEDIA_URL,
						o_ph.chem_ph,
						t_attrs_ph['id_doss'],
						t_attrs_ph['int_ph'],
						t_attrs_ph['descr_ph'],
						t_attrs_ph['id_ppv_ph'],
						t_attrs_ph['dt_pv_ph']
					))

			# Je traite le cas où je dois modifier le commentaire de l'onglet "Réglementations".
			if get_action == 'modifier-reglementation' :

				# Je vérifie le droit d'écriture.
				ger_droits(request.user, o_doss, False)

				# Je soumets le formulaire.
				f_modif_doss_regl = GererDossier_Reglementations(
					request.POST, instance = o_doss, prefix = 'GererDossier'
				)

				if f_modif_doss_regl.is_valid() :

					# Je modifie l'instance TDossier.
					o_doss_regl_modif = f_modif_doss_regl.save(commit = False)
					o_doss_regl_modif.save()

					# J'affiche le message de succès.
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'Le dossier {0} a été mis à jour avec succès.'.format(o_doss_regl_modif),
							'redirect' : reverse('cons_doss', args = [o_doss_regl_modif.pk])
						}}), 
						content_type = 'application/json'
					)

					# Je renseigne l'onglet actif après rechargement de la page.
					request.session['tab_doss'] = ['#ong_arr', -1]

					# Je complète le fichier log.
					rempl_fich_log(
						[request.user.pk, request.user, 'U', 'Réglementation d\'un dossier', o_doss_regl_modif.pk]
					)

				else :

					# J'affiche les erreurs.
					t_err = {}
					for k, v in f_modif_doss_regl.errors.items() :
						t_err['GererDossier-{0}'.format(k)] = v
					output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

			# Je traite le cas où je dois afficher le formulaire d'ajout d'un avenant.
			if get_action == 'afficher-form-avenant' :
				if request.GET['prestation'] :

					# Je vérifie l'existence d'un objet TPrestationsDossier.
					o_prest_doss = get_object_or_404(TPrestationsDossier, pk = request.GET['prestation'])

					output = HttpResponse(gen_f_ajout_aven(request, o_prest_doss, reverse('ajout_aven_racc')))

			# Je traite le cas où je dois filtrer les prestations.
			if get_action == 'filtrer-prestations' :

				# Je soumets le formulaire.
				f_ch_prest = ChoisirPrestation(request.POST, prefix = 'ChoisirPrestation')

				if f_ch_prest.is_valid() :

					# Je récupère les données du formulaire valide.
					cleaned_data = f_ch_prest.cleaned_data
					v_progr = cleaned_data.get('zl_progr')
					v_org_prest = cleaned_data.get('zl_org_prest')

					# J'initialise les conditions de la requête.
					t_sql = { 'and' : {}, 'or' : [] }
					if v_progr :
						t_sql['and']['tprestationsdossier__id_doss__id_progr'] = v_progr
					t_sql['and']['tprestationsdossier__id_doss__id_org_moa__id_org_moa'] = o_doss.id_org_moa.pk
					if v_org_prest :
						t_sql['and']['id_org_prest'] = v_org_prest

					# Je stocke le jeu de données des prestations filtrées du maître d'ouvrage du dossier.
					qs_prest_moa_doss_filtr = TPrestation.objects.filter(**t_sql['and']).exclude(
						tprestationsdossier__id_doss = o_doss
					).distinct().order_by('id_org_prest', 'int_prest')

					# Je définis si le montant du dossier est en HT ou en TTC.
					ht_ou_ttc = 'HT'
					if o_doss.est_ttc_doss == True :
						ht_ou_ttc = 'TTC'

					# J'initialise le tableau des prestations filtrées du maître d'ouvrage du dossier.
					t_prest_moa_doss_filtr = []
					for pmd in qs_prest_moa_doss_filtr :

						# Je vérifie si je peux choisir la prestation courante pour une redistribution.
						peut_ch = True
						for dp in TPrestationsDossier.objects.filter(id_prest = pmd.pk) :
							ht_ou_ttc_dp = 'HT'
							if dp.id_doss.est_ttc_doss == True :
								ht_ou_ttc_dp = 'TTC'
							if ht_ou_ttc != ht_ou_ttc_dp :
								peut_ch = False

						# J'initialise le contenu de la dernière balise <td/>.
						dern_td = ''
						if peut_ch == True :
							dern_td = '''
							<span action="?action=afficher-form-redistribution-prestation&prestation={0}" 
							class="choose-icon pointer pull-right" title="Choisir la prestation"></span>
							'''.format(pmd.pk)

						t_prest_moa_doss_filtr.append([
							pmd.id_org_prest.n_org, 
							pmd.int_prest, 
							dt_fr(pmd.dt_notif_prest), 
							obt_mont(pmd.mont_prest), 
							', '.join([
								(dp.id_doss.num_doss) for dp in TPrestationsDossier.objects.filter(
									id_prest = pmd
								).order_by('id_doss')
							]),
							dern_td
						])

					# J'envoie le tableau des prestations filtrées.
					output = HttpResponse(
						json.dumps({ 
							'success' : { 'datatable' : t_prest_moa_doss_filtr }
						}), content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs.
					t_err = {}
					for k, v in f_ch_prest.errors.items() :
						t_err['ChoisirPrestation-{0}'.format(k)] = v
					output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

			# Je traite le cas où je dois afficher le formulaire de redistribution des montants d'une prestation.
			if get_action == 'afficher-form-redistribution-prestation' :

				# J'initialise l'identifiant de la prestation (-1 étant un identifiant inexistant).
				v_prest = -1
				if request.GET['prestation'] :
					v_prest = request.GET['prestation']

				# Je vérifie l'existence d'un objet TPrestation.
				o_prest = get_object_or_404(TPrestation, pk = v_prest)

				t_lg = []
				for index, dp in enumerate(TPrestationsDossier.objects.filter(id_prest = o_prest)) :

					# Je pointe vers l'objet VSuiviPrestationsDossier.
					o_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(pk = dp.pk)

					# Je pointe vers l'objet VSuiviDossier.
					o_suivi_doss = VSuiviDossier.objects.get(pk = dp.id_doss.pk)

					# J'instancie un objet "formulaire".
					f_red_prest = RedistribuerPrestation(
						instance = dp, prefix = 'RedistribuerPrestation{0}'.format(index)
					)

					# J'initialise le gabarit de chaque champ du formulaire.
					t_red_prest = init_f(f_red_prest)

					# J'initialise la somme des factures émises selon le mode de taxe du dossier.
					mont_fact_sum = o_suivi_prest_doss.mont_ht_fact_sum
					if o_doss.est_ttc_doss == True :
						mont_fact_sum = o_suivi_prest_doss.mont_ttc_fact_sum

					lg = '''
					<tr>
						<td class="b">{0}</td>
						<td>{1}</td>
						<td>{2}</td>
						<td>{3}</td>
						<td>{4}</td>
					</tr>
					'''.format(
						dp.id_doss.num_doss,
						t_red_prest['mont_prest_doss'],
						obt_mont(o_suivi_prest_doss.mont_aven_sum),
						obt_mont(mont_fact_sum),
						obt_mont(o_suivi_doss.mont_rae)
					)

					# J'empile le tableau des lignes du tableau HTML des dossiers déjà reliés à la prestation que l'on
					# veut redistribuer.
					t_lg.append(lg)

				# Je pointe vers l'objet VSuiviDossier.
				o_suivi_doss = VSuiviDossier.objects.get(pk = o_doss.pk)

				# J'instancie un objet "formulaire".
				f_red_prest = RedistribuerPrestation(prefix = 'RedistribuerPrestation', k_doss = o_doss)

				# J'initialise le gabarit de chaque champ du formulaire.
				t_red_prest = init_f(f_red_prest)

				lg = '''
				<tr style="background-color: #F8B862;">
					<td class="b">{0}</td>
					<td>{1}</td>
					<td>0</td>
					<td>0</td>
					<td>{2}</td>
				</tr>
				'''.format(
					o_doss.num_doss,
					t_red_prest['mont_prest_doss'],
					obt_mont(o_suivi_doss.mont_rae)
				)

				# J'empile le tableau des lignes du tableau HTML de redistribution d'une prestation en ajoutant la
				# ligne relative au dossier que l'on souhaite relier à la prestation choisie.
				t_lg.append(lg)

				# J'envoie le formulaire de redistribution d'une prestation.
				output = HttpResponse(
					'''
					<div id="za_red_prest_etape_2" style="margin-top: 20px;">
						<span class="my-label">
							<span class="u">Étape 2 :</span> Redistribuer les montants dédiés de cette prestation
						</span>
						<form action="?action=relier-prestation" name="f_red_prest" method="post" onsubmit="soum_f(event)">
							<input name="csrfmiddlewaretoken" type="hidden" value="{0}">
							<div style="margin-bottom: 20px;">
								<div class="my-table" id="t_red_prest">
									<table>
										<thead>
											<tr>
												<th>N° du dossier</th>
												<th>Montant de la prestation (en €)</th>
												<th>Somme des avenants (en €)</th>
												<th>Somme des factures émises (en €)</th>
												<th>Reste à engager pour le dossier (en €)</th>
											</tr>
										</thead>
										<tbody>{1}</tbody>
									</table>
								</div>
								<span class="form-grouped-error"></span>
							</div>
							<button class="center-block green-btn my-btn" type="submit">Valider</button>
						</form>
					</div>
					'''.format(csrf(request)['csrf_token'], '\n'.join(t_lg))
				)

				# Je stocke en mémoire l'identifiant de la prestation valide.
				request.session['relier-prestation'] = o_prest.pk

			# Je traite le cas où je dois relier une prestation à un autre dossier.
			if get_action == 'relier-prestation' :

				# J'initialise l'identifiant de la prestation (-1 étant un identifiant inexistant).
				v_prest = -1
				if 'relier-prestation' in request.session :
					v_prest = request.session['relier-prestation']

				# Je vérifie l'existence d'un objet TPrestation.
				o_prest = get_object_or_404(TPrestation, pk = v_prest)

				# Je vérifie le droit d'écriture.
				ger_droits(request.user, o_doss, False)

				# J'initialise le montant global de la prestation après redistribution.
				mont_prest_doss_sum = 0

				# J'initialise le tableau des erreurs tous formulaires confondus.
				t_err = {}

				# J'initialise le tableau des instances TPrestationsDossier à créer ou à modifier.
				t_inst_prest_doss = []

				for index, dp in enumerate(TPrestationsDossier.objects.filter(id_prest = o_prest)) :

					# Je soumets le formulaire.
					f_red_prest = RedistribuerPrestation(
						request.POST, instance = dp, prefix = 'RedistribuerPrestation{0}'.format(index)
					)

					if f_red_prest.is_valid() :

						# Je récupère les données du formulaire valide.
						cleaned_data = f_red_prest.cleaned_data

						# J'ajoute le montant du couple prestation/dossier courant.
						mont_prest_doss_sum += cleaned_data.get('mont_prest_doss')

						# J'empile le tableau des instances TPrestationsDossier.
						t_inst_prest_doss.append(f_red_prest.save(commit = False))

					else :

						# J'empile le tableau des erreurs.
						for k, v in f_red_prest.errors.items() :
							t_err['RedistribuerPrestation{0}-{1}'.format(index, k)] = v

				# Je soumets le formulaire.
				f_red_prest = RedistribuerPrestation(
					request.POST, prefix = 'RedistribuerPrestation', k_doss = o_doss, k_prest = o_prest
				)

				if f_red_prest.is_valid() :

					# Je récupère les données du formulaire valide.
					cleaned_data = f_red_prest.cleaned_data

					# J'ajoute le montant souhaité pour le futur couple prestation/dossier.
					mont_prest_doss_sum += cleaned_data.get('mont_prest_doss')

					# J'empile le tableau des instances TPrestationsDossier.
					t_inst_prest_doss.append(f_red_prest.save(commit = False))

				else :

					# J'empile le tableau des erreurs.
					for k, v in f_red_prest.errors.items() :
						t_err['RedistribuerPrestation-{0}'.format(k)] = v
				
				if len(t_err) > 0 :

					# J'affiche les erreurs.
					output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

				else :
					if mont_prest_doss_sum == o_prest.mont_prest :

						# Je créé ou modifie chaque instance TPrestationsDossier.
						for i in range(0, len(t_inst_prest_doss)) :
							t_inst_prest_doss[i].save()

						# J'affiche le message de succès.
						output = HttpResponse(
							json.dumps({ 'success' : {
								'message' : '''
								La prestation « {0} » a été reliée avec succès au dossier {1}.
								'''.format(o_prest, o_doss),
								'modal' : 'ajout_prest',
								'redirect' : reverse('cons_doss', args = [o_doss.pk])
							}}), 
							content_type = 'application/json'
						)

						# Je renseigne l'onglet actif après rechargement de la page.
						request.session['tab_doss'] = ['#ong_prest', -1]

						if 'relier-prestation' in request.session :
							del request.session['relier-prestation']

						# Je complète le fichier log.
						rempl_fich_log([
							request.user.pk,
							request.user,
							'C',
							'Couple prestation/dossier (reliage)',
							t_inst_prest_doss[-1].pk
						])

					else :

						# J'affiche l'erreur groupée.
						output = HttpResponse(
							json.dumps({ 'errors' : ['La somme des montants n\'est pas égale à {0} €.'.format(obt_mont(
								o_prest.mont_prest
							))] }), 
							content_type = 'application/json'
						)

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'un financement.
request : Objet requête
'''
@verif_acc
def ajout_fin(request) :

	# Imports
	from app.forms.gestion_dossiers import GererFinancement
	from app.functions import ger_droits
	from app.functions import rempl_fich_log
	from app.models import TDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json

	output = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		try :
			o_doss_droit = TDossier.objects.get(num_doss = request.POST.get('GererFinancement-za_num_doss'))
		except :
			o_doss_droit = None
		if o_doss_droit :
			ger_droits(request.user, o_doss_droit, False)

		# Je soumets le formulaire.
		f_ajout_fin = GererFinancement(request.POST, request.FILES, prefix = 'GererFinancement')

		if f_ajout_fin.is_valid() :

			# Je créé la nouvelle instance TFinancement.
			o_nv_fin = f_ajout_fin.save(commit = False)
			o_nv_fin.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : '''
					L\'organisme financeur « {0} » a été ajouté avec succès au plan de financement du dossier {1}.
					'''.format(o_nv_fin.id_org_fin, o_nv_fin.id_doss),
					'redirect' : reverse('cons_doss', args = [o_nv_fin.id_doss.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_doss'] = ['#ong_fin', -1]

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'C', 'Financement', o_nv_fin.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_fin.errors.items() :
				t_err['GererFinancement-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'un financement ou de traiter le formulaire de mise à jour d'un
financement.
request : Objet requête
_f : Identifiant d'un financement
'''
@verif_acc
@nett_f
def modif_fin(request, _f) :

	# Imports
	from app.forms.gestion_dossiers import GererFinancement
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import rempl_fich_log
	from app.models import TFinancement
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TFinancement.
	o_fin = get_object_or_404(TFinancement, pk = _f)

	# Je vérifie le droit d'écriture.
	ger_droits(request.user, o_fin.id_doss, False)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_fin = GererFinancement(instance = o_fin, prefix = 'GererFinancement')

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_fin', 'Modifier un financement')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/modif_fin.html',
			{ 'f' : o_fin, 'f_modif_fin' : init_f(f_modif_fin), 't_fm' : t_fm, 'title' : 'Modifier un financement' }
		)

	else :

		# Je soumets le formulaire.
		f_modif_fin = GererFinancement(request.POST, request.FILES, instance = o_fin, prefix = 'GererFinancement')

		if f_modif_fin.is_valid() :

			# Je modifie l'instance TFinancement.
			o_fin_modif = f_modif_fin.save(commit = False)
			o_fin_modif.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'Le plan de financement du dossier {0} a été mis à jour avec succès.'.format(
						o_fin_modif.id_doss
					),
					'redirect' : reverse('cons_fin', args = [o_fin_modif.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'U', 'Financement', o_fin_modif.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_modif_fin.errors.items() :
				t_err['GererFinancement-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de consultation d'un financement.
request : Objet requête
_f : Identifiant d'un financement
'''
@verif_acc
def cons_fin(request, _f) :

	# Imports
	from app.functions import init_pg_cons
	from app.functions import dt_fr
	from app.functions import ger_droits
	from app.functions import obt_mont
	from app.functions import obt_pourc
	from app.models import TFinancement
	from app.sql_views import VFinancement
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TFinancement.
	o_fin = get_object_or_404(TFinancement, pk = _f)

	if request.method == 'GET' :

		# Je vérifie le droit de lecture.
		ger_droits(request.user, o_fin.id_doss)

		o_suivi_fin = VFinancement.objects.get(pk = o_fin.pk)

		# Je définis si le montant du financement est en HT ou en TTC.
		ht_ou_ttc = 'HT'
		if o_fin.id_doss.est_ttc_doss == True :
			ht_ou_ttc = 'TTC'

		# Je prépare le volet de consultation du financement.
		t_attrs_fin = {
			'id_doss' : { 'label' : 'Numéro du dossier', 'value' : o_fin.id_doss },
			'id_org_fin' : { 'label' : 'Organisme financeur', 'value' : o_fin.id_org_fin },
			'num_arr_fin' : { 'label' : 'Numéro de l\'arrêté ou convention', 'value' : o_fin.num_arr_fin },
			'mont_elig_fin' : {
				'label' : 'Montant {0} de l\'assiette éligible de la subvention (en €)'.format(ht_ou_ttc),
				'value' : obt_mont(o_fin.mont_elig_fin) or ''
			},
			'pourc_elig_fin' : {
				'label' : 'Pourcentage de l\'assiette éligible',
				'value' : obt_pourc(o_fin.pourc_elig_fin) or ''
			},
			'pourc_glob_fin' : {
				'label' : 'Pourcentage global',
				'value' : obt_pourc(o_suivi_fin.pourc_glob_fin)
			},
			'mont_part_fin' : {
				'label' : 'Montant {0} total de la participation (en €)'.format(ht_ou_ttc),
				'value' : obt_mont(o_fin.mont_part_fin)
			},
			'dt_deb_elig_fin' : {
				'label' : 'Date de début d\'éligibilité', 'value' : dt_fr(o_fin.dt_deb_elig_fin) or ''
			},
			'dt_fin_elig_fin' : {
				'label' : 'Date de fin d\'éligibilité', 'value' : dt_fr(o_suivi_fin.dt_fin_elig_fin) or ''
			},
			'duree_valid_fin' : { 
				'label' : 'Durée de validité de l\'aide (en mois)', 'value' : o_fin.duree_valid_fin
			},
			'duree_pror_fin' : {
				'label' : 'Durée de la prorogation (en mois)', 'value' : o_fin.duree_pror_fin
			},
			'dt_lim_deb_oper_fin' : {
				'label' : 'Date limite du début de l\'opération', 'value' : dt_fr(o_fin.dt_lim_deb_oper_fin) or ''
			},
			'dt_lim_prem_ac_fin' : {
				'label' : 'Date limite du premier acompte', 'value' : dt_fr(o_fin.dt_lim_prem_ac_fin) or ''
			},
			'id_paiem_prem_ac' : {
				'label' : 'Premier acompte payé en fonction de', 'value' : o_fin.id_paiem_prem_ac or ''
			},
			'pourc_real_fin' : {
				'label' : 'Pourcentage de réalisation des travaux', 'value' : obt_pourc(o_fin.pourc_real_fin) or ''
			},
			'chem_pj_fin' : {
				'label' : 'Consulter l\'arrêté de subvention', 'value' : o_fin.chem_pj_fin, 'pdf' : True
			},
			'comm_fin' : { 'label' : 'Commentaire', 'value' : o_fin.comm_fin or '' }
		} 

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/cons_fin.html',
			{
				'f' : o_fin,
				'forbidden' : ger_droits(request.user, o_fin.id_doss, False, False),
				't_attrs_fin' : init_pg_cons(t_attrs_fin),
				'title' : 'Consulter un financement'
			}
		)

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'une prestation.
request : Objet requête
'''
@verif_acc
def ajout_prest(request) :

	# Imports
	from app.forms.gestion_dossiers import GererPrestation
	from app.functions import ger_droits
	from app.functions import rempl_fich_log
	from app.models import TDossier
	from app.models import TPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json

	output = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		try :
			o_doss_droit = TDossier.objects.get(num_doss = request.POST.get('GererPrestation-za_num_doss'))
		except :
			o_doss_droit = None
		if o_doss_droit :
			ger_droits(request.user, o_doss_droit, False)

		# Je soumets le formulaire.
		f_ajout_prest = GererPrestation(request.POST, request.FILES, prefix = 'GererPrestation')

		if f_ajout_prest.is_valid() :

			# Je récupère les données du formulaire valide.
			cleaned_data = f_ajout_prest.cleaned_data
			v_num_doss = cleaned_data.get('za_num_doss')

			# Je créé la nouvelle instance TPrestation.
			o_nvelle_prest = f_ajout_prest.save(commit = False)
			o_nvelle_prest.save()

			# Je fais le lien avec la table TPrestationsDossier.
			o_nvelle_prest_doss = TPrestationsDossier.objects.create(
				id_doss = TDossier.objects.get(num_doss = v_num_doss),
				id_prest = o_nvelle_prest,
				mont_prest_doss = o_nvelle_prest.mont_prest
			)

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : '''
					La prestation « {0} » a été ajoutée avec succès au dossier {1}.
					'''.format(o_nvelle_prest, v_num_doss),
					'redirect' : reverse('cons_doss', args = [o_nvelle_prest_doss.id_doss.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_doss'] = ['#ong_prest', -1]

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'C', 'Prestation', o_nvelle_prest.pk])
			rempl_fich_log(
				[request.user.pk, request.user, 'C', 'Couple prestation/dossier (ajout)', o_nvelle_prest_doss.pk]
			)

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_prest.errors.items() :
				t_err['GererPrestation-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'une prestation ou de traiter le formulaire de mise à jour d'une
prestation.
request : Objet requête
_p : Identifiant d'une prestation
'''
@verif_acc
@nett_f
def modif_prest(request, _pd) :

	# Imports
	from app.forms.gestion_dossiers import GererPrestation
	from app.forms.gestion_dossiers import RedistribuerPrestation
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import obt_mont
	from app.functions import rempl_fich_log
	from app.models import TPrestationsDossier
	from app.sql_views import VSuiviDossier
	from app.sql_views import VSuiviPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from django.template.context_processors import csrf
	import json
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TFacture.
	o_prest = get_object_or_404(TPrestationsDossier, pk = _pd)

	# Je vérifie le droit d'écriture.
	ger_droits(request.user, o_prest.id_doss, False)

	if request.method == 'GET' :

		# Variable globale
		global g_f_modif_prest

		# J'instancie un objet "formulaire".
		f_modif_prest = GererPrestation(instance = o_prest.id_prest, prefix = 'GererPrestation')

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_prest', 'Modifier une prestation')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/modif_prest.html',
			{ 
				'pd' : o_prest, 
				'f_modif_prest' : init_f(f_modif_prest), 
				't_fm' : t_fm, 
				'title' : 'Modifier une prestation'
			}
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois valider la première étape du processus de modification d'une prestation.
			if get_action == 'valider-etape-1' :

				# Je soumets le formulaire.
				f_modif_prest = GererPrestation(
					request.POST, request.FILES, instance = o_prest.id_prest, prefix = 'GererPrestation'
				)

				if f_modif_prest.is_valid() :

					t_lg = []
					for index, dp in enumerate(TPrestationsDossier.objects.filter(id_prest = o_prest.id_prest)) :

						# Je pointe vers l'objet VSuiviPrestationsDossier.
						o_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(pk = dp.pk)

						# Je pointe vers l'objet VSuiviDossier.
						o_suivi_doss = VSuiviDossier.objects.get(pk = dp.id_doss.pk)

						# J'instancie un objet "formulaire".
						f_red_prest = RedistribuerPrestation(
							instance = dp, prefix = 'RedistribuerPrestation{0}'.format(index)
						)

						# J'initialise le gabarit de chaque champ du formulaire.
						t_red_prest = init_f(f_red_prest)

						# J'initialise la somme des factures émises selon le mode de taxe du dossier.
						mont_fact_sum = o_suivi_prest_doss.mont_ht_fact_sum
						if o_suivi_prest_doss.id_doss.est_ttc_doss == True :
							mont_fact_sum = o_suivi_prest_doss.mont_ttc_fact_sum

						lg = '''
						<tr>
							<td class="b">{0}</td>
							<td>{1}</td>
							<td>{2}</td>
							<td>{3}</td>
							<td>{4}</td>
						</tr>
						'''.format(
							dp.id_doss.num_doss,
							t_red_prest['mont_prest_doss'],
							obt_mont(o_suivi_prest_doss.mont_aven_sum),
							obt_mont(mont_fact_sum),
							obt_mont(o_suivi_doss.mont_rae)
						)

						# J'empile le tableau des lignes du tableau HTML des dossiers déjà reliés à la prestation que l'on
						# veut modifier.
						t_lg.append(lg)

					# Je mets en forme le formulaire de l'étape suivante.
					f_suiv = '''
					<form action="?action=valider-etape-2" method="post" name="f_modif_prest_etape_2" onsubmit="soum_f(event)">
						<input name="csrfmiddlewaretoken" type="hidden" value="{0}">
						<fieldset class="my-fieldset">
							<legend>Modifier une prestation (étape 2)</legend>
							<div>
								<div class="my-table" id="t_modif_prest_etape_1_next">
									<table>
										<thead>
											<tr>
												<th>N° du dossier</th>
												<th>Montant de la prestation (en €)</th>
												<th>Somme des avenants (en €)</th>
												<th>Somme des factures émises (en €)</th>
												<th>Reste à engager pour le dossier (en €)</th>
											</tr>
										</thead>
										<tbody>{1}</tbody>
									</table>
								</div>
								<span class="form-grouped-error"></span>
							</div>
							<div class="text-center" style="margin-top: 15px;">
								<button class="green-btn my-btn to-block" id="bt_modif_prest_etape_2_previous" 
								style="display: inline-block;">Revenir à l'étape précédente</button>
								<button class="green-btn my-btn" style="display: inline-block;" type="submit">Valider</button>
							</div>
						</fieldset>
					</form>
					'''.format(csrf(request)['csrf_token'], '\n'.join(t_lg))

					# Je stocke en mémoire le nouveau montant souhaité de la prestation.
					request.session['mont_prest_temp'] = f_modif_prest.cleaned_data.get('mont_prest')

					# Je mets à jour la variable globale.
					g_f_modif_prest = f_modif_prest

					# J'affiche le formulaire de redistribution de la prestation.
					output = HttpResponse(
						json.dumps({ 'success' : {
							'next' : f_suiv
						}}), 
						content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs.
					t_err = {}
					for k, v in f_modif_prest.errors.items() :
						t_err['GererPrestation-{0}'.format(k)] = v
					output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

			# Je traite le cas où je dois valider la dernière étape du processus de modification d'une prestation.
			if get_action == 'valider-etape-2' :

				# J'initialise le montant total de la prestation.
				mont_prest = o_prest.id_prest.mont_prest
				if 'mont_prest_temp' in request.session :
					mont_prest = request.session['mont_prest_temp']

				# J'initialise le montant global de la prestation après redistribution.
				mont_prest_doss_sum = 0

				# J'initialise le tableau des erreurs tous formulaires confondus.
				t_err = {}

				# J'initialise le tableau des instances TPrestationsDossier à modifier.
				t_inst_prest_doss = []

				for index, dp in enumerate(TPrestationsDossier.objects.filter(id_prest = o_prest.id_prest)) :

					# Je soumets le formulaire.
					f_red_prest = RedistribuerPrestation(
						request.POST, 
						instance = dp, 
						prefix = 'RedistribuerPrestation{0}'.format(index), 
						k_mont_prest = mont_prest
					)

					if f_red_prest.is_valid() :

						# Je récupère les données du formulaire valide.
						cleaned_data = f_red_prest.cleaned_data

						# J'ajoute le montant du couple prestation/dossier courant.
						mont_prest_doss_sum += cleaned_data.get('mont_prest_doss')

						# J'empile le tableau des instances TPrestationsDossier.
						t_inst_prest_doss.append(f_red_prest.save(commit = False))

					else :

						# J'empile le tableau des erreurs.
						for k, v in f_red_prest.errors.items() :
							t_err['RedistribuerPrestation{0}-{1}'.format(index, k)] = v

				if len(t_err) > 0 :

					# J'affiche les erreurs.
					output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

				else :
					if mont_prest_doss_sum == mont_prest :

						# Je modifie l'instance TPrestation via la variable globale.
						o_prest_modif = g_f_modif_prest.save(commit = False)
						o_prest_modif.save()

						# Je modifie chaque instance TPrestationsDossier.
						for i in range(0, len(t_inst_prest_doss)) :
							t_inst_prest_doss[i].save()

						# J'affiche le message de succès.
						output = HttpResponse(
							json.dumps({ 'success' : {
								'message' : 'La prestation « {0} » a été mise à jour avec succès.'.format(
									o_prest.id_prest
								),
								'modal' : 'modif_prest',
								'redirect' : reverse('cons_prest', args = [o_prest.pk])
							}}), 
							content_type = 'application/json'
						)

						# Je complète le fichier log.
						rempl_fich_log([request.user.pk, request.user, 'U', 'Prestation', o_prest_modif.pk])

					else :

						# J'affiche l'erreur groupée.
						output = HttpResponse(
							json.dumps({ 'errors' : ['La somme des montants n\'est pas égale à {0} €.'.format(obt_mont(
								mont_prest
							))] }), 
							content_type = 'application/json'
						)

	return output

'''
Cette vue permet d'afficher la page de consultation d'une prestation.
request : Objet requête
_p : Identifiant d'une prestation
'''
@verif_acc
@nett_f
def cons_prest(request, _pd) :

	# Imports
	from app.functions import init_fm
	from app.functions import init_pg_cons
	from app.functions import dt_fr
	from app.functions import gen_f_ajout_aven
	from app.functions import ger_droits
	from app.functions import obt_mont
	from app.models import TAvenant
	from app.models import TPrestationsDossier
	from app.sql_views import VSuiviPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TPrestationsDossier.
	o_prest_doss = get_object_or_404(TPrestationsDossier, pk = _pd)

	if request.method == 'GET' :

		# Je vérifie le droit de lecture.
		ger_droits(request.user, o_prest_doss.id_doss)

		# Je désigne l'onglet actif du navigateur à onglets relatif à une prestation.
		if 'tab_prest' not in request.session :
			request.session['tab_prest'] = ['#ong_prest', -1]
		request.session['tab_prest'][1] += 1
		if request.session['tab_prest'][1] > 0 :
			del request.session['tab_prest']

		# Je définis si le montant de la prestation est en HT ou en TTC.
		ht_ou_ttc = 'HT'
		if o_prest_doss.id_doss.est_ttc_doss == True :
			ht_ou_ttc = 'TTC'

		# Je pointe vers l'objet VSuiviPrestationsDossier.
		o_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(pk = o_prest_doss.pk)

		# J'initialise la valeur attributaire liée à la somme des factures émises.
		v_mont_fact_sum = o_suivi_prest_doss.mont_ht_fact_sum
		if ht_ou_ttc == 'TTC' :
			v_mont_fact_sum = o_suivi_prest_doss.mont_ttc_fact_sum

		# Je prépare le volet de consultation de la prestation.
		t_attrs_prest_doss = {
			'id_org_prest' : { 'label': 'Prestataire', 'value' : o_prest_doss.id_prest.id_org_prest },
			'int_prest' : { 'label': 'Intitulé de la prestation', 'value' : o_prest_doss.id_prest.int_prest },
			'ref_prest' : { 'label': 'Référence de la prestation', 'value' : o_prest_doss.id_prest.ref_prest },
			'mont_prest' : {
				'label': 'Montant {0} total de la prestation (en €)'.format(ht_ou_ttc), 
				'value' : obt_mont(o_prest_doss.id_prest.mont_prest)
			},
			'dt_notif_prest' : { 
				'label' : 'Date de notification de la prestation', 
				'value' : dt_fr(o_prest_doss.id_prest.dt_notif_prest)
			},
			'dt_fin_prest' : {
				'label' : 'Date de fin de la prestation', 'value' : dt_fr(o_prest_doss.id_prest.dt_fin_prest)
			},
			'id_nat_prest' : { 'label' : 'Nature de la prestation', 'value' : o_prest_doss.id_prest.id_nat_prest },
			'chem_pj_prest' : {
				'label' : 'Consulter le contrat de prestation', 'value' : o_prest_doss
				.id_prest.chem_pj_prest, 
				'pdf' : True
			},
			'comm_prest' : { 'label' : 'Commentaire', 'value' : o_prest_doss.id_prest.comm_prest or '' },
			'mont_prest_doss' : { 
				'label' : 'Montant {0} de la prestation (en €)'.format(ht_ou_ttc),
				'value' : obt_mont(o_prest_doss.mont_prest_doss)
			},
			'nb_aven' : { 'label' : 'Nombre d\'avenants', 'value' : o_suivi_prest_doss.nb_aven },
			'mont_aven_sum' : { 
				'label' : 'Somme {0} des avenants (en €)'.format(ht_ou_ttc), 
				'value' : obt_mont(o_suivi_prest_doss.mont_aven_sum)
			},
			'mont_fact_sum' : {
				'label' : 'Somme {0} des factures émises (en €)'.format(ht_ou_ttc),
				'value' : obt_mont(v_mont_fact_sum)
			},
			'mont_raf' : { 
				'label' : 'Reste à facturer {0} (en €)'.format(ht_ou_ttc),
				'value' : obt_mont(o_suivi_prest_doss.mont_raf),
				'help-text' : '''
				= montant {ht_ou_ttc} de la prestation + somme {ht_ou_ttc} des avenants - somme {ht_ou_ttc} des
				factures émises
				'''.format(ht_ou_ttc = ht_ou_ttc)
			}
		}

		# J'initialise le tableau des autres dossiers reliés à la prestation.
		t_doss = [{
			'id_doss' : d.id_doss,
			'mont_prest_doss' : obt_mont(d.mont_prest_doss),
			'mont_aven_sum' : obt_mont(d.mont_aven_sum),
			'pk' : d.pk
		} for d in VSuiviPrestationsDossier.objects.filter(id_prest = o_prest_doss.id_prest).exclude(
			pk = o_prest_doss.pk
		).order_by('id_doss')]

		# J'initialise le tableau des avenants du couple prestation/dossier.
		t_aven = [{
			'num_aven' : index + 1,
			'int_aven' : a.int_aven,
			'dt_aven' : dt_fr(a.dt_aven),
			'mont_aven' : obt_mont(a.mont_aven),
			'pk' : a.pk
		} for index, a in enumerate(TAvenant.objects.filter(
			id_doss = o_prest_doss.id_doss, id_prest = o_prest_doss.id_prest
		).order_by('num_aven'))]

		# Je déclare un tableau qui stocke le contenu de certaines fenêtres modales.
		t_cont_fm = {
			'ajout_aven' : gen_f_ajout_aven(request, o_prest_doss, reverse('ajout_aven'))
		}

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('ajout_aven', 'Ajouter un avenant', t_cont_fm['ajout_aven']),
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/cons_prest.html',
			{
				'pd' : o_prest_doss,
				'forbidden' : ger_droits(request.user, o_prest_doss.id_doss, False, False),
				'ht_ou_ttc' : ht_ou_ttc,
				't_attrs_prest_doss' : init_pg_cons(t_attrs_prest_doss),
				't_aven' : t_aven,
				't_doss' : t_doss,
				't_fm' : t_fm,
				'title' : 'Consulter une prestation'
			}
		)

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'un avenant.
request : Objet requête
_r : Paramètres de redirection
'''
@verif_acc
def ajout_aven(request, _r) :

	# Imports
	from app.forms.gestion_dossiers import GererAvenant
	from app.functions import ger_droits
	from app.functions import rempl_fich_log
	from app.models import TDossier
	from app.models import TPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json

	output = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		try :
			o_doss_droit = TDossier.objects.get(num_doss = request.POST.get('GererAvenant-za_num_doss'))
		except :
			o_doss_droit = None
		if o_doss_droit :
			ger_droits(request.user, o_doss_droit, False)

		# Je soumets le formulaire.
		f_ajout_aven = GererAvenant(request.POST, prefix = 'GererAvenant')

		# Je rajoute des choix valides pour la liste déroulante des prestations (prévention d'erreurs).
		post_prest = request.POST.get('GererAvenant-zl_prest')
		if post_prest :
			f_ajout_aven.fields['zl_prest'].choices = [(post_prest, post_prest)]

		if f_ajout_aven.is_valid() :

			# Je récupère les données du formulaire valide.
			cleaned_data = f_ajout_aven.cleaned_data
			v_num_doss = cleaned_data.get('za_num_doss')
			v_prest = cleaned_data.get('zl_prest')

			# Je pointe vers l'objet TPrestationsDossier.
			o_prest_doss = TPrestationsDossier.objects.get(id_doss__num_doss = v_num_doss, id_prest = v_prest)

			# Je créé la nouvelle instance TAvenant.
			o_nv_aven = f_ajout_aven.save(commit = False)
			o_nv_aven.num_aven = o_prest_doss.seq_aven_prest_doss
			o_nv_aven.save()

			# Je mets à jour l'objet TPrestationsDossier.
			o_prest_doss.seq_aven_prest_doss += 1
			o_prest_doss.save()

			if _r == 'cons_prest' :
				url = reverse(
					'cons_prest', 
					args = [TPrestationsDossier.objects.get(
						id_doss = o_nv_aven.id_doss, id_prest = o_nv_aven.id_prest
					).pk]
				)
				tab = 'tab_prest'
				ong = '#ong_aven'
			if _r == 'cons_doss' :
				url = reverse(
					'cons_doss', 
					args = [o_nv_aven.id_doss.pk]
				)
				tab = 'tab_doss'
				ong = '#ong_prest'

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'L\'avenant a été ajouté avec succès à la prestation « {0} » du dossier {1}.'.format(
						o_nv_aven.id_prest, o_nv_aven.id_doss
					),
					'redirect' : url
				}}), 
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session[tab] = [ong, -1]

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'C', 'Avenant', o_nv_aven.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_aven.errors.items() :
				t_err['GererAvenant-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'un avenant ou de traiter le formulaire de mise à jour d'un
avenant
request : Objet requête
_a : Identifiant d'un avenant
'''
@verif_acc
@nett_f
def modif_aven(request, _a) :

	# Imports
	from app.forms.gestion_dossiers import GererAvenant
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import rempl_fich_log
	from app.models import TAvenant
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TAvenant.
	o_aven = get_object_or_404(TAvenant, pk = _a)

	# Je vérifie le droit d'écriture.
	ger_droits(request.user, o_aven.id_doss, False)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_aven = GererAvenant(instance = o_aven, prefix = 'GererAvenant')

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_aven', 'Modifier un avenant')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/modif_aven.html',
			{ 'a' : o_aven, 'f_modif_aven' : init_f(f_modif_aven), 't_fm' : t_fm, 'title' : 'Modifier un avenant' }
		)

	else :

		# Je soumets le formulaire.
		f_modif_aven = GererAvenant(request.POST, instance = o_aven, prefix = 'GererAvenant')

		if f_modif_aven.is_valid() :

			# Je modifie l'instance TAvenant.
			o_aven_modif = f_modif_aven.save(commit = False)
			o_aven_modif.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'L\'avenant a été mis à jour avec succès.',
					'redirect' : reverse('cons_aven', args = [o_aven_modif.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'U', 'Avenant', o_aven_modif.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_modif_aven.errors.items() :
				t_err['GererAvenant-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de consultation d'un avenant.
request : Objet requête
_a : Identifiant d'un avenant
'''
@verif_acc
def cons_aven(request, _a) :

	# Imports
	from app.functions import init_pg_cons
	from app.functions import dt_fr
	from app.functions import ger_droits
	from app.functions import obt_mont
	from app.models import TAvenant
	from app.models import TPrestationsDossier
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TAvenant.
	o_aven = get_object_or_404(TAvenant, pk = _a)

	# Je pointe vers l'objet TPrestationsDossier.
	o_prest_doss = TPrestationsDossier.objects.get(id_doss = o_aven.id_doss, id_prest = o_aven.id_prest)

	if request.method == 'GET' :

		# Je vérifie le droit de lecture.
		ger_droits(request.user, o_aven.id_doss)

		# Je définis si le montant de l'avenant est en HT ou en TTC.
		ht_ou_ttc = 'HT'
		if o_aven.id_doss.est_ttc_doss == True :
			ht_ou_ttc = 'TTC'

		# Je prépare le volet de consultation de l'avenant.
		t_attrs_aven = {
			'id_doss' : { 'label': 'Numéro du dossier', 'value' : o_aven.id_doss },
			'id_prest' : { 'label' : 'Prestation', 'value' : o_aven.id_prest },
			'int_aven' : { 'label' : 'Intitulé de l\'avenant', 'value' : o_aven.int_aven },
			'dt_aven' : { 'label' : 'Date de fin de l\'avenant', 'value' : dt_fr(o_aven.dt_aven) },
			'mont_aven' : { 
				'label' : 'Montant {0} de l\'avenant (en €)'.format(ht_ou_ttc), 'value' : obt_mont(o_aven.mont_aven)
			},
			'comm_aven' : { 'label' : 'Commentaire', 'value' : o_aven.comm_aven or '' }
		}

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/cons_aven.html',
			{
				'a' : o_aven,
				'forbidden' : ger_droits(request.user, o_aven.id_doss, False, False),
				'ht_ou_ttc' : ht_ou_ttc,
				'pd' : o_prest_doss,
				't_attrs_aven' : init_pg_cons(t_attrs_aven),
				'title' : 'Consulter un avenant'
			}
		)

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'une facture.
request : Objet requête
'''
@verif_acc
def ajout_fact(request) :

	# Imports
	from app.forms.gestion_dossiers import GererFacture
	from app.functions import ger_droits
	from app.functions import rempl_fich_log
	from app.models import TDossier
	from app.models import TPrestation
	from app.models import TPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json

	output = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		try :
			o_doss_droit = TDossier.objects.get(num_doss = request.POST.get('GererFacture-za_num_doss'))
		except :
			o_doss_droit = None
		if o_doss_droit :
			ger_droits(request.user, o_doss_droit, False)

		# Je soumets le formulaire.
		f_ajout_fact = GererFacture(request.POST, request.FILES, prefix = 'GererFacture')

		# Je rajoute des choix valides pour la liste déroulante des prestations (prévention d'erreurs).
		post_prest = request.POST.get('GererFacture-zl_prest')
		if post_prest :
			f_ajout_fact.fields['zl_prest'].choices = [(p.pk, p) for p in TPrestation.objects.filter(pk = post_prest)]

		if f_ajout_fact.is_valid() :

			# Je récupère les données du formulaire valide.
			cleaned_data = f_ajout_fact.cleaned_data
			v_num_doss = cleaned_data.get('za_num_doss')
			v_prest = cleaned_data.get('zl_prest')
			v_suivi_fact = cleaned_data.get('zl_suivi_fact')

			# Je complète le suivi de la facture en cas d'un acompte.
			o_prest_doss = None
			if v_suivi_fact == 'Acompte' :
				o_prest_doss = TPrestationsDossier.objects.get(id_doss__num_doss = v_num_doss, id_prest = v_prest)
				v_suivi_fact += ' {0}'.format(o_prest_doss.seq_ac_prest_doss)

			# Je créé la nouvelle instance TFacture.
			o_nvelle_fact = f_ajout_fact.save(commit = False)
			o_nvelle_fact.suivi_fact = v_suivi_fact
			o_nvelle_fact.save()

			# Je mets à jour l'objet TPrestationsDossier en cas d'un acompte.
			if o_prest_doss :
				o_prest_doss.seq_ac_prest_doss = o_prest_doss.seq_ac_prest_doss + 1
				o_prest_doss.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : '''
					La facture N°{0} a été ajoutée avec succès à la prestation « {1} » du dossier {2}.
					'''.format(o_nvelle_fact.num_fact, o_nvelle_fact.id_prest, o_nvelle_fact.id_doss),
					'redirect' : reverse('cons_doss', args = [o_nvelle_fact.id_doss.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_doss'] = ['#ong_fact', -1]

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'C', 'Facture', o_nvelle_fact.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_fact.errors.items() :
				t_err['GererFacture-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'une facture ou de traiter le formulaire de mise à jour d'une
facture.
request : Objet requête
_f : Identifiant d'une facture
'''
@verif_acc
@nett_f
def modif_fact(request, _f) :

	# Imports
	from app.forms.gestion_dossiers import GererFacture
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import rempl_fich_log
	from app.models import TFacture
	from app.models import TPrestationsDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TFacture.
	o_fact = get_object_or_404(TFacture, pk = _f)

	# Je vérifie le droit d'écriture.
	ger_droits(request.user, o_fact.id_doss, False)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_fact = GererFacture(instance = o_fact, prefix = 'GererFacture')

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_fact', 'Modifier une facture')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/modif_fact.html',
			{ 'f' : o_fact, 'f_modif_fact' : init_f(f_modif_fact), 't_fm' : t_fm, 'title' : 'Modifier une facture' }
		)

	else :

		# Je soumets le formulaire.
		f_modif_fact = GererFacture(request.POST, request.FILES, instance = o_fact, prefix = 'GererFacture')

		if f_modif_fact.is_valid() :

			# Je récupère les données du formulaire valide.
			cleaned_data = f_modif_fact.cleaned_data
			v_prest = cleaned_data.get('zl_prest')
			v_suivi_fact = cleaned_data.get('zl_suivi_fact')

			# J'initialise le suivi de la facture.
			o_prest_doss = None
			if v_suivi_fact == 'Acompte' :
				if o_fact.suivi_fact == 'Solde' :

					# Je traite le cas ou je passe de "Solde" vers "Acompte" sans changement de prestation.
					o_prest_doss = TPrestationsDossier.objects.get(id_doss = o_fact.id_doss, id_prest = v_prest)
					v_suivi_fact += ' {0}'.format(o_prest_doss.seq_ac_prest_doss)

				else :
					if o_fact.id_prest.pk == int(v_prest) :
						v_suivi_fact = o_fact.suivi_fact
					else :

						# Je traite le cas ou je change de prestation (regénération du séquentiel "Acompte").
						o_prest_doss = TPrestationsDossier.objects.get(id_doss = o_fact.id_doss, id_prest = v_prest)
						v_suivi_fact += ' {0}'.format(o_prest_doss.seq_ac_prest_doss)

			# Je modifie l'instance TFacture.
			o_fact_modif = f_modif_fact.save(commit = False)
			o_fact_modif.suivi_fact = v_suivi_fact
			o_fact_modif.save()

			# Je mets à jour l'objet TPrestationsDossier en cas d'un nouvel acompte.
			if o_prest_doss :
				o_prest_doss.seq_ac_prest_doss = o_prest_doss.seq_ac_prest_doss + 1
				o_prest_doss.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'La facture N°{0} a été mise à jour avec succès.'.format(o_fact_modif.num_fact),
					'redirect' : reverse('cons_fact', args = [o_fact_modif.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'U', 'Facture', o_fact_modif.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_modif_fact.errors.items() :
				t_err['GererFacture-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de consultation d'une facture.
request : Objet requête
_f : Identifiant d'une facture
'''
@verif_acc
def cons_fact(request, _f) :

	# Imports
	from app.functions import init_pg_cons
	from app.functions import dt_fr
	from app.functions import ger_droits
	from app.functions import obt_mont
	from app.models import TFacture
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TFinancement.
	o_fact = get_object_or_404(TFacture, pk = _f)

	# Je vérifie le droit de lecture.
	ger_droits(request.user, o_fact.id_doss)

	if request.method == 'GET' :

		# Je prépare le volet de consultation de la facture.
		t_attrs_fact = {
			'id_doss' : { 'label' : 'Numéro du dossier', 'value' : o_fact.id_doss },
			'id_prest' : { 'label' : 'Prestation', 'value' : o_fact.id_prest },
			'num_fact' : { 'label' : 'Numéro de facture', 'value' : o_fact.num_fact },
			'dt_mand_moa_fact' : { 
				'label' : 'Date de mandatement par le maître d\'ouvrage', 'value' : dt_fr(o_fact.dt_mand_moa_fact)
			},
			'mont_ht_fact' : { 'label' : 'Montant HT de la facture (en €)', 'value' : obt_mont(o_fact.mont_ht_fact) },
			'mont_ttc_fact' : {
				'label' : 'Montant TTC de la facture (en €)', 'value' : obt_mont(o_fact.mont_ttc_fact)
			},
			'dt_rec_fact' : { 'label' : 'Date de réception de la facture', 'value' : dt_fr(o_fact.dt_rec_fact) },
			'num_mandat_fact' : { 'label' : 'Numéro de mandat', 'value' : o_fact.num_mandat_fact },
			'num_bord_fact' : { 'label' : 'Numéro de bordereau', 'value' : o_fact.num_bord_fact },
			'suivi_fact' : { 'label' : 'Suivi de la facturation', 'value' : o_fact.suivi_fact },
			'chem_pj_fact' : { 
				'label' : 'Consulter le fichier scanné de la facture', 'value' : o_fact.chem_pj_fact, 'pdf' : True 
			},
			'comm_fact' : { 'label' : 'Commentaire', 'value' : o_fact.comm_fact or '' },
		} 

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/cons_fact.html',
			{
				'f' : o_fact,
				'forbidden' : ger_droits(request.user, o_fact.id_doss, False, False),
				't_attrs_fact' : init_pg_cons(t_attrs_fact),
				'title' : 'Consulter une facture'
			}
		)

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'une demande de versement.
request : Objet requête
'''
@verif_acc
def ajout_ddv(request) :

	# Imports
	from app.forms.gestion_dossiers import GererDemandeVersement
	from app.functions import gen_t_html_fact_doss
	from app.functions import ger_droits
	from app.functions import rempl_fich_log
	from app.models import TDossier
	from app.models import TFacture
	from app.models import TFacturesDemandeVersement
	from app.models import TFinancement
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json

	output = HttpResponse()

	if request.method == 'POST' :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois filtrer les factures.
			if get_action == 'filtrer-factures' :
				output = HttpResponse(gen_t_html_fact_doss(request.POST.get('GererDemandeVersement-zl_fin')))

		else :

			# Je vérifie le droit d'écriture.
			try :
				o_doss_droit = TDossier.objects.get(num_doss = request.POST.get('GererDemandeVersement-za_num_doss'))
			except :
				o_doss_droit = None
			if o_doss_droit :
				ger_droits(request.user, o_doss_droit, False)

			# Je soumets le formulaire.
			f_ajout_ddv = GererDemandeVersement(request.POST, request.FILES, prefix = 'GererDemandeVersement')

			# Je rajoute des choix valides pour les listes déroulantes des financements et des factures (prévention d'
			# erreurs).
			post_doss = request.POST.get('GererDemandeVersement-za_num_doss')
			post_fin = request.POST.get('GererDemandeVersement-zl_fin')
			if post_doss and post_fin :
				f_ajout_ddv.fields['zl_fin'].choices = [(f.pk, f.id_org_fin) for f in TFinancement.objects.filter(
					id_doss__num_doss = post_doss, pk = post_fin
				)]
			if post_fin :
				try :
					o_doss = TFinancement.objects.get(pk = post_fin).id_doss
				except :
					o_doss = None
				f_ajout_ddv.fields['cbsm_fact'].choices = [(f.pk, f) for f in TFacture.objects.filter(
					id_doss = o_doss
				)]

			if f_ajout_ddv.is_valid() :

				# Je créé la nouvelle instance TDemandeVersement.
				o_nvelle_ddv = f_ajout_ddv.save(commit = False)
				o_nvelle_ddv.save()

				# Je fais le lien avec la table TFacturesDemandeVersement.
				v_fact = request.POST.getlist('GererDemandeVersement-cbsm_fact')
				for i in range(0, len(v_fact)) :
					TFacturesDemandeVersement.objects.create(
						id_ddv = o_nvelle_ddv, 
						id_fact = TFacture.objects.get(pk = v_fact[i])
					)

				# J'affiche le message de succès.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : '''
						La demande de versement a été ajoutée avec succès au partenaire financier « {0} » du dossier {1}.
						'''.format(o_nvelle_ddv.id_fin.id_org_fin, o_nvelle_ddv.id_fin.id_doss),
						'redirect' : reverse('cons_doss', args = [o_nvelle_ddv.id_fin.id_doss.pk])
					}}), 
					content_type = 'application/json'
				)

				# Je renseigne l'onglet actif après rechargement de la page.
				request.session['tab_doss'] = ['#ong_ddv', -1]

				# Je complète le fichier log.
				rempl_fich_log([request.user.pk, request.user, 'C', 'Demande de versement', o_nvelle_ddv.pk])

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_ajout_ddv.errors.items() :
					t_err['GererDemandeVersement-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'une demande de versement ou de traiter le formulaire de mise à 
jour d'une demande de versement.
request : Objet requête
_d : Identifiant d'une demande de versement
'''
@verif_acc
@nett_f
@csrf_exempt
def modif_ddv(request, _d) :

	# Imports
	from app.forms.gestion_dossiers import GererDemandeVersement
	from app.functions import gen_t_html_fact_doss
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import rempl_fich_log
	from app.models import TDemandeVersement
	from app.models import TFacture
	from app.models import TFacturesDemandeVersement
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TDemandeVersement.
	o_ddv = get_object_or_404(TDemandeVersement, pk = _d)

	# Je vérifie le droit d'écriture.
	ger_droits(request.user, o_ddv.id_fin.id_doss, False)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_ddv = GererDemandeVersement(instance = o_ddv, prefix = 'GererDemandeVersement')

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('ger_ddv', 'Modifier une demande de versement')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/modif_ddv.html',
			{
				'd' : o_ddv,
				'f_modif_ddv' : init_f(f_modif_ddv),
				't_fact_doss' : gen_t_html_fact_doss(o_ddv.id_fin.pk, o_ddv, True),
				't_fm' : t_fm,
				'title' : 'Modifier une demande de versement'
			}
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois filtrer les factures.
			if get_action == 'filtrer-factures' :
				output = HttpResponse(gen_t_html_fact_doss(request.POST.get('GererDemandeVersement-zl_fin'), o_ddv))

		else :

			# Je soumets le formulaire.
			f_modif_ddv = GererDemandeVersement(
				request.POST, request.FILES, instance = o_ddv, prefix = 'GererDemandeVersement'
			)

			if f_modif_ddv.is_valid() :

				# Je modifie l'instance TDemandeVersement.
				o_ddv_modif = f_modif_ddv.save(commit = False)
				o_ddv_modif.save()

				# Je supprime tous les enregistrements liés à la demande de versement afin de les recréer.
				TFacturesDemandeVersement.objects.filter(id_ddv = o_ddv_modif).delete()

				# Je fais le lien avec la table TFacturesDemandeVersement.
				v_fact = request.POST.getlist('GererDemandeVersement-cbsm_fact')
				for i in range(0, len(v_fact)) :
					TFacturesDemandeVersement.objects.create(
						id_ddv = o_ddv_modif, 
						id_fact = TFacture.objects.get(pk = v_fact[i])
					)

				# J'affiche le message de succès.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'La demande de versement a été mise à jour avec succès.',
						'redirect' : reverse('cons_ddv', args = [o_ddv_modif.pk])
					}}), 
					content_type = 'application/json'
				)

				# Je complète le fichier log.
				rempl_fich_log([request.user.pk, request.user, 'U', 'Demande de versement', o_ddv_modif.pk])

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_modif_ddv.errors.items() :
					t_err['GererDemandeVersement-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de consultation d'une demande de versement.
request : Objet requête
_d : Identifiant d'une demande de versement
'''
@verif_acc
def cons_ddv(request, _d) :

	# Imports
	from app.functions import init_pg_cons
	from app.functions import dt_fr
	from app.functions import ger_droits
	from app.functions import obt_mont
	from app.models import TDemandeVersement
	from app.models import TFacturesDemandeVersement
	from app.sql_views import VDemandeVersement
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TDemandeVersement.
	o_ddv = get_object_or_404(TDemandeVersement, pk = _d)

	if request.method == 'GET' :

		# Je vérifie le droit de lecture.
		ger_droits(request.user, o_ddv.id_fin.id_doss)

		o_suivi_ddv = VDemandeVersement.objects.get(pk = o_ddv.pk)

		# Je prépare le volet de consultation de la demande de versement.
		t_attrs_ddv = {
			'id_doss' : { 'label' : 'Numéro du dossier', 'value' : o_suivi_ddv.id_doss },
			'id_org_fin' : { 'label' : 'Partenaire financier', 'value' : o_suivi_ddv.id_org_fin },
			'id_type_vers' : { 'label' : 'Type de demande de versement', 'value' : o_ddv.id_type_vers },
			'int_ddv' : { 'label' : 'Intitulé de la demande de versement', 'value' : o_ddv.int_ddv },
			'mont_ht_ddv' : {
				'label' : 'Montant HT de la demande de versement (en €)', 'value' : obt_mont(o_ddv.mont_ht_ddv)
			},
			'mont_ttc_ddv' : {
				'label' : 'Montant TTC de la demande de versement (en €)', 'value' : obt_mont(o_ddv.mont_ttc_ddv)
			},
			'dt_ddv' : { 'label' : 'Date de la demande de versement', 'value' : dt_fr(o_ddv.dt_ddv) },
			'dt_vers_ddv' : { 'label' : 'Date de versement', 'value' : dt_fr(o_ddv.dt_vers_ddv) or '' },
			'mont_ht_verse_ddv' : { 'label' : 'Montant HT versé (en €)', 'value' : obt_mont(o_ddv.mont_ht_verse_ddv) },
			'mont_ttc_verse_ddv' : {
				'label' : 'Montant TTC versé (en €)', 'value' : obt_mont(o_ddv.mont_ttc_verse_ddv)
			},
			'map_ht_ddv' : { 'label' : 'Manque à percevoir HT (en €)', 'value' : obt_mont(o_suivi_ddv.map_ht_ddv) },
			'map_ttc_ddv' : { 'label' : 'Manque à percevoir TTC (en €)', 'value' : obt_mont(o_suivi_ddv.map_ttc_ddv) },
			'chem_pj_ddv' : {
				'label' : 'Consulter le courrier scanné de la demande de versement', 
				'value' : o_ddv.chem_pj_ddv, 
				'pdf' : True
			},
			'comm_ddv' : { 'label' : 'Commentaire', 'value' : o_ddv.comm_ddv or '' }
		}

		# J'initialise le tableau des factures reliées à la demande de versement.
		t_fact_ddv = []
		for fd in TFacturesDemandeVersement.objects.filter(id_ddv = o_ddv) :

			mont_fact = fd.id_fact.mont_ht_fact
			if fd.id_fact.id_doss.est_ttc_doss == True :
				mont_fact = fd.id_fact.mont_ttc_fact

			t_fact_ddv.append({
				'id_prest' : fd.id_fact.id_prest,
				'num_fact' : fd.id_fact.num_fact,
				'dt_mand_moa_fact' : dt_fr(fd.id_fact.dt_mand_moa_fact),
				'mont_fact' : obt_mont(mont_fact),
				'id_fact__pk' : fd.id_fact.pk
			})

		# Je définis si le montant du dossier est en HT ou en TTC.
		ht_ou_ttc = 'HT'
		if o_ddv.id_fin.id_doss.est_ttc_doss == True :
			ht_ou_ttc = 'TTC'

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/cons_ddv.html',
			{
				'd' : o_ddv,
				'forbidden' : ger_droits(request.user, o_ddv.id_fin.id_doss, False, False),
				'ht_ou_ttc' : ht_ou_ttc,
				't_attrs_ddv' : init_pg_cons(t_attrs_ddv),
				't_fact_ddv' : t_fact_ddv,
				'title' : 'Consulter une demande de versement'
			}
		)

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'un arrêté.
request : Objet requête
'''
@verif_acc
def ajout_arr(request) :

	# Imports
	from app.forms.gestion_dossiers import GererArrete
	from app.functions import ger_droits
	from app.functions import rempl_fich_log
	from app.models import TDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json

	output = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		try :
			o_doss_droit = TDossier.objects.get(num_doss = request.POST.get('GererArrete-za_num_doss'))
		except :
			o_doss_droit = None
		if o_doss_droit :
			ger_droits(request.user, o_doss_droit, False)

		# Je soumets le formulaire.
		f_ajout_arr = GererArrete(request.POST, request.FILES, prefix = 'GererArrete')

		if f_ajout_arr.is_valid() :

			# Je créé la nouvelle instance TArretesDossier.
			o_nv_arr = f_ajout_arr.save(commit = False)
			o_nv_arr.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'Le type de déclaration « {0} » a été ajouté avec succès au dossier {1}.'.format(
						o_nv_arr.id_type_decl, o_nv_arr.id_doss
					),
					'redirect' : reverse('cons_doss', args = [o_nv_arr.id_doss.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_doss'] = ['#ong_arr', -1]

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'C', 'Arrêté', o_nv_arr.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_arr.errors.items() :
				t_err['GererArrete-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'un arrêté ou de traiter le formulaire de mise à jour d'un arrêté.
request : Objet requête
_a : Identifiant d'un arrêté
'''
@verif_acc
@nett_f
def modif_arr(request, _a) :

	# Imports
	from app.forms.gestion_dossiers import GererArrete
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import rempl_fich_log
	from app.models import TArretesDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TArretesDossier
	o_arr = get_object_or_404(TArretesDossier, pk = _a)

	# Je vérifie le droit d'écriture.
	ger_droits(request.user, o_arr.id_doss, False)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_arr = GererArrete(instance = o_arr, prefix = 'GererArrete')

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_arr', 'Modifier un arrêté')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/modif_arr.html',
			{ 'a' : o_arr, 'f_modif_arr' : init_f(f_modif_arr), 't_fm' : t_fm, 'title' : 'Modifier un arrêté' }
		)

	else :

		# Je soumets le formulaire.
		f_modif_arr = GererArrete(request.POST, request.FILES, instance = o_arr, prefix = 'GererArrete')

		if f_modif_arr.is_valid() :

			# Je modifie l'instance TArretesDossier.
			o_arr_modif = f_modif_arr.save(commit = False)
			o_arr_modif.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'Le type de déclaration « {0} » du dossier {1} a été mis à jour avec succès.'.format(
						o_arr_modif.id_type_decl, o_arr_modif.id_doss
					),
					'redirect' : reverse('cons_arr', args = [o_arr_modif.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'U', 'Arrêté', o_arr_modif.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_modif_arr.errors.items() :
				t_err['GererArrete-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet de traiter le formulaire de suppression d'un arrêté.
request : Objet requête
_a : Identifiant d'un arrêté
'''
@verif_acc
@csrf_exempt
def suppr_arr(request, _a) :

	# Imports
	from app.functions import ger_droits
	from app.functions import rempl_fich_log
	from app.models import TArretesDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TArretesDossier.
	o_arr = get_object_or_404(TArretesDossier, pk = _a)

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		ger_droits(request.user, o_arr.id_doss, False)

		# Je pointe vers les objets TDossier et TTypeDeclaration liés à l'objet TArretesDossier.
		o_doss = o_arr.id_doss
		o_type_decl = o_arr.id_type_decl

		# Je récupère l'identifiant de l'arrêté afin de le renseigner dans le fichier log.
		v_id_arr_doss = o_arr.pk

		# Je supprime l'objet TArretesDossier.
		o_arr.delete()

		# J'affiche le message de succès.
		output = HttpResponse(
			json.dumps({ 'success' : {
				'message' : 'Le type de déclaration « {0} » a été supprimé avec succès du dossier {1}.'.format(
					o_type_decl, o_doss
				),
				'redirect' : reverse('cons_doss', args = [o_doss.pk])
			}}), 
			content_type = 'application/json'
		)

		# Je renseigne l'onglet actif après rechargement de la page.
		request.session['tab_doss'] = ['#ong_arr', -1]

		# Je complète le fichier log.
		rempl_fich_log([request.user.pk, request.user, 'D', 'Arrêté', v_id_arr_doss])

	return output

'''
Cette vue permet d'afficher la page de consultation d'un arrêté.
request : Objet requête
_a : Identifiant d'un arrêté
'''
@verif_acc
@csrf_exempt
def cons_arr(request, _a) :

	# Imports
	from app.functions import dt_fr
	from app.functions import ger_droits
	from app.functions import init_fm
	from app.functions import init_pg_cons
	from app.functions import suppr
	from app.models import TArretesDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	
	output = HttpResponse()

	# Je vérifie l'existence d'un objet TArretesDossier.
	o_arr = get_object_or_404(TArretesDossier, pk = _a)

	if request.method == 'GET' :

		# Je vérifie le droit de lecture.
		ger_droits(request.user, o_arr.id_doss)

		# Je prépare le volet de consultation de l'arrêté.
		t_attrs_arr = {
			'id_doss' : { 'label' : 'Numéro du dossier', 'value' : o_arr.id_doss },
			'id_type_decl' : { 'label' : 'Type de déclaration', 'value' : o_arr.id_type_decl },
			'id_type_av_arr' : { 'label' : 'Avancement', 'value' : o_arr.id_type_av_arr },
			'num_arr' : { 'label' : 'Numéro de l\'arrêté', 'value' : o_arr.num_arr },
			'dt_sign_arr' : { 'label' : 'Date de signature de l\'arrêté', 'value' : dt_fr(o_arr.dt_sign_arr) or '' },
			'dt_lim_encl_trav_arr' : { 
				'label' : 'Date limite d\'enclenchement des travaux', 'value' : dt_fr(o_arr.dt_lim_encl_trav_arr) or ''
			},
			'chem_pj_arr' : {
				'label' : 'Consulter le fichier scanné de l\'arrêté', 'value' : o_arr.chem_pj_arr, 'pdf' : True 
			},
			'comm_arr' : { 'label' : 'Commentaire', 'value' : o_arr.comm_arr or '' },
		}

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('suppr_arr', 'Supprimer un arrêté')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/cons_arr.html',
			{
				'a' : o_arr,
				'forbidden' : ger_droits(request.user, o_arr.id_doss, False, False),
				't_attrs_arr' : init_pg_cons(t_attrs_arr), 
				't_fm' : t_fm, 
				'title' : 'Consulter un arrêté'
			}
		)

	else :
		if 'action' in request.GET :

			# Je traite le cas où je dois supprimer un arrêté.
			if request.GET['action'] == 'supprimer-arrete' :
				if request.GET['arrete'] :
					output = HttpResponse(suppr(reverse('suppr_arr', args = [request.GET['arrete']])))

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'une photo.
request : Objet requête
'''
@verif_acc
def ajout_ph(request) :

	# Imports
	from app.forms.gestion_dossiers import GererPhoto
	from app.functions import ger_droits
	from app.functions import rempl_fich_log
	from app.models import TDossier
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	import json

	output = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		try :
			o_doss_droit = TDossier.objects.get(num_doss = request.POST.get('GererPhoto-za_num_doss'))
		except :
			o_doss_droit = None
		if o_doss_droit :
			ger_droits(request.user, o_doss_droit, False)

		# Je soumets le formulaire.
		f_ajout_ph = GererPhoto(request.POST, request.FILES, prefix = 'GererPhoto')

		if f_ajout_ph.is_valid() :

			# Je créé la nouvelle instance TPhoto.
			o_nvelle_ph = f_ajout_ph.save(commit = False)
			o_nvelle_ph.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'La photo a été ajoutée avec succès au dossier {0}.'.format(o_nvelle_ph.id_doss),
					'redirect' : reverse('cons_doss', args = [o_nvelle_ph.id_doss.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_doss'] = ['#ong_ph', -1]

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'C', 'Photo', o_nvelle_ph.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_ph.errors.items() :
				t_err['GererPhoto-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'une photo ou de traiter le formulaire de mise à jour
d'une photo.
request : Objet requête
_p : Identifiant d'une photo
'''
@verif_acc
@nett_f
def modif_ph(request, _p) :

	# Imports
	from app.forms.gestion_dossiers import GererPhoto
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import rempl_fich_log
	from django.core.urlresolvers import reverse
	from app.models import TPhoto
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TPhoto.
	o_ph = get_object_or_404(TPhoto, pk = _p)

	# Je vérifie le droit d'écriture.
	ger_droits(request.user, o_ph.id_doss, False)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_ph = GererPhoto(instance = o_ph, prefix = 'GererPhoto')

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_ph', 'Modifier une photo')
		]

		# J'affiche le template.
		output = render(
			request, 
			'./gestion_dossiers/modif_ph.html',
			{ 'f_modif_ph' : init_f(f_modif_ph), 'p' : o_ph, 't_fm' : t_fm, 'title' : 'Modifier une photo' }
		)

	else :

		# Je soumets le formulaire.
		f_modif_ph = GererPhoto(request.POST, request.FILES, instance = o_ph, prefix = 'GererPhoto')

		if f_modif_ph.is_valid() :

			# Je modifie l'instance TPhoto.
			o_ph_modif = f_modif_ph.save(commit = False)
			o_ph_modif.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'La photo a été mise à jour avec succès.',
					'redirect' : reverse('cons_doss', args = [o_ph.id_doss.pk])
				}}), 
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_doss'] = ['#ong_ph', -1]

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'U', 'Photo', o_ph_modif.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_modif_ph.errors.items() :
				t_err['GererPhoto-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet de traiter le formulaire de suppression d'une photo.
request : Objet requête
_p : Identifiant d'une photo
'''
@verif_acc
@csrf_exempt
def suppr_ph(request, _p) :

	# Imports
	from app.functions import ger_droits
	from app.functions import rempl_fich_log
	from app.models import TPhoto
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TPhoto.
	o_ph = get_object_or_404(TPhoto, pk = _p)

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		ger_droits(request.user, o_ph.id_doss, False)

		# Je pointe vers l'objet TDossier lié à l'objet TPhoto.
		o_doss = o_ph.id_doss

		# Je récupère l'identifiant de la photo afin de le renseigner dans le fichier log.
		v_id_ph = o_ph.pk

		# Je supprime l'objet TPhoto.
		o_ph.delete()

		# J'affiche le message de succès.
		output = HttpResponse(
			json.dumps({ 'success' : {
				'message' : 'La photo a été supprimée avec succès du dossier {0}.'.format(o_doss),
				'redirect' : reverse('cons_doss', args = [o_doss.pk])
			}}), 
			content_type = 'application/json'
		)

		# Je renseigne l'onglet actif après rechargement de la page.
		request.session['tab_doss'] = ['#ong_ph', -1]

		# Je complète le fichier log.
		rempl_fich_log([request.user.pk, request.user, 'D', 'Photo', v_id_ph])

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'un prestataire.
request : Objet requête
'''
@verif_acc
@nett_f
def ajout_org_prest(request) :

	# Imports
	from app.forms.gestion_dossiers import AjouterPrestataire
	from app.functions import rempl_fich_log
	from django.http import HttpResponse
	import json

	output = HttpResponse()

	if request.method == 'POST' :

		# Je soumets le formulaire.
		f_ajout_org_prest = AjouterPrestataire(request.POST, prefix = 'AjouterPrestataire')

		if f_ajout_org_prest.is_valid() :

			# Je créé la nouvelle instance TPrestataire.
			o_nv_org_prest = f_ajout_org_prest.save(commit = False)
			o_nv_org_prest.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'Le prestataire {0} a été créé avec succès.'.format(o_nv_org_prest),
					'display' : ['#id_GererPrestation-zsac_siret_org_prest', o_nv_org_prest.siret_org_prest]
				}}), 
				content_type = 'application/json'
			)

			# Je complète le fichier log.
			rempl_fich_log([request.user.pk, request.user, 'C', 'Prestataire', o_nv_org_prest.pk])

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_org_prest.errors.items() :
				t_err['AjouterPrestataire-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output