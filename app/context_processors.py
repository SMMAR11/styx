#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from django.conf import settings

def global_settings(request) :

	return {
		'ACC_STR' : settings.ACC_STR,
		'ACOMPT_STR' : settings.ACOMPT_STR,
		'EA_STR' : settings.EA_STR,
		'EP_STR' : settings.EP_STR,
		'PRT_STR' : settings.PRT_STR,
		'REF_STR' : settings.REF_STR,
		'SO_STR' : settings.SO_STR,
		'SOLD_STR' : settings.SOLD_STR,
		'SOLD_STR_2' : settings.SOLD_STR_2,
		'VALID_STR' : settings.VALID_STR
	}