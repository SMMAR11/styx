# coding: utf-8

# Imports
from django.db import models

class Class(models.DecimalField) :
	'''Champ euro'''
	def __init__(self, min_value = 0, *args, **kwargs) :
		from django.core.validators import MinValueValidator
		kwargs['decimal_places'] = kwargs.get('decimal_places', 2); kwargs['max_digits'] = kwargs.get('max_digits', 26)
		super().__init__(*args, **kwargs); self.min_value = min_value
		default_validators = [MinValueValidator(self.min_value)]