# coding: utf-8

# Imports
from django.db import models

class Class(models.CharField) :
	'''Champ numéro de téléphone'''
	from django.core.validators import RegexValidator; default_validators = [RegexValidator(r'^[0-9]{10}')]
	def __init__(self, *args, **kwargs) :
		kwargs['max_length'] = kwargs.get('max_length', 10); super().__init__(*args, **kwargs)