# coding: utf-8

# Imports
from django import forms

class EtatPrestations(forms.Form):

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

	zl_id_techn = forms.ModelChoiceField(
		label='Agent référent',
		queryset=None,
		required=False
	)

	zl_id_av = forms.ModelChoiceField(
		label='Avancement du dossier',
		queryset=None,
		required=False
	)

	zl_id_nat_prest = forms.ModelChoiceField(
		label='Nature de prestation',
		queryset=None,
		required=False
	)

	zl_id_org_prest = forms.ModelChoiceField(
		label='Prestataire',
		queryset=None,
		required=False
	)

	# Méthodes Django

	def __init__(self, *args, **kwargs):

		# Imports
		from app.functions import init_mess_err
		from app.models import TAction
		from app.models import TAvancement
		from app.models import TAxe
		from app.models import TMoa
		from app.models import TNaturePrestation
		from app.models import TPrestataire
		from app.models import TProgramme
		from app.models import TSousAxe
		from app.models import TTechnicien

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

		self.fields['zl_id_techn'].queryset = TTechnicien.objects.filter(
			en_act=True
		)

		self.fields['zl_id_nat_prest'].queryset \
			= TNaturePrestation.objects.all()

		self.fields['zl_id_org_prest'].queryset = TPrestataire.objects.all()

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
			'zl_id_techn',
			'zl_id_av',
			'zl_id_nat_prest',
			'zl_id_org_prest'
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
		from app.models import TPrestationsDossier
		from app.models import TRegroupementsMoa
		from app.models import TOrdreService
		from app.models import TUtilisateur
		from app.models import VSuiviDossier
		from app.models import VSuiviPrestationsDossier
		from django.urls import reverse

		# Initialisation des données
		data = []

		# Si requête HTTP "GET", alors...
		if not self.data:

			# Définition d'un jeu de données vierge
			qsPrsDdss = TPrestationsDossier.objects.none()

		# Sinon (requête HTTP "POST")...
		else:

			# Récupération des données nettoyées du formulaire
			cleaned_data = self.__cleaned_data()

			# Initialisation des filtres
			ands = {}

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

			# Filtre agent référent
			id_techn = cleaned_data['zl_id_techn']
			if id_techn:
				ands['id_doss__id_techn'] = id_techn

			# Filtre avancement du dossier
			id_av = cleaned_data['zl_id_av']
			if id_av:
				ands['id_doss__id_av'] = id_av

			# Filtre nature de prestation
			id_nat_prest = cleaned_data['zl_id_nat_prest']
			if id_nat_prest:
				ands['id_prest__id_nat_prest'] = id_nat_prest

			# Filtre prestataire
			id_org_prest = cleaned_data['zl_id_org_prest']
			if id_org_prest:
				ands['id_prest__id_org_prest'] = id_org_prest
				
			# Définition du jeu de données
			_qsPrsDdss = TPrestationsDossier.objects.filter(**ands)

			# Filtrage des droits d'accès (un utilisateur ne peut
			# accéder aux prestations dont il n'a aucune permission en
			# lecture a minima)
			qsPrsDdss = TPrestationsDossier.objects.none()
			permissions = TUtilisateur.objects.get(pk=self.rq.user.pk) \
				.get_permissions(read_or_write='R')
			for iPrsDds in _qsPrsDdss:
				if (
					iPrsDds.id_doss.id_org_moa.pk,
					iPrsDds.id_doss.id_progr.id_type_progr.pk
				) in permissions:
					qsPrsDdss |= TPrestationsDossier.objects.filter(
						pk=iPrsDds.pk
					)

		# Pour chaque enregistrement...
		for oPrsDds in qsPrsDdss:

			# Récupération d'objets
			voDds = VSuiviDossier.objects.get(pk=oPrsDds.id_doss.pk)
			voPrsDds = VSuiviPrestationsDossier.objects.get(pk=oPrsDds.pk)
			oOds = TOrdreService.objects.filter(
				id_doss=oPrsDds.id_doss.pk,
				id_prest=oPrsDds.id_prest.pk,
				id_type_os__nom_type_os='Démarrage'
			).last()

			# Empilement des données
			data.append({
				'_link': '''
				<a
					href="{}"
					class="consult-icon pull-right"
					target="_blank"
					title="Consulter la prestation"
				></a>
				'''.format(reverse('cons_prest', args=[oPrsDds.pk])),
				'id_progr': oPrsDds.id_doss.id_progr,
				'num_doss': oPrsDds.id_doss.num_doss,
				'int_doss': voDds.int_doss,
				'id_org_moa': oPrsDds.id_doss.id_org_moa,
				'num_oper_budg_doss': oPrsDds.id_doss.num_oper_budg_doss,
				'id_av': oPrsDds.id_doss.id_av,
				'id_techn': oPrsDds.id_doss.id_techn,
				'id_nat_prest': oPrsDds.id_prest.id_nat_prest,
				'id_org_prest': oPrsDds.id_prest.id_org_prest,
				'nb_aven': voPrsDds.nb_aven,
				'mont_prest_doss': oPrsDds.mont_prest_doss,
				'mont_aven_sum': voPrsDds.mont_aven_sum,
				'mont_tot_prest_doss': voPrsDds.mont_tot_prest_doss,
				'mont_fact_sum': voPrsDds.mont_fact_sum,
				'mont_fact_mand_sum': voPrsDds.mont_fact_mand_sum,
				'mont_raf': voPrsDds.mont_raf,
				'dt_notif_prest': oPrsDds.id_prest.dt_notif_prest or '',
				'd_emiss_os': oOds.d_emiss_os if oOds else '',
				'duree_prest_doss': oPrsDds.duree_prest_doss,
				'duree_aven_sum': voPrsDds.duree_aven_sum,
				'duree_tot_prest_doss': voPrsDds.duree_tot_prest_doss,
				'duree_w_os_sum': voPrsDds.duree_w_os_sum,
				'duree_w_rest_os_sum': voPrsDds.duree_w_rest_os_sum
			})

		return data

	def __get_datatable(self):

		"""Mise en forme du tableau"""

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont

		# Récupération des données filtrées
		data = self.__get_data()

		# Mise en forme de la balise </tbody>
		tbody = ''.join(['<tr>{}</tr>'.format(
			''.join(['<td>{}</td>'.format(key) for key in [
				element['_link'],
				element['id_progr'],
				element['num_doss'],
				element['int_doss'],
				element['id_org_moa'],
				element['num_oper_budg_doss'],
				element['id_av'],
				element['id_techn'],
				element['id_nat_prest'],
				element['id_org_prest'],
				element['nb_aven'],
				obt_mont(element['mont_prest_doss']),
				obt_mont(element['mont_aven_sum']),
				obt_mont(element['mont_tot_prest_doss']),
				obt_mont(element['mont_fact_sum']),
				obt_mont(element['mont_fact_mand_sum']),
				obt_mont(element['mont_raf']),
				dt_fr(element['dt_notif_prest']),
				dt_fr(element['d_emiss_os']),
				element['duree_prest_doss'],
				element['duree_aven_sum'],
				element['duree_tot_prest_doss'],
				element['duree_w_os_sum'],
				element['duree_w_rest_os_sum']
			]])
		) for element in data])

		# Mise en forme de la balise </tfoot>
		tfoot = '''
		<tr>
			<td colspan="11">Total</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td colspan="8">{}</td>
		</tr>
		'''.format(
			obt_mont(sum([element['mont_prest_doss'] for element in data])),
			obt_mont(sum([element['mont_aven_sum'] for element in data])),
			obt_mont(sum([
				element['mont_tot_prest_doss'] for element in data
			])),
			obt_mont(sum([element['mont_fact_sum'] for element in data])),
			obt_mont(sum([
				element['mont_fact_mand_sum'] for element in data
			])),
			obt_mont(sum([element['mont_raf'] for element in data]))
		) if data else ''

		return '''
		<div class="my-table" id="t_EtatPrestations">
			<table>
				<thead>
					<tr>
						<th rowspan="2"></th>
						<th colspan="7">Les dossiers</th>
						<th colspan="3">Caractéristiques des prestations</th>
						<th colspan="6">Gestion financière</th>
						<th colspan="7">Gestion des délais (en jours ouvrés)</th>
					</tr>
					<tr>
						<th>Programme</th>
						<th>N° du dossier</th>
						<th>Intitulé du dossier</th>
						<th>Maître d'ouvrage</th>
						<th>N° d'opération budgétaire du syndicat</th>
						<th>Avancement du dossier</th>
						<th>Agent responsable</th>
						<th>Nature de prestations</th>
						<th>Titulaire</th>
						<th>Nombre d'avenants</th>
						<th>Montant initial de commande (1)</th>
						<th>Montant supplémentaire (avenants) (2)</th>
						<th>Montant total de la prestation (1 + 2)</th>
						<th>Total des factures émises par les prestataires</th>
						<th>Total des factures mandatées</th>
						<th>Total restant à facturer</th>
						<th>Date de notification de la prestation</th>
						<th>Date d'effet de l'OS de démarrage</th>
						<th>Durée initiale de prestation (1)</th>
						<th>Durée supplémentaire (avenants) (2)</th>
						<th>Durée totale de la prestation (1 + 2)</th>
						<th>Durée travaillée</th>
						<th>Durée restante à travaillée</th>
					</tr>
				</thead>
				<tbody>{}</tbody>
				<tfoot id="za_tfoot_EtatPrestations">{}</tfoot>
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
		<form action="" method="post" name="f_EtatPrestations" onsubmit="soum_f(event);">
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
			form['zl_id_techn'],
			form['zl_id_av'],
			form['zl_id_nat_prest'],
			form['zl_id_org_prest']
		)

	# Méthodes publiques

	def get_datatable(self):
		"""Mise en forme du tableau"""
		return self.__get_datatable()

	def get_form(self):
		"""Mise en forme du formulaire"""
		return self.__get_form()