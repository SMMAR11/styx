#!/usr/bin/env python
#-*- coding: utf-8

'''
Ce décorateur vide un formulaire dès la fin du rechargement d'une page HTML.
'''
def nett_f(_vf) :

	# Imports
	from functools import wraps

	def _dec(request, *args, **kwargs) :

		# Imports
		from django.shortcuts import redirect

		if 'reload' not in request.session :
			request.session['reload'] = -1
		request.session['reload'] += 1
		if request.method == 'GET' and request.session['reload'] > 0 :
			del request.session['reload']
			return redirect(request.path)
		else :
			return _vf(request, *args, **kwargs)

	return wraps(_vf)(_dec)

'''
Ce décorateur vérifie si l'accès à une page est autorisé.
'''
def verif_acc(_vf) :

	# Imports
	from functools import wraps

	def _dec(request, *args, **kwargs) :

		# Imports
		from django.core.exceptions import PermissionDenied

		if request.user.is_authenticated() :
			return _vf(request, *args, **kwargs)
		else :
			raise PermissionDenied

	return wraps(_vf)(_dec)