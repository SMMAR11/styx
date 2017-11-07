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
		from django.db import connection

		# Rédaction des requêtes SQL (initialisation des vues)
		sqls = [
			'DROP VIEW IF EXISTS v_suivi_dossier;',
			'''
			CREATE OR REPLACE VIEW v_suivi_dossier
			AS
			SELECT
			id_doss,
			mont_doss,
			mont_suppl_doss,
			mont_tot_doss,
			est_ttc_doss,
			mont_part_fin_sum,
			mont_prest_doss_sum,
			mont_aven_sum,
			mont_tot_prest_doss,
			CASE
				WHEN mont_fact_sum NOTNULL THEN mont_fact_sum
				ELSE 0
			END AS mont_fact_sum,
			mont_doss - mont_part_fin_sum AS mont_raf,
			mont_tot_doss - mont_tot_prest_doss AS mont_rae
			FROM
			(
				SELECT *
				FROM
				(
					SELECT
					*,
					mont_prest_doss_sum + mont_aven_sum AS mont_tot_prest_doss
					FROM
					(
						SELECT
						id_doss,
						mont_doss,
						mont_suppl_doss,
						mont_doss + mont_suppl_doss AS mont_tot_doss,
						est_ttc_doss,
						mont_part_fin_sum,
						CASE
							WHEN mont_prest_doss_sum NOTNULL THEN mont_prest_doss_sum
							ELSE 0
						END AS mont_prest_doss_sum,
						CASE
							WHEN mont_aven_sum NOTNULL THEN mont_aven_sum
							ELSE 0
						END AS mont_aven_sum
						FROM
						(
							SELECT
							id_doss,
							mont_doss,
							mont_suppl_doss,
							est_ttc_doss,
							CASE
								WHEN mont_part_fin_sum NOTNULL THEN mont_part_fin_sum
								ELSE 0
							END AS mont_part_fin_sum
							FROM
							(
								SELECT
								id_doss_id,
								SUM(mont_part_fin) AS mont_part_fin_sum
								FROM t_financement
								GROUP BY id_doss_id
							) AS temp1
							RIGHT JOIN t_dossier
							ON id_doss_id = id_doss
						) AS temp2
						LEFT JOIN
						(
							SELECT 
							temp3.id_doss_id,
							mont_prest_doss_sum, 
							SUM(mont_aven) AS mont_aven_sum
							FROM
							(
								SELECT 
								id_doss_id, 
								SUM(mont_prest_doss) AS mont_prest_doss_sum
								FROM t_prestations_dossier
								GROUP BY id_doss_id
							) AS temp3
							LEFT JOIN t_avenant
							ON temp3.id_doss_id = t_avenant.id_doss_id
							GROUP BY temp3.id_doss_id, mont_prest_doss_sum
						) AS temp4
						ON id_doss = id_doss_id
						ORDER BY id_doss
					) AS temp5
				) AS temp9
				LEFT JOIN
				(
					SELECT
					id_doss_id,
					CASE
						WHEN est_ttc_doss = True THEN mont_ttc_fact_sum
						ELSE mont_ht_fact_sum
					END AS mont_fact_sum
					FROM
					(
						SELECT
						id_doss_id,
						SUM(mont_ht_fact) AS mont_ht_fact_sum,
						SUM(mont_ttc_fact) AS mont_ttc_fact_sum
						FROM t_facture
						GROUP BY id_doss_id
					) AS temp7, t_dossier
					WHERE id_doss = id_doss_id
				) AS temp8
				ON id_doss = id_doss_id
			) AS temp10
			ORDER BY id_doss;
			''',
			'DROP VIEW IF EXISTS v_financement;',
			'''
			CREATE OR REPLACE VIEW v_financement
			AS
			SELECT
			t_financement.id_fin,
			a_inf_fin,
			chem_pj_fin,
			comm_fin,
			t_financement.dt_deb_elig_fin,
			dt_fin_elig_fin,
			dt_lim_deb_oper_fin,
			dt_lim_prem_ac_fin,
			duree_pror_fin,
			duree_valid_fin,
			CASE
				WHEN est_ttc_doss = TRUE THEN mont_ttc_ddv_sum
				ELSE mont_ht_ddv_sum
			END AS mont_ddv_sum,
			mont_elig_fin,
			t_financement.mont_part_fin,
			CASE
				WHEN est_ttc_doss = TRUE THEN mont_ttc_rad
				ELSE mont_ht_rad
			END AS mont_rad,
			num_arr_fin,
			pourc_elig_fin,
			pourc_glob_fin,
			pourc_real_fin,
			t_financement.id_doss_id,
			id_org_fin_id,
			id_paiem_prem_ac_id
			FROM
			(
				SELECT *
				FROM
				(
					SELECT
					temp2.*,
					id_doss_id,
					est_ttc_doss,
					(mont_part_fin / mont_doss) * 100 AS pourc_glob_fin
					FROM
					(
						SELECT 
						id_fin,
						dt_deb_elig_fin,
						DATE(dt_deb_elig_fin + SUM(duree_pror_fin + duree_valid_fin) * INTERVAL '1 month') AS dt_fin_elig_fin
						FROM
						(
							SELECT 
							id_fin,
							dt_deb_elig_fin,
							CASE
								WHEN duree_pror_fin NOTNULL THEN duree_pror_fin
								ELSE 0
							END AS duree_pror_fin,
							CASE
								WHEN duree_valid_fin NOTNULL THEN duree_valid_fin
								ELSE 0
							END AS duree_valid_fin
							FROM t_financement
						) AS temp1
						GROUP BY id_fin, dt_deb_elig_fin
					) AS temp2
					INNER JOIN t_financement ON temp2.id_fin = t_financement.id_fin
					INNER JOIN t_dossier ON id_doss = id_doss_id
				) AS temp5,
				(
					SELECT
					*,
					mont_part_fin - mont_ht_ddv_sum AS mont_ht_rad,
					mont_part_fin - mont_ttc_ddv_sum AS mont_ttc_rad
					FROM
					(
						SELECT
						id_fin_temp,
						mont_part_fin,
						CASE
							WHEN mont_ht_ddv_sum NOTNULL THEN mont_ht_ddv_sum
							ELSE 0
						END AS mont_ht_ddv_sum,
						CASE
							WHEN mont_ttc_ddv_sum NOTNULL THEN mont_ttc_ddv_sum
							ELSE 0
						END AS mont_ttc_ddv_sum
						FROM
						(
							SELECT
							id_fin AS id_fin_temp,
							mont_part_fin,
							SUM(mont_ht_ddv) AS mont_ht_ddv_sum,
							SUM(mont_ttc_ddv) AS mont_ttc_ddv_sum
							FROM t_financement
							LEFT JOIN t_demande_versement
							ON id_fin = id_fin_id
							GROUP BY id_fin
						) AS temp3
					) AS temp4
				) AS temp6
				WHERE id_fin = id_fin_temp
			) AS temp7
			INNER JOIN t_financement ON temp7.id_fin = t_financement.id_fin
			ORDER BY t_financement.id_fin;
			''',
			'DROP VIEW IF EXISTS v_suivi_prestations_dossier;',
			'''
			CREATE OR REPLACE VIEW v_suivi_prestations_dossier
			AS
			SELECT
			id,
			id_prest_id,
			id_doss_id,
			mont_prest_doss,
			nb_aven,
			mont_aven_sum,
			nb_fact,
			mont_ht_fact_sum,
			mont_ttc_fact_sum,
			mont_tot_prest_doss,
			CASE
				WHEN est_ttc_doss = true THEN mont_tot_prest_doss - mont_ttc_fact_sum
				ELSE mont_tot_prest_doss - mont_ht_fact_sum
			END AS mont_raf
			FROM
			(	SELECT
				*,
				mont_prest_doss + mont_aven_sum AS mont_tot_prest_doss
				FROM
				(
					SELECT
					id,
					id_prest_id,
					id_doss_id,
					mont_prest_doss,
					CASE
						WHEN nb_aven NOTNULL THEN nb_aven
						ELSE 0
					END AS nb_aven,
					CASE
						WHEN mont_aven_sum NOTNULL THEN mont_aven_sum
						ELSE 0
					END AS mont_aven_sum,
					CASE
						WHEN nb_fact NOTNULL THEN nb_fact
						ELSE 0
					END AS nb_fact,
					CASE
						WHEN mont_ht_fact_sum NOTNULL THEN mont_ht_fact_sum
						ELSE 0
					END AS mont_ht_fact_sum,
					CASE
						WHEN mont_ttc_fact_sum NOTNULL THEN mont_ttc_fact_sum
						ELSE 0
					END AS mont_ttc_fact_sum
					FROM
					(
						SELECT *
						FROM
						(
							SELECT *
							FROM t_prestations_dossier
							LEFT JOIN
							(
								SELECT 
								id_doss_id AS id_doss_id_temp, 
								id_prest_id AS id_prest_id_temp, 
								COUNT(*) AS nb_aven, 
								SUM(mont_aven) AS mont_aven_sum
								FROM t_avenant
								GROUP BY id_doss_id, id_prest_id
							) AS temp1
							ON id_doss_id = id_doss_id_temp
							AND id_prest_id = id_prest_id_temp
						) AS temp2
						LEFT JOIN
						(
							SELECT 
							id_doss_id AS id_doss_id_temp, 
							id_prest_id AS id_prest_id_temp, 
							COUNT(*) AS nb_fact, 
							SUM(mont_ht_fact) AS mont_ht_fact_sum,
							SUM(mont_ttc_fact) AS mont_ttc_fact_sum
							FROM t_facture
							GROUP BY id_doss_id, id_prest_id
						) AS temp3
						ON id_doss_id = temp3.id_doss_id_temp
						AND id_prest_id = temp3.id_prest_id_temp
					) AS temp4
				) AS temp5
			) AS temp6, t_dossier
			WHERE id_doss = id_doss_id
			ORDER BY id;
			''',
			'DROP VIEW IF EXISTS v_demande_versement;',
			'''
			CREATE OR REPLACE VIEW v_demande_versement
			AS
			SELECT
			id_ddv,
			chem_pj_ddv,
			comm_ddv,
			dt_ddv,
			dt_vers_ddv,
			int_ddv,
			mont_ht_ddv - mont_ht_verse_ddv AS map_ht_ddv,
			mont_ttc_ddv - mont_ttc_verse_ddv AS map_ttc_ddv,
			mont_ht_ddv,
			mont_ht_verse_ddv,
			mont_ttc_ddv,
			mont_ttc_verse_ddv,
			id_doss_id,
			id_fin_id,
			id_org_fin_id,
			id_type_vers_id
			FROM t_demande_versement, t_financement
			WHERE id_fin = id_fin_id
			ORDER BY id_ddv;
			''',
			'DROP VIEW IF EXISTS v_prestation;',
			'''
			CREATE OR REPLACE VIEW v_prestation
			AS
			SELECT
			id_prest,
			chem_pj_prest,
			comm_prest,
			dt_fin_prest,
			dt_notif_prest,
			int_prest,
			mont_prest,
			ref_prest,
			id_nat_prest_id,
			id_org_prest_id
			FROM
			t_prestation,
			(
				SELECT id_prest_id, SUM(mont_prest_doss) AS mont_prest
				FROM t_prestations_dossier
				GROUP BY id_prest_id
			) AS temp
			WHERE id_prest = id_prest_id
			ORDER BY id_prest;
			'''
		]

		# Exécution de chaque requête SQL
		for sql in sqls :
			with connection.cursor() as cursor : cursor.execute(sql)
			del cursor

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