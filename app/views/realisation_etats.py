from app.decorators import *
from app.forms import realisation_etats
from app.functions import *
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from functools import reduce
from itertools import chain
from styx.settings import MEDIA_ROOT, MEDIA_URL
from time import localtime, strftime
import csv
import json
import operator

@verif_acces
def exporter_csv_selectionner_dossiers(request, p_complet) :

	reponse = None

	if request.method == 'GET' :

		# J'initialise le nom du fichier CSV.
		nom_fichier = [
			str(request.session['utilisateur']['id_util']),
			strftime('%d%m%Y%H%M%S', localtime())
		]
		nom_fichier = '_'.join(nom_fichier).lower()
		nom_fichier = crypt_val(nom_fichier)
		nom_fichier += '.csv'

		# J'initialise le chemin du fichier CSV.
		chemin_fichier = MEDIA_ROOT + '\\temp\\' + nom_fichier

		# J'ouvre le fichier CSV.
		with open(chemin_fichier, 'w', newline = '') as fichier :

			# Je définis le droit d'écriture ainsi que le délimiteur.
			writer = csv.writer(fichier, delimiter = ';')

			if 'export_csv_dossiers_selectionnes' in request.session :

				# J'importe l'ensemble des dossiers sélectionnés après X recherches (sans doublons).
				tab_lignes = request.session['export_csv_dossiers_selectionnes']

				if p_complet == False :

					# J'écris l'en-tête du fichier CSV.
					writer.writerow((
						'numero_du_dossier',
						'intitule_du_dossier',
						'moa_du_dossier',
						'date_de_deliberation_au_moa_du_dossier',
						'programme_du_dossier',
						'nature_du_dossier',
						'montant_ht_du_dossier'
					))

					# Je parcours la datatable afin de pouvoir compléter le fichier CSV.
					for i in range(0, len(tab_lignes)) :
						ligne = tab_lignes[i]
						tab_cellules_ligne = []
						for j in range(0, len(ligne) - 1) :
							cellule = ligne[j]
							tab_cellules_ligne.append(cellule)

						# J'écris une ligne du fichier CSV.
						writer.writerow(tab_cellules_ligne)

				else :

					for i in range(0, len(tab_lignes)) :

						# Je récupère le numéro du dossier courant.
						v_numero_dossier = tab_lignes[i][0]

						# [TODO] (numéro du dossier associé...) 
						obj_dossier = TDossier.objects.get(num_doss = v_numero_dossier)
						tab_cellules_ligne = [
							conv_none(obj_dossier.comm_doss),
							conv_none(obj_dossier.descr_objs_doss),
							conv_none(reecr_dt(obj_dossier.dt_av_cp_doss)),
							conv_none(reecr_dt(obj_dossier.dt_delib_moa_doss)),
							conv_none(obj_dossier.int_doss),
							conv_none(float_to_int(obj_dossier.mont_ht_doss)),
							conv_none(float_to_int(obj_dossier.mont_ttc_doss)),
							conv_none(obj_dossier.num_doss),
							conv_none(obj_dossier.quant_objs_doss),
							conv_none(obj_dossier.quant_real_doss),
							conv_none(obj_dossier.id_nat_doss.int_nat_doss),
							conv_none(obj_dossier.id_type_doss.int_type_doss),
							
							conv_none(obj_dossier.id_act),
							conv_none(obj_dossier.id_ss_axe),
							conv_none(obj_dossier.id_axe),
							conv_none(obj_dossier.id_progr.int_progr),
							conv_none(obj_dossier.id_av_cp.int_av_cp),
							conv_none(obj_dossier.id_techn.n_techn) + ' ' + conv_none(obj_dossier.id_techn.pren_techn),
							conv_none(obj_dossier.id_org_moa.id_org_moa.n_org),
							conv_none(obj_dossier.id_av.int_av)
						]

						# J'écris une ligne du fichier CSV.
						writer.writerow(tab_cellules_ligne)

			# Je ferme le fichier CSV.
			fichier.close()

		# Je permets le téléchargement du fichier CSV produit.
		reponse = redirect(MEDIA_URL + 'temp/' + nom_fichier)

		return reponse

'''
Cette vue permet d'afficher le menu du module de réalisation des états.
request : Objet requête
'''
@verif_acces
def index(request) :

	# J'affiche le template.
	return render(
		request,
		'./realisation_etats/main.html',
		{ 'title' : 'Réalisation d\'états' }
	)

@verif_acces
@nett_form
def selectionner_dossiers(request) :

	reponse = None

	if request.method == 'GET' :

		# Je déclare un tableau de session qui contiendra l'ensemble des dossiers sélectionnés après X recherches (avec
		# doublons).
		request.session['dossiers_selectionnes'] = []

		# Je déclare un tableau de session qui contiendra l'ensemble des dossiers sélectionnés après X recherches (sans
		# doublons) afin de pouvoir générer un fichier au format CSV.
		request.session['export_csv_dossiers_selectionnes'] = []

		# Je déclare un objet "formulaire" permettant une future manipulation des champs.
		f1 = realisation_etats.SelectionnerDossiers()

		# J'affiche le template.
		reponse = render(
			request,
			'./realisation_etats/selectionner_dossiers.html',
			{ 
				'f1' : init_form(f1),
				'title' : 'Réalisation d\'états en sélectionnant des dossiers'
			}
		)

	else :
		if 'action' in request.GET :
			if len(request.GET) == 1 and request.GET['action'] == 'filtrer-dossiers' :

				# Je déclare un objet "formulaire" permettant de traiter le formulaire de réalisation d'un état en
				# sélectionnant les dossiers.
				f1 = realisation_etats.SelectionnerDossiers(request.POST)

				# Je réinitialise la liste des choix pour certaines listes déroulantes du formulaire (prévention d'erreurs).
				v_programme = request.POST.get('zld_progr')
				v_axe = request.POST.get('zld_axe')
				v_sous_axe = request.POST.get('zld_ss_axe')
				v_action = request.POST.get('zld_act')

				axe_valide = False
				try :
					TAxe.objects.get(id_progr = v_programme, id_axe = v_axe)
					axe_valide = True
				except :
					if v_axe == 'D' or v_axe == 'DBP' :
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
					if v_sous_axe == 'D' or v_sous_axe == 'DBP' :
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
					if v_action == 'D' or v_action == 'DBP' :
						action_valide = True
					else :
						pass

				if action_valide == True :
					f1.fields['zld_act'].choices = [(
						v_action, 
						v_action
					)]

				if f1.is_valid() :

					# Je récupère les données du formulaire valide.
					tab_donnees = f1.cleaned_data
					tab_moa = request.POST.getlist('cbsm_moa')
					v_programme = integer(tab_donnees['zld_progr'])
					v_axe = integer(tab_donnees['zld_axe'])
					v_sous_axe = integer(tab_donnees['zld_ss_axe'])
					v_action = integer(tab_donnees['zld_act'])
					v_nature_dossier = integer(tab_donnees['zl_nat_doss'])
					v_date_debut_deliberation_moa_dossier = chang_form_dt(nett_val(tab_donnees['zd_dt_delib_moa_doss_tr_deb']))
					v_date_fin_deliberation_moa_dossier = chang_form_dt(nett_val(tab_donnees['zd_dt_delib_moa_doss_tr_fin']))
					v_avis_cp_dossier = integer(tab_donnees['zl_av_cp'])
					v_montant_ht_dossier_min = nett_val(tab_donnees['zs_mont_ht_doss_min'])
					v_montant_ht_dossier_max = nett_val(tab_donnees['zs_mont_ht_doss_max'])
					v_dossiers_non_soldes = tab_donnees['cb_doss_dep_non_sold']
					v_integration_dossiers_associes = tab_donnees['cb_int_doss_ass']
					v_ajouter_selection_existante = tab_donnees['cb_ajout_select_exist']

					# Je déclare et j'empile le tableau des conditions ayant les clauses "OR" et "AND".
					args = []
					kwargs = {}

					for i in range(0, len(tab_moa)) :

						# Je convertis en entier l'identifiant du maître d'ouvrage courant.
						v_moa = integer(tab_moa[i])

						if v_moa < 0 :

							# Je réinitialise le tableau des conditions ayant la clause "OR" si la case "Tous" est
							# cochée.
							args = []

							# Je sors de la boucle.
							break;

						else :

							# J'empile le tableau des conditions ayant la clause "OR".
							les_moa_anciens = TRegroupementMoa.objects.filter(id_org_moa_fil = v_moa)
							for un_moa_ancien in les_moa_anciens :
								args.append(Q(**{ 'id_org_moa' : un_moa_ancien.id_org_moa_anc }))

							args.append(Q(**{ 'id_org_moa' : v_moa }))
							
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

					if v_date_debut_deliberation_moa_dossier is not None :
						kwargs['dt_delib_moa_doss__gte'] = v_date_debut_deliberation_moa_dossier

					if v_date_fin_deliberation_moa_dossier is not None :
						kwargs['dt_delib_moa_doss__lte'] = v_date_fin_deliberation_moa_dossier

					if v_avis_cp_dossier > -1 :
						kwargs['id_av_cp'] = v_avis_cp_dossier

					if v_montant_ht_dossier_min is not None :
						kwargs['mont_ht_doss__gte'] = v_montant_ht_dossier_min

					if v_montant_ht_dossier_max is not None :
						kwargs['mont_ht_doss__lte'] = v_montant_ht_dossier_max

					if len(tab_moa) > 0 :

						# Je stocke dans un tableau les dossiers après filtrage.
						if len(args) == 0 :
							les_dossiers = TDossier.objects.filter(**kwargs)
						else :
							les_dossiers = TDossier.objects.filter(reduce(operator.or_, args), **kwargs)

						# Je trie les dossiers filtrés.
						les_dossiers = les_dossiers.order_by('-dt_delib_moa_doss', 'num_doss')

						# Je retire les dossiers soldés du tableau des dossiers après filtrage si et seulement la case
						# "Dossiers dont les dépenses sont non-soldées" est cochée.
						if v_dossiers_non_soldes == True :
							les_dossiers = les_dossiers.exclude(id_av__int_av = 'Soldé')

						# J'ajoute les dossiers d'une même famille si et seulement si la case "Intégration des dossiers
						# associés dans le résultat" est cochée.
						if v_integration_dossiers_associes == True :

							# Je déclare et j'empile le tableau des familles.
							tab_familles = []
							for un_dossier in les_dossiers :
								tab_familles.append(un_dossier.id_fam.id_fam)

							# Je supprime les doublons du tableau des familles.
							tab_familles = list(set(tab_familles))

							# Je déclare et j'empile le tableau des conditions ayant la clause "OR".
							args = []
							for i in range(0, len(tab_familles)) :
								args.append(Q(**{ 'id_fam' : int(tab_familles[i]) }))

							# Je stocke dans un tableau les dossiers associés après filtrage (dossiers d'une même 
							# famille).
							les_dossiers = TDossier.objects.filter(reduce(operator.or_, args)).order_by('num_doss')

					else :
						les_dossiers = []

					# Je créé un tableau de dossiers filtrés reprenant les colonnes du tableau HTML des dossiers après
					# filtrage.
					tab_dossiers_filtres = []
					for un_dossier in les_dossiers :
						tab_dossiers_filtres.append([
							conv_none(un_dossier.num_doss),
							conv_none(un_dossier.int_doss),
							conv_none(un_dossier.id_org_moa.id_org_moa.n_org),
							conv_none(reecr_dt(un_dossier.dt_delib_moa_doss)),
							conv_none(un_dossier.id_progr.int_progr),
							conv_none(un_dossier.id_nat_doss.int_nat_doss),
							conv_none(float_to_int(un_dossier.mont_ht_doss)),
							'<a href="{0}" class="bt-consulter pull-right"></a>'.format(
								reverse('consulter_dossier', args = [un_dossier.id_doss])
							)
						])

					# Je reviens à l'état initial lorsque la case "Ajouter à la sélection existante" est décochée.
					if v_ajouter_selection_existante == False :
						request.session['dossiers_selectionnes'] = []

					# J'empile le tableau de session des dossiers sélectionnés après X recherches (avec doublons).
					request.session['dossiers_selectionnes'].append(tab_dossiers_filtres)

					# J'initialise la valeur du tableau qui alimentera la datatable.
					if v_ajouter_selection_existante == False :
						tab_success = tab_dossiers_filtres
					else :
						tab_success = suppr_doubl_dtable(request.session['dossiers_selectionnes'])

					# J'empile le tableau de session des dossiers sélectionnés après X recherches (sans doublons),
					# permettant de remplir le fichier au format CSV.
					request.session['export_csv_dossiers_selectionnes'] = tab_success
							
					# J'envoie la liste des dossiers après filtrage.
					reponse = HttpResponse(json.dumps(
						{ 'success' : tab_success }), content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs du formulaire de réalisation d'un état en sélectionnat les dossiers.
					reponse = HttpResponse(json.dumps(f1.errors), content_type = 'application/json')

		else :

			# J'alimente les listes déroulantes des axes, des sous-axes, des actions et des types de dossiers.
			reponse = HttpResponse(json.dumps(alim_liste(request)), content_type = 'application/json')

	return reponse