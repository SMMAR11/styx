# coding: utf-8

# Imports
from django import forms

class Class(forms.DecimalField) :
	'''Champ euro'''
	def __init__(self, min_value = 0, **kwargs) :
		from django.core.validators import MinValueValidator
		kwargs['validators'] = [*self.default_validators, MinValueValidator(min_value)]
		super().__init__(decimal_places = 2, max_digits = 26, **kwargs)