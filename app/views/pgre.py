#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.decorators import *
from django.views.decorators.csrf import csrf_exempt

'''
Cette vue permet d'afficher le menu principal du module de gestion des actions PGRE.
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
		output = render(request, './pgre/main.html', {
			'menu' : get_thumbnails_menu('pgre', 3), 'title' : 'Gestion des actions PGRE'
		})

	return output

'''
Cette vue permet d'afficher la page de création d'une action PGRE ou de traiter une action.
request : Objet requête
'''
@verif_acc
@csrf_exempt
def cr_act_pgre(request) :

	# Imports
	from app.forms.pgre import GererActionPgre
	from app.functions import alim_ld
	from app.functions import dt_fr
	from app.functions import filtr_doss
	from app.functions import gen_t_ch_doss
	from app.functions import init_f
	from app.functions import init_fm
	from app.models import TInstancesConcertationPgreAtelierPgre
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = HttpResponse()

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_cr_act_pgre = GererActionPgre(prefix = 'GererActionPgre')

		# Je déclare un tableau qui stocke le contenu de certaines fenêtres modales.
		t_cont_fm = {
			'ch_doss' : gen_t_ch_doss(request)
		}

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('ch_doss', 'Choisir un dossier de correspondance', t_cont_fm['ch_doss']),
			init_fm('ger_act_pgre', 'Créer une action PGRE')
		]

		# J'affiche le template.
		output = render(
			request,
			'./pgre/cr_act_pgre.html',
			{ 'f_cr_act_pgre' : init_f(f_cr_act_pgre), 't_fm' : t_fm, 'title' : 'Créer une action PGRE' }
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois filtrer les ateliers selon l'instance de concertation choisie.
			if get_action == 'filtrer-ateliers' :

				try :

					# Je stocke les ateliers concernés par l'instance de concertation.
					qs_ic_pgre_atel_pgre = TInstancesConcertationPgreAtelierPgre.objects.filter(
						id_ic_pgre = request.POST.get('GererActionPgre-id_ic_pgre')
					).order_by('id_atel_pgre')

					t_atel_pgre = [(
						a.id_atel_pgre.int_atel_pgre,
						'''
						<input type="checkbox" class="pull-right" id="id_GererActionPgre-cbsm_atel_pgre_{0}"
						name="GererActionPgre-cbsm_atel_pgre" value="{1}">
						'''.format(index, a.id_atel_pgre.pk)
					) for index, a in enumerate(qs_ic_pgre_atel_pgre)]

				except :
					t_atel_pgre = []

				# J'envoie le tableau des ateliers filtrés.
				output = HttpResponse(
					json.dumps({
						'bypass' : True,
						'success' : { 'datatable' : t_atel_pgre, 'datatable_name' : 'GererActionPgre-cbsm_atel_pgre' }
					}), content_type = 'application/json'
				)

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
					d.get_int_doss(),
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
			f_cr_act_pgre = GererActionPgre(
				request.POST,
				request.FILES,
				prefix = 'GererActionPgre',
				k_util = request.user,
				k_ic_pgre = request.POST.get('GererActionPgre-id_ic_pgre')
			)

			if f_cr_act_pgre.is_valid() :

				# Je créé la nouvelle instance TDossierPgre.
				o_nvelle_act_pgre = f_cr_act_pgre.save(commit = False)
				o_nvelle_act_pgre.save()

				# J'affiche le message de succès.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'L\'action PGRE N°{0} a été créée avec succès.'.format(o_nvelle_act_pgre),
						'redirect' : reverse('cons_act_pgre', args = [o_nvelle_act_pgre.pk])
					}}),
					content_type = 'application/json'
				)

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_cr_act_pgre.errors.items() :
					t_err['GererActionPgre-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'une action PGRE ou de traiter une action.
request : Objet requête
_a : Identifiant d'une action PGRE
'''
@verif_acc
@csrf_exempt
def modif_act_pgre(request, _a) :

	# Imports
	from app.forms.pgre import GererActionPgre
	from app.functions import alim_ld
	from app.functions import dt_fr
	from app.functions import filtr_doss
	from app.functions import gen_t_ch_doss
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.models import TDossierPgre
	from app.models import TDossierPgreGeom
	from app.models import TInstancesConcertationPgreAtelierPgre
	from app.models import TMoaDossierPgre
	from django.contrib.gis import geos
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from styx.settings import T_DONN_BDD_INT
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TDossierPgre.
	o_act_pgre = get_object_or_404(TDossierPgre, pk = _a)

	# Je vérifie le droit d'écriture.
	ger_droits(
		request.user,
		[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
			id_doss_pgre = o_act_pgre
		)],
		False
	)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_act_pgre = GererActionPgre(
			instance = o_act_pgre, prefix = 'GererActionPgre', k_ic_pgre = o_act_pgre.id_ic_pgre
		)

		# Je déclare un tableau qui stocke le contenu de certaines fenêtres modales.
		t_cont_fm = {
			'ch_doss' : gen_t_ch_doss(request)
		}

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('ch_doss', 'Choisir un dossier de correspondance', t_cont_fm['ch_doss']),
			init_fm('ger_act_pgre', 'Modifier une action PGRE')
		]

		# J'affiche le template.
		output = render(
			request,
			'./pgre/modif_act_pgre.html',
			{
				'a' : o_act_pgre,
				'f_modif_act_pgre' : init_f(f_modif_act_pgre),
				't_fm' : t_fm,
				'title' : 'Modifier une action PGRE'
			}
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois filtrer les ateliers selon l'instance de concertation choisie.
			if get_action == 'filtrer-ateliers' :

				try :

					# Je stocke les ateliers concernés par l'instance de concertation.
					qs_ic_pgre_atel_pgre = TInstancesConcertationPgreAtelierPgre.objects.filter(
						id_ic_pgre = request.POST.get('GererActionPgre-id_ic_pgre')
					).order_by('id_atel_pgre')

					t_atel_pgre = [(
						a.id_atel_pgre.int_atel_pgre,
						'''
						<input type="checkbox" class="pull-right" id="id_GererActionPgre-cbsm_atel_pgre_{0}"
						name="GererActionPgre-cbsm_atel_pgre" value="{1}">
						'''.format(index, a.id_atel_pgre.pk)
					) for index, a in enumerate(qs_ic_pgre_atel_pgre)]

				except :
					t_atel_pgre = []

				# J'envoie le tableau des ateliers filtrés.
				output = HttpResponse(
					json.dumps({
						'bypass' : True,
						'success' : { 'datatable' : t_atel_pgre, 'datatable_name' : 'GererActionPgre-cbsm_atel_pgre' }
					}), content_type = 'application/json'
				)

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
					d.get_int_doss(),
					d.id_org_moa.n_org,
					dt_fr(d.dt_delib_moa_doss) or '-',
					'<span class="choose-icon pointer pull-right" title="Choisir le dossier"></span>'
				) for d in filtr_doss(request)]

				# J'envoie le tableau des dossiers filtrés.
				output = HttpResponse(
					json.dumps({ 'success' : { 'datatable' : t_doss }}), content_type = 'application/json'
				)

			# Je traite le cas où je dois modifier la géométrie de l'objet TDossierPgre.
			if get_action == 'modifier-geom' :

				# Je supprime les géométries existantes de l'action PGRE.
				TDossierPgreGeom.objects.filter(id_doss_pgre = o_act_pgre).delete()

				if request.POST['edit-geom'] :

					# Je récupère les objets créés.
					editgeom = request.POST['edit-geom'].split(';')

					# Je créé la nouvelle instance TDossierPgreGeom.
					for g in editgeom :
						geom = geos.GEOSGeometry(g)
						geom_act_pgre = TDossierPgreGeom(id_doss_pgre = o_act_pgre)
						if geom and isinstance(geom, geos.Polygon):
							geom_act_pgre.geom_pol = geom
						if geom and isinstance(geom, geos.LineString):
							geom_act_pgre.geom_lin = geom
						if geom and isinstance(geom, geos.Point):
							geom_act_pgre.geom_pct = geom
						geom_act_pgre.save()

				# J'affiche le message de succès.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : '''
						La géométrie de l'action PGRE N°{0} a été mise à jour avec succès.
						'''.format(o_act_pgre),
						'redirect' : reverse('cons_act_pgre', args = [o_act_pgre.pk])
					}}),
					content_type = 'application/json'
				)

		else :

			# Je soumets le formulaire.
			f_modif_act_pgre = GererActionPgre(
				request.POST,
				request.FILES,
				instance = o_act_pgre,
				prefix = 'GererActionPgre',
				k_util = request.user,
				k_ic_pgre = request.POST.get('GererActionPgre-id_ic_pgre')
			)

			if f_modif_act_pgre.is_valid():

				# Je modifie l'instance TDossierPgre.
				o_act_pgre_modif = f_modif_act_pgre.save(commit = False)
				o_act_pgre_modif.save()

				# J'affiche le message de succès.
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'L\'action PGRE N°{0} a été modifiée avec succès.'.format(o_act_pgre_modif),
						'redirect' : reverse('cons_act_pgre', args = [o_act_pgre_modif.pk])
					}}),
					content_type = 'application/json'
				)

			else :

				# J'affiche les erreurs.
				t_err = {}
				for k, v in f_modif_act_pgre.errors.items() :
					t_err['GererActionPgre-{0}'.format(k)] = v
				output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet de traiter le formulaire de suppression d'une action PGRE.
request : Objet requête
_a : Identifiant d'une action PGRE
'''
@verif_acc
@csrf_exempt
def suppr_act_pgre(request, _a) :

	# Imports
	from app.functions import ger_droits
	from app.models import TAteliersPgreDossierPgre
	from app.models import TControleDossierPgre
	from app.models import TDossierPgre
	from app.models import TDossierPgreGeom
	from app.models import TMoaDossierPgre
	from app.models import TPhotoPgre
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from styx.settings import T_DONN_BDD_INT
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TDossierPgre.
	o_act_pgre = get_object_or_404(TDossierPgre, pk = _a)

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		ger_droits(
			request.user,
			[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
				id_doss_pgre = o_act_pgre
			)],
			False
		)

		# J'initialise un tableau de jeu de données.
		t_qs = [
			['Photo', TPhotoPgre.objects.filter(id_doss_pgre = o_act_pgre)],
			['Objet géométrique', TDossierPgreGeom.objects.filter(id_doss_pgre = o_act_pgre)]
		]

		# Je vérifie si je peux exécuter ou non la suppression de l'action PGRE.
		peut_suppr = True
		t_elem_a_suppr = []
		for i in range(0, len(t_qs)) :
			if len(t_qs[i][1]) > 0 :
				peut_suppr = False
				cle = t_qs[i][0]
				if len(t_qs[i][1]) > 1 :
					split = cle.split(' ')
					for j in range(0, len(split)) :
						split[j] += 's'
					cle = ' '.join(split)
				t_elem_a_suppr.append('{0} : {1}'.format(cle, len(t_qs[i][1])))

		if peut_suppr == True :

			# J'effectue les suppressions en cascade.
			TAteliersPgreDossierPgre.objects.filter(id_doss_pgre = o_act_pgre).delete()
			TMoaDossierPgre.objects.filter(id_doss_pgre = o_act_pgre).delete()
			TControleDossierPgre.objects.filter(id_doss_pgre = o_act_pgre).delete()

			# Je pointe vers l'objet TDossierPgre à supprimer.
			o_act_pgre_suppr = o_act_pgre

			# Je supprime l'objet TDossierPgre.
			o_act_pgre.delete()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'L\'action PGRE N°{0} a été supprimée avec succès.'.format(o_act_pgre_suppr),
					'redirect' : reverse('ch_act_pgre')
				}}),
				content_type = 'application/json'
			)

		else :

			# Je prépare le message d'alerte.
			mess_html = 'Veuillez d\'abord supprimer le/les élément(s) suivant(s) :'
			mess_html += '<ul class="list-inline">'
			for i in range(0, len(t_elem_a_suppr)) :
				mess_html += '<li>{0}</li>'.format(t_elem_a_suppr[i])
			mess_html += '</ul>'

			# J'affiche le message d'alerte.
			output = HttpResponse(json.dumps([mess_html]), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de choix d'une action PGRE ou de traiter une action.
request : Objet requête
'''
@verif_acc
def ch_act_pgre(request) :

	# Imports
	from app.forms.pgre import ChoisirActionPgre
	from app.functions import init_f
	from app.functions import obt_act_pgre_regr
	from app.models import TAteliersPgreDossierPgre
	from app.models import TDossierPgre
	from app.models import TMoa
	from app.models import TMoaDossierPgre
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = HttpResponse()

	if request.method == 'GET' :

		# J'initialise la valeur de l'argument "k_org_moa".
		try :
			v_org_moa = TMoa.objects.get(
				pk = TUtilisateur.objects.get(pk = request.user.pk).id_org,
				peu_doss_pgre = True,
				en_act_doss_pgre = True
			).pk
		except :
			v_org_moa = None

		# J'instancie un objet "formulaire".
		f_ch_act_pgre = ChoisirActionPgre(prefix = 'ChoisirActionPgre', k_org_moa = v_org_moa)

		# Je prépare le tableau des actions PGRE.
		if v_org_moa :
			qs_act_pgre = obt_act_pgre_regr(v_org_moa)
		else :
			qs_act_pgre = TDossierPgre.objects.all()
		t_act_pgre = [{
			'pk' : a.pk,
			'num_doss_pgre' : a,
			'int_doss_pgre' : a.int_doss_pgre,
			'moa' : ', '.join([str(m.id_org_moa) for m in TMoaDossierPgre.objects.filter(id_doss_pgre = a)]),
			'id_ic_pgre' : a.id_ic_pgre,
			'atel_pgre' : ', '.join([str(at.id_atel_pgre) for at in TAteliersPgreDossierPgre.objects.filter(
				id_doss_pgre = a
			)]),
			'id_nat_doss' : a.id_nat_doss
		} for a in qs_act_pgre]

		# J'affiche le template.
		output = render(
			request,
			'./pgre/ch_act_pgre.html',
			{ 'f_ch_act_pgre' : init_f(f_ch_act_pgre), 't_act_pgre' : t_act_pgre, 'title' : 'Choisir une action PGRE' }
		)

	else :

		# Je soumets le formulaire.
		f_ch_act_pgre = ChoisirActionPgre(request.POST, prefix = 'ChoisirActionPgre')

		if f_ch_act_pgre.is_valid() :

			# Je récupère les données du formulaire valide.
			cleaned_data = f_ch_act_pgre.cleaned_data
			v_org_moa = cleaned_data.get('zl_org_moa')
			v_ic_pgre = cleaned_data.get('zl_ic_pgre')
			v_atel_pgre = cleaned_data.get('zl_atel_pgre')
			v_nat_doss = cleaned_data.get('zl_nat_doss')

			# J'initialise les conditions de la requête.
			t_sql = { 'and' : {}, 'or' : [] }
			if v_ic_pgre :
				t_sql['and']['id_ic_pgre'] = v_ic_pgre
			if v_atel_pgre :
				t_sql['and']['atel_pgre__id_atel_pgre'] = v_atel_pgre
			if v_nat_doss :
				t_sql['and']['id_nat_doss'] = v_nat_doss

			# J'initialise la requête.
			if v_org_moa :
				qs_act_pgre = obt_act_pgre_regr(v_org_moa).filter(**t_sql['and'])
			else :
				qs_act_pgre = TDossierPgre.objects.filter(**t_sql['and'])

			# J'initialise le tableau des actions PGRE filtrées.
			t_act_pgre = [(
				str(a),
				a.int_doss_pgre,
				', '.join([str(m.id_org_moa) for m in TMoaDossierPgre.objects.filter(id_doss_pgre = a)]),
				str(a.id_ic_pgre),
				', '.join([str(at.id_atel_pgre) for at in TAteliersPgreDossierPgre.objects.filter(
					id_doss_pgre = a
				)]),
				str(a.id_nat_doss),
				'<a href="{0}" class="consult-icon pull-right" title="Consulter l\'action PGRE"></a>'.format(
					reverse('cons_act_pgre', args = [a.pk])
				)
			) for a in qs_act_pgre]

		else :
			t_act_pgre = []

		# J'envoie le tableau des actions PGRE filtrées.
		output = HttpResponse(
			json.dumps({ 'success' : { 'datatable' : t_act_pgre }}), content_type = 'application/json'
		)

	return output

'''
Cette vue permet d'afficher la page de consultation d'une action PGRE ou de traiter une action.
request : Objet requête
_a : Identifiant d'une action PGRE
'''
@verif_acc
@csrf_exempt
def cons_act_pgre(request, _a) :

	# Imports
	from app.forms.pgre import GererControleActionPgre
	from app.forms.pgre import GererPhotoPgre
	from app.forms.pgre import GererSsActionPgre
	from app.functions import dt_fr
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import init_pg_cons
	from app.functions import suppr
	from app.models import TAteliersPgreDossierPgre
	from app.models import TControleDossierPgre
	from app.models import TDossierPgre
	from app.models import TDossierPgreGeom
	from app.models import TMoaDossierPgre
	from app.models import TPhotoPgre
	from app.models import TUtilisateur
	from datetime import date
	from django.conf import settings
	from django.contrib.gis import geos
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from django.template.context_processors import csrf
	from styx.settings import MEDIA_URL
	from styx.settings import T_DONN_BDD_INT
	import datetime
	import json
	import time

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TDossierPgre.
	o_act_pgre = get_object_or_404(TDossierPgre, pk = _a)

	# J'initialise le tableau des couples pouvant accéder à la vue.
	t_coupl_val = [(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
		id_doss_pgre = o_act_pgre
	)]

	# Je stocke le jeu de données des points de contrôle de l'année courante.
	annee = date.today().year
	qs_pdc = TControleDossierPgre.objects.filter(id_doss_pgre = o_act_pgre, dt_contr_doss_pgre__year = annee)

	if request.method == 'GET' :

		# Je vérifie le droit de lecture.
		ger_droits(request.user, t_coupl_val)

		# Je désigne l'onglet actif du navigateur à onglets relatif à une action PGRE.
		if 'tab_act_pgre' not in request.session :
			request.session['tab_act_pgre'] = '#ong_act_pgre'

		# Je prépare l'onglet "Caractéristiques".
		t_attrs_act_pgre = {
			'num_doss_pgre' : { 'label' : 'Numéro de l\'action PGRE', 'value' : o_act_pgre },
			'id_ic_pgre' : { 'label' : 'Instance de concertation', 'value' : o_act_pgre.id_ic_pgre },
			'atel_pgre' : {
				'label' : 'Atelier(s) concerné(s)',
				'value' : ', '.join([str(a.id_atel_pgre) for a in TAteliersPgreDossierPgre.objects.filter(
					id_doss_pgre = o_act_pgre
				).order_by('id_atel_pgre')])
			},
			'int_doss_pgre' : { 'label' : 'Intitulé de l\'action PGRE', 'value' : o_act_pgre.int_doss_pgre },
			'id_doss' : { 'label' : 'Dossier de correspondance', 'value' : o_act_pgre.id_doss or '' },
			'moa' : {
				'label' : 'Maître(s) d\'ouvrage(s)',
				'value' : ', '.join([str(m.id_org_moa) for m in TMoaDossierPgre.objects.filter(
					id_doss_pgre = o_act_pgre
				).order_by('id_org_moa')])
			},
			'id_pr_pgre' : { 'label' : 'Priorité', 'value' : o_act_pgre.id_pr_pgre },
			'mont_doss_pgre' : { 'label' : 'Montant dossier PGRE', 'value' : o_act_pgre.mont_doss_pgre_ppt },
			'obj_econ_ress_doss_pgre' : {
				'label' : 'Objectifs d\'économie de la ressource en eau (en m<sup>3</sup>)',
				'value' : o_act_pgre.obj_econ_ress_doss_pgre_ppt
			},
			'ann_prev_deb_doss_pgre' : {
				'label' : 'Année prévisionnelle du début de l\'action PGRE',
				'value' : o_act_pgre.ann_prev_deb_doss_pgre
			},
			'dt_deb_doss_pgre' : {
				'label' : 'Date de début de l\'action PGRE', 'value' : dt_fr(o_act_pgre.dt_deb_doss_pgre) or ''
			},
			'dt_fin_doss_pgre' : {
				'label' : 'Date de fin de l\'action PGRE', 'value' : dt_fr(o_act_pgre.dt_fin_doss_pgre) or ''
			},
			'id_nat_doss' : { 'label' : 'Nature de l\'action PGRE', 'value' : o_act_pgre.id_nat_doss },
			'id_av_pgre' : { 'label' : 'État d\'avancement', 'value' : o_act_pgre.id_av_pgre },
			'chem_pj_doss_pgre' : {
				'label' : 'Consulter la fiche action', 'value' : o_act_pgre.chem_pj_doss_pgre, 'pdf' : True
			},
			'comm_doss_pgre' : { 'label' : 'Commentaire', 'value' : o_act_pgre.comm_doss_pgre or '', 'text_area': True}
		}

		# J'initialise le tableau des points de contrôle de l'année courante.
		t_pdc = []
		econ_tot = 0
		for index, p in enumerate(qs_pdc) :

			# Je renseigne l'identifiant du dernier point de contrôle (le seul que l'on puisse modifier ou supprimer).
			pk = None
			if index == len(qs_pdc) - 1 :
				pk = p.pk

			t_pdc.append({
				'dt_contr_doss_pgre' : dt_fr(p.dt_contr_doss_pgre),
				'obj_real_contr_doss_pgre' : p.obj_real_contr_doss_pgre,
				'pk' : pk
			})

			# Je calcule l'économie totale réalisée.
			econ_tot += p.obj_real_contr_doss_pgre

		# Je stocke le jeu de données des photos de l'action PGRE.
		qs_ph_pgre = TPhotoPgre.objects.filter(id_doss_pgre = o_act_pgre)

		# J'initialise le tableau des photos de l'action PGRE.
		t_ph_pgre = [{
			'id_doss_pgre' : p.id_doss_pgre.pk,
			'chem_ph_pgre' : p.chem_ph_pgre,
			'int_ph_pgre' : p.int_ph_pgre,
			'int_ppv_ph_pgre' : p.id_ppv_ph,
			'dt_pv_ph_pgre' : dt_fr(p.dt_pv_ph_pgre) or '-',
			'pk' : p.pk
		} for p in qs_ph_pgre]

		# Je stocke le jeu de données des sous-actions de l'action PGRE.
		qs_ss_action_pgre = o_act_pgre.ss_action_pgre.all().order_by('-dt_deb_ss_action_pgre')

		# J'initialise le tableau des sous-actions de l'action PGRE.
		t_ss_action_pgre = [{
			'pk' : ssa.pk,
			'id_ss_act' : ssa.id_ss_act,
			'lib_ss_act' : ssa.lib_ss_act,
			'mont_ss_action_pgre' : ssa.mont_ss_action_pgre,
			'obj_econ_ress_ss_action_pgre' : ssa.obj_econ_ress_ss_action_pgre,
			't_nature_dossier' : ssa.t_nature_dossier,
			'id_av_pgre' : ssa.id_av_pgre,
			'dt_deb_ss_action_pgre' : dt_fr(ssa.dt_deb_ss_action_pgre),
			'dt_fin_ss_action_pgre' :  dt_fr(ssa.dt_fin_ss_action_pgre),
			'dt_prevision_ss_action_pgre' : dt_fr(ssa.dt_prevision_ss_action_pgre) or '-'
		} for ssa in qs_ss_action_pgre]

		# J'initialise le tableau des géométries de l'action PGRE.
		qs_geom_act_pgre = TDossierPgreGeom.objects.filter(id_doss_pgre = o_act_pgre)
		t_geom_act_pgre = []
		for g in qs_geom_act_pgre :
			if g.geom_pol :
				la_geom = geos.GEOSGeometry(g.geom_pol)
			if g.geom_lin :
				la_geom = geos.GEOSGeometry(g.geom_lin)
			if g.geom_pct :
				la_geom = geos.GEOSGeometry(g.geom_pct)
			t_geom_act_pgre.append(la_geom.geojson)

		# Je prépare la fenêtre modale relative au diaporama des photos de l'action PGRE.
		t_ph_pgre_diap = { 'li' : [], 'div' : [] }
		for index, p in enumerate(qs_ph_pgre) :

			t_attrs_li = ['data-target="#my-carousel"', 'data-slide-to="{0}"'.format(index)]
			if index == 0 :
				t_attrs_li.append('class="active"')
			li = '<li {0}></li>'.format(' '.join(t_attrs_li))

			class_div = 'item'
			if index == 0 :
				class_div += ' active'
			div = '''
			<div class="{0}">
				<img src="{1}">
			</div>
			'''.format(class_div, MEDIA_URL + str(p.chem_ph_pgre))

			t_ph_pgre_diap['li'].append(li)
			t_ph_pgre_diap['div'].append(div)

		# J'instancie des objets "formulaire".
		f_ajout_ph_pgre = GererPhotoPgre(prefix = 'GererPhotoPgre', k_doss_pgre = o_act_pgre)
		f_ajout_contr_act_pgre = GererControleActionPgre(prefix = 'GererControleActionPgre', k_doss_pgre = o_act_pgre)
		f_ajout_ss_action_pgre = GererSsActionPgre(prefix = 'GererSsActionPgre', k_doss_pgre = o_act_pgre)

		# J'initialise le gabarit de chaque champ de chaque formulaire.
		t_ajout_ph_pgre = init_f(f_ajout_ph_pgre)
		t_ajout_contr_act_pgre = init_f(f_ajout_contr_act_pgre)
		t_ajout_ss_action_pgre = init_f(f_ajout_ss_action_pgre)

		# Je déclare un tableau qui stocke le contenu de certaines fenêtres modales.
		t_cont_fm = {
			'ajout_pdc' : '''
			<form action="?action=ajouter-point-de-controle" name="f_ajout_pdc" method="post" onsubmit="soum_f(event)">
				<input name="csrfmiddlewaretoken" type="hidden" value="{0}">
				{1}
				{2}
				{3}
				<button class="center-block green-btn my-btn" type="submit">Valider</button>
			</form>
			'''.format(
				csrf(request)['csrf_token'],
				t_ajout_contr_act_pgre['za_num_doss_pgre'],
				t_ajout_contr_act_pgre['dt_contr_doss_pgre'],
				t_ajout_contr_act_pgre['obj_real_contr_doss_pgre']
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
				reverse('ajout_ph_pgre'),
				csrf(request)['csrf_token'],
				t_ajout_ph_pgre['za_num_doss_pgre'],
				t_ajout_ph_pgre['int_ph_pgre'],
				t_ajout_ph_pgre['descr_ph_pgre'],
				t_ajout_ph_pgre['id_ppv_ph'],
				t_ajout_ph_pgre['dt_pv_ph_pgre'],
				t_ajout_ph_pgre['chem_ph_pgre']
			),
			'lanc_diap' : '''
			<div class="carousel my-carousel slide" data-interval="false" data-ride="carousel" id="my-carousel">
				<ol class="carousel-indicators">{0}</ol>
				<div class="carousel-inner" role="listbox">{1}</div>
				<a href="#my-carousel" class="left carousel-control" data-slide="prev" role="button">
					<span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>
				</a>
				<a href="#my-carousel" class="right carousel-control" data-slide="next" role="button">
					<span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
				</a>
			</div>
			'''.format(
				'\n'.join(t_ph_pgre_diap['li']),
				'\n'.join(t_ph_pgre_diap['div'])
			),
			'ajout_ss_action' : '''
			<form action="{action}" enctype="multipart/form-data" name="f_ajout_ss_action" method="post" onsubmit="soum_f(event)">
				<input name="csrfmiddlewaretoken" type="hidden" value="{csrf}">
				{pk}
				<div class="row">
					<div class="col-sm-6">{lib}</div>
					<div class="col-sm-6">{desc}</div>
					<div class="col-sm-12">{comm}</div>
					<div class="col-sm-12">{dt_prev}</div>
					<div class="col-sm-6">{dt_deb}</div>
					<div class="col-sm-6">{dt_fin}</div>
					<div class="col-sm-6">{mont}</div>
					<div class="col-sm-6">{obj_econ}</div>
					<div class="col-sm-12">{moa}</div>
					<div class="col-sm-6">{nat_doss}</div>
					<div class="col-sm-6">{id_av_pgre}</div>
				</div>
				<button class="center-block green-btn my-btn" type="submit">Valider</button>
			</form>
			'''.format(
				action=reverse('ajout_ss_act_pgre'),
				csrf=csrf(request)['csrf_token'],
				pk=t_ajout_ss_action_pgre['za_num_doss_pgre'],
				lib=t_ajout_ss_action_pgre['lib_ss_act'],
				comm=t_ajout_ss_action_pgre['comm_ss_act'],
				desc=t_ajout_ss_action_pgre['desc_ss_act'],
				dt_prev=t_ajout_ss_action_pgre['dt_prevision_ss_action_pgre'],
				dt_deb=t_ajout_ss_action_pgre['dt_deb_ss_action_pgre'],
				dt_fin=t_ajout_ss_action_pgre['dt_fin_ss_action_pgre'],
				mont=t_ajout_ss_action_pgre['mont_ss_action_pgre'],
				obj_econ=t_ajout_ss_action_pgre['obj_econ_ress_ss_action_pgre'],
				moa=t_ajout_ss_action_pgre['moa'],
				nat_doss=t_ajout_ss_action_pgre['t_nature_dossier'],
				id_av_pgre=t_ajout_ss_action_pgre['id_av_pgre'],
			)
		}
		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('ajout_ph', 'Ajouter une photo', t_cont_fm['ajout_ph']),
			init_fm('modif_carto', 'Modifier une action PGRE'),
			init_fm('suppr_act_pgre', 'Supprimer une action PGRE'),
			init_fm('ajout_ss_action', 'Ajouter une sous-action PGRE', t_cont_fm['ajout_ss_action']),
		]

		# Je complète le tableau de fenêtres modales dans le cas où l'action PGRE comporte des photos.
		if len(t_ph_pgre) > 0 :
			t_fm += [
				init_fm('cons_ph', 'Consulter une photo'),
				init_fm('lanc_diap', 'Lancer le diaporama', t_cont_fm['lanc_diap']),
				init_fm('suppr_ph', 'Supprimer une photo')
			]

		# Je regarde si l'utilisateur connecté provient de la DDTM.
		est_ddtm = False
		if not settings.CONSTRAINT_DDTM : est_ddtm = True
		if TUtilisateur.objects.get(pk = request.user.pk).id_org.pk == T_DONN_BDD_INT['DDTM_PK'] : est_ddtm = True

		# Je complète le tableau de fenêtres modales dans le cas où l'utilisateur connecté provient de la DDTM.
		if est_ddtm == True :
			t_fm += [
				init_fm('ajout_pdc', 'Ajouter un point de contrôle', t_cont_fm['ajout_pdc']),
				init_fm('suppr_pdc', 'Supprimer le dernier point de contrôle')
			]

		# Je complète le tableau de fenêtres modales dans le cas où l'action PGRE comporte des sous-actions.
		if len(t_ajout_ss_action_pgre) > 0 :
			t_fm += [
				init_fm('cons_ss_action', 'Consulter une sous-action'),
				init_fm('suppr_ss_action', 'Supprimer une sous-action')
			]

		# J'affiche le template.
		output = render(
			request,
			'./pgre/cons_act_pgre.html',
			{
				'a' : o_act_pgre,
				'annee' : annee,
				'econ_tot' : econ_tot,
				'est_ddtm' : est_ddtm,
				'forbidden' : ger_droits(request.user, t_coupl_val, False, False),
				't_attrs_act_pgre' : init_pg_cons(t_attrs_act_pgre),
				't_fm' : t_fm,
				't_geom_act_pgre' : t_geom_act_pgre,
				't_pdc' : t_pdc,
				't_pdc_length' : len(t_pdc),
				't_ph_pgre' : t_ph_pgre,
				't_ph_pgre_length' : len(t_ph_pgre),
				't_ss_action_pgre': t_ss_action_pgre,
				'title' : 'Consulter une action PGRE'
			}
		)

		# Je supprime la variable de session liée au navigateur à onglets relatif à une action PGRE.
		del request.session['tab_act_pgre']

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" dont la clé est "action".
			get_action = request.GET['action']

			# Je traite le cas où je dois supprimer une photo.
			if get_action == 'supprimer-photo' :
				if request.GET['photo'] :
					output = HttpResponse(suppr(reverse('suppr_ph_pgre', args = [request.GET['photo']])))

			# Je traite le cas où je dois consulter une photo.
			if get_action == 'consulter-photo' :
				if request.GET['photo'] :

					# Je vérifie l'existence d'un objet TPhoto.
					o_ph_pgre = get_object_or_404(TPhotoPgre, pk = request.GET['photo'])

					# Je vérifie le droit de lecture.
					ger_droits(request.user, t_coupl_val)

					# Je prépare le volet de consultation de la photo.
					t_attrs_ph_pgre = {
						'id_doss_pgre' : { 'label' : 'Numéro de l\'action PGRE', 'value' : o_ph_pgre.id_doss_pgre },
						'int_ph_pgre' : { 'label' : 'Intitulé de la photo', 'value' : o_ph_pgre.int_ph_pgre },
						'descr_ph_pgre' : { 'label' : 'Description', 'value' : o_ph_pgre.descr_ph_pgre or '' },
						'id_ppv_ph' : { 'label' : 'Période de prise de vue', 'value' : o_ph_pgre.id_ppv_ph },
						'dt_pv_ph_pgre' : {
							'label' : 'Date de prise de vue', 'value' : dt_fr(o_ph_pgre.dt_pv_ph_pgre) or ''
						}
					}

					t_attrs_ph_pgre = init_pg_cons(t_attrs_ph_pgre)

					output = HttpResponse(
					'''
					<div style="margin-bottom: -20px;">
						<div class="attribute-wrapper">
							<span class="attribute-label">Visualisation</span>
							<img src="{0}{1}" style="display: block; margin: 0 auto; max-width: 100%;">
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
						o_ph_pgre.chem_ph_pgre,
						t_attrs_ph_pgre['id_doss_pgre'],
						t_attrs_ph_pgre['int_ph_pgre'],
						t_attrs_ph_pgre['descr_ph_pgre'],
						t_attrs_ph_pgre['id_ppv_ph'],
						t_attrs_ph_pgre['dt_pv_ph_pgre']
					))

			# Je traite le cas où je dois ajouter un point de contrôle.
			if get_action == 'ajouter-point-de-controle' :

				# Je soumets le formulaire.
				f_ajout_pdc = GererControleActionPgre(
					request.POST, prefix = 'GererControleActionPgre', k_doss_pgre = o_act_pgre
				)

				if f_ajout_pdc.is_valid() :

					# Je créé la nouvelle instance TControleDossierPgre.
					o_nv_pdc = f_ajout_pdc.save(commit = False)
					o_nv_pdc.save()

					# J'affiche le message de succès.
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'Le point de contrôle a été ajouté avec succès à l\'action PGRE N°{0}.'.format(
								o_nv_pdc.id_doss_pgre
							),
							'redirect' : reverse('cons_act_pgre', args = [o_nv_pdc.id_doss_pgre.pk])
						}}),
						content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs.
					t_err = {}
					for k, v in f_ajout_pdc.errors.items() :
						t_err['GererControleActionPgre-{0}'.format(k)] = v
					output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

			# Je traite le cas où je dois initialiser les points du graphique des points de contrôle.
			if get_action == 'initialiser-graphique' :
				t_pts_graph_pdc = [[], []]
				econ_tot = 0
				for index, c in enumerate(qs_pdc) :

					# Je stocke le timestamp ainsi que le niveau d'économie de la ressource en eau.
					ts = time.mktime(c.dt_contr_doss_pgre.timetuple()) * 1000
					econ_tot += c.obj_real_contr_doss_pgre

					# J'empile le tableau des points de contrôle.
					t_pts_graph_pdc[0].append([ts, econ_tot])

					# Je prépare la courbe parallèle à l'axe des abscisses.
					if index == 0 or index == len(qs_pdc) - 1 :
						t_pts_graph_pdc[1].append([ts, o_act_pgre.obj_econ_ress_doss_pgre])

				output = HttpResponse([t_pts_graph_pdc], content_type = 'application/json')

			# Je traite le cas où je dois supprimer un point de contrôle.
			if get_action == 'supprimer-point-de-controle' :
				if request.GET['point-de-controle'] :
					output = HttpResponse(suppr(reverse('suppr_pdc', args = [request.GET['point-de-controle']])))

			# Je traite le cas où je dois supprimer une sous-action.
			if get_action == 'supprimer-sous-action-pgre' :
				if request.GET['sous-action'] :
					output = HttpResponse(suppr(reverse('suppr_ss_act_pgre', args = [request.GET['sous-action']])))

			# Je traite le cas où je dois une action PGRE.
			if get_action == 'supprimer-action-pgre' :
				output = HttpResponse(suppr(reverse('suppr_act_pgre', args = [o_act_pgre.pk])))

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'une photo.
request : Objet requête
'''
@verif_acc
def ajout_ph_pgre(request) :

	# Imports
	from app.forms.pgre import GererPhotoPgre
	from app.functions import ger_droits
	from app.models import TDossierPgre
	from app.models import TMoaDossierPgre
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from styx.settings import T_DONN_BDD_INT
	import json

	output = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		try :
			o_act_pgre_droit = TDossierPgre.objects.get(
				num_doss_pgre = request.POST.get('GererPhotoPgre-za_num_doss_pgre')
			)
		except :
			o_act_pgre_droit = None
		if o_act_pgre_droit :
			ger_droits(
				request.user,
				[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
					id_doss_pgre = o_act_pgre_droit
				)],
				False
			)

		# Je soumets le formulaire.
		f_ajout_ph_pgre = GererPhotoPgre(request.POST, request.FILES, prefix = 'GererPhotoPgre')

		if f_ajout_ph_pgre.is_valid() :

			# Je créé la nouvelle instance TPhotoPgre.
			o_nvelle_ph_pgre = f_ajout_ph_pgre.save(commit = False)
			o_nvelle_ph_pgre.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'La photo a été ajoutée avec succès à l\'action PGRE N°{0}.'.format(
						o_nvelle_ph_pgre.id_doss_pgre
					),
					'redirect' : reverse('cons_act_pgre', args = [o_nvelle_ph_pgre.id_doss_pgre.pk])
				}}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_act_pgre'] = '#ong_ph'

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_ph_pgre.errors.items() :
				t_err['GererPhotoPgre-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'une photo ou de traiter le formulaire de mise à jour
d'une photo.
request : Objet requête
_p : Identifiant d'une photo
'''
@verif_acc
def modif_ph_pgre(request, _p) :

	# Imports
	from app.forms.pgre import GererPhotoPgre
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.models import TMoaDossierPgre
	from django.core.urlresolvers import reverse
	from app.models import TPhotoPgre
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from styx.settings import T_DONN_BDD_INT
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TPhotoPgre.
	o_ph_pgre = get_object_or_404(TPhotoPgre, pk = _p)

	# Je vérifie le droit d'écriture.
	ger_droits(
		request.user,
		[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
			id_doss_pgre = o_ph_pgre.id_doss_pgre
		)],
		False
	)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_ph_pgre = GererPhotoPgre(instance = o_ph_pgre, prefix = 'GererPhotoPgre')

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_ph', 'Modifier une photo')
		]

		# J'affiche le template.
		output = render(
			request,
			'./pgre/modif_ph_pgre.html',
			{
				'f_modif_ph_pgre' : init_f(f_modif_ph_pgre),
				'p' : o_ph_pgre,
				't_fm' : t_fm,
				'title' : 'Modifier une photo'
			}
		)

	else :

		# Je soumets le formulaire.
		f_modif_ph_pgre = GererPhotoPgre(request.POST, request.FILES, instance = o_ph_pgre, prefix = 'GererPhotoPgre')

		if f_modif_ph_pgre.is_valid() :

			# Je modifie l'instance TPhotoPgre.
			o_ph_pgre_modif = f_modif_ph_pgre.save(commit = False)
			o_ph_pgre_modif.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'La photo a été mise à jour avec succès.',
					'redirect' : reverse('cons_act_pgre', args = [o_ph_pgre.id_doss_pgre.pk])
				}}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_act_pgre'] = '#ong_ph'

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_modif_ph_pgre.errors.items() :
				t_err['GererPhotoPgre-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet de traiter le formulaire de suppression d'une photo.
request : Objet requête
_p : Identifiant d'une photo
'''
@verif_acc
@csrf_exempt
def suppr_ph_pgre(request, _p) :

	# Imports
	from app.functions import ger_droits
	from app.models import TMoaDossierPgre
	from app.models import TPhotoPgre
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from styx.settings import T_DONN_BDD_INT
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TPhoto.
	o_ph_pgre = get_object_or_404(TPhotoPgre, pk = _p)

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		ger_droits(
			request.user,
			[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
				id_doss_pgre = o_ph_pgre.id_doss_pgre
			)],
			False
		)

		# Je pointe vers l'objet TDossierPgre lié à l'objet TPhotoPgre.
		o_act_pgre = o_ph_pgre.id_doss_pgre

		# Je supprime l'objet TPhotoPgre.
		o_ph_pgre.delete()

		# J'affiche le message de succès.
		output = HttpResponse(
			json.dumps({ 'success' : {
				'message' : 'La photo a été supprimée avec succès de l\'action PGRE N°{0}.'.format(o_act_pgre),
				'redirect' : reverse('cons_act_pgre', args = [o_act_pgre.pk])
			}}),
			content_type = 'application/json'
		)

		# Je renseigne l'onglet actif après rechargement de la page.
		request.session['tab_act_pgre'] = '#ong_ph'

	return output

'''
Cette vue permet d'afficher la page de modification d'un point de contrôle ou de traiter le formulaire de mise à jour
d'un point de contrôle.
request : Objet requête
_p : Identifiant d'un point de contrôle
'''
@verif_acc
def modif_pdc(request, _p) :

	# Imports
	from app.forms.pgre import GererControleActionPgre
	from app.functions import ger_droits
	from app.functions import init_f
	from app.functions import init_fm
	from app.models import TMoaDossierPgre
	from django.core.urlresolvers import reverse
	from app.models import TControleDossierPgre
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from styx.settings import T_DONN_BDD_INT
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TPhotoPgre.
	o_pdc = get_object_or_404(TControleDossierPgre, pk = _p)

	# Je vérifie le droit d'écriture.
	ger_droits(
		request.user,
		[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
			id_doss_pgre = o_pdc.id_doss_pgre
		)],
		False
	)

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_pdc = GererControleActionPgre(instance = o_pdc, prefix = 'GererControleActionPgre')

		# Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_pdc', 'Modifier le dernier point de contrôle')
		]

		# J'affiche le template.
		output = render(
			request,
			'./pgre/modif_pdc.html',
			{
				'f_modif_pdc' : init_f(f_modif_pdc),
				'p' : o_pdc,
				't_fm' : t_fm,
				'title' : 'Modifier le dernier point de contrôle'
			}
		)

	else :

		# Je soumets le formulaire.
		f_modif_pdc = GererControleActionPgre(
			request.POST, request.FILES, instance = o_pdc, prefix = 'GererControleActionPgre'
		)

		if f_modif_pdc.is_valid() :

			# Je modifie l'instance TControleDossierPgre.
			o_pdc_modif = f_modif_pdc.save(commit = False)
			o_pdc_modif.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : '''
					Le dernier point de contrôle de l'action PGRE N°{0} a été mis à jour avec succès.
					'''.format(o_pdc_modif.id_doss_pgre),
					'redirect' : reverse('cons_act_pgre', args = [o_pdc_modif.id_doss_pgre.pk])
				}}),
				content_type = 'application/json'
			)

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_modif_pdc.errors.items() :
				t_err['GererControleActionPgre-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet de traiter le formulaire de suppression d'un point de contrôle.
request : Objet requête
_p : Identifiant d'un point de contrôle
'''
@verif_acc
@csrf_exempt
def suppr_pdc(request, _p) :

	# Imports
	from app.functions import ger_droits
	from app.models import TControleDossierPgre
	from app.models import TMoaDossierPgre
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from styx.settings import T_DONN_BDD_INT
	import json

	output = HttpResponse()

	# Je vérifie l'existence d'un objet TControleDossierPgre.
	o_pdc = get_object_or_404(TControleDossierPgre, pk = _p)

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		ger_droits(
			request.user,
			[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
				id_doss_pgre = o_pdc.id_doss_pgre
			)],
			False
		)

		# Je pointe vers l'objet TDossierPgre lié à l'objet TControleDossierPgre.
		o_act_pgre = o_pdc.id_doss_pgre

		# Je supprime l'objet TControleDossierPgre.
		o_pdc.delete()

		# J'affiche le message de succès.
		output = HttpResponse(
			json.dumps({ 'success' : {
				'message' : '''
				Le dernier point de contrôle de l'action PGRE N°{0} a été supprimé avec succès.
				'''.format(o_act_pgre),
				'redirect' : reverse('cons_act_pgre', args = [o_act_pgre.pk])
			}}),
			content_type = 'application/json'
		)

	return output

'''
Affichage du formulaire de réalisation d'un état "action PGRE" ou traitement d'une requête quelconque
_req : Objet "requête"
'''
@verif_acc
def filtr_act_pgre(_req) :

	# Imports
	from app.forms.pgre import FiltrerActionsPgre
	from app.functions import datatable_reset
	from app.functions import dt_fr
	from app.functions import gen_cdc
	from app.models import TDossierPgre
	from django.http import HttpResponse
	from django.shortcuts import render
	import csv
	import json

	output = None

	if _req.method == 'GET' :
		if 'action' in _req.GET :
			if _req.GET['action'] == 'exporter-csv' :

				# Génération d'un fichier au format CSV
				output = HttpResponse(content_type = 'text/csv', charset = 'cp1252')
				output['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(gen_cdc())

				# Accès en écriture
				writer = csv.writer(output, delimiter = ';')

				# Initialisation des données "historique"
				donnees = _req.session.get('filtr_act_pgre') if 'filtr_act_pgre' in _req.session else []

				# Définition de l'en-tête
				writer.writerow([
					'Numéro de l\'action PGRE',
					'Intitulé de l\'action PGRE',
					'Instance de concertation',
					'Atelier(s) concerné(s)',
					'Dossier de correspondance',
					'Maître(s) d\'ouvrage(s)',
					'Priorité',
					'Montant',
					'Objectifs d\'économie de la ressource en eau (en m3)',
					'Année prévisionnelle du début de l\'action PGRE',
					'Date de début de l\'action PGRE',
					'Date de fin de l\'action PGRE',
					'Nature de l\'action PGRE',
					'État d\'avancement',
					'Commentaire',
					'Action parente',
				])

				for dpgre in TDossierPgre.objects.filter(pk__in = donnees) :
					# Ajout d'une nouvelle ligne
					writer.writerow([
						dpgre.num_doss_pgre,
						dpgre.int_doss_pgre,
						dpgre.id_ic_pgre,
						', '.join([str(apgre) for apgre in dpgre.atel_pgre.all()]),
						dpgre.id_doss,
						', '.join([str(m) for m in dpgre.moa.all()]),
						dpgre.id_pr_pgre,
						dpgre.mont_doss_pgre_ppt,
						dpgre.obj_econ_ress_doss_pgre_ppt,
						dpgre.ann_prev_deb_doss_pgre,
						dt_fr(dpgre.dt_deb_doss_pgre),
						dt_fr(dpgre.dt_fin_doss_pgre),
						dpgre.id_nat_doss,
						dpgre.id_av_pgre,
						dpgre.comm_doss_pgre,
						'',  # Action parente
					])
					for ssa in dpgre.ss_action_pgre.all():
						# Ajout d'une nouvelle ligne pour les sous-action
						writer.writerow([
							'',  # Numéro de l'action PGRE
							ssa.lib_ss_act,
							'',  # Instance de concertation
							'',  # Ateliers concernés
							'',  # Dossier de correspondance
							', '.join([str(m) for m in ssa.moa.all()]),
							'',  # Priorité
							ssa.mont_ss_action_pgre,
							ssa.obj_econ_ress_ss_action_pgre,
							ssa.dt_prevision_ss_action_pgre.year,
							dt_fr(ssa.dt_deb_ss_action_pgre),
							dt_fr(ssa.dt_fin_ss_action_pgre),
							ssa.t_nature_dossier,
							ssa.id_av_pgre,
							ssa.comm_ss_act,
							dpgre.num_doss_pgre,
						])

		else :

			# Initialisation de la variable "historique"
			_req.session['filtr_act_pgre'] = []

			# Initialisation du formulaire et de ses attributs
			form_filtr_act_pgre = FiltrerActionsPgre()

			# Affichage du template
			output = render(_req, './pgre/filtr_act_pgre.html', {
				'dtab_filtr_act_pgre' : form_filtr_act_pgre.get_datatable(_req),
				'form_filtr_act_pgre' : form_filtr_act_pgre.get_form(_req),
				'title' : 'Réalisation d\'états PGRE en sélectionnant des actions PGRE'
			})

	else :

		# Soumission du formulaire
		form_filtr_act_pgre = FiltrerActionsPgre(_req.POST)

		# Rafraîchissement de la datatable ou affichage des erreurs
		if form_filtr_act_pgre.is_valid() :
			output = datatable_reset(form_filtr_act_pgre.get_datatable(_req))
		else :
			output = HttpResponse(json.dumps(form_filtr_act_pgre.errors), content_type = 'application/json')

	return output

'''
Cette vue permet de traiter le formulaire d'ajout d'une sous-action.
request : Objet requête
'''
@verif_acc
def ajout_ss_act_pgre(request) :

	# Imports
	from app.forms.pgre import GererSsActionPgre
	from app.functions import ger_droits
	from app.models import TDossierPgre
	from app.models import TMoaDossierPgre
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from styx.settings import T_DONN_BDD_INT
	import json

	output = HttpResponse()

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		try :
			o_act_pgre = TDossierPgre.objects.get(
				num_doss_pgre = request.POST.get('GererSsActionPgre-za_num_doss_pgre')
			)
		except :
			o_act_pgre = None

		if o_act_pgre :
			ger_droits(
				request.user,
				[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
					id_doss_pgre = o_act_pgre
				)],
				False
			)

		# Je soumets le formulaire.
		f_ajout_ss_action_pgre = GererSsActionPgre(
			request.POST, request.FILES, prefix = 'GererSsActionPgre')

		if f_ajout_ss_action_pgre.is_valid() :

			# Je créé la nouvelle instance TPhotoPgre.
			o_nvelle_ss_act_pgre = f_ajout_ss_action_pgre.save()

			# J'ajoute la sous-action à son action parente
			o_act_pgre.ss_action_pgre.add(o_nvelle_ss_act_pgre)

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : "La sous-action N°{0} a été crée pour l'action PGRE N°{1}.".format(
						o_nvelle_ss_act_pgre.id_ss_act, o_act_pgre.id_doss_pgre),
					'redirect' : reverse('cons_act_pgre', args = [o_act_pgre.pk])
				}}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_act_pgre'] = '#ong_ss_action'

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_ss_action_pgre.errors.items() :
				t_err['GererSsActionPgre-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	return output

'''
Cette vue permet d'afficher la page de modification d'une sous-action ou de traiter le formulaire de mise à jour
d'une sous-action.
request : Objet requête
_ssa : Identifiant d'une sous-action
'''
@verif_acc
def modif_ss_act_pgre(request, _ssa) :

	# Imports
	from app.forms.pgre import GererSsActionPgre
	from app.functions import init_f
	from app.functions import init_fm
	from app.functions import ger_droits
	from app.models import TDossierPgre
	from app.models import TMoaDossierPgre
	from app.models import TDossierSsAction
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from styx.settings import T_DONN_BDD_INT
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json

	output = HttpResponse()

	o_ss_action_pgre = get_object_or_404(TDossierSsAction, pk=_ssa)

	if request.method == 'POST' :

		# Je vérifie le droit d'écriture.
		o_act_pgre = o_ss_action_pgre.tdossierpgre_set.first() or None
		if o_act_pgre :
			ger_droits(
				request.user,
				[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
					id_doss_pgre = o_act_pgre
				)],
				False
			)

		# Je soumets le formulaire.
		f_modif_ss_action_pgre = GererSsActionPgre(
			request.POST, request.FILES,
			prefix = 'GererSsActionPgre',
			instance=o_ss_action_pgre)

		if f_modif_ss_action_pgre.is_valid() :

			# Je créé la nouvelle instance TPhotoPgre.
			o_ss_act_pgre = f_modif_ss_action_pgre.save()

			# J'affiche le message de succès.
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : "La sous-action N°{0} a bien été mise à jour pour l'action PGRE N°{1}.".format(
						o_ss_act_pgre.id_ss_act, o_act_pgre.id_doss_pgre),
					'redirect' : reverse('cons_act_pgre', args = [o_act_pgre.pk])
				}}),
				content_type = 'application/json'
			)

			# Je renseigne l'onglet actif après rechargement de la page.
			request.session['tab_act_pgre'] = '#ong_ss_action'

		else :

			# J'affiche les erreurs.
			t_err = {}
			for k, v in f_ajout_ss_action_pgre.errors.items() :
				t_err['GererSsActionPgre-{0}'.format(k)] = v
			output = HttpResponse(json.dumps(t_err), content_type = 'application/json')

	if request.method == 'GET' :

		# J'instancie un objet "formulaire".
		f_modif_ss_action_pgre = GererSsActionPgre(
			instance = o_ss_action_pgre,
			prefix = 'GererSsActionPgre')

		# # Je déclare un tableau de fenêtres modales.
		t_fm = [
			init_fm('modif_ss_action_pgre', 'Modifier une sous-action')
		]

		# J'affiche le template.
		output = render(
			request,
			'pgre/modif_ss_act_pgre.html',
			{
				'f_modif_ss_action_pgre' : init_f(f_modif_ss_action_pgre),
				'p_act' : o_ss_action_pgre.tdossierpgre_set.first(),
				't_fm' : t_fm,
				'title' : 'Modifier une sous-action'
			}
		)
	return output
'''
Cette vue permet de traiter le formulaire de suppression d'une sous-action.
request : Objet requête
_ssa : Identifiant d'une sous-action
'''
@verif_acc
@csrf_exempt
def suppr_ss_act_pgre(request, _ssa) :

	# Imports
	from app.functions import ger_droits
	from app.models import TMoaDossierPgre
	from app.models import TDossierSsAction
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from styx.settings import T_DONN_BDD_INT
	import json

	output = HttpResponse()


	# Je vérifie l'existance d'un objet TDossierSsAction
	o_ss_action_pgre = get_object_or_404(TDossierSsAction, pk=_ssa)

	o_act_pgre = o_ss_action_pgre.tdossierpgre_set.first() or None

	if o_act_pgre :
		# Je vérifie le droit d'écriture.
		ger_droits(
			request.user,
			[(m.id_org_moa.pk, T_DONN_BDD_INT['PGRE_PK']) for m in TMoaDossierPgre.objects.filter(
				id_doss_pgre = o_act_pgre
			)],
			False
		)

	if request.method == 'POST' :

		# Je supprime l'objet TDossierSsAction.
		o_ss_action_pgre.delete()

		# J'affiche le message de succès.
		output = HttpResponse(
			json.dumps({ 'success' : {
				'message' : 'La sous-action a été supprimée avec succès de l\'action PGRE N°{0}.'.format(o_act_pgre),
				'redirect' : reverse('cons_act_pgre', args = [o_act_pgre.pk])
			}}),
			content_type = 'application/json'
		)

		# Je renseigne l'onglet actif après rechargement de la page.
		request.session['tab_act_pgre'] = '#ong_ss_action'

	return output
