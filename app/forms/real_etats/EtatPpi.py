# coding: utf-8

# Imports
from django import forms

class EtatPpi(forms.Form):

	# Imports
	from app.constants import DEFAULT_OPTION

	# Filtres

	zl_ppi_an = forms.ChoiceField(
		choices=[DEFAULT_OPTION],
		label='Année du PPI',
		required=False
	)

	zl_id_org_moa = forms.ModelChoiceField(
		label='Maître d\'ouvrage',
		queryset=None,
		required=False
	)

	zl_id_progr = forms.ModelChoiceField(
		label='Programme d\'actions',
		queryset=None,
		required=False
	)

	zl_axe = forms.ChoiceField(
		choices=[DEFAULT_OPTION],
		label='Axe',
		required=False,
		widget=forms.Select(attrs={'class': 'hide-field'})
	)

	zl_ss_axe = forms.ChoiceField(
		choices=[DEFAULT_OPTION],
		label='Sous-axe',
		required=False,
		widget=forms.Select(attrs={'class': 'hide-field'})
	)

	zl_act = forms.ChoiceField(
		choices=[DEFAULT_OPTION],
		label='Action',
		required=False,
		widget=forms.Select(attrs={'class': 'hide-field'})
	)

	# Méthodes Django

	def __init__(self, *args, **kwargs):

		# Imports
		from app.functions import init_mess_err
		from app.models import TAction
		from app.models import TAxe
		from app.models import TFinanceur
		from app.models import TMoa
		from app.models import TPlanPluriannuelInvestissementPpi
		from app.models import TProgramme
		from app.models import TSousAxe
		from django.db.models import Min
		from django.db.models import Max

		# Initialisation des arguments
		self.rq = kwargs.pop('kwarg_rq')
		self.pro = kwargs.pop('kwarg_pro', None)
		self.axe = kwargs.pop('kwarg_axe', None)
		self.ssa = kwargs.pop('kwarg_ssa', None)

		super().__init__(*args, **kwargs)

		# Variables globales

		self.qsFins = TFinanceur.objects.all()

		qsPpis = TPlanPluriannuelInvestissementPpi.objects.all()
		ppi_an_min = qsPpis.aggregate(Min('ppi_an'))['ppi_an__min']
		ppi_an_max = qsPpis.aggregate(Max('ppi_an'))['ppi_an__max']
		self.ppi_an_range \
			= range(ppi_an_min, ppi_an_max+1) if ppi_an_max else []

		# Initialisation des messages d'erreur
		init_mess_err(self)

		years = list(set(
			TPlanPluriannuelInvestissementPpi \
				.objects \
				.values_list('ppi_an', flat=True)
		))
		self.fields['zl_ppi_an'].choices += [(i, i) for i in years]

		# Définition des jeux de données des listes déroulantes

		self.fields['zl_id_org_moa'].queryset \
			= TMoa.objects.filter(peu_doss=True, en_act_doss=True)

		self.fields['zl_id_progr'].queryset \
			= TProgramme.objects.filter(en_act=True)

		if self.pro:
			self.fields['zl_axe'].choices = [
				(axe.pk, axe) for axe in TAxe.objects.filter(
					id_progr=self.pro
				)
			]
			if self.axe :
				self.fields['zl_ss_axe'].choices = [
					(ssa.pk, ssa) for ssa in TSousAxe.objects.filter(
						id_axe=self.axe
					)
				]
				if self.ssa :
					self.fields['zl_act'].choices = [
						(act.pk, act) for act in TAction.objects.filter(
							id_ss_axe=self.ssa
						)
					]

	# Méthodes privées

	def __cleaned_data(self):

		"""Récupération des données nettoyées du formulaire"""

		# Définition des clés
		keys = [
			'zl_ppi_an',
			'zl_id_org_moa',
			'zl_id_progr',
			'zl_axe',
			'zl_ss_axe',
			'zl_act'
		]

		if not self.data:
			return {element: self.fields[element].initial for element in keys}
		else:
			return {
				element: self.cleaned_data.get(element) for element in keys
			}

	def __get_data(self):

		"""Récupération des données du tableau"""

		# Imports
		from app.models import TPlanPluriannuelInvestissementPpi
		from app.models import TRegroupementsMoa
		from app.models import TUtilisateur
		from app.models import VFinancement
		from django.core.urlresolvers import reverse

		# Initialisation des données
		data = []

		# Si requête HTTP "GET", alors...
		if not self.data:

			# Définition d'un jeu de données vierge
			qsPpis = TPlanPluriannuelInvestissementPpi.objects.none()

		# Sinon (requête HTTP "POST")...
		else:

			# Récupération des données nettoyées du formulaire
			cleaned_data = self.__cleaned_data()

			# Initialisation des filtres
			ands = {}

			# Filtre année du PPI
			ppi_an = cleaned_data['zl_ppi_an']
			if ppi_an:
				ands['ppi_an'] = ppi_an

			# Filtre maître d'ouvrage
			id_org_moa = cleaned_data['zl_id_org_moa']
			if id_org_moa:
				moaids = [id_org_moa.pk] + [
					rm.id_org_moa_anc.pk for rm in \
					TRegroupementsMoa.objects.filter(
						id_org_moa_fil=id_org_moa.pk
					)
				]
				ands['dds_id__id_org_moa__in'] = moaids

			# Filtre programme d'actions
			id_progr = cleaned_data['zl_id_progr']
			if id_progr:
				ands['dds_id__id_progr'] = id_progr

			# Filtre axe
			axe = cleaned_data['zl_axe']
			if axe:
				ands['dds_id__num_axe'] = axe.split('_')[-1]

			# Filtre sous-axe
			ss_axe = cleaned_data['zl_ss_axe']
			if ss_axe:
				ands['dds_id__num_ss_axe'] = ss_axe.split('_')[-1]

			# Filtre action
			act = cleaned_data['zl_act']
			if act:
				ands['dds_id__num_act'] = act.split('_')[-1]
				
			# Définition du jeu de données
			_qsPpis = TPlanPluriannuelInvestissementPpi.objects.filter(**ands)

			# Filtrage des droits d'accès (un utilisateur ne peut
			# accéder aux plans pluriannuels d'investissement dont il
			# n'a aucune permission en lecture a minima)
			qsPpis = TPlanPluriannuelInvestissementPpi.objects.none()
			permissions = TUtilisateur.objects.get(pk=self.rq.user.pk) \
				.get_permissions(read_or_write='R')
			for iPpi in _qsPpis:
				if (
					iPpi.dds_id.id_org_moa.pk,
					iPpi.dds_id.id_progr.id_type_progr.pk
				) in permissions:
					qsPpis |= TPlanPluriannuelInvestissementPpi \
						.objects \
						.filter(pk=iPpi.pk)

		# Pour chaque enregistrement...
		for oPpi in qsPpis:

			# Récupération d'objets
			voDds = oPpi.dds_id.get_view_object()

			# Définition des données de la ligne Programmation
			_data = {
				'_link': '''
				<a
					href="{}"
					class="consult-icon pull-right"
					target="_blank"
					title="Consulter le PPI"
				></a>
				'''.format(reverse('getppi', args=[oPpi.pk])),
				'ppi_an': oPpi.ppi_an,
				'dds_id__id_progr': oPpi.dds_id.id_progr,
				'dds_id__num_axe': oPpi.dds_id.num_axe,
				'dds_id__id_org_moa': oPpi.dds_id.id_org_moa,
				'dds_id__num_oper_budg_doss': oPpi.dds_id.num_oper_budg_doss,
				'dds_id__num_doss': oPpi.dds_id.num_doss,
				'vdds__int_doss': voDds.int_doss,
				'ppi_ntr_dps': oPpi.ppi_ntr_dps,
				'dds_id__duree_amor_ppi_doss': oPpi.dds_id.duree_amor_ppi_doss,
				'vdds__mont_ht_tot_doss': voDds.mont_ht_tot_doss,
				'vdds__mont_ttc_tot_doss': voDds.mont_ttc_tot_doss,
				'dds_id__priorite_doss': oPpi.dds_id.priorite_doss,
				'vdds__pourc_glob_fin_sum': voDds.pourc_glob_fin_sum,
				'ppi_real_an_pcdt_dps_ttc': oPpi.ppi_real_an_pcdt_dps_ttc,
				'ppi_budget_an_dps_ttc': oPpi.ppi_budget_an_dps_ttc,
				'vppi__ppi_dps_ttc_sum': oPpi.vppi.ppi_dps_ttc_sum,
				'vdds__mont_part_fin_sum': voDds.mont_part_fin_sum,
				'ppi_real_an_pcdt_vsm_previ': oPpi.ppi_real_an_pcdt_vsm_previ,
				'ppi_budget_an_vsm_previ': oPpi.ppi_budget_an_vsm_previ,
				'vppi__ppi_vsm_previ_sum': oPpi.vppi.ppi_vsm_previ_sum,
				'vppi__ppi_tx_eli_fctva_moyen': oPpi.vppi.ppi_tx_eli_fctva_moyen
			}

			# Définition des données de la ligne Subventions attendues
			# (en €)
			for oFin in self.qsFins:
				voFnn = VFinancement.objects.filter(
					id_doss=oPpi.dds_id.pk, id_org_fin=oFin.pk
				).first()
				_data['vfin__mont_part_fin_' + str(oFin.pk)] \
					= voFnn.mont_part_fin if voFnn else 0

			# Définition des données
			for i in self.ppi_an_range:

				oPap = oPpi \
					.tprospectiveannuelleppipap_set \
					.filter(pap_an=i) \
					.first()

				# ... de la ligne Dépenses TTC (en €)
				_data[
					'tprospectiveannuelleppipap_set__pap_dps_ttc_rp_' + str(i)
				] = oPap.pap_dps_ttc_rp if oPap else 0

				# ... de la ligne Versements prévisionnels (en €)
				_data[
					'tprospectiveannuelleppipap_set__pap_vsm_previ_rp_' \
					+ str(i)
				] = oPap.pap_vsm_previ_rp if oPap else 0

				# ... de la ligne Dépenses éligibles FCTVA (en €)
				_data[
					'tprospectiveannuelleppipap_set__pap_dps_eli_fctva_' \
					+ str(i)
				] = oPap.pap_dps_eli_fctva if oPap else 0

			# Empilement des données
			data.append(_data)

		return data

	def __get_datatable(self):

		"""Mise en forme du tableau"""

		# Imports
		from app.functions import obt_mont
		from statistics import mean

		# Récupération des données filtrées
		data = self.__get_data()

		# Mise en forme des parties de la balise <thead/>
		thead2 = ''.join([
			'<th>{} réel projeté</th>'.format(i) for i in self.ppi_an_range
		])
		thead3 = ''.join(['<th>{}</th>'.format(i) for i in self.qsFins])
		thead4 = ''.join([
			'<th>{} réel projeté</th>'.format(i) for i in self.ppi_an_range
		])
		thead5 = ''.join(['<th>Dépenses éligibles FCTVA {}</th>'.format(
			i
		) for i in self.ppi_an_range])

		# Mise en forme de la balise </tbody>
		trs = []
		for element in data:

			# Définition des valeurs des premières balises <td/>
			_tds1 = [
				element['_link'],
				element['ppi_an'],
				element['dds_id__id_progr'],
				element['dds_id__num_axe'],
				element['dds_id__id_org_moa'],
				element['dds_id__num_oper_budg_doss'],
				element['dds_id__num_doss'],
				element['vdds__int_doss'],
				element['ppi_ntr_dps'],
				element['dds_id__duree_amor_ppi_doss'] or '',
				obt_mont(element['vdds__mont_ht_tot_doss']),
				obt_mont(element['vdds__mont_ttc_tot_doss']),
				element['dds_id__priorite_doss'],
				element['vdds__pourc_glob_fin_sum']
			]

			# Définition des valeurs des balises <td/> de la ligne
			# Dépenses TTC (en €)

			_tds2 = [
				obt_mont(element['ppi_real_an_pcdt_dps_ttc']),
				obt_mont(element['ppi_budget_an_dps_ttc'])
			]

			for i in self.ppi_an_range:
				_tds2.append(obt_mont(element[
					'tprospectiveannuelleppipap_set__pap_dps_ttc_rp_' + str(i)
				]))

			_tds2.append(obt_mont(element['vppi__ppi_dps_ttc_sum']))

			# Définition des valeurs des balises <td/> de la ligne
			# Subventions attendues (en €)

			_tds3 = [obt_mont(element['vdds__mont_part_fin_sum'])]

			for oFin in self.qsFins:
				_tds3.append(
					obt_mont(element['vfin__mont_part_fin_' + str(oFin.pk)])
				)

			# Définition des valeurs des balises <td/> de la ligne
			# Versements prévisionnels (en €)

			_tds4 = [
				obt_mont(element['ppi_real_an_pcdt_vsm_previ']),
				obt_mont(element['ppi_budget_an_vsm_previ'])
			]

			for i in self.ppi_an_range:
				_tds4.append(obt_mont(element[
					'tprospectiveannuelleppipap_set__pap_vsm_previ_rp_' \
					+ str(i)
				]))

			_tds4.append(obt_mont(element['vppi__ppi_vsm_previ_sum']))

			# Définition des valeurs des balises <td/> de la ligne
			# Dépenses éligibles FCTVA (en €)

			_tds5 = []

			for i in self.ppi_an_range:
				_tds5.append(obt_mont(element[
					'tprospectiveannuelleppipap_set__pap_dps_eli_fctva_' \
					+ str(i)
				]))

			_tds5.append(element['vppi__ppi_tx_eli_fctva_moyen'])

			# Concaténation des différents tableaux de balises <td/>
			_tds = _tds1 + _tds2 + _tds3 + _tds4 + _tds5

			tds = ''.join(['<td>{}</td>'.format(element2) for element2 in _tds])
			tr = '<tr>{}</tr>'.format(tds)
			trs.append(tr)
		tbody = ''.join(trs)

		# Mise en forme de la balise </tfoot>
		tfoot = '''
		<tr>
			<td colspan="10">Total</td>
			<td>{}</td>
			<td colspan="2">{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			{}
			<td>{}</td>
			<td>{}</td>
			{}
			<td>{}</td>
			<td>{}</td>
			{}
			<td>{}</td>
			{}
			<td>{}</td>
		</tr>
		'''.format(
			obt_mont(sum([
				element['vdds__mont_ht_tot_doss'] for element in data
			])),
			obt_mont(sum([
				element['vdds__mont_ttc_tot_doss'] for element in data
			])),
			round(mean([
				element['vdds__pourc_glob_fin_sum'] or 0 for element in data
			]) if data else 0, 3),
			obt_mont(sum([
				element['ppi_real_an_pcdt_dps_ttc'] for element in data
			])),
			obt_mont(sum([
				element['ppi_budget_an_dps_ttc'] for element in data
			])),
			''.join(['<td>{}</td>'.format(obt_mont(sum(element[
				'tprospectiveannuelleppipap_set__pap_dps_ttc_rp_' + str(i)
			] for element in data))) for i in self.ppi_an_range]),
			obt_mont(sum([
				element['vppi__ppi_dps_ttc_sum'] for element in data
			])),
			obt_mont(sum([
				element['vdds__mont_part_fin_sum'] for element in data
			])),
			''.join(['<td>{}</td>'.format(obt_mont(sum(element[
				'vfin__mont_part_fin_' + str(oFin.pk)
			] for element in data))) for oFin in self.qsFins]),
			obt_mont(sum([
				element['ppi_real_an_pcdt_vsm_previ'] for element in data
			])),
			obt_mont(sum([
				element['ppi_budget_an_vsm_previ'] for element in data
			])),
			''.join(['<td>{}</td>'.format(obt_mont(sum(element[
				'tprospectiveannuelleppipap_set__pap_vsm_previ_rp_' + str(i)
			] for element in data))) for i in self.ppi_an_range]),
			obt_mont(sum([
				element['vppi__ppi_vsm_previ_sum'] for element in data
			])),
			''.join(['<td>{}</td>'.format(obt_mont(sum(element[
				'tprospectiveannuelleppipap_set__pap_dps_eli_fctva_' + str(i)
			] for element in data))) for i in self.ppi_an_range]),
			round(mean([element[
				'vppi__ppi_tx_eli_fctva_moyen'
			] or 0 for element in data]) if data else 0, 3)
		)

		return '''
		<div class="my-table" id="t_EtatPpi">
			<table>
				<thead>
					<tr>
						<th rowspan="2"></th>
						<th rowspan="2">Année du PPI</th>
						<th rowspan="2">Programme d'actions</th>
						<th rowspan="2">Axe</th>
						<th rowspan="2">Maître d'ouvrage</th>
						<th rowspan="2">N° d'opération budgétaire</th>
						<th rowspan="2">N° du dossier</th>
						<th rowspan="2">Intitulé du dossier</th>
						<th rowspan="2">Nature de la dépense</th>
						<th rowspan="2">Durée d'amortissement (en années)</th>
						<th rowspan="2">Montant HT total du dossier (en €)</th>
						<th rowspan="2">Montant TTC total du dossier (en €)</th>
						<th rowspan="2">Priorité du dossier</th>
						<th rowspan="2">Taux des subventions (en %)</th>
						<th colspan="{}">Dépenses TTC (en €)</th>
						<th colspan="{}">Subventions attendues (en €)</th>
						<th colspan="{}">Versements prévisionnels (en €)</th>
						<th colspan="{}">Dépenses éligibles FCTVA (en €)</th>
					</tr>
					<tr>
						<th>Réalisé au 31/12 de l'année précédente du PPI hors RAR</th>
						<th>Budget de l'année du PPI (RAR + nouvelles propositions)</th>
						{}
						<th>Bilan des dépenses TTC</th>
						<th>Total sur l'opération</th>
						{}
						<th>Réalisé au 31/12 de l'année précédente du PPI hors RAR</th>
						<th>Budget de l'année du PPI (RAR + nouvelles propositions)</th>
						{}
						<th>Bilan des subventions</th>
						{}
						<th>Taux d'éligibilité FCTVA moyen (en %)</th>
					</tr>
				</thead>
				<tbody>{}</tbody>
				<tfoot id="za_tfoot_EtatPpi">{}</tfoot>
			</table>
		</div>
		'''.format(
			len(self.ppi_an_range) + 3,
			self.qsFins.count() + 1,
			len(self.ppi_an_range) + 3,
			len(self.ppi_an_range) + 1,
			thead2,
			thead3,
			thead4,
			thead5,
			tbody,
			tfoot
		)

	def __get_form(self):

		"""Mise en forme du formulaire"""

		# Imports
		from app.functions import init_f
		from django.template.context_processors import csrf

		# Initialisation des contrôles
		form = init_f(self)

		return '''
		<form action="" method="post" name="f_EtatPpi" onsubmit="soum_f(event);">
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			<fieldset class="my-fieldset">
				<legend>Filtrer par</legend>
				<div>
					{}
					{}
					{}
					{}
					{}
					{}
					<button class="center-block green-btn my-btn" type="submit">Valider</button>
				</div>
			</fieldset>
		</form>
		'''.format(
			csrf(self.rq)['csrf_token'],
			form['zl_ppi_an'],
			form['zl_id_org_moa'],
			form['zl_id_progr'],
			form['zl_axe'],
			form['zl_ss_axe'],
			form['zl_act']
		)

	# Méthodes publiques

	def get_datatable(self):
		"""Mise en forme du tableau"""
		return self.__get_datatable()

	def get_form(self):
		"""Mise en forme du formulaire"""
		return self.__get_form()