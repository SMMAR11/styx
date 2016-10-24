from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

'''
Ce décorateur vérifie si l'accès à une page est autorisé.
'''
def verif_acces(view_func) :

	def _decorator(request, *args, **kwargs) :

		# Je vérifie qu'une session est ouverte afin d'autoriser ou non l'accès à une page.
		if 'utilisateur' not in request.session :
			raise PermissionDenied
		else :
			return view_func(request, *args, **kwargs)

	return wraps(view_func)(_decorator)

'''
Ce décorateur nettoie les champs d'un formulaire lors d'un rechargement de page.
'''
def nett_form(view_func) :

	def _decorator(request, *args, **kwargs) :

		# J'initialise la variable de session à l'indice refresh si elle n'est pas déclarée.
		if 'refresh' not in request.session :
			request.session['refresh'] = -1

		# J'incrémente la variable de session à l'indice refresh de 1.
		request.session['refresh'] += 1

		# J'efface la variable de session à l'indice refresh et je recharge la page courante si les conditions sont 
		# respectées.
		if request.method == 'GET' and request.session['refresh'] > 0 :
			del request.session['refresh']
			return redirect(request.path)
		else :
			return view_func(request, *args, **kwargs)

	return wraps(view_func)(_decorator)