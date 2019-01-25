# coding: utf-8

# Imports
from django import forms

class Class(forms.ModelChoiceField) :

	'''Champ liste déroulante modèle vierge'''

	# Méthodes publiques

	def label_from_instance(self, obj) :
		if self.obj_label :
			lbls = [str(getattr(obj, i.strip())()) for i in self.obj_label.split('|')]
		else :
			lbls = [super().label_from_instance(obj)]
		return '|'.join(lbls)

	# Méthodes système

	def __init__(self, obj_label = '', *args, **kwargs) :
		super().__init__(*args, **kwargs); self.obj_label = obj_label