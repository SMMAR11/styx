# coding: utf-8

# Imports
from django import forms

class EtatSubventions(forms.Form):

	# Imports
	from app.constants import DEFAULT_OPTION

	# Filtres

	zl_id_org_fin = forms.ModelChoiceField(
		label='Financeur',
		queryset=None,
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

	zl_id_av_cp = forms.ModelChoiceField(
		label='Etat de programmation',
		queryset=None,
		required=False
	)

	zl_id_av = forms.ModelChoiceField(
		label='Avancement du dossier',
		queryset=None,
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
		from app.models import TFinanceur
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

		self.fields['zl_id_org_fin'].queryset = TFinanceur.objects.all()
		self.fields['zl_id_org_moa'].queryset = TMoa.objects.filter(
			peu_doss=True, en_act_doss=True
		)
		self.fields['zl_id_progr'].queryset = TProgramme.objects.filter(
			en_act=True
		)
		self.fields['zl_id_av_cp'].queryset = TAvisCp.objects.all()
		self.fields['zl_id_av'].queryset = TAvancement.objects.all()

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
			'zl_id_org_fin',
			'zl_id_org_moa',
			'zl_id_progr',
			'zl_axe',
			'zl_ss_axe',
			'zl_act',
			'zl_id_av_cp',
			'zl_id_av'
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
		from app.models import TFinancement
		from app.models import TRegroupementsMoa
		from app.models import TUtilisateur
		from app.models import VFinancement
		from app.models import VSuiviDossier
		from django.urls import reverse

		# Initialisation des données
		data = []

		# Si requête HTTP "GET", alors...
		if not self.data:

			# Définition d'un jeu de données vierge
			qsFins = TFinancement.objects.none()

		# Sinon (requête HTTP "POST")...
		else:

			# Récupération des données nettoyées du formulaire
			cleaned_data = self.__cleaned_data()

			# Initialisation des filtres
			ands = {}

			# Filtre financeur
			id_org_fin = cleaned_data['zl_id_org_fin']
			if id_org_fin:
				ands['id_org_fin'] = id_org_fin

			# Filtre maître d'ouvrage
			id_org_moa = cleaned_data['zl_id_org_moa']
			if id_org_moa:
				moaids = [id_org_moa.pk] + [
					rm.id_org_moa_anc.pk for rm in \
					TRegroupementsMoa.objects.filter(
						id_org_moa_fil=id_org_moa.pk
					)
				]
				ands['id_doss__id_org_moa__in'] = moaids

			# Filtre programme d'actions
			id_progr = cleaned_data['zl_id_progr']
			if id_progr:
				ands['id_doss__id_progr'] = id_progr

			# Filtre axe
			axe = cleaned_data['zl_axe']
			if axe:
				ands['id_doss__num_axe'] = axe.split('_')[-1]

			# Filtre sous-axe
			ss_axe = cleaned_data['zl_ss_axe']
			if ss_axe:
				ands['id_doss__num_ss_axe'] = ss_axe.split('_')[-1]

			# Filtre action
			act = cleaned_data['zl_act']
			if act:
				ands['id_doss__num_act'] = act.split('_')[-1]

			# Filtre état de programmation
			id_av_cp = cleaned_data['zl_id_av_cp']
			if id_av_cp:
				ands['id_doss__pk__in'] = VSuiviDossier.objects.filter(
					id_av_cp=id_av_cp.pk
				).values_list('pk', flat=True)

			# Filtre avancement du dossier
			id_av = cleaned_data['zl_id_av']
			if id_av:
				ands['id_doss__id_av'] = id_av

			# Définition du jeu de données
			_qsFins = TFinancement.objects.filter(**ands)

			# Filtrage des droits d'accès (un utilisateur ne peut
			# accéder aux financements dont il n'a aucune permission en
			# lecture a minima)
			qsFins = TFinancement.objects.none()
			permissions = TUtilisateur.objects.get(pk=self.rq.user.pk) \
				.get_permissions(read_or_write='R')
			for iFin in _qsFins:
				if (
					iFin.id_doss.id_org_moa.pk,
					iFin.id_doss.id_progr.id_type_progr.pk
				) in permissions:
					qsFins |= TFinancement.objects.filter(pk=iFin.pk)

			# Tri par numéro de dossier et par financeur
			qsFins = qsFins.order_by('id_doss', 'id_org_fin')

		# Pour chaque enregistrement...
		for oFin in qsFins:

			# Récupération d'objets
			voDds = VSuiviDossier.objects.get(pk=oFin.id_doss.pk)
			voFin = VFinancement.objects.get(id_fin=oFin.pk)

			# Empilement des données
			data.append({
				'_link': '''
				<a
					href="{}"
					class="consult-icon pull-right"
					target="_blank"
					title="Consulter le financement"
				></a>
				'''.format(reverse('cons_fin', args=[oFin.pk])),
				'num_doss': oFin.id_doss.num_doss,
				'int_doss': voDds.int_doss,
				'id_org_moa': oFin.id_doss.id_org_moa,
				'id_progr': oFin.id_doss.id_progr,
				'num_axe': oFin.id_doss.num_axe,
				'num_ss_axe': oFin.id_doss.num_ss_axe,
				'num_act': oFin.id_doss.num_act,
				'id_nat_doss': oFin.id_doss.id_nat_doss,
				'id_type_doss': oFin.id_doss.id_type_doss,
				'id_techn': oFin.id_doss.id_techn,
				'mont_doss': oFin.id_doss.mont_doss,
				'type_mont_doss': voDds.type_mont_doss,
				'annee_prev_doss': oFin.id_doss.annee_prev_doss,
				'id_av_cp': voDds.id_av_cp,
				'dt_av_cp_doss': voDds.dt_av_cp_doss,
				'id_av': oFin.id_doss.id_av,
				'mont_tot_prest_doss': voDds.mont_tot_prest_doss,
				'mont_fact_sum': voDds.mont_fact_sum,
				'id_org_fin': oFin.id_org_fin,
				'mont_elig_fin': oFin.mont_elig_fin,
				'pourc_elig_fin': oFin.pourc_elig_fin,
				'mont_part_fin': oFin.mont_part_fin,
				'mont_ddv_sum': voFin.mont_ddv_sum,
				'mont_verse_ddv_sum': voFin.mont_verse_ddv_sum,
				'mont_ddv_attente_vers_sum': voFin.mont_ddv_attente_vers_sum,
				'mont_rad': voFin.mont_rad,
				'num_arr_fin': oFin.num_arr_fin,
				'dt_deb_elig_fin': oFin.dt_deb_elig_fin,
				'dt_fin_elig_fin': voFin.dt_fin_elig_fin,
				'dt_lim_deb_oper_fin': oFin.dt_lim_deb_oper_fin
			})

		return data

	def __get_datatable(self):

		"""Mise en forme du tableau"""

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont
		from statistics import mean

		# Récupération des données filtrées
		data = self.__get_data()

		# Mise en forme de la balise </tbody>
		tbody = ''.join(['<tr>{}</tr>'.format(
			''.join(['<td>{}</td>'.format(key) for key in [
				element['_link'],
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
				element['id_av_cp'],
				dt_fr(element['dt_av_cp_doss']) or '',
				element['id_av'],
				obt_mont(element['mont_tot_prest_doss']),
				obt_mont(element['mont_fact_sum']),
				element['id_org_fin'],
				obt_mont(element['mont_elig_fin']) or '',
				element['pourc_elig_fin'] or '',
				obt_mont(element['mont_part_fin']) or '',
				obt_mont(element['mont_ddv_sum']),
				obt_mont(element['mont_verse_ddv_sum']),
				obt_mont(element['mont_ddv_attente_vers_sum']),
				obt_mont(element['mont_rad']),
				element['num_arr_fin'],
				dt_fr(element['dt_deb_elig_fin']) or '',
				dt_fr(element['dt_fin_elig_fin']) or '',
				dt_fr(element['dt_lim_deb_oper_fin']) or ''
			]])
		) for element in data])

		# Mise en forme de la balise </tfoot>
		tfoot = '''
		<tr>
			<td colspan="22">Total</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td colspan="5">{}</td>
		</tr>
		'''.format(
			obt_mont(sum([
				element['mont_part_fin'] or 0 for element in data
			])),
			obt_mont(sum([element['mont_ddv_sum'] for element in data])),
			obt_mont(sum([
				element['mont_verse_ddv_sum'] for element in data
			])),
			obt_mont(sum([
				element['mont_ddv_attente_vers_sum'] for element in data
			])),
			obt_mont(sum([element['mont_rad'] for element in data]))
		) if data else ''

		return '''
		<div class="my-table" id="t_EtatSubventions">
			<table>
				<thead>
					<tr>
						<th rowspan="2"></th>
						<th colspan="18">Programmation</th>
						<th colspan="12">Contribution financière</th>
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
						<th>Avis du comité de programmation - CD GEMAPI</th>
						<th>Date de l'avis du CD GEMAPI</th>
						<th>Etat d'avancement du dossier</th>
						<th>Montant commandé (en €)</th>
						<th>Montant payé (en €)</th>
						<th>Financeur</th>
						<th>Assiette éligible du financeur</th>
						<th>Taux d'aide du financeur sur l'assiette éligible</th>
						<th>Montant maximum de l'aide</th>
						<th>Contribution financière "déjà demandée"</th>
						<th>Contribution financière "déjà versée"</th>
						<th>Contribution financière "en attente de versement"</th>
						<th>Contribution financière "restante à demander"</th>
						<th>N° de référence de l'aide</th>
						<th>Date de début d'éligibilité</th>
						<th>Date de fin d'éligibilité</th>
						<th>Date limite du début de l'opération</th>
					</tr>
				</thead>
				<tbody>{}</tbody>
				<tfoot id="za_tfoot_EtatSubventions">{}</tfoot>
			</table>
		</div>
		'''.format(tbody, tfoot)

	def __get_form(self):

		"""Mise en forme du formulaire"""

		# Imports
		from app.functions import init_f
		from django.template.context_processors import csrf

		# Initialisation des contrôles
		form = init_f(self)

		return '''
		<form action="" method="post" name="f_EtatSubventions" onsubmit="soum_f(event);">
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
					<button class="center-block green-btn my-btn" type="submit">Valider</button>
				</div>
			</fieldset>
		</form>
		'''.format(
			csrf(self.rq)['csrf_token'],
			form['zl_id_org_fin'],
			form['zl_id_org_moa'],
			form['zl_id_progr'],
			form['zl_axe'],
			form['zl_ss_axe'],
			form['zl_act'],
			form['zl_id_av_cp'],
			form['zl_id_av']
		)

	# Méthodes publiques

	def get_datatable(self):
		"""Mise en forme du tableau"""
		return self.__get_datatable()

	def get_form(self):
		"""Mise en forme du formulaire"""
		return self.__get_form()