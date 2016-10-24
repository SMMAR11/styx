from app.decorators import *
from app.forms import session
from app.functions import *
from app.models import *
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.context_processors import csrf
import json

'''
Cette vue permet d'afficher la page de consultation du compte de l'utilisateur connecté.
request : Objet requête
'''
@verif_acces
def consulter_compte(request) :

	reponse = None

	if request.method == 'GET' :

		# J'affiche le template.
		reponse = render(
			request,
			'./autres/gestion_compte/consulter_compte.html',
			{
				'title' : 'Consulter mon compte'
			}
		)

	return reponse

'''
Cette vue permet d'afficher la page principale dès la fermeture de la session active.
request : Objet requête
'''
@verif_acces
def deconnecter(request) :

	reponse = None

	if request.method == 'GET' :

		# Je vide les variables de session si la session est active (je ferme la session par conséquent).
		if 'utilisateur' in request.session :
			for une_cle in list(request.session.keys()) :
				del request.session[une_cle]

		# Je suis redirigé vers la page principale.
		reponse = redirect('index')

	return reponse

'''
Cette vue permet soit d'afficher la page principale, soit de traiter l'un des formulaires de la page principale. 
request : Objet requête
p_action : Quel formulaire ai-je soumis ?
'''
@nett_form
def index(request) :

	reponse = None

	if request.method == 'GET' :

		# Je déclare des objets "formulaire" permettant une future manipulation des champs.
		f1 = session.Identifier()
		f2 = session.OublierMotDePasse()

		# J'initialise le gabarit d'affichage des champs du formulaire de demande de réinitialisation du mot de passe.
		tab_champs_f2 = init_form(f2)

		# J'initialise le tableau du contenu des différentes fenêtres modales.
		tab_contenus_fm = {
			'oublier_mdp' : '''
			<form name="form_oublier_mdp" method="post" action="{0}" class="c-theme">
				<input name="csrfmiddlewaretoken" value="{1}" type="hidden">
				{2}
				<button type="submit" class="center-block btn bt-vert to-unfocus">Valider</button>
			</form>
			'''.format(
				reverse('index') + '?action=oublier-mdp',
				csrf(request)['csrf_token'],
				tab_champs_f2['zs_courr']
			)
		}

		# Je déclare un tableau de fenêtres modales selon l'état de la session, ainsi que le contenu de la balise
		# <title/>.
		if 'utilisateur' in request.session :
			tab_fm = []
			title = 'Accueil'
		else :
			tab_fm = [
				init_fm('identification', 'Identification'),
				init_fm('oublier_mdp', 'Oubli de votre mot de passe', tab_contenus_fm['oublier_mdp'])
			]
			title = 'Identification'

		# J'affiche le template.
		reponse = render(
			request,
			'./main.html',
			{
				'f1' : init_form(f1),
				'les_fm' : tab_fm,
				'title' : title
			}
		)

	else :
		if 'action' in request.GET :

			# Je stocke la valeur du paramètre "GET" relatif à l'action effectuée.
			action = request.GET['action']

			# Je traite le cas lié à la soumission du formulaire d'identification.
			if action == 'identifier' :

				# Je déclare un objet "formulaire" permettant de traiter le formulaire d'identification.
				f1 = session.Identifier(request.POST)

				if f1.is_valid() :

					# Je récupère les données du formulaire valide.
					tab_donnees = f1.cleaned_data
					v_pseudo = tab_donnees['zs_pseudo']
					v_mdp = tab_donnees['zs_mdp']

					# Je récupère les données de l'utilisateur connecté.
					obj_utilisateur = TUtilisateur.objects.get(pseudo_util = v_pseudo)

					# J'initialise un tableau qui contient les données de l'utilisateur connecté.
					tab_donnees_utilisateur = {
						'id_util' : obj_utilisateur.id_util,
						'n_util' : obj_utilisateur.n_util,
						'pren_util' : obj_utilisateur.pren_util
					}

					# Je déclare la session.
					request.session['utilisateur'] = tab_donnees_utilisateur

					# J'affiche le message de succès de la procédure d'identification.
					reponse = HttpResponse(
						json.dumps({
							'success' : 'Connexion réussie !',
							'redirect' : reverse('index')
						}), 
						content_type = 'application/json'
					)

				else :

					# J'affiche les erreurs du formulaire d'identification.
					reponse = HttpResponse(json.dumps(f1.errors), content_type = 'application/json')

			if action == 'oublier-mdp' :

				# Je déclare un objet "formulaire" permettant de traiter le formulaire de demande de réinitialisation du
				# mot de passe.
				f2 = session.OublierMotDePasse(request.POST)

				if f2.is_valid() :

					# Je récupère la donnée du formulaire valide.
					tab_donnees = f2.cleaned_data
					v_courriel = tab_donnees['zs_courr']

					# J'envoie un mail au courriel renseigné.
					# [TODO]

					# J'affiche le message de succès de la procédure de demande de réinitialisation du mot de passe.
					reponse = HttpResponse(
						json.dumps({ 
							'success' : 'Un email a été envoyé à ' + v_courriel + '.',
							'redirect' : reverse('index')
						}), 
						content_type = 'application/json'
					)
					
				else :

					# J'affiche les erreurs du formulaire de demande de réinitialisation du mot de passe.
					reponse = HttpResponse(json.dumps(f2.errors), content_type = 'application/json')

	return reponse