# coding: utf-8

# Imports
from django.views.generic import View

class EtatPpi(View):

	# Imports
	from app.forms.real_etats.EtatPpi import EtatPpi as fEtatPpi

	# Options Django
	form_class = fEtatPpi
	template_name = './real_etats/template.html'

	# Méthodes Django

	def get(self, rq, *args, **kwargs):

		# Imports
		from django.shortcuts import render

		# Initialisation du formulaire
		form = self.form_class(kwarg_rq=rq, prefix='EtatPpi')

		return render(rq, self.template_name, {
			'datatable': form.get_datatable(),
			'form': form.get_form(),
			'title': 'Bilan d\'un Plan Pluriannuel d\'Investissement (PPI)'
		})

	def post(self, rq, *args, **kwargs):

		# Imports
		from app.functions import alim_ld
		from app.functions import datatable_reset
		from django.http import HttpResponse
		from bs4 import BeautifulSoup
		import json

		# Récupération du paramètre GET "action"
		action = rq.GET.get('action')

		if action:

			# Gestion d'affichage des champs "Axe", "Sous-axe" et
			# "Action"
			if action == 'alimenter-listes':
				return HttpResponse(
					json.dumps(alim_ld(rq)),
					content_type='application/json'
				)

		else:

			# Soumission du formulaire
			form = self.form_class(
				rq.POST,
				kwarg_rq=rq,
				kwarg_pro=rq.POST.get('EtatPpi-zl_id_progr'),
				kwarg_axe=rq.POST.get('EtatPpi-zl_axe'),
				kwarg_ssa=rq.POST.get('EtatPpi-zl_ss_axe'),
				prefix='EtatPpi'
			)

			# Si le formulaire est valide, alors rafraîchissement de la
			# datatable
			if form.is_valid():
				datatable = form.get_datatable()
				bs = BeautifulSoup(datatable)
				return datatable_reset(datatable, {
					'elements': [
						['#za_tfoot_EtatPpi', str(bs.find(
							'tfoot', id='za_tfoot_EtatPpi'
						))]
					]
				})

			# Sinon, affichage des erreurs
			else:
				return HttpResponse(json.dumps({
					'EtatPpi-' + key: val \
					for key, val in form.errors.items()
				}), content_type = 'application/json')

		return None