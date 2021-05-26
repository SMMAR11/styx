# coding: utf-8

# Imports
from django import forms

class EtatDossiers(forms.Form):

	# Imports
	from app.constants import DEFAULT_OPTION

	# Filtres

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

	zl_acp_id = forms.ModelChoiceField(
		label='Etat de programmation',
		queryset=None,
		required=False
	)

	zl_cdg_id = forms.ModelChoiceField(
		label='Date du CD GEMAPI',
		queryset=None,
		required=False
	)

	zl_id_av = forms.ModelChoiceField(
		label='Avancement du dossier',
		queryset=None,
		required=False
	)

	zl_id_type_doss = forms.ModelChoiceField(
		label='Type du dossier',
		queryset=None,
		required=False
	)

	zl_id_techn = forms.ModelChoiceField(
		label='Agent référent',
		queryset=None,
		required=False
	)

	zl_id_nat_doss = forms.ModelChoiceField(
		label='Nature du dossier',
		queryset=None,
		required=False
	)

	zl_annee_prev_doss = forms.ChoiceField(
		choices=[DEFAULT_OPTION],
		label='Année prévisionnelle du dossier',
		required=False
	)

	# Méthodes Django

	def __init__(self, *args, **kwargs):

		# Imports
		from app.functions import init_mess_err
		from app.models import TAction
		from app.models import TAvancement
		from app.models import TAvisCp
		from app.models import TAxe
		from app.models import TCDGemapiCdg
		from app.models import TDossier
		from app.models import TMoa
		from app.models import TNatureDossier
		from app.models import TProgramme
		from app.models import TSousAxe
		from app.models import TTechnicien
		from app.models import TTypeDossier

		# Initialisation des arguments
		self.rq = kwargs.pop('kwarg_rq')
		self.pro = kwargs.pop('kwarg_pro', None)
		self.axe = kwargs.pop('kwarg_axe', None)
		self.ssa = kwargs.pop('kwarg_ssa', None)

		super().__init__(*args, **kwargs)

		# Initialisation des messages d'erreur
		init_mess_err(self)

		# Définition des jeux de données des listes déroulantes

		self.fields['zl_id_org_moa'].queryset = TMoa.objects.filter(
			peu_doss=True, en_act_doss=True
		)

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

		self.fields['zl_acp_id'].queryset = TAvisCp.objects.all()

		self.fields['zl_cdg_id'].queryset = TCDGemapiCdg.objects.all()

		self.fields['zl_id_av'].queryset = TAvancement.objects.all()

		self.fields['zl_id_type_doss'].queryset = TTypeDossier.objects.all()

		self.fields['zl_id_techn'].queryset = TTechnicien.objects.filter(
			en_act=True
		)

		self.fields['zl_id_nat_doss'].queryset = TNatureDossier.objects.all()

		years = sorted(list(set([int(i) for i in TDossier.objects.values_list(
			'annee_prev_doss', flat=True
		) if i])))
		self.fields['zl_annee_prev_doss'].choices += [(i, i) for i in years]

	# Méthodes privées

	def __cleaned_data(self):

		"""Récupération des données nettoyées du formulaire"""

		# Définition des clés
		keys = [
			'zl_id_org_moa',
			'zl_id_progr',
			'zl_axe',
			'zl_ss_axe',
			'zl_act',
			'zl_acp_id',
			'zl_cdg_id',
			'zl_id_av',
			'zl_id_type_doss',
			'zl_id_techn',
			'zl_id_nat_doss',
			'zl_annee_prev_doss'
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
		from app.models import TDossier
		from app.models import TFinanceur
		from app.models import TRegroupementsMoa
		from app.models import TUtilisateur
		from app.models import VFinancement
		from app.models import VSuiviDossier
		from django.core.urlresolvers import reverse

		# Initialisation des données
		data = []

		# Si requête HTTP "GET", alors...
		if not self.data:

			# Définition d'un jeu de données vierge
			qsDdss = TDossier.objects.none()

		# Sinon (requête HTTP "POST")...
		else:

			# Récupération des données nettoyées du formulaire
			cleaned_data = self.__cleaned_data()

			# Initialisation des filtres
			ands = {}

			# Initialisation des filtres "pk__in"
			pks = []

			# Filtre maître d'ouvrage
			id_org_moa = cleaned_data['zl_id_org_moa']
			if id_org_moa:
				moaids = [id_org_moa.pk] + [
					rm.id_org_moa_anc.pk for rm in \
					TRegroupementsMoa.objects.filter(
						id_org_moa_fil=id_org_moa.pk
					)
				]
				ands['id_org_moa__in'] = moaids

			# Filtre programme d'actions
			id_progr = cleaned_data['zl_id_progr']
			if id_progr:
				ands['id_progr'] = id_progr

			# Filtre axe
			axe = cleaned_data['zl_axe']
			if axe:
				ands['num_axe'] = axe.split('_')[-1]

			# Filtre sous-axe
			ss_axe = cleaned_data['zl_ss_axe']
			if ss_axe:
				ands['num_ss_axe'] = ss_axe.split('_')[-1]

			# Filtre action
			act = cleaned_data['zl_act']
			if act:
				ands['num_act'] = act.split('_')[-1]

			# Filtre état de programmation
			acp_id = cleaned_data['zl_acp_id']
			if acp_id:
				pks.append(VSuiviDossier.objects.filter(
					id_av_cp=acp_id.pk
				).values_list('pk', flat=True))

			# Filtre date du CD GEMAPI
			cdg_id = cleaned_data['zl_cdg_id']
			if cdg_id:
				pks.append(VSuiviDossier.objects.filter(
					dt_av_cp_doss=cdg_id.cdg_date
				).values_list('pk', flat=True))

			# Filtre avancement du dossier
			id_av = cleaned_data['zl_id_av']
			if id_av:
				ands['id_av'] = id_av

			# Filtre type du dossier
			id_type_doss = cleaned_data['zl_id_type_doss']
			if id_type_doss:
				ands['id_type_doss'] = id_type_doss

			# Filtre agent référent
			id_techn = cleaned_data['zl_id_techn']
			if id_techn:
				ands['id_techn'] = id_techn

			# Filtre nature du dossier
			id_nat_doss = cleaned_data['zl_id_nat_doss']
			if id_nat_doss:
				ands['id_nat_doss'] = id_nat_doss

			annee_prev_doss = cleaned_data['zl_annee_prev_doss']
			if annee_prev_doss:
				ands['annee_prev_doss'] = annee_prev_doss

			# Filtre "pk__in"
			if pks:
				ands['pk__in'] = set(pks[0]).intersection(*pks)
				
			# Définition du jeu de données
			_qsDdss = TDossier.objects.filter(**ands)

			# Filtrage des droits d'accès (un utilisateur ne peut
			# accéder aux dossiers dont il n'a aucune permission en
			# lecture a minima)
			qsDdss = TDossier.objects.none()
			permissions = TUtilisateur.objects.get(pk=self.rq.user.pk) \
				.get_permissions(read_or_write='R')
			for iDds in _qsDdss:
				if (
					iDds.id_org_moa.pk,
					iDds.id_progr.id_type_progr.pk
				) in permissions:
					qsDdss |= TDossier.objects.filter(pk=iDds.pk)

		# Pour chaque enregistrement...
		for oDds in qsDdss:

			# Récupération d'objets
			voDds = VSuiviDossier.objects.get(pk=oDds.pk)

			# Définition des données de la ligne Programmation
			_data = {
				'_link': '''
				<a
					href="{}"
					class="consult-icon pull-right"
					target="_blank"
					title="Consulter le dossier"
				></a>
				'''.format(reverse('cons_doss', args=[oDds.pk])),
				'id_progr': oDds.id_progr,
				'num_doss': oDds.num_doss,
				'int_doss': voDds.int_doss,
				'num_oper_budg_doss': oDds.num_oper_budg_doss,
				'id_org_moa': oDds.id_org_moa,
				'num_axe': oDds.num_axe,
				'num_ss_axe': oDds.num_ss_axe,
				'num_act': oDds.num_act,
				'id_nat_doss': oDds.id_nat_doss,
				'id_type_doss': oDds.id_type_doss,
				'id_techn': oDds.id_techn,
				'id_sage': oDds.id_sage,
				'mont_doss': oDds.mont_doss,
				'mont_suppl_doss': oDds.mont_suppl_doss,
				'mont_tot_doss': voDds.mont_tot_doss,
				'type_mont_doss': voDds.type_mont_doss,
				'annee_prev_doss': oDds.annee_prev_doss,
				'priorite_doss': oDds.priorite_doss,
				'id_av': oDds.id_av,
				'dt_delib_moa_doss': oDds.dt_delib_moa_doss,
				'dt_av_cp_doss': voDds.dt_av_cp_doss,
				'id_av_cp': voDds.id_av_cp,
				'mont_tot_prest_doss': voDds.mont_tot_prest_doss,
				'mont_fact_sum': voDds.mont_fact_sum,
				'tx_engag_doss': voDds.tx_engag_doss,
				'tx_real_doss': voDds.tx_real_doss
			}

			# Récupération des financeurs
			qsFins = TFinanceur.objects.all()

			# Définition des données de la ligne Financement
			# prévisionnel (= plan de financement)
			_data['mont_part_fin_autofin'] = VFinancement.objects.get(
				id_doss=oDds.pk, id_org_fin=None
			).mont_part_fin
			for oFin in qsFins:
				voFnn = VFinancement.objects.filter(
					id_doss=oDds.pk, id_org_fin=oFin.pk
				).first()
				_data['mont_part_fin_' + str(oFin.pk)] \
					= voFnn.mont_part_fin if voFnn else 0

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
		from statistics import mean

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
				element['_link'],
				element['id_progr'],
				element['num_doss'],
				element['int_doss'],
				element['num_oper_budg_doss'],
				element['id_org_moa'],
				element['num_axe'],
				element['num_ss_axe'],
				element['num_act'],
				element['id_nat_doss'],
				element['id_type_doss'],
				element['id_techn'],
				element['id_sage'] or '',
				obt_mont(element['mont_doss']),
				obt_mont(element['mont_suppl_doss']),
				obt_mont(element['mont_tot_doss']),
				element['type_mont_doss'],
				element['annee_prev_doss'] or '',
				element['priorite_doss'],
				element['id_av'],
				dt_fr(element['dt_delib_moa_doss']) or '',
				dt_fr(element['dt_av_cp_doss']) or '',
				element['id_av_cp'],
				obt_mont(element['mont_tot_prest_doss']),
				obt_mont(element['mont_fact_sum']),
				element['tx_engag_doss'],
				element['tx_real_doss']
			]

			# Définition des valeurs de la ligne Financement
			# prévisionnel (= plan de financement)
			_tds.append(obt_mont(element['mont_part_fin_autofin']))
			for oFin in qsFins:
				_tds.append(obt_mont(
					element['mont_part_fin_' + str(oFin.pk)]
				))

			tds = ''.join(['<td>{}</td>'.format(element2) for element2 in _tds])
			tr = '<tr>{}</tr>'.format(tds)
			trs.append(tr)
		tbody = ''.join(trs)

		# Mise en forme de la partie de la balise </tfoot> consacrée
		# aux financeurs
		tfoot_fins = ''.join([
			'<td>{}</td>'.format(obt_mont(sum(
				element['mont_part_fin_' + str(oFin.pk)] for element in data
			))) for oFin in qsFins
		])

		# Mise en forme de la balise </tfoot>
		tfoot = '''
		<tr>
			<td colspan="13">Total</td>
			<td>{}</td>
			<td>{}</td>
			<td colspan="8">{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			{}
		</tr>
		'''.format(
			obt_mont(sum([element['mont_doss'] for element in data])),
			obt_mont(sum([element['mont_suppl_doss'] for element in data])),
			obt_mont(sum([element['mont_tot_doss'] for element in data])),
			obt_mont(sum([
				element['mont_tot_prest_doss'] for element in data
			])),
			obt_mont(sum([element['mont_fact_sum'] for element in data])),
			round(mean([
				element['tx_engag_doss'] or 0 for element in data
			]) if data else 0, 3),
			round(mean([
				element['tx_real_doss'] or 0 for element in data
			]) if data else 0, 3),
			obt_mont(sum([
				element['mont_part_fin_autofin'] for element in data
			])),
			tfoot_fins
		) if data else ''

		return '''
		<div class="my-table" id="t_EtatDossiers">
			<table>
				<thead>
					<tr>
						<th rowspan="2"></th>
						<th colspan="26">Programmation</th>
						<th colspan="{}">Financement prévisionnel (= plan de financement)</th>
					</tr>
					<tr>
						<th>Programme d'actions</th>
						<th>N° du dossier</th>
						<th>Intitulé du dossier</th>
						<th>N° d'opération budgétaire</th>
						<th>Maître d'ouvrage</th>
						<th>Axe</th>
						<th>Sous-axe</th>
						<th>Action</th>
						<th>Nature du dossier</th>
						<th>Type de dossier</th>
						<th>Agent responsable</th>
						<th>SAGE</th>
						<th>Montant du dossier présenté au CD GEMAPI (en €) <span class="field-complement">(A)</span></th>
						<th>Dépassement du dossier (en €)</th>
						<th>Montant total du dossier (en €)</th>
						<th>Type de montant du dossier</th>
						<th>Année prévisionnelle d'engagement du dossier</th>
						<th>Priorité</th>
						<th>Etat d'avancement du dossier</th>
						<th>Date de délibération au maître d'ouvrage</th>
						<th>Date du CD GEMAPI</th>
						<th>Avis du CD GEMAPI</th>
						<th>Montant commandé <span class="field-complement">(B)</span></th>
						<th>Montant payé <span class="field-complement">(C)</span></th>
						<th>Taux d'engagement <span class="field-complement">(B/A)</span></th>
						<th>Taux de réalisation <span class="field-complement">(C/B)</span></th>
						<th>Autofinancement</th>
						{}
					</tr>
				</thead>
				<tbody>{}</tbody>
				<tfoot id="za_tfoot_EtatDossiers">{}</tfoot>
			</table>
		</div>
		'''.format(
			qsFins_count + 1,
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
		<form action="" method="post" name="f_EtatDossiers" onsubmit="soum_f(event);">
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
			form['zl_id_org_moa'],
			form['zl_id_progr'],
			form['zl_axe'],
			form['zl_ss_axe'],
			form['zl_act'],
			form['zl_acp_id'],
			form['zl_cdg_id'],
			form['zl_id_av'],
			form['zl_id_type_doss'],
			form['zl_id_techn'],
			form['zl_id_nat_doss'],
			form['zl_annee_prev_doss']
		)

	# Méthodes publiques

	def get_datatable(self):
		"""Mise en forme du tableau"""
		return self.__get_datatable()

	def get_form(self):
		"""Mise en forme du formulaire"""
		return self.__get_form()