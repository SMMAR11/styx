# coding: utf-8

class FormSet:

	"""
	Classe exploitant un formulaire groupé
	"""

	# Constructeur

	def __init__(
		self,
		columns,
		form,
		formset,
		label,
		name,
		rq,
		form_kwargs={},
		formset_kwargs={}
	):

		# Imports
		from django.forms import formset_factory

		self.columns = columns
		self.label = label

		if formset_kwargs.get('prefix'):
			self.name = '{}-{}'.format(formset_kwargs['prefix'], name)
		else :
			self.name = name

		FS = formset_factory(form, extra=0, formset=formset)
		if rq.method == 'GET':
			self.formset = FS(form_kwargs=form_kwargs, **formset_kwargs)
		else:
			self.formset \
				= FS(rq.POST, form_kwargs=form_kwargs, **formset_kwargs)

	# Méthodes privées

	def __display_formset(self):
		"""
		Affichage du formulaire groupé
		"""
		return [self.__get_formset(), self.__get_empty_form()]

	def __get_empty_form(self):
		"""
		Mise en forme du formulaire vierge
		"""
		return '''
		<div id="fw_{name}_empty_form" style="display: none;">
			<table>
				<tbody>{tr}</tbody>
			</table>
		</div>
		'''.format(
			name=self.name, tr=self.__get_tr(form=self.formset.empty_form)
		)

	def __get_errors(self):

		"""
		Récupération des erreurs de formulaire
		"""

		# Initialisation des erreurs
		errors = {}

		# Si le formulaire groupé est invalide, alors...
		if not self.formset.is_valid():
			# Pour chaque formulaire...
			for form in self.formset:
				# Empilement des erreurs
				for k, v in form.errors.items():
					errors[form.prefix + '-' + k] = v

		return errors

	def __get_formset(self):

		"""
		Mise en forme du formulaire groupé
		"""

		# -------------------------------------------------------------
		# Méthodes locales
		# -------------------------------------------------------------

		def get_tbody(self):
			"""
			Mise en forme du contenu de la balise HTML <tbody/>
			"""
			return ''.join(
				[self.__get_tr(form=form) for form in self.formset]
			)

		def get_thead(self):

			"""
			Mise en forme du contenu de la balise HTML <thead/>
			"""

			# Imports
			from bs4 import BeautifulSoup

			# Initialisation des balises HTML <th/>
			ths = []

			# Récupération des gabarits HTML du formulaire vierge
			tpls = self.__get_templates(form=self.formset.empty_form)

			# Pour chaque gabarit HTML...
			for tpl in tpls:

				# Récupération du gabarit HTML sous forme d'un objet
				# BeautifulSoup
				bs = BeautifulSoup(tpl, 'html.parser')

				# Récupération du label
				label = ''.join([str(i) for i in bs.find(
					'span', {'class': 'field-label'}
				).contents])

				# Empilement des balises HTML <th/>
				th = '<th>' + label + '</th>'
				ths.append(th)

			# Empilement des balises HTML <th/> (bouton d'ajout d'un
			# nouveau formulaire au sein du formulaire groupé)
			ths.append(
				'''
				<th>
					<span
						class="fa fa-plus-circle"
						onclick="new FormSet(event).add_form();"
						style="cursor: pointer;"
						title="Ajouter"
					></span>
				</th>
				'''
			)

			return '<tr>{}</tr>'.format(''.join(ths))

		# -------------------------------------------------------------

		return '''
		<div class="field-wrapper" id="fw_{name}">
			{management_form}
			<span class="field-label">{label}</span>
			<div class="my-table" id="t_{name}">
				<table>
					<thead>{thead}</thead>
					<tbody>{tbody}</tbody>
				</table>
			</div>
			<span class="field-error"></span>
		</div>
		'''.format(
			label=self.label,
			management_form= self.formset.management_form,
			name=self.name,
			tbody=get_tbody(self=self),
			thead=get_thead(self=self)
		)

	def __get_templates(self, form):

		"""
		Récupération des gabarits HTML d'un formulaire spécifié
		"""

		# Imports
		from app.functions import init_f


		# Initialisation des gabarits HTML
		tpls = []

		# Récupération des gabarits HTML du formulaire spécifié
		formTpls = init_f(form)

		# Stockage des clés
		formTpls_keys = formTpls.keys()

		# Pour chaque colonne...
		for i in self.columns:
			# Pour chaque clé...
			for j in formTpls_keys:
				# Si correspondance colonne/clé, alors...
				if j.endswith(i):
					# Empilement des gabarits HTML
					tpl = formTpls[j]
					tpls.append(tpl)

		return tpls

	def __get_tr(self, form):

		"""
		Mise en forme d'une balise HTML <tr/>
		"""

		# Imports
		from bs4 import BeautifulSoup

		# Initialisation des balises HTML <td/>
		tds = []

		# Récupération des gabarits HTML du formulaire spécifié
		tpls = self.__get_templates(form=form)

		# Pour chaque gabarit HTML...
		for tpl in tpls:

			# Récupération du gabarit HTML sous forme d'un objet
			# BeautifulSoup
			bs = BeautifulSoup(tpl, 'html.parser')

			# Suppression du label
			label = bs.find('span', {'class': 'field-label'})
			label.replaceWith('')

			# Empilement des balises HTML <td/>
			td = str(bs)
			tds.append(td)

		# Empilement des balises HTML <td/> (suppression d'un
		# formulaire du formulaire groupé)
		tds.append(
			'''
			<span
				class="delete-icon pointer pull-right"
				onclick="new FormSet(event).remove_form();"
				title="Supprimer"
			></span>
			'''.format()
		)

		return '<tr>{}</tr>'.format(
			''.join(['<td>{}</td>'.format(td) for td in tds])
		)

	def __save(self, **kwargs):
		"""
		Enregistrement du formulaire groupé
		"""
		return self.formset.save(**kwargs)

	# Méthodes publiques

	def display_formset(self):
		"""
		Affichage du formulaire groupé
		"""
		return self.__display_formset()

	def get_errors(self):
		"""
		Récupération des erreurs de formulaire
		"""
		return self.__get_errors()

	def save(self, **kwargs):
		"""
		Enregistrement du formulaire groupé
		"""
		return self.__save(**kwargs)