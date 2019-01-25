# coding: utf-8

# Imports
from django.db import models

class Class(models.DecimalField) :
	'''Champ pourcentage'''
	from django.core.validators import MinValueValidator; from django.core.validators import MaxValueValidator
	default_validators = [MinValueValidator(0), MaxValueValidator(100)]
	def __init__(self, *args, **kwargs) :
		kwargs['decimal_places'] = kwargs.get('decimal_places', 3); kwargs['max_digits'] = kwargs.get('max_digits', 6)
		super().__init__(*args, **kwargs)