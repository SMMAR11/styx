from app.decorators import *
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

'''
Cette vue permet de savoir l'onglet actif du menu des dossiers.
request : Objet requête
'''
@csrf_exempt
def retourner_onglet_actif(request) :

	reponse = '#ong_caracteristiques'

	if request.method == 'POST' :
		if 'menu_dossier' in request.session :
			reponse = request.session['menu_dossier']
			del request.session['menu_dossier']
	else :
		raise PermissionDenied

	return HttpResponse(reponse)