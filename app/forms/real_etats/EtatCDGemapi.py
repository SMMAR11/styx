# coding: utf-8

# Imports
from django import forms

class EtatCDGemapi(forms.Form):

	# Imports
	from app.constants import DEFAULT_OPTION

	# Filtres

	zl_cdg_id = forms.ModelChoiceField(
		label='Date du CD GEMAPI',
		queryset=None,
		required=False
	)

	zl_acp_id = forms.ModelChoiceField(
		label='Etat de programmation',
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

	zl_id_org_moa = forms.ModelChoiceField(
		label='Maître d\'ouvrage',
		queryset=None,
		required=False
	)

	# Méthodes Django

	def __init__(self, *args, **kwargs):

		# Imports
		from app.functions import init_mess_err
		from app.models import TAction
		from app.models import TAvisCp
		from app.models import TAxe
		from app.models import TCDGemapiCdg
		from app.models import TMoa
		from app.models import TProgramme
		from app.models import TSousAxe

		# Initialisation des arguments
		self.rq = kwargs.pop('kwarg_rq')
		self.pro = kwargs.pop('kwarg_pro', None)
		self.axe = kwargs.pop('kwarg_axe', None)
		self.ssa = kwargs.pop('kwarg_ssa', None)

		super().__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		# Définition des jeux de données des listes déroulantes

		self.fields['zl_cdg_id'].queryset = TCDGemapiCdg.objects.all()

		self.fields['zl_acp_id'].queryset = TAvisCp.objects.all()

		self.fields['zl_id_progr'].queryset = TProgramme.objects.filter(
			en_act=True
		)

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

		self.fields['zl_id_org_moa'].queryset = TMoa.objects.filter(
			peu_doss=True, en_act_doss=True
		)

	# Méthodes privées

	def __cleaned_data(self):

		"""Récupération des données nettoyées du formulaire"""

		# Définition des clés
		keys = [
			'zl_cdg_id',
			'zl_acp_id',
			'zl_id_progr',
			'zl_axe',
			'zl_ss_axe',
			'zl_act',
			'zl_id_org_moa'
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
		from app.models import TAcpFinDdsCdg
		from app.models import TDdsCdg
		from app.models import TFinanceur
		from app.models import TRegroupementsMoa
		from app.models import VFinancement
		from app.models import VSuiviDossier

		# Initialisation des données
		data = []

		# Si requête HTTP "GET", alors...
		if not self.data:

			# Définition d'un jeu de données vierge
			qsDdsCdgs = TDdsCdg.objects.none()

		# Sinon (requête HTTP "POST")...
		else:

			# Récupération des données nettoyées du formulaire
			cleaned_data = self.__cleaned_data()

			# Initialisation des filtres
			ands = {}

			# Filtre date du CD GEMAPI
			cdg_id = cleaned_data['zl_cdg_id']
			if cdg_id:
				ands['cdg_id'] = cdg_id

			# Filtre état de programmation
			acp_id = cleaned_data['zl_acp_id']
			if acp_id:
				ands['acp_id'] = acp_id

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
				
			# Définition du jeu de données
			qsDdsCdgs = TDdsCdg.objects.filter(**ands)

		# Pour chaque enregistrement...
		for oDdsCdg in qsDdsCdgs:

			# Récupération d'objets
			voDds = VSuiviDossier.objects.get(pk=oDdsCdg.dds_id.pk)

			# Définition des données de la ligne Programmation
			_data = {
				'num_doss': oDdsCdg.dds_id.num_doss,
				'int_doss': voDds.int_doss,
				'id_org_moa': oDdsCdg.dds_id.id_org_moa,
				'id_progr': oDdsCdg.dds_id.id_progr,
				'num_axe': oDdsCdg.dds_id.num_axe,
				'num_ss_axe': oDdsCdg.dds_id.num_ss_axe,
				'num_act': oDdsCdg.dds_id.num_act,
				'id_nat_doss': oDdsCdg.dds_id.id_nat_doss,
				'id_type_doss': oDdsCdg.dds_id.id_type_doss,
				'id_techn': oDdsCdg.dds_id.id_techn,
				'mont_doss': oDdsCdg.dds_id.mont_doss,
				'type_mont_doss': voDds.type_mont_doss,
				'annee_prev_doss': oDdsCdg.dds_id.annee_prev_doss,
				'cdg_date': oDdsCdg.cdg_id.cdg_date,
				'acp_id': oDdsCdg.acp_id
			}

			# Récupération des financeurs
			qsFins = TFinanceur.objects.all()

			# Définition des données de la ligne Avis des financeurs
			for oFin in qsFins:
				oAcpFinDdsCdg = TAcpFinDdsCdg.objects.filter(
					ddscdg_id=oDdsCdg.pk, fin_id=oFin.pk
				).first()
				_data['acp_id_' + str(oFin.pk)] \
					= oAcpFinDdsCdg.acp_id if oAcpFinDdsCdg else ''

			# Définition des données de la ligne Plan de financement en
			# vigueur
			for oFin in qsFins:
				voFnn = VFinancement.objects.filter(
					id_doss=oDdsCdg.dds_id.pk, id_org_fin=oFin.pk
				).first()
				_data['mont_part_fin_' + str(oFin.pk)] \
					= voFnn.mont_part_fin if voFnn else 0
			_data['mont_part_fin_autofin'] = VFinancement.objects.get(
				id_doss=oDdsCdg.dds_id.pk, id_org_fin=None
			).mont_part_fin

			# Empilement des données
			data.append(_data)

		return data

	def __get_datatable(self):

		"""Mise en forme du tableau"""

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont
		from app.models import TFinanceur
		from app.models import VFinancement

		# Récupération des financeurs
		qsFins = TFinanceur.objects.all()
		# Récupération du nombre de financeurs
		qsFins_count = qsFins.count()

		# Récupération des données filtrées
		data = self.__get_data()

		# Mise en forme de la partie de la balise </thead> consacrée
		# aux financeurs
		thead_fins = ''.join(['<th>{}</th>'.format(fin) for fin in qsFins])

		# Mise en forme de la balise </tbody>
		trs = []
		for element in data:

			# Définition des valeurs de la ligne Programmation
			_tds = [
				element['num_doss'],
				element['int_doss'],
				element['id_org_moa'],
				element['id_progr'],
				element['num_axe'],
				element['num_ss_axe'],
				element['num_act'],
				element['id_nat_doss'],
				element['id_type_doss'],
				element['id_techn'],
				obt_mont(element['mont_doss']),
				element['type_mont_doss'],
				element['annee_prev_doss'] or '',
				dt_fr(element['cdg_date']),
				element['acp_id']
			]

			# Définition des valeurs de la ligne Avis des financeurs
			for oFin in qsFins:
				_tds.append(element['acp_id_' + str(oFin.pk)])

			# Définition des valeurs de la ligne Plan de financement en
			# vigueur
			for oFin in qsFins:
				_tds.append(obt_mont(
					element['mont_part_fin_' + str(oFin.pk)]
				))
			_tds.append(obt_mont(element['mont_part_fin_autofin']))

			tds = ''.join(['<td>{}</td>'.format(element2) for element2 in _tds])
			tr = '<tr>{}</tr>'.format(tds)
			trs.append(tr)
		tbody = ''.join(trs)

		# Mise en forme de la partie de la balise </tfoot> consacrée
		# au plan de financement en vigueur
		tfoot_fins = ''.join([
			'<td>{}</td>'.format(obt_mont(sum(
				element['mont_part_fin_' + str(oFin.pk)] for element in data
			))) for oFin in qsFins
		])

		# Mise en forme de la balise </tfoot>
		tfoot = '''
		<tr>
			<td colspan="10">Total</td>
			<td colspan="{}">{}</td>
			{}
			<td>{}</td>
		</tr>
		'''.format(
			5 + qsFins_count,
			obt_mont(sum([element['mont_doss'] for element in data])),
			tfoot_fins,
			obt_mont(sum([
				element['mont_part_fin_autofin'] for element in data
			]))
		) if data else ''

		return '''
		<div class="my-table" id="t_EtatCDGemapi">
			<table>
				<thead>
					<tr>
						<th colspan="15">Programmation</th>
						<th colspan="{}">Avis des financeurs</th>
						<th colspan="{}">Plan de financement en vigueur</th>
					</tr>
					<tr>
						<th>N° du dossier</th>
						<th>Intitulé du dossier</th>
						<th>Maître d'ouvrage</th>
						<th>Programme</th>
						<th>Axe</th>
						<th>Sous-axe</th>
						<th>Action</th>
						<th>Nature du dossier</th>
						<th>Type de dossier</th>
						<th>Agent responsable</th>
						<th>Montant du dossier présenté au CD GEMAPI (en €)</th>
						<th>Type de montant du dossier</th>
						<th>Année prévisionnelle d'engagement du dossier</th>
						<th>Date du CD GEMAPI</th>
						<th>Avis global du comité de programmation - CD GEMAPI</th>
						{}
						{}
						<th>Autofinancement</th>
					</tr>
				</thead>
				<tbody>{}</tbody>
				<tfoot id="za_tfoot_EtatCDGemapi">{}</tfoot>
			</table>
		</div>
		'''.format(
			qsFins_count,
			qsFins_count + 1,
			thead_fins,
			thead_fins,
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
		<form action="" method="post" name="f_EtatCDGemapi" onsubmit="soum_f(event);">
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
					{}
					<button class="center-block green-btn my-btn" type="submit">Valider</button>
				</div>
			</fieldset>
		</form>
		'''.format(
			csrf(self.rq)['csrf_token'],
			form['zl_cdg_id'],
			form['zl_acp_id'],
			form['zl_id_progr'],
			form['zl_axe'],
			form['zl_ss_axe'],
			form['zl_act'],
			form['zl_id_org_moa']
		)

	# Méthodes publiques

	def get_datatable(self):
		"""Mise en forme du tableau"""
		return self.__get_datatable()

	def get_form(self):
		"""Mise en forme du formulaire"""
		return self.__get_form()