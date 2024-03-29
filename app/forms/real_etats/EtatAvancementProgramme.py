# coding: utf-8

# Imports
from django import forms

class EtatAvancementProgramme(forms.Form):

	# Imports
	from app.constants import DEFAULT_OPTION

	# Filtres

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
		from app.models import TAxe
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

		self.fields['zl_id_progr'].queryset = TProgramme.objects.filter(
			pk__in = [
				element[0] for element in self.__get_data(code='PRO')[1]
			]
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

	def __get_data(self, code=None) :

		"""Récupération des données du tableau"""

		# Imports
		from django.db import connection

		# Renvoi du couple entêtes/lignes
		with connection.cursor() as c:
			try:
				c.execute(self.__get_sql(code=code))
				return [c.description, c.fetchall()]
			except:
				return []

	def __get_datatable(self):

		"""Mise en forme du tableau"""

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont

		# Récupération des données filtrées
		data = self.__get_data()

		# Erreur si requête incorrecte
		if not data:
			raise Exception('PB !')

		# Définition des colonnes à ne pas afficher
		undisplayed_ndxs = [0, 1, 2, 3, 4, 5]

		# Mise en forme de la balise </tbody>
		trs = []
		for element in data[1]:
			tds = []
			for ndx, element2 in enumerate(element):
				if ndx not in undisplayed_ndxs:
					td = '<td>{}</td>'.format(
						element2 if element2 is not None else ''
					)
					tds.append(td)
			tr = '<tr>{}</tr>'.format(''.join(tds))
			trs.append(tr)
		tbody = ''.join(trs)

		# Récupération des différents montants globaux (contractualisé,
		# programmé, commandé et facturé)
		col_a = sum([element[16] or 0 for element in data[1]])
		col_b = sum([element[21] or 0 for element in data[1]])
		col_c = sum([element[24] or 0 for element in data[1]])
		col_d = sum([element[27] or 0 for element in data[1]])

		# Mise en forme de la balise </tfoot>
		tfoot = '''
		<tr>
			<td colspan="7">Total</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td colspan="2">{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
			<td>{}</td>
		</tr>
		'''.format(
			sum([element[13] or 0 for element in data[1]]),
			sum([element[14] for element in data[1]]),
			sum([element[15] for element in data[1]]),
			round(col_a, 2),
			round(sum([element[18] or 0 for element in data[1]]), 2),
			round(sum([element[19] or 0 for element in data[1]]), 2),
			round(sum([element[20] or 0 for element in data[1]]), 2),
			round(col_b, 2),
			round(sum([element[22] or 0 for element in data[1]]), 2),
			round(sum([element[23] or 0 for element in data[1]]), 2),
			round(col_c, 2),
			round(sum([element[25] or 0 for element in data[1]]), 2),
			round(sum([element[26] or 0 for element in data[1]]), 2),
			round(col_d, 2),
			round(((col_b / col_a) if col_a > 0 else 0) * 100, 2),
			round(((col_c / col_b) if col_b > 0 else 0) * 100, 2),
			round(((col_d / col_c) if col_c > 0 else 0) * 100, 2)
		) if data[1] else ''

		return '''
		<div class="my-table" id="t_EtatAvancementProgramme">
			<table>
				<thead>
					<tr>
						<th rowspan="2">Programme d'actions</th>
						<th rowspan="2">Axe</th>
						<th rowspan="2">Sous-axe</th>
						<th rowspan="2">Action</th>
						<th rowspan="2">Libellé (axe)</th>
						<th rowspan="2">Libellé (action)</th>
						<th rowspan="2">Maître d\'ouvrage</th>
						<th rowspan="2">Programme - Nombre de dossiers</th>
						<th rowspan="2">STYX - Nombre de dossiers créés</th>
						<th rowspan="2">STYX - Nombre de dossiers programmés au CD GEMAPI</th>
						<th rowspan="2">Programme - Montant contractualisé (en €) <span class="field-complement">(A)</span></th>
						<th rowspan="2">Programme - HT/TTC</th>
						<th colspan="4"> Montant programmé (en €)</th>
						<th colspan="3"> Montant commandé (en €)</th>
						<th colspan="3"> Montant facturé (en €)</th>
						<th rowspan="2">Taux de programmation (en %) <span class="field-complement">(B/A)</span></th>
						<th rowspan="2">Taux d'engagement (en %) <span class="field-complement">(C/B)</span></th>
						<th rowspan="2">Taux de réalisation (en %) <span class="field-complement">(D/C)</span></th>
					</tr>
					<tr>
						<th>SMMAR et syndicats (CD GEMAPI)</th>
						<th>SMMAR et syndicats (autofinancement)</th>
						<th>Autres</th>
						<th>Total <span class="field-complement">(B)</span></th>
						<th>SMMAR et syndicats</th>
						<th>Autres</th>
						<th>Total <span class="field-complement">(C)</span></th>
						<th>SMMAR et syndicats</th>
						<th>Autres</th>
						<th>Total <span class="field-complement">(D)</span></th>
					</tr>
				</thead>
				<tbody>{}</tbody>
				<tfoot id="za_tfoot_EtatAvancementProgramme">{}</tfoot>
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
		<form action="" method="post" name="f_EtatAvancementProgramme" onsubmit="soum_f(event);">
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			<fieldset class="my-fieldset">
				<legend>Filtrer par</legend>
				<div>
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
			form['zl_id_progr'],
			form['zl_axe'],
			form['zl_ss_axe'],
			form['zl_act'],
			form['zl_id_org_moa']
		)

	def __get_sql(self, code):

		"""Mise en forme de la requête SQL"""

		# Imports
		from app.models import TUtilisateur

		# Requête de sélection des programmes dont les montants
		# contractualisés ont été renseignés dans la base de données
		if code == 'PRO':
			sql = 'SELECT DISTINCT "_proId" FROM "hors_public"."v_suivi_prg";'

		# Requête de sélection des données du tableau
		else:

			# Initialisation de la requête SQL
			sql = 'SELECT * FROM "hors_public"."v_suivi_prg"'

			# Initialisation des filtres
			ands = []

			# Si requête HTTP "GET", alors renvoi d'un jeu de données vierge
			if not self.data:
				ands.append('1 = 0')

			# Sinon (requête HTTP "POST")...
			else:

				# Récupération des données nettoyées du formulaire
				cleaned_data = self.__cleaned_data()

				# Filtrage des droits d'accès (un utilisateur ne peut
				# accéder aux programmes dont il n'a aucune permission
				# en lecture a minima)
				ors = []
				permissions = TUtilisateur.objects.get(pk=self.rq.user.pk) \
					.get_permissions(read_or_write='R')
				for i in permissions:
					# Filtrage sur le couple maître d'ouvrage/type de
					# programme d'actions
					ors.append(
						'( \'' \
						+ str(i[0]) \
						+ '\' = any(string_to_array("_moaId", \';\')) ' \
						+ 'AND "_typId" = \'' \
						+ str(i[1]) \
						+ '\')'
					)
					# Affichage des lignes sans maître d'ouvrage
					# affecté
					ors.append(
						'("_moaId" = \'\' AND "_typId" = \'' \
						+ str(i[1]) \
						+ '\')'
					)
				if len(ors) > 0:
					ands.append('(' + ' OR '.join(ors) + ')')

				# Filtre programme d'actions
				id_progr = cleaned_data['zl_id_progr']
				if id_progr:
					ands.append('"_proId" = \'' + str(id_progr.pk) + '\'')

				# Filtre axe
				axe = cleaned_data['zl_axe']
				if axe:
					ands.append(
						'"_axeId" = \'' + str(axe.split('_')[-1]) + '\''
					)

				# Filtre sous-axe
				ss_axe = cleaned_data['zl_ss_axe']
				if ss_axe:
					ands.append(
						'"_ssaId" = \'' + str(ss_axe.split('_')[-1]) + '\''
					)

				# Filtre action
				act = cleaned_data['zl_act']
				if act:
					ands.append(
						'"_actId" = \'' + str(act.split('_')[-1]) + '\''
					)

				# Filtre maître d'ouvrage
				moa = cleaned_data['zl_id_org_moa']
				if moa:
					ands.append(
						'"_moaId" = \'' + str(moa.pk) + '\''
					)

			# Application des filtres
			if ands:
				sql += ' WHERE ' + ' AND '.join(ands)

			# Intégration du point-virgule final (facultatif)
			sql += ';'

		return sql

	# Méthodes publiques

	def get_datatable(self):
		"""Mise en forme du tableau"""
		return self.__get_datatable()

	def get_form(self):
		"""Mise en forme du formulaire"""
		return self.__get_form()