#!/usr/bin/env python
#-*- coding: utf-8

DEFAULT_OPTION = (None, '---------')
ERROR_MESSAGES = {
	'blank' : 'Veuillez renseigner une valeur.',
	'invalid' : 'Veuillez renseigner une valeur valide.',
	'invalid_choice' : 'Veuillez renseigner une valeur valide.',
	'invalid_pk_value' : 'Veuillez renseigner une valeur valide.',
	'null' : 'Veuillez renseigner une valeur.',
	'required' : 'Veuillez renseigner une valeur.',
	'unique' : 'Veuillez renseigner une valeur unique.'
}
MAY_BE_REQUIRED = '<span class="may-be-required-field"></span>'
REQUIRED = '<span class="required-field"></span>'