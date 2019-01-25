# coding: utf-8

# Imports
from django.contrib.auth.models import BaseUserManager

class Class(BaseUserManager):

	def get_authenticated_user(self, req) :
		'''Instance :model:`app.TUtilisateur` (ou objet NoneType)'''
		try :
			return self.get(pk = req.user.pk)
		except :
			return None