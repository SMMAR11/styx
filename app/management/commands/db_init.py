# coding: utf-8

# Import
from django.core.management.base import BaseCommand

class Command(BaseCommand) :

	help = 'Initialisation de la base de données STYX'

	def handle(self, *args, **kwargs) :

		# Imports
		from app.models import TAvancement
		from app.models import TAvisCp
		from app.models import TDroit
		from app.models import TMoa
		from app.models import TOrganisme
		from app.models import TPaiementPremierAcompte
		from app.models import TTypeAvancementArrete
		from app.models import TTypeGeom
		from app.models import TTypeProgramme
		from app.models import TTypeVersement
		from app.models import TUtilisateur
		
		# Initialisation des données attributaires de chaque état d'avancement
		attrs_av = [
			{ 'int_av' : 'Abandonné', 'ordre_av' : 5 },
			{ 'int_av' : 'En cours', 'ordre_av' : 2 },
			{ 'int_av' : 'En projet', 'ordre_av' : 1 },
			{ 'int_av' : 'Soldé', 'ordre_av' : 4 },
			{ 'int_av' : 'Terminé', 'ordre_av' : 3 }
		]

		# Création des instances TAvancement
		for attrs in attrs_av :
			if TAvancement.objects.filter(int_av = attrs['int_av']).count() == 0 : TAvancement.objects.create(**attrs)

		# Création des instances TAvisCp
		for attrs in ['Accordé', 'Ajourné', 'En attente', 'Refusé', 'Sans objet'] :
			if TAvisCp.objects.filter(int_av_cp = attrs).count() == 0 : TAvisCp.objects.create(int_av_cp = attrs)

		# Création des instances TPaiementPremierAcompte
		for attrs in ['Justificatif et lancement de l\'opération', 'Pourcentage de réalisation des travaux'] :
			if TPaiementPremierAcompte.objects.filter(int_paiem_prem_ac = attrs).count() == 0 :
				TPaiementPremierAcompte.objects.create(int_paiem_prem_ac = attrs)

		# Initialisation des données attributaires de chaque type d'avancement lié au module "Réglementations"
		attrs_taa = [
			{ 'int_type_av_arr' : 'Instruction', 'ordre_type_av_arr' : 2 },
			{ 'int_type_av_arr' : 'Rédaction', 'ordre_type_av_arr' : 1 },
			{ 'int_type_av_arr' : 'Validé', 'ordre_type_av_arr' : 3 }
		]

		# Création des instances TTypeAvancementArrete
		for attrs in attrs_taa :
			if TTypeAvancementArrete.objects.filter(int_type_av_arr = attrs['int_type_av_arr']).count() == 0 :
				TTypeAvancementArrete.objects.create(**attrs)

		# Création des instances TTypeGeom
		for attrs in ['marker', 'polygon', 'polyline'] :
			if TTypeGeom.objects.filter(int_type_geom = attrs).count() == 0 :
				TTypeGeom.objects.create(int_type_geom = attrs)

		# Création d'une instance TTypeProgramme
		if TTypeProgramme.objects.filter(int_type_progr = 'PGRE').count() == 0 :
			TTypeProgramme.objects.create(int_type_progr = 'PGRE')

		# Création des instances TTypeVersement
		for attrs in ['Acompte', 'Avance forfaitaire', 'Solde'] :
			if TTypeVersement.objects.filter(int_type_vers = attrs).count() == 0 :
				TTypeVersement.objects.create(int_type_vers = attrs)

		# Création d'organismes requis au bon fonctionnement de l'application
		if TOrganisme.objects.filter(n_org = 'DDTM').count() == 0 : TOrganisme.objects.create(n_org = 'DDTM')
		if TMoa.objects.filter(n_org = 'SMMAR').count() == 0 :
			obj_moa = TMoa.objects.create(
				dim_org_moa = 'SMMAR',
				en_act_doss = True,
				en_act_doss_pgre = True,
				n_org = 'SMMAR',
				peu_doss = True,
				peu_doss_pgre = True
			)
		else :
			obj_moa = TMoa.objects.get(n_org = 'SMMAR')

		# Création du super-administrateur STYX
		if TUtilisateur.objects.filter(username = 'ADMIN_styx2').count() == 0 :

			# Création d'une instance TUtilisateur
			obj_util = TUtilisateur(
				id_org = obj_moa,
				is_active = True,
				is_staff = True,
				is_superuser = True,
				username = 'ADMIN_styx2'
			)
			obj_util.set_password('password')
			obj_util.save()

			# Création d'une instance TDroit
			TDroit.objects.create(
				en_ecr = True,
				en_lect = True,
				id_util = obj_util
			)

		print('La base de données STYX a été initialisée avec succès.')