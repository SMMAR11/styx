# coding: utf-8

# Import
from django.core.management.base import BaseCommand

class Command(BaseCommand) :

	help = """Initialisation de de la table de changement d'avancement des dossiers PGRE.
	Cette commande permet d'alimenter la table TAvancementPgreTrace avec les données
	initialement saisie.
	"""

	def handle(self, *args, **kwargs) :

		# Imports
		from app.models import TAvancementPgreTraces
		from app.models import TDossierPgre
		from django.db import connection

		# Tous les dossiers pgre sans trace:
		avancement_traces = TAvancementPgreTraces.objects.all()
		dossiers_init = TDossierPgre.objects.exclude(id_doss_pgre__in=[at.id_doss_pgre for at in avancement_traces])
		for doss in dossiers_init:
			TAvancementPgreTraces.objects.create(
				id_doss_pgre=doss,
				id_av_pgre=doss.id_av_pgre)
		print("Les états initiaux d'avancement des dossiers PGRE sont renseignés sur TAvancementPgreTraces.")
