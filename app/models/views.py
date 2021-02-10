# coding: utf-8

# Imports
from app.models.tables import *
from django.db import models
from django_pgviews import view

class VDemandeVersement(view.View) :

	'''Ensemble des demandes de versement d'un financement (vue système)'''

	# Imports
	from app.classes.MFEuroField import Class as MFEuroField

	id_ddv = models.IntegerField(primary_key = True)
	map_ht_ddv = MFEuroField()
	map_ttc_ddv = MFEuroField()
	id_doss = models.ForeignKey(TDossier, db_column = 'id_doss_id', on_delete = models.DO_NOTHING)
	id_fin = models.ForeignKey(TFinancement, db_column = 'id_fin_id', on_delete = models.DO_NOTHING)
	id_org_fin = models.ForeignKey(TFinanceur, db_column = 'id_org_fin_id', on_delete = models.DO_NOTHING)

    # Requête
	sql = '''
	SELECT
		V.id_ddv,
		V.mont_ht_ddv - V.mont_ht_verse_ddv AS map_ht_ddv,
		V.mont_ttc_ddv - V.mont_ttc_verse_ddv AS map_ttc_ddv,
		F.id_doss_id,
		V.id_fin_id,
		F.id_org_fin_id
	FROM
		t_demande_versement AS V,
		t_financement AS F
	WHERE F.id_fin = V.id_fin_id
	'''

	class Meta :
		db_table = 'v_demande_versement'
		managed = False
		ordering = ['id_org_fin__n_org']

	# Extra-getters

	def get_instance(self) :
		'''Instance :model:`app.TDemandeVersement`'''
		return TDemandeVersement.objects.get(pk = self.pk)

class VFinancement(view.View) :

	'''Ensemble des financements d'un dossier (autofinancements compris) (vue système)'''

	# Imports
	from app.classes.MFEuroField import Class as MFEuroField
	from app.classes.MFPercentField import Class as MFPercentField

	# Colonnes
	vfin_id = models.IntegerField(primary_key = True)
	id_fin = models.ForeignKey(
		TFinancement, blank = True, db_column = 'id_fin', on_delete = models.DO_NOTHING, null = True
	)
	dt_fin_elig_fin = models.DateField(blank = True, null = True)
	mont_ddv_sum = MFEuroField()
	mont_part_fin = MFEuroField()
	mont_rad = MFEuroField(blank = True, null = True)
	mont_verse_ddv_sum = MFEuroField(blank=True, null=True)
	pourc_glob_fin = MFPercentField()
	id_doss = models.ForeignKey(TDossier, db_column = 'id_doss_id', on_delete = models.DO_NOTHING)
	id_org_fin = models.ForeignKey(TFinanceur, db_column = 'id_org_fin_id', on_delete = models.DO_NOTHING)
	n_org_fin = models.CharField(max_length = 255)
	mont_ddv_attente_vers_sum = MFEuroField(blank=True, null=True)

	# Requête
	sql = '''
	SELECT
		ROW_NUMBER() OVER()::INTEGER AS vfin_id,
		tmp.*
	FROM (
		SELECT
			tmp.*,
			(tmp.mont_ddv_sum - tmp.mont_verse_ddv_sum)::NUMERIC(26, 2) AS mont_ddv_attente_vers_sum
		FROM (
			SELECT
				F.id_fin,
				DATE(F.dt_deb_elig_fin + (
					COALESCE(F.duree_pror_fin, 0) + COALESCE(F.duree_valid_fin, 0)
				) * '1 month'::INTERVAL) AS dt_fin_elig_fin,
				COALESCE(
					CASE WHEN D.est_ttc_doss = false THEN D2.mont_ht_ddv_sum ELSE D2.mont_ttc_ddv_sum END, 0
				)::NUMERIC(26, 2) AS mont_ddv_sum,
				F.mont_part_fin,
				(F.mont_part_fin - COALESCE(
					CASE WHEN D.est_ttc_doss = false THEN D2.mont_ht_ddv_sum ELSE D2.mont_ttc_ddv_sum END, 0
				))::NUMERIC(26, 2) AS mont_rad,
				COALESCE(
					CASE WHEN D.est_ttc_doss = false THEN D2.mont_ht_verse_ddv_sum ELSE D2.mont_ttc_verse_ddv_sum END, 0
				)::NUMERIC(26, 2) AS mont_verse_ddv_sum,
				((F.mont_part_fin / D.mont_doss) * 100)::NUMERIC(6, 3) AS pourc_glob_fin,
				F.id_doss_id,
				F.id_org_fin_id,
				O.n_org AS n_org_fin
			FROM public.t_financement AS F
			INNER JOIN public.t_dossier AS D ON D.id_doss = F.id_doss_id
			INNER JOIN public.t_organisme AS O ON O.id_org = F.id_org_fin_id
			LEFT OUTER JOIN (
				SELECT
					D.id_fin_id AS fin_id_tmp,
					SUM(D.mont_ht_ddv) AS mont_ht_ddv_sum,
					SUM(D.mont_ttc_ddv) AS mont_ttc_ddv_sum,
					SUM(D.mont_ht_verse_ddv) AS mont_ht_verse_ddv_sum,
					SUM(D.mont_ttc_verse_ddv) AS mont_ttc_verse_ddv_sum
				FROM public.t_demande_versement AS D
				GROUP BY D.id_fin_id
			) AS D2 ON D2.fin_id_tmp = F.id_fin
			UNION
			SELECT
				NULL,
				NULL,
				NULL,
				(D.mont_doss - COALESCE(D2.mont_part_fin_sum, 0))::NUMERIC(26, 2),
				NULL::NUMERIC(26, 2),
				NULL::NUMERIC(26, 2),
				(100 - COALESCE(D2.pourc_glob_fin, 0))::NUMERIC(6, 3),
				D.id_doss,
				NULL,
				FORMAT('Autofinancement - %s', O.n_org)
			FROM public.t_dossier AS D
			INNER JOIN public.t_organisme AS O ON O.id_org = D.id_org_moa_id
			LEFT OUTER JOIN (
				SELECT
					F.id_doss_id AS dos_id_tmp,
					SUM(F.mont_part_fin) AS mont_part_fin_sum,
					SUM((F.mont_part_fin / D.mont_doss) * 100) AS pourc_glob_fin
				FROM public.t_financement AS F
				INNER JOIN public.t_dossier AS D ON D.id_doss = F.id_doss_id
				GROUP BY F.id_doss_id
			) AS D2 ON D2.dos_id_tmp = D.id_doss
		) AS tmp
	) AS tmp
	'''

	class Meta :
		db_table = 'v_financement'
		managed = False
		ordering = ['n_org_fin']

class VPrestation(view.View) :

	'''Ensemble des prestations (vue système)'''

	# Imports
	from app.classes.MFEuroField import Class as MFEuroField

	# Colonnes
	id_prest = models.IntegerField(primary_key = True)
	mont_prest = MFEuroField()

	# Requête
	sql = '''
	SELECT
		P.id_prest,
		PD.mont_prest
	FROM public.t_prestation AS P
	INNER JOIN (
		SELECT
			id_prest_id,
			SUM(mont_prest_doss) AS mont_prest
		FROM t_prestations_dossier
		GROUP BY id_prest_id
	) AS PD ON PD.id_prest_id = P.id_prest
	'''

	class Meta :
		db_table = 'v_prestation'
		managed = False

	def get_instance(self) :
		'''Instance :model:`app.TPrestation`'''
		return TPrestation.objects.get(pk = self.pk)

class VSuiviDossier(view.View) :

	'''Suivi financier de l'ensemble des dossiers (vue système)'''

	# Imports
	from app.classes.MFEuroField import Class as MFEuroField
	from app.classes.MFPercentField import Class as MFPercentField

	# Colonnes
	id_doss = models.IntegerField(primary_key = True)
	dt_av_cp_doss = models.DateField(blank=True, null=True)
	est_ttc_doss = models.BooleanField()
	int_doss = models.TextField()
	mont_aven_sum = MFEuroField()
	mont_doss = MFEuroField()
	mont_fact_sum = MFEuroField()
	mont_part_fin_sum = MFEuroField()
	mont_prest_doss_sum = MFEuroField()
	mont_rae = MFEuroField()
	mont_raf = MFEuroField()
	mont_suppl_doss = MFEuroField()
	mont_tot_doss = MFEuroField()
	mont_tot_prest_doss = MFEuroField()
	num_axe_compl = models.TextField(blank = True)
	pourc_comm = MFPercentField()
	pourc_paye = MFPercentField()
	tx_engag_doss = MFPercentField()
	tx_real_doss = MFPercentField()
	type_mont_doss = models.TextField()
	id_av_cp = models.ForeignKey(
		'TAvisCp',
		blank=True,
		db_column='id_av_cp',
		null=True,
		on_delete=models.DO_NOTHING,
        verbose_name='Avis du comité de programmation - CD GEMAPI'
    )

	# Requête
	sql = '''
	SELECT
		D.id_doss,
		CDG.dt_av_cp_doss,
		D.est_ttc_doss,
		FORMAT('%s - %s - %s - %s', N.int_nat_doss, T.int_type_doss, D.lib_1_doss, D.lib_2_doss) AS int_doss,
		COALESCE(A.mont_aven_sum, 0)::NUMERIC(26, 2) AS mont_aven_sum,
		D.mont_doss,
		COALESCE(
			CASE WHEN D.est_ttc_doss = false THEN F2.mont_ht_fact_sum ELSE F2.mont_ttc_fact_sum END, 0
		)::NUMERIC(26, 2) AS mont_fact_sum,
		COALESCE(F.mont_part_fin_sum, 0)::NUMERIC(26, 2) AS mont_part_fin_sum,
		COALESCE(P.mont_prest_doss_sum, 0)::NUMERIC(26, 2) AS mont_prest_doss_sum,
		(
			(D.mont_doss + D.mont_suppl_doss) - (COALESCE(P.mont_prest_doss_sum, 0) + COALESCE(A.mont_aven_sum, 0))
		)::NUMERIC(26, 2) AS mont_rae,
		(D.mont_doss - COALESCE(F.mont_part_fin_sum, 0))::NUMERIC(26, 2) AS mont_raf,
		D.mont_suppl_doss,
		(D.mont_doss + D.mont_suppl_doss)::NUMERIC(26, 2) AS mont_tot_doss,
		(COALESCE(P.mont_prest_doss_sum, 0) + COALESCE(A.mont_aven_sum, 0))::NUMERIC(26, 2) AS mont_tot_prest_doss,
		CONCAT_WS('.', NULLIF(D.num_axe, ''), NULLIF(D.num_ss_axe, ''), NULLIF(D.num_act, '')) AS num_axe_compl,
		(((
			COALESCE(P.mont_prest_doss_sum, 0) + COALESCE(A.mont_aven_sum, 0)
		) / (D.mont_doss + D.mont_suppl_doss)) * 100)::NUMERIC(6, 3) AS pourc_comm,
		((COALESCE(
			CASE WHEN D.est_ttc_doss = false THEN F2.mont_ht_fact_sum ELSE F2.mont_ttc_fact_sum END, 0
		) / (D.mont_doss + D.mont_suppl_doss)) * 100)::NUMERIC(6, 3) AS pourc_paye,
		(
			((COALESCE(P.mont_prest_doss_sum, 0) + COALESCE(A.mont_aven_sum, 0)) / D.mont_doss) * 100
		)::NUMERIC(6, 3) AS tx_engag_doss,
		((COALESCE(
			CASE WHEN D.est_ttc_doss = false THEN F2.mont_ht_fact_sum ELSE F2.mont_ttc_fact_sum END, 0
		) / D.mont_doss) * 100)::NUMERIC(6, 3) AS tx_real_doss,
		CASE WHEN D.est_ttc_doss = false THEN 'HT' ELSE 'TTC' END AS type_mont_doss,
		CASE
			WHEN AVN.int_av = 'Abandonné' THEN (
				SELECT id_av_cp
				FROM public.t_avis_cp
				WHERE int_av_cp = 'Dossier abandonné'
			)
			WHEN D.est_autofin_doss = true THEN (
				SELECT id_av_cp
				FROM public.t_avis_cp
				WHERE int_av_cp = 'Dossier en autofinancement'
			)
			WHEN CDG.id_av_cp IS NULL THEN (
				SELECT id_av_cp
				FROM public.t_avis_cp
				WHERE int_av_cp = 'En attente'
			)
			ELSE CDG.id_av_cp
		END AS id_av_cp
	FROM public.t_dossier AS D
	INNER JOIN public.t_nature_dossier AS N ON N.id_nat_doss = D.id_nat_doss_id
	INNER JOIN public.t_type_dossier AS T ON T.id_type_doss = D.id_type_doss_id
	INNER JOIN public.t_avancement AS AVN ON AVN.id_av = D.id_av_id
	LEFT OUTER JOIN (
		SELECT
			F.id_doss_id AS dos_id_tmp,
			SUM(F.mont_part_fin) AS mont_part_fin_sum
		FROM public.t_financement AS F
		GROUP BY F.id_doss_id
	) AS F ON F.dos_id_tmp = D.id_doss
	LEFT OUTER JOIN (
		SELECT
			P.id_doss_id AS dos_id_tmp,
			SUM(P.mont_prest_doss) AS mont_prest_doss_sum
		FROM public.t_prestations_dossier AS P
		GROUP BY P.id_doss_id
	) AS P ON P.dos_id_tmp = D.id_doss
	LEFT OUTER JOIN (
		SELECT
			A.id_doss_id AS dos_id_tmp,
			SUM(A.mont_aven) AS mont_aven_sum
		FROM public.t_avenant AS A
		GROUP BY A.id_doss_id
	) AS A ON A.dos_id_tmp = D.id_doss
	LEFT OUTER JOIN (
		SELECT
			F.id_doss_id AS dos_id_tmp,
			SUM(F.mont_ht_fact) AS mont_ht_fact_sum,
			SUM(F.mont_ttc_fact) AS mont_ttc_fact_sum
		FROM public.t_facture AS F
		GROUP BY F.id_doss_id
	) AS F2 ON F2.dos_id_tmp = D.id_doss
	LEFT OUTER JOIN (
		SELECT
			ddscdg.dds_id,
			ddscdg.acp_id AS id_av_cp,
			cdg.cdg_date AS dt_av_cp_doss
		FROM public.t_ddscdg AS ddscdg
		INNER JOIN public.t_cdgemapi_cdg AS cdg ON cdg.cdg_id = ddscdg.cdg_id
		WHERE cdg.cdg_date = (
			SELECT MAX(cdg2.cdg_date)
			FROM public.t_ddscdg AS ddscdg2
			INNER JOIN public.t_cdgemapi_cdg AS cdg2 ON cdg2.cdg_id = ddscdg2.cdg_id
			WHERE ddscdg2.dds_id = ddscdg.dds_id
		)
	) AS CDG ON CDG.dds_id = D.id_doss
	'''

	class Meta :
		db_table = 'v_suivi_dossier'
		managed = False

class VSuiviPrestationsDossier(view.View) :

	'''Suivi financier de l'ensemble des prestations d'un dossier (vue système)'''

	# Imports
	from app.classes.MFEuroField import Class as MFEuroField

	# Colonnes
	id_prest_doss = models.IntegerField(db_column = 'id', primary_key = True)
	id_doss = models.ForeignKey(TDossier, db_column = 'id_doss_id', on_delete = models.DO_NOTHING)
	id_prest = models.ForeignKey(TPrestation, db_column = 'id_prest_id', on_delete = models.DO_NOTHING)
	duree_aven_sum = models.IntegerField()
	mont_aven_sum = MFEuroField(verbose_name = 'Somme @ht_ttc@ des avenants')
	mont_ht_fact_sum = MFEuroField(verbose_name = 'Somme HT des factures émises')
	mont_ttc_fact_sum = MFEuroField(verbose_name = 'Somme TTC des factures émises')
	mont_prest_doss = MFEuroField()
	mont_raf = MFEuroField(verbose_name = 'Reste à facturer @ht_ttc@')
	mont_tot_prest_doss = MFEuroField(verbose_name = 'Montant @ht_ttc@ total (avenants compris)')
	nb_aven = models.IntegerField(verbose_name = 'Nombre d\'avenants')
	nb_fact = models.IntegerField(verbose_name = 'Nombre de factures')
	duree_tot_prest_doss = models.IntegerField()
	duree_w_os_sum = models.IntegerField(verbose_name = 'Durée travaillée (en nombre de jours travaillés)')
	duree_w_rest_os_sum = models.IntegerField(
		verbose_name = 'Durée restante à travailler (en nombre de jours travaillés)'
	)
	nbr_os = models.IntegerField(verbose_name = 'Nombre d\'OS')
	mont_fact_sum = MFEuroField()
	mont_fact_mand_sum = MFEuroField()

	# Requête
	sql = '''
	SELECT
		P.id,
		P.id_doss_id,
		P.id_prest_id,
		COALESCE(A.duree_aven_sum, 0) AS duree_aven_sum,
		COALESCE(A.mont_aven_sum, 0)::NUMERIC(26, 2) AS mont_aven_sum,
		COALESCE(F.mont_ht_fact_sum, 0)::NUMERIC(26, 2) AS mont_ht_fact_sum,
		COALESCE(F.mont_ttc_fact_sum, 0)::NUMERIC(26, 2) AS mont_ttc_fact_sum,
		P.mont_prest_doss,
		((P.mont_prest_doss + COALESCE(A.mont_aven_sum, 0)) - COALESCE(
			CASE WHEN D.est_ttc_doss = false THEN F.mont_ht_fact_sum ELSE F.mont_ttc_fact_sum END, 0
		))::NUMERIC(26, 2) AS mont_raf,
		(P.mont_prest_doss + COALESCE(A.mont_aven_sum, 0))::NUMERIC(26, 2) AS mont_tot_prest_doss,
		COALESCE(A.nb_aven, 0) AS nb_aven,
		COALESCE(F.nb_fact, 0) AS nb_fact,
		P.duree_prest_doss + COALESCE(A.duree_aven_sum, 0) AS duree_tot_prest_doss,
		COALESCE(OS.duree_w_os_sum, 0) AS duree_w_os_sum,
		P.duree_prest_doss + COALESCE(A.duree_aven_sum, 0) - COALESCE(OS.duree_w_os_sum, 0)AS duree_w_rest_os_sum,
		COALESCE(OS.nbr_os, 0) AS nbr_os,
		CASE
			WHEN D.est_ttc_doss = true THEN COALESCE(F.mont_ttc_fact_sum, 0)
			ELSE COALESCE(F.mont_ht_fact_sum, 0)
		END AS mont_fact_sum,
		CASE
			WHEN D.est_ttc_doss = true THEN COALESCE(F2.mont_ttc_fact_sum, 0)
			ELSE COALESCE(F2.mont_ht_fact_sum, 0)
		END AS mont_fact_mand_sum
	FROM public.t_prestations_dossier AS P
	INNER JOIN public.t_dossier AS D ON D.id_doss = P.id_doss_id
	LEFT OUTER JOIN (
		SELECT
			A.id_doss_id,
			A.id_prest_id,
			SUM(A.duree_aven) AS duree_aven_sum,
			SUM(A.mont_aven) AS mont_aven_sum,
			COUNT(*) AS nb_aven
		FROM public.t_avenant AS A
		GROUP BY
			A.id_doss_id,
			A.id_prest_id
	) AS A ON (A.id_doss_id = P.id_doss_id AND A.id_prest_id = P.id_prest_id)
	LEFT OUTER JOIN (
		SELECT
			F.id_doss_id,
			F.id_prest_id,
			SUM(mont_ht_fact) AS mont_ht_fact_sum,
			SUM(mont_ttc_fact) AS mont_ttc_fact_sum,
			COUNT(*) AS nb_fact
		FROM public.t_facture AS F
		GROUP BY
			F.id_doss_id,
			F.id_prest_id
	) AS F ON (F.id_doss_id = P.id_doss_id AND F.id_prest_id = P.id_prest_id)
	LEFT OUTER JOIN (
		SELECT
			F.id_doss_id,
			F.id_prest_id,
			SUM(mont_ht_fact) AS mont_ht_fact_sum,
			SUM(mont_ttc_fact) AS mont_ttc_fact_sum
		FROM public.t_facture AS F
		WHERE F.dt_mand_moa_fact IS NOT NULL
		GROUP BY
			F.id_doss_id,
			F.id_prest_id
	) AS F2 ON (F2.id_doss_id = P.id_doss_id AND F2.id_prest_id = P.id_prest_id)
	LEFT OUTER JOIN (
		SELECT
			os.id_doss,
			os.id_prest,
			SUM(os.duree_w_os) AS duree_w_os_sum,
			COUNT(*) AS nbr_os
		FROM public.t_ordre_service AS os
		GROUP BY
			os.id_doss,
			os.id_prest
	) AS OS ON (OS.id_doss = P.id_doss_id AND OS.id_prest = P.id_prest_id)
	'''

	class Meta :
		db_table = 'v_suivi_prestations_dossier'
		managed = False
		ordering = ['id_prest__id_org_prest', 'id_prest__dt_notif_prest', 'id_prest__int_prest']

class VFacture(view.View):

	"""Ensemble des factures (vue système)"""

	# Imports
	from app.classes.MFEuroField import Class as MFEuroField

	# Colonnes
	id_fact = models.IntegerField(primary_key=True)
	mont_tva_fact = MFEuroField()

	# Requête
	sql = '''
	SELECT
		fac.id_fact,
		(fac.mont_ttc_fact - fac.mont_ht_fact)::NUMERIC(26, 2) AS mont_tva_fact
	FROM public.t_facture AS fac
	'''

	class Meta:
		db_table = 'v_facture'
		managed = False