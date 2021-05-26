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
		from statistics import mean

		# Récupération des données filtrées
		data = self.__get_data()

		# Erreur si requête incorrecte
		if not data:
			raise Exception('PB !')

		# Définition des colonnes à ne pas afficher
		undisplayed_ndxs = [0, 1, 2, 3, 4, 5]

		# Définition des labels
		lbls = {
			'PRO': 'Programme d\'actions',
			'AXE': 'Axe',
			'SS-AXE': 'Sous-axe',
			'ACTION': 'Action',
			'LIB-AXE': 'Libellé (axe)',
			'LIB-ACTION': 'Libellé (action)',
			'MOA': 'Maître d\'ouvrage',
			'PRO-NBRE-DDS': 'Programme - Nombre de dossiers',
			'STYX-NBRE-DDS': 'STYX - Nombre de dossiers créés',
			'STYX-NBRE-DDS-PRO': '''
			STYX - Nombre de dossiers programmés au CD GEMAPI
			''',
			'PRO-MNT-CONTRAC': '''
			Programme - Montant contractualisé (en €) <span
			class="field-complement">(A)</span>
			''',
			'PRO-HT-TTC': 'Programme - HT/TTC',
			'STYX-MNT-PRO-CDG': '''
			STYX- Montant des dossiers programmés au CD GEMAPI
			''',
			'STYX-MNT-PRO-AUTRES': '''
			STYX - Montant des dossiers programmés en autofinancement
			''',
			'STYX-MNT-PRO': '''
			Montant programmé (en €) <span class="field-complement">(B)</span>
			''',
			'STYX-MNT-COM': '''
			Montant commandé (en €) <span class="field-complement">(C)</span>
			''',
			'STYX-MNT-FAC': '''
			Montant facturé (en €) <span class="field-complement">(D)</span>
			''',
			'TX-PRO': '''
			Taux de programmation (en %) <span
			class="field-complement">(B/A)</span>
			''',
			'TX-ENGAGE': '''
			Taux d'engagement (en %) <span
			class="field-complement">(C/B)</span>
			''',
			'TX-REA': '''
			Taux de réalisation (en %) <span
			class="field-complement">(D/C)</span>
			'''
		}

		# Mise en forme de la balise </thead>
		ths = []
		for ndx, element in enumerate(data[0]):
			if ndx not in undisplayed_ndxs:
				th = '<th>{}</th>'.format(lbls.get(element[0], element[0]))
				ths.append(th)
		thead = ''.join(ths)

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
		</tr>
		'''.format(
			sum([element[13] or 0 for element in data[1]]),
			sum([element[14] for element in data[1]]),
			sum([element[15] for element in data[1]]),
			sum([element[16] or 0 for element in data[1]]),
			sum([element[18] for element in data[1]]),
			sum([element[19] for element in data[1]]),
			sum([element[20] for element in data[1]]),
			sum([element[21] for element in data[1]]),
			sum([element[22] for element in data[1]]),
			round(mean([
				element[23] for element in data[1]
			]) if data[1] else 0, 3),
			round(mean([
				element[24] for element in data[1]
			]) if data[1] else 0, 3),
			round(mean([
				element[25] for element in data[1]
			]) if data[1] else 0, 3)
		) if data[1] else ''

		return '''
		<div class="my-table" id="t_EtatAvancementProgramme">
			<table>
				<thead>
					<tr>{}</tr>
				</thead>
				<tbody>{}</tbody>
				<tfoot id="za_tfoot_EtatAvancementProgramme">{}</tfoot>
			</table>
		</div>
		'''.format(thead, tbody, tfoot)

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
					ors.append(
						'("_moaId" = \'' \
						+ str(i[0]) \
						+ '\' AND "_typId" = \'' \
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