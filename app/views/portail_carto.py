from app.decorators import *
from app.models import *
from django.shortcuts import get_object_or_404, render

@verif_acces
def consulter_carto(request, p_dossier) :

	reponse = None

	if request.method == 'GET' :

		obj_famille = get_object_or_404(TDossier, id_doss = p_dossier)

		# J'affiche le template.
		reponse = render(
			request,
			'./portail_carto/consulter_carto.html',
			{ 'title' : 'Consulter un objet géographique' }
		)

	return reponse

'''
Cette vue permet d'afficher le menu du portail cartographique.
request : Objet requête
'''
@verif_acces
def index(request) :

	# J'affiche le template.
	return render(
		request,
		'./portail_carto/main.html',
		{ 'title' : 'Portail cartographique' }
	)