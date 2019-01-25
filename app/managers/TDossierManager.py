# coding: utf-8

# Imports
from django.db import models

class Class(models.Manager) :

	def custom_filter(self, remove_completed = False, **kwargs) :

		'''Ensemble des dossiers (mise en place de pré-filtres)'''

		# Définition des dossiers 
		doss = self.filter(**kwargs)

		# Exclusion des dossiers soldés
		if remove_completed : doss = doss.exclude(id_av__int_av = 'Soldé')

		return doss

	def get_years(self, mdl_column, **kwargs):
		'''Ensemble d'années'''
		return [(i, i) for i in sorted(set(
			[dos.year for dos in self.filter(**kwargs).values_list(mdl_column, flat = True) if dos is not None]
		))]