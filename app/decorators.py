#!/usr/bin/env python
#-*- coding: utf-8

'''
Ce décorateur vérifie si l'accès à une page est autorisé.
'''
def verif_acc(_vf) :

	# Imports
	from functools import wraps

	def _dec(request, *args, **kwargs) :

		# Imports
		from django.core.exceptions import PermissionDenied

		if request.user.is_authenticated :
			return _vf(request, *args, **kwargs)
		else :
			raise PermissionDenied

	return wraps(_vf)(_dec)