#!/usr/bin/env python
#-*- coding: utf-8

'''
Ce décorateur nettoie un formulaire lors d'un rechargement de page.
'''
def nett_form(view_func) :

	''' Imports '''
	from functools import wraps

	def _decorator(request, *args, **kwargs) :

		''' Imports '''
		from django.shortcuts import redirect

		# J'initialise la variable de session à l'indice "refresh".
		if 'refresh' not in request.session :
			request.session['refresh'] = -1

		# J'incrémente la variable de session à l'indice "refresh" de 1.
		request.session['refresh'] += 1

		# J'efface la variable de session à l'indice "refresh" et je recharge la page courante si besoin afin de 
		# nettoyer le formulaire.
		if request.method == 'GET' and request.session['refresh'] > 0 :
			del request.session['refresh']
			return redirect(request.path)
		else :
			return view_func(request, *args, **kwargs)

	return wraps(view_func)(_decorator)

'''
Ce décorateur vérifie si l'accès à une page est autorisé.
'''
def verif_acces(view_func) :

	''' Imports '''
	from functools import wraps

	def _decorator(request, *args, **kwargs) :

		''' Imports '''
		from django.core.exceptions import PermissionDenied

		# Je regarde l'état de la session.
		if request.user.is_authenticated() :
			return view_func(request, *args, **kwargs)
		else :
			raise PermissionDenied

	return wraps(view_func)(_decorator)