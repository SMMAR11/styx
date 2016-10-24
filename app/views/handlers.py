from django.shortcuts import render_to_response
from django.template import RequestContext

'''
Cette vue permet d'afficher le template relatif à la page interdisant l'accès à une URL.
request : Objet requête
'''
def handler_403(request) :

	reponse = render_to_response(
		'./autres/handlers/403.html',
		{
			'title' : 'Erreur 403'
		},
		context_instance = RequestContext(request)
	)

	reponse.status_code = 403

	return reponse

'''
Cette vue permet d'afficher le template relatif à la page informant que l'URL saisie est inexistante.
request : Objet requête
'''
def handler_404(request) :

	reponse = render_to_response(
		'./autres/handlers/404.html',
		{
			'title' : 'Erreur 404'
		},
		context_instance = RequestContext(request)
	)

	reponse.status_code = 404

	return reponse