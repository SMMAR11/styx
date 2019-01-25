# coding: utf-8

# Imports
from django.db import models

class Class(models.Manager) :

	def get_rmoas(self, moa) :

		'''Ensemble des maîtres d'ouvrage (anciens) liés à l'instance'''

		# Imports
		from app.models import TRegroupementsMoa

		# Obtention d'une instance TMoa
		moa = self.get(pk = moa)

		# Définition des maîtres d'ouvrage (anciens)
		moas = self.filter(pk = moa.pk)
		moas |= self.filter(pk__in = TRegroupementsMoa.objects.filter(id_org_moa_fil = moa.pk).values_list(
			'id_org_moa_anc', flat = True
		))

		return moas