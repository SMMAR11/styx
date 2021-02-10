#!/usr/bin/env python
#-*- coding: utf-8

from app.classes.FFEuroField import Class as FFEuroField
from app.constants import *
from app.functions import init_f
from app.functions import init_mess_err
from app.models import TAction
from app.models import TAvancement
from app.models import TAvisCp
from app.models import TAxe
from app.models import TFinanceur
from app.models import TPrestataire
from app.models import TDossier
from app.models import TSousAxe
from app.models import TMoa
from django.template.context_processors import csrf
from django import forms


class FiltrerDossiers(forms.ModelForm) :

	# Champs
	cbsm_org_moa = forms.MultipleChoiceField(
		label = 'Maître(s) d\'ouvrage(s)|Nom|__zcc__', required = False, widget = forms.SelectMultiple()
	)
	zl_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_ss_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Sous-axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_act = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Action',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zd_dt_deb_delib_moa_doss = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'Du' })
	)
	zd_dt_fin_delib_moa_doss = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'au' })
	)
	zl_av_cp = forms.ModelChoiceField(
		label = 'Avis du comité de programmation - CD GEMAPI', queryset = TAvisCp.objects.all(), required = False
	)
	zd_dt_deb_av_cp_doss = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'Du' })
	)
	zd_dt_fin_av_cp_doss = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'au' })
	)
	zs_mont_doss_min = FFEuroField(
		label = '',
		required = False,
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : '0 par défaut' })
	)
	zs_mont_doss_max = FFEuroField(
		label = '',
		required = False,
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : 'infini par défaut' })
	)
	zl_mode_taxe_doss = forms.ChoiceField(
		choices = [DEFAULT_OPTION, (0, 'HT'), (1, 'TTC')], label = 'Mode de taxe', required = False
	)
	cb_doss_dep_nn_sold = forms.BooleanField(
		label = 'Dossiers dont les dépenses sont non-soldées', required = False, widget = forms.CheckboxInput()
	)
	cb_doss_ddv_nn_sold = forms.BooleanField(
		label = 'Dossiers dont les demandes de versements sont non-soldées',
		required = False,
		widget = forms.CheckboxInput()
	)
	zl_org_fin = forms.ModelChoiceField(
		label = 'Organisme financier', queryset = TFinanceur.objects.all(), required = False
	)
	zl_org_prest = forms.ModelChoiceField(
		label = 'Prestataire', queryset = TPrestataire.objects.all(), required = False
	)
	cb_integr_doss_ass = forms.BooleanField(
		label = 'Intégration des dossiers associés dans le résultat',
		required = False,
		widget = forms.CheckboxInput()
	)
	cb_ajout_select_exist = forms.BooleanField(
		label = 'Ajouter à la sélection existante', required = False, widget = forms.CheckboxInput()
	)
	zl_gby = forms.ChoiceField(
		choices = [
			DEFAULT_OPTION,
			('AV_CP', 'Avis du comité de programmation - CD GEMAPI'),
			('ORG_FIN', 'Financeur'),
			('ORG_MOA', 'Maître d\'ouvrage'),
			('NAT_DOSS', 'Nature du dossier'),
			('PROGR', 'Programme'),
			('TYPE_DOSS', 'Type de dossier')
		],
		label = 'Regrouper les dossiers par'
	)

	id_av = forms.ModelMultipleChoiceField(
		label="État d'avancement",
		queryset=TAvancement.objects.all(),
		widget=forms.CheckboxSelectMultiple(attrs={'style':'vertical-align'})
	)

	class Meta :
		model = TDossier
		fields = [
			'id_nat_doss',
			'id_progr',
			'id_sage',
			'id_techn',
			'id_type_doss',
		]

	def __init__(self, *args, **kwargs):

		# Initialisation des arguments
		self.kw_gby = kwargs.pop('kw_gby')
		kw_progr = kwargs.pop('kw_progr', None)
		kw_axe = kwargs.pop('kw_axe', None)
		kw_ss_axe = kwargs.pop('kw_ss_axe', None)

		super(FiltrerDossiers, self).__init__(*args, **kwargs)
		# Passage des champs requis à l'état non-requis
		unrequired = ['id_av', 'id_nat_doss', 'id_progr', 'id_sage', 'id_techn', 'id_type_doss']
		if self.kw_gby == False : unrequired.append('zl_gby')
		for elem in unrequired : self.fields[elem].required = False

		init_mess_err(self)

		# Définition des choix de certaines listes déroulantes
		self.fields['cbsm_org_moa'].choices = [[m.pk, '|'.join([str(m), '__zcc__'])] for m in TMoa.objects.filter(
			peu_doss = True, en_act_doss = True
		)]

		# self.fields['id_av'].choices = [
		# 	[m.pk, '|'.join([str(m), '__zcc__'])] for m in TAvancement.objects.all(
		# )]

		if kw_progr :
			self.fields['zl_axe'].choices = [(a.pk, a) for a in TAxe.objects.filter(id_progr = kw_progr)]
			if kw_axe :
				self.fields['zl_ss_axe'].choices = [(sa.pk, sa) for sa in TSousAxe.objects.filter(id_axe = kw_axe)]
				if kw_ss_axe :
					self.fields['zl_act'].choices = [(a.pk, a) for a in TAction.objects.filter(id_ss_axe = kw_ss_axe)]

	def clean(self) :
		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(FiltrerDossiers, self).clean()
		v_dt_deb_delib_moa_doss = cleaned_data.get('zd_dt_deb_delib_moa_doss')
		v_dt_fin_delib_moa_doss = cleaned_data.get('zd_dt_fin_delib_moa_doss')
		v_dt_deb_av_cp_doss = cleaned_data.get('zd_dt_deb_av_cp_doss')
		v_dt_fin_av_cp_doss = cleaned_data.get('zd_dt_fin_av_cp_doss')

		# Je gère le renseignement de la période de délibération au maître d'ouvrage d'un dossier.
		if v_dt_deb_delib_moa_doss and not v_dt_fin_delib_moa_doss :
			self.add_error('zd_dt_fin_delib_moa_doss', ERROR_MESSAGES['required'])
		if v_dt_fin_delib_moa_doss and not v_dt_deb_delib_moa_doss :
			self.add_error('zd_dt_deb_delib_moa_doss', ERROR_MESSAGES['required'])

		# Gestion du renseignement de la période de l'avis du comité de programmation
		if v_dt_deb_av_cp_doss and not v_dt_fin_av_cp_doss :
			self.add_error('zd_dt_fin_av_cp_doss', ERROR_MESSAGES['required'])
		if v_dt_fin_av_cp_doss and not v_dt_deb_av_cp_doss :
			self.add_error('zd_dt_deb_av_cp_doss', ERROR_MESSAGES['required'])

	def get_form(self, _req) :

		form = init_f(self)

		return '''
		<form action="" method="post" name="f_filtr_doss" onsubmit="soum_f(event);">
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			<fieldset class="my-fieldset">
				<legend>Rechercher par</legend>
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
					Période de délibération au maître d'ouvrage
					<div class="row">
						<div class="col-xs-6">{}</div>
						<div class="col-xs-6">{}</div>
					</div>
					{}
					Période de l'avis du comité de programmation - CD GEMAPI
					<div class="row">
						<div class="col-xs-6">{}</div>
						<div class="col-xs-6">{}</div>
					</div>
					Montant du dossier présenté au CD GEMAPI compris entre
					<div class="row">
						<div class="col-xs-6">{}</div>
						<div class="col-xs-6">{}</div>
					</div>
					{}
					<div class="checkboxes-group">
						{}
						<!--{}-->
					</div>
					{}
					{}
					<div class="checkboxes-group">
						{}
						{}
					</div>
					{}
					<div class="buttons-group">
						<button class="green-btn my-btn" type="reset">Réinitialiser</button>
						<button class="green-btn my-btn" type="submit">Valider</button>
					</div>
				</div>
			</fieldset>
		</form>
		'''.format(
			csrf(_req)['csrf_token'],
			form['cbsm_org_moa'],
			form['id_progr'],
			form['zl_axe'],
			form['zl_ss_axe'],
			form['zl_act'],
			form['id_nat_doss'],
			form['id_type_doss'],
			form['id_techn'],
			form['id_sage'],
			form['id_av'],
			form['zd_dt_deb_delib_moa_doss'],
			form['zd_dt_fin_delib_moa_doss'],
			form['zl_av_cp'],
			form['zd_dt_deb_av_cp_doss'],
			form['zd_dt_fin_av_cp_doss'],
			form['zs_mont_doss_min'],
			form['zs_mont_doss_max'],
			form['zl_mode_taxe_doss'],
			form['cb_doss_dep_nn_sold'],
			form['cb_doss_ddv_nn_sold'],
			form['zl_org_fin'],
			form['zl_org_prest'],
			form['cb_integr_doss_ass'],
			form['cb_ajout_select_exist'] if self.kw_gby == False else '',
			form['zl_gby'] if self.kw_gby == True else ''
		)

	def get_datatable(self, _req, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont
		from app.models import TAvancement
		from app.models import TAvisCp
		from app.models import TDossier
		from app.models import TFinancement
		from app.models import TFinanceur
		from app.models import TMoa
		from app.models import TNatureDossier
		from app.models import TProgramme
		from app.models import TRegroupementsMoa
		from app.models import TTypeDossier
		from app.models import VDemandeVersement
		from app.models import VFinancement
		from app.models import VSuiviDossier
		from bs4 import BeautifulSoup
		from django.conf import settings
		from django.core.urlresolvers import reverse

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_org_moa = self.fields['cbsm_org_moa'].initial
			val_progr = self.fields['id_progr'].initial
			val_axe = self.fields['zl_axe'].initial
			val_ss_axe = self.fields['zl_ss_axe'].initial
			val_act = self.fields['zl_act'].initial
			val_nat_doss = self.fields['id_nat_doss'].initial
			val_type_doss = self.fields['id_type_doss'].initial
			val_techn = self.fields['id_techn'].initial
			val_sage = self.fields['id_sage'].initial
			val_av = self.fields['id_av'].initial
			val_dt_deb_delib_moa_doss = self.fields['zd_dt_deb_delib_moa_doss'].initial
			val_dt_fin_delib_moa_doss = self.fields['zd_dt_fin_delib_moa_doss'].initial
			val_av_cp = self.fields['zl_av_cp'].initial
			val_dt_deb_av_cp_doss = self.fields['zd_dt_deb_av_cp_doss'].initial
			val_dt_fin_av_cp_doss = self.fields['zd_dt_fin_av_cp_doss'].initial
			val_mont_doss_min = self.fields['zs_mont_doss_min'].initial
			val_mont_doss_max = self.fields['zs_mont_doss_max'].initial
			val_mode_taxe_doss = self.fields['zl_mode_taxe_doss'].initial
			val_doss_dep_nn_sold = self.fields['cb_doss_dep_nn_sold'].initial
			val_doss_ddv_nn_sold = self.fields['cb_doss_ddv_nn_sold'].initial
			val_org_fin = self.fields['zl_org_fin'].initial
			val_org_prest = self.fields['zl_org_prest'].initial
			val_integr_doss_ass = self.fields['cb_integr_doss_ass'].initial
			val_ajout_select_exist = self.fields['cb_ajout_select_exist'].initial
			val_gby = self.fields['zl_gby'].initial
		else :
			cleaned_data = self.cleaned_data
			val_org_moa = cleaned_data.get('cbsm_org_moa')
			val_progr = cleaned_data.get('id_progr')
			val_axe = cleaned_data.get('zl_axe')
			val_ss_axe = cleaned_data.get('zl_ss_axe')
			val_act = cleaned_data.get('zl_act')
			val_nat_doss = cleaned_data.get('id_nat_doss')
			val_type_doss = cleaned_data.get('id_type_doss')
			val_techn = cleaned_data.get('id_techn')
			val_sage = cleaned_data.get('id_sage')
			val_av = cleaned_data.get('id_av')
			val_dt_deb_delib_moa_doss = cleaned_data.get('zd_dt_deb_delib_moa_doss')
			val_dt_fin_delib_moa_doss = cleaned_data.get('zd_dt_fin_delib_moa_doss')
			val_av_cp = cleaned_data.get('zl_av_cp')
			val_dt_deb_av_cp_doss = cleaned_data.get('zd_dt_deb_av_cp_doss')
			val_dt_fin_av_cp_doss = cleaned_data.get('zd_dt_fin_av_cp_doss')
			val_mont_doss_min = cleaned_data.get('zs_mont_doss_min')
			val_mont_doss_max = cleaned_data.get('zs_mont_doss_max')
			val_mode_taxe_doss = cleaned_data.get('zl_mode_taxe_doss')
			val_doss_dep_nn_sold = cleaned_data.get('cb_doss_dep_nn_sold')
			val_doss_ddv_nn_sold = cleaned_data.get('cb_doss_ddv_nn_sold')
			val_org_fin = cleaned_data.get('zl_org_fin')
			val_org_prest = cleaned_data.get('zl_org_prest')
			val_integr_doss_ass = cleaned_data.get('cb_integr_doss_ass')
			val_ajout_select_exist = cleaned_data.get('cb_ajout_select_exist')
			val_gby = cleaned_data.get('zl_gby')

		# Initialisation des conditions de la requête
		ands = {}

		# Préparation des conditions
		if val_org_moa :
			ids = val_org_moa
			for m in val_org_moa :
				ids += [rm.id_org_moa_anc.pk for rm in TRegroupementsMoa.objects.filter(id_org_moa_fil = m)]
			ands['id_org_moa__in'] = ids
		if val_av :
			ands['id_av__in'] = val_av
		if val_progr : ands['id_progr'] = val_progr
		if val_axe : ands['num_axe'] = val_axe.split('_')[-1]
		if val_ss_axe : ands['num_ss_axe'] = val_ss_axe.split('_')[-1]
		if val_act : ands['num_act'] = val_act.split('_')[-1]
		if val_nat_doss : ands['id_nat_doss'] = val_nat_doss
		if val_type_doss : ands['id_type_doss'] = val_type_doss
		if val_techn : ands['id_techn'] = val_techn
		if val_dt_deb_delib_moa_doss : ands['dt_delib_moa_doss__gte'] = val_dt_deb_delib_moa_doss
		if val_dt_fin_delib_moa_doss : ands['dt_delib_moa_doss__lte'] = val_dt_fin_delib_moa_doss

		'''
		if val_av_cp : ands['id_av_cp'] = val_av_cp
		if val_dt_deb_av_cp_doss : ands['dt_av_cp_doss__gte'] = val_dt_deb_av_cp_doss
		if val_dt_fin_av_cp_doss : ands['dt_av_cp_doss__lte'] = val_dt_fin_av_cp_doss
		'''


		if val_mont_doss_min : ands['mont_doss__gte'] = val_mont_doss_min
		if val_mont_doss_max : ands['mont_doss__lte'] = val_mont_doss_max
		if val_mode_taxe_doss : ands['est_ttc_doss'] = { 0 : False, 1 : True }[int(val_mode_taxe_doss)]
		if val_org_fin : ands['tfinancement__id_org_fin'] = val_org_fin
		if val_org_prest : ands['tprestationsdossier__id_prest__id_org_prest'] = val_org_prest

		# Préparation du jeu de données des dossiers
		qs_doss = TDossier.objects.filter(**ands)

		# Ajout des dossiers associés
		if val_integr_doss_ass == True :
			qs_doss_temp = TDossier.objects.none()
			for d in qs_doss :
				qs_doss_temp |= TDossier.objects.filter(id_fam = d.id_fam)
				qs_doss |= qs_doss_temp
			del qs_doss_temp

		# Retrait des dossiers soldés
		if val_doss_dep_nn_sold == True :
			qs_doss = qs_doss.exclude(id_av__int_av = settings.T_DONN_BDD_STR['AV_SOLDE'])

		# Initialisation des balises <tr/>
		trs = []

		if self.kw_gby == False :

			# Réinitialisation de la variable "historique" si l'option "Ajouter à la sélection existante" n'est pas
			# cochée
			if not val_ajout_select_exist : _req.session['filtr_doss'] = []

			# Empilement de la variable "historique"
			_req.session['filtr_doss'] += [d.pk for d in qs_doss]

			# Suppression de variables
			del qs_doss

			# Initialisation du jeu de données des dossiers
			_qs_doss = TDossier.objects.filter(pk__in = _req.session.get('filtr_doss'))

			for d in _qs_doss :

				# Obtention d'une instance VSuiviDossier
				obj_sd = VSuiviDossier.objects.get(pk = d.pk)

				# Préparation des données de la colonne "Financement"
				fins = [obt_mont(VFinancement.objects.get(id_doss = d, id_org_fin = None).mont_part_fin)]
				for f in TFinanceur.objects.all() :
					fin = VFinancement.objects.filter(id_doss = d, id_org_fin = f).first()
					fins.append(obt_mont(fin.mont_part_fin if fin else 0))

					# Suppression de variables
					del f

				# Préparation des colonnes
				tds = [
					d,
					d.get_int_doss(),
					d.id_doss_ass or '-',
					d.id_org_moa,
					d.id_progr,
					d.get_axe_doss() or '-',
					d.id_nat_doss,
					d.id_type_doss,
					d.id_techn,
					d.id_sage or '-',
					obt_mont(d.mont_doss),
					obt_mont(d.mont_suppl_doss),
					obt_mont(obj_sd.mont_tot_doss),
					'TTC' if d.est_ttc_doss == True else 'HT',
					d.id_av,
					dt_fr(d.dt_delib_moa_doss) or '-',
					d.annee_prev_doss or '-',
					obj_sd.id_av_cp,
					dt_fr(obj_sd.dt_av_cp_doss) or '-',
					obt_mont(obj_sd.mont_tot_prest_doss),
					obt_mont(obj_sd.mont_fact_sum),
					d.get_view_object().tx_engag_doss,
					d.get_view_object().tx_real_doss,
					*fins,
					d.num_oper_budg_doss,
					d.comm_doss,
					'<a href="{0}" class="consult-icon pull-right" title="Consulter le dossier"></a>'.format(
						reverse('cons_doss', args = [d.pk])
					)
				]

				# Empilement des balises <tr/>
				trs.append('<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tds])))

				# Suppression de variables
				del d, fins, obj_sd, tds

			# Stockage des financeurs
			org_fins = ['<th>Autofinancement</th>'] + ['<th>{}</th>'.format(f) for f in TFinanceur.objects.all()]

			# Détermination de la balise <tfoot/>
			if _qs_doss.count() > 0 :

				# Initialisation du jeu de données des dossiers (vue)
				_qs_suivi_doss = VSuiviDossier.objects.filter(pk__in = [d.pk for d in _qs_doss])

				# Initialisation des données liées aux financements
				sums_fins = [[] for i in range(TFinanceur.objects.count() + 1)]

				for d in _qs_doss :

					# Obtention d'une instance VSuiviDossier
					obj_sd = VSuiviDossier.objects.get(pk = d.pk)

					# Préparation des données liées aux financements
					sums_fins[0].append(VFinancement.objects.get(id_doss = d, id_org_fin = None).mont_part_fin)
					for index, f in enumerate(TFinanceur.objects.all()) :
						fin = VFinancement.objects.filter(id_doss = d, id_org_fin = f).first()
						sums_fins[index + 1].append(fin.mont_part_fin if fin else 0)

						# Suppression de variables
						del f, index

					# Suppression de variables
					del d, obj_sd

				# Mise en forme des balises <td/>
				tds_fins = []
				for index, elem in enumerate(sums_fins) :
					td = '<td>{}</td>' if index + 1 != len(sums_fins) else '<td colspan="4">{}</td>'
					tds_fins.append(td.format(obt_mont(sum(elem))))

					# Suppression de variables
					del elem, index, td

				tfoot = '''
				<tr>
					<td colspan="10">Total</td>
					<td>{}</td>
					<td>{}</td>
					<td colspan="7">{}</td>
					<td>{}</td>
					<td colspan="3">{}</td>
					{}
				</tr>
				'''.format(
					obt_mont(sum([d.mont_doss for d in _qs_doss])),
					obt_mont(sum([d.mont_suppl_doss for d in _qs_doss])),
					obt_mont(sum([sd.mont_tot_doss for sd in _qs_suivi_doss])),
					obt_mont(sum([sd.mont_tot_prest_doss for sd in _qs_suivi_doss])),
					obt_mont(sum([sd.mont_fact_sum for sd in _qs_suivi_doss])),
					''.join(tds_fins)
				)

				# Suppression de variables
				del _qs_suivi_doss, sums_fins, tds_fins

			else :
				tfoot = ''

			# Suppression de variables
			del _qs_doss

			return {
				'table' : '''
				<div class="my-table" id="t_select_doss">
					<table>
						<thead>
							<tr>
								<th>N° du dossier</th>
								<th>Intitulé du dossier</th>
								<th>Dossier associé et/ou contrepartie</th>
								<th>Maître d'ouvrage</th>
								<th>Programme</th>
								<th>Axe</th>
								<th>Nature du dossier</th>
								<th>Type de dossier</th>
								<th>Agent responsable</th>
								<th>SAGE</th>
								<th>Montant du dossier présenté au CD GEMAPI (en €)</th>
								<th>Dépassement du dossier (en €)</th>
								<th>Montant total du dossier (en €)</th>
								<th>Type de montant du dossier</th>
								<th>État d'avancement</th>
								<th>Date de délibération au maître d'ouvrage</th>
								<th>Année prévisionnelle du dossier</th>
								<th>Avis du comité de programmation - CD GEMAPI</th>
								<th>Date de l'avis du comité de programmation</th>
								<th>Montant commandé (en €)</th>
								<th>Montant payé (en €)</th>
								<th>Taux d'engagement</th>
								<th>Taux de réalisation</th>
								{}
								<th>Numéro d'opération budgétaire</th>
								<th>Commentaire</th>
								<th></th>
							</tr>
						</thead>
						<tbody>{}</tbody>
						<tfoot id="za_tfoot_select_doss">{}</tfoot>
					</table>
				</div>
				'''.format(''.join(org_fins), ''.join(trs), tfoot),
				'len_numbers' : 0
			}

		else :

			# Réinitialisation de la variable "historique"
			_req.session['filtr_doss'] = []

			# Initialisation des lignes
			rows = []

			# Initialisation des paramètres globaux
			gparams = {
				'AV_CP' : {
					'numbers' : ['TOTAL', 'COMMANDE', 'FACTURE', 'DDV', 'VERSE'],
					'queryset' : [TAvisCp.objects.all(), 'id_av_cp']
				},
				'NAT_DOSS' : {
					'numbers' : ['TOTAL', 'COMMANDE', 'FACTURE', 'DDV', 'VERSE'],
					'queryset' : [TNatureDossier.objects.all(), 'id_nat_doss']
				},
				'ORG_FIN' : {
					'numbers' : ['TOTAL', 'PARTICIPATION', 'DDV', 'VERSE'],
					'queryset' : [TFinanceur.objects.all(), 'tfinancement__id_org_fin']
				},
				'ORG_MOA' : {
					'numbers' : ['TOTAL', 'COMMANDE', 'FACTURE', 'DDV', 'VERSE'],
					'queryset' : None
				},
				'PROGR' : {
					'numbers' : ['TOTAL', 'COMMANDE', 'FACTURE', 'DDV', 'VERSE'],
					'queryset' : [TProgramme.objects.all(), 'id_progr']
				},
				'TYPE_DOSS' : {
					'numbers' : ['TOTAL', 'COMMANDE', 'FACTURE', 'DDV', 'VERSE'],
					'queryset' : [TTypeDossier.objects.all(), 'id_type_doss']
				}
			}

			# Initialisation des balises <th/>
			ths = [
				dict(self.fields['zl_gby'].choices)[val_gby],
				'Nombre de dossiers',
				'Nombre de dossiers HT',
				'Nombre de dossiers TTC'
			]

			# Initialisation du nombre de colonnes de type "nombre"
			len_numbers = len(ths) - 1

			# Initialisation des lignes
			rows = []

			if val_gby in gparams.keys() :

				# Récupération des paramètres locaux
				lparams = gparams[val_gby]

				if lparams['queryset'] :

					# Étape n°1...
					for i in lparams['queryset'][0] :

						# Récupération des dossiers utiles
						ldoss = qs_doss.filter(**{ lparams['queryset'][1] : i }).values_list('pk', flat = True)

						# Empilement des lignes
						rows.append([ldoss, i.pk, str(i)])

					# Étape n°1 bis...
					if val_gby == 'ORG_FIN' :

						# Récupération des dossiers utiles
						ldoss = VSuiviDossier.objects.filter(
							pk__in = [d.pk for d in qs_doss], mont_raf__gt = 0
						).values_list('pk', flat = True)

						# Empilement des lignes (intégration de l'autofinancement) + tri par ordre alphabétique
						rows.append([ldoss, None, 'Autofinancement'])
						rows = sorted(rows, key = lambda l : l[2])

				else :

					# Étape n°1...
					if val_gby == 'ORG_MOA' :
						for moa in TMoa.objects.filter(peu_doss = True, en_act_doss = True) :

							# Récupération des maîtres d'ouvrages utiles
							lmoas = list(TRegroupementsMoa.objects.filter(id_org_moa_fil = moa).values_list(
								'id_org_moa_anc__pk', flat = True
							)) + [moa.pk]

							# Récupération des dossiers utiles
							ldoss = qs_doss.filter(id_org_moa__in = lmoas).values_list('pk', flat = True)

							# Empilement des lignes
							rows.append([ldoss, None, str(moa)])

				# Initialisation des paramètres montants
				thsparams = {
					'TOTAL' : 'Montant total (en €)',
					'PARTICIPATION' : 'Montant de participation (en €)',
					'COMMANDE' : 'Montant commandé (en €)',
					'FACTURE' : 'Montant facturé (en €)',
					'DDV' : 'Montant HT demandé (en €);Montant TTC demandé (en €)',
					'VERSE' : 'Montant HT versé (en €);Montant TTC versé (en €)'
				}

				# Empilement des balises </th>
				ths += [j for i in lparams['numbers'] for j in thsparams[i].split(';')]

				# Réinitialisation du nombre de colonnes de type "nombre"
				len_numbers += sum([len(thsparams[i].split(';')) for i in lparams['numbers']])

			for row in rows :

				# Stockage des identifiants de dossiers
				doss = row[0]

				# Empilement des colonnes de la ligne courante (nombre de dossiers)
				row.append(len(doss))

				nb_doss = { 'HT' : 0, 'TTC' : 0 }
				for dos in doss : nb_doss[VSuiviDossier.objects.get(pk = dos).type_mont_doss] += 1
				row.append(nb_doss['HT'])
				row.append(nb_doss['TTC'])

				for i in lparams['numbers'] :

					# Intégration des montants totaux
					if i == 'TOTAL' :

						# Calcul des montants totaux
						mnt = 0
						for sd in VSuiviDossier.objects.filter(pk__in = doss) :
							mnt += sd.mont_tot_doss

						# Empilement des colonnes de la ligne courante
						row.append(mnt)

					# Intégration des montants de participation
					if i == 'PARTICIPATION' :

						# Stockage de l'identifiant du financeur
						fin = row[1]

						# Calcul des montants de participation
						mnt = 0

						for f in VFinancement.objects.filter(id_doss__in = doss, id_org_fin = fin) :
							mnt += f.mont_part_fin

						# Empilement des colonnes de la ligne courante
						row.append(mnt)

					# Intégration des montants commandés
					if i == 'COMMANDE' :

						# Calcul des montants commandés
						mnt = 0
						for sd in VSuiviDossier.objects.filter(pk__in = doss) :
							mnt += sd.mont_tot_prest_doss

						# Empilement des colonnes de la ligne courante
						row.append(mnt)

					# Intégration des montants facturés
					if i == 'FACTURE' :

						# Calcul des montants facturés
						mnt = 0
						for sd in VSuiviDossier.objects.filter(pk__in = doss) :
							mnt += sd.mont_fact_sum

						# Empilement des colonnes de la ligne courante
						row.append(mnt)

					# Intégration des montants demandés
					if i == 'DDV' :

						# Calcul des montants demandés
						mnts = { 'HT' : 0, 'TTC' : 0 }
						for ddv in VDemandeVersement.objects.filter(id_doss__in = doss) :
							mnts['HT'] += ddv.get_instance().mont_ht_ddv or 0
							mnts['TTC'] += ddv.get_instance().mont_ttc_ddv or 0

						# Empilement des colonnes de la ligne courante
						row.append(mnts['HT'])
						row.append(mnts['TTC'])

					# Intégration des montants versés
					if i == 'VERSE' :

						# Calcul des montants versés
						mnts = { 'HT' : 0, 'TTC' : 0 }

						# Détermination du jeu de données
						if val_gby != 'ORG_FIN' :
							ddvs = VDemandeVersement.objects.filter(id_doss__in = doss)
						else :
							ddvs = VDemandeVersement.objects.filter(id_doss__in = doss, id_org_fin = fin)

						for ddv in ddvs :
							mnts['HT'] += ddv.get_instance().mont_ht_verse_ddv or 0
							mnts['TTC'] += ddv.get_instance().mont_ttc_verse_ddv or 0

						# Empilement des colonnes de la ligne courante
						row.append(mnts['HT'])
						row.append(mnts['TTC'])

				# Suppression des deux premières colonnes (devenues inutiles)
				for i in range(2) : del row[0]

			# Initialisation des colonnes de la balise <tfoot/>
			tfoot_cols = []
			for ndx, row in enumerate(rows) :
				if ndx == 0 : tfoot_cols = (len(row) - 1) * [0] # Réinitialisation des colonnes de la balise <tfoot/>
				for i in range(1, len(row)) : tfoot_cols[i - 1] += row[i]

			# Mise en forme de la balise <tfoot/>
			if tfoot_cols :
				tfoot = '<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(i) for i in (
					['Total'] + [obt_mont(j) if ndx > 2 else j for ndx, j in enumerate(tfoot_cols)]
				)]))
			else :
				tfoot = ''

			output = '''
			<div class="my-table" id="t_regr_doss">
				<table>
					<thead>
						<tr>{}</tr>
					</thead>
					<tbody>{}</tbody>
					<tfoot>{}</tfoot>
				</table>
			</div>
			'''.format(
				''.join(['<th>{}</th>'.format(th) for th in ths]),
				''.join(['<tr>{}</tr>'.format(''.join([
					'<td>{}</td>'.format(obt_mont(td) if ndx > 3 else td) for ndx, td in enumerate(tr)
				])) for tr in rows if tr[1] > 0]),
				tfoot
			)

			return { 'table' : output, 'len_numbers' : len_numbers }

class FiltrerPrestations(forms.Form) :

	# Imports
	from app.classes.FFEuroField import Class as FFEuroField
	from app.models import TDepartement
	from app.models import TNaturePrestation
	from app.models import TPrestataire
	from app.models import TProgramme

	# Champs
	zl_org_prest = forms.ModelChoiceField(
		label = 'Prestataire', queryset = TPrestataire.objects.all(), required = False
	)
	cbsm_org_moa = forms.MultipleChoiceField(
		label = 'Maître(s) d\'ouvrage(s)|Nom|__zcc__', required = False, widget = forms.SelectMultiple()
	)
	zl_progr = forms.ModelChoiceField(label = 'Programme', queryset = TProgramme.objects.all(), required = False)
	zl_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_ss_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Sous-axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_act = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Action',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zd_dt_deb_notif_prest = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'Du' })
	)
	zd_dt_fin_notif_prest = forms.DateField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'input-group-addon' : 'date', 'placeholder' : 'au' })
	)
	zl_nat_prest = forms.ModelChoiceField(
		label = 'Nature de la prestation', queryset = TNaturePrestation.objects.all(), required = False
	)
	zs_mont_prest_min = FFEuroField(
		label = '',
		required = False,
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : '0 par défaut' })
	)
	zs_mont_prest_max = FFEuroField(
		label = '',
		required = False,
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : 'infini par défaut' })
	)
	zl_mode_taxe_prest = forms.ChoiceField(
		choices = [DEFAULT_OPTION, (0, 'HT'), (1, 'TTC')], label = 'Mode de taxe', required = False
	)
	zl_dep = forms.ModelChoiceField(
		label = 'Département d\'origine du prestataire', queryset = TDepartement.objects.all(), required = False
	)
	cb_ajout_select_exist = forms.BooleanField(
		label = 'Ajouter à la sélection existante', required = False, widget = forms.CheckboxInput()
	)

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TAction
		from app.models import TAxe
		from app.models import TMoa
		from app.models import TSousAxe

		# Initialisation des arguments
		self.kw_gby = kwargs.pop('kw_gby')
		kw_progr = kwargs.pop('kw_progr', None)
		kw_axe = kwargs.pop('kw_axe', None)
		kw_ss_axe = kwargs.pop('kw_ss_axe', None)

		super(FiltrerPrestations, self).__init__(*args, **kwargs)

		init_mess_err(self)

		# Définition des choix de certaines listes déroulantes
		self.fields['cbsm_org_moa'].choices = [[m.pk, '|'.join([str(m), '__zcc__'])] for m in TMoa.objects.filter(
			peu_doss = True, en_act_doss = True
		)]
		if kw_progr :
			self.fields['zl_axe'].choices = [(a.pk, a) for a in TAxe.objects.filter(id_progr = kw_progr)]
			if kw_axe :
				self.fields['zl_ss_axe'].choices = [(sa.pk, sa) for sa in TSousAxe.objects.filter(id_axe = kw_axe)]
				if kw_ss_axe :
					self.fields['zl_act'].choices = [(a.pk, a) for a in TAction.objects.filter(id_ss_axe = kw_ss_axe)]

	def clean(self) :

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(FiltrerPrestations, self).clean()
		val_dt_deb_notif_prest = cleaned_data.get('zd_dt_deb_notif_prest')
		val_dt_fin_notif_prest = cleaned_data.get('zd_dt_fin_notif_prest')

		# Je gère le renseignement de la période de notification d'une prestation.
		if val_dt_deb_notif_prest and not val_dt_fin_notif_prest :
			self.add_error('zd_dt_fin_notif_prest', ERROR_MESSAGES['required'])
		if val_dt_fin_notif_prest and not val_dt_deb_notif_prest :
			self.add_error('zd_dt_deb_notif_prest', ERROR_MESSAGES['required'])

	def get_form(self, _req) :

		# Imports
		from app.functions import init_f
		from django.template.context_processors import csrf

		form = init_f(self)

		return '''
		<form action="" method="post" name="f_filtr_prest" onsubmit="soum_f(event);">
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			<fieldset class="my-fieldset">
				<legend>Rechercher par</legend>
				<div>
					{}
					{}
					{}
					{}
					{}
					{}
					Période de notification de la prestation
					<div class="row">
						<div class="col-xs-6">{}</div>
						<div class="col-xs-6">{}</div>
					</div>
					{}
					Montant de la prestation compris entre
					<div class="row">
						<div class="col-xs-6">{}</div>
						<div class="col-xs-6">{}</div>
					</div>
					{}
					{}
					<div class="checkboxes-group">{}</div>
					<div class="buttons-group">
						<button class="green-btn my-btn" type="reset">Réinitialiser</button>
						<button class="green-btn my-btn" type="submit">Valider</button>
					</div>
				</div>
			</fieldset>
		</form>
		'''.format(
			csrf(_req)['csrf_token'],
			form['zl_org_prest'],
			form['cbsm_org_moa'],
			form['zl_progr'],
			form['zl_axe'],
			form['zl_ss_axe'],
			form['zl_act'],
			form['zd_dt_deb_notif_prest'],
			form['zd_dt_fin_notif_prest'],
			form['zl_nat_prest'],
			form['zs_mont_prest_min'],
			form['zs_mont_prest_max'],
			form['zl_mode_taxe_prest'],
			form['zl_dep'],
			form['cb_ajout_select_exist'] if self.kw_gby == False else '',
		)

	def get_datatable(self, _req, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont
		from app.functions import obt_pourc
		from app.models import TPrestataire
		from app.models import TPrestationsDossier
		from app.models import TRegroupementsMoa
		from app.models import VSuiviPrestationsDossier
		from bs4 import BeautifulSoup
		from django.core.urlresolvers import reverse

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_org_prest = self.fields['zl_org_prest'].initial
			val_org_moa = self.fields['cbsm_org_moa'].initial
			val_progr = self.fields['zl_progr'].initial
			val_axe = self.fields['zl_axe'].initial
			val_ss_axe = self.fields['zl_ss_axe'].initial
			val_act = self.fields['zl_act'].initial
			val_dt_deb_notif_prest = self.fields['zd_dt_deb_notif_prest'].initial
			val_dt_fin_notif_prest = self.fields['zd_dt_fin_notif_prest'].initial
			val_nat_prest = self.fields['zl_nat_prest'].initial
			val_mont_prest_min = self.fields['zs_mont_prest_min'].initial
			val_mont_prest_max = self.fields['zs_mont_prest_max'].initial
			val_mode_taxe_prest = self.fields['zl_mode_taxe_prest'].initial
			val_dep = self.fields['zl_dep'].initial
			val_ajout_select_exist = self.fields['cb_ajout_select_exist'].initial
		else :
			cleaned_data = self.cleaned_data
			val_org_prest = cleaned_data.get('zl_org_prest')
			val_org_moa = cleaned_data.get('cbsm_org_moa')
			val_progr = cleaned_data.get('zl_progr')
			val_axe = cleaned_data.get('zl_axe')
			val_ss_axe = cleaned_data.get('zl_ss_axe')
			val_act = cleaned_data.get('zl_act')
			val_dt_deb_notif_prest = cleaned_data.get('zd_dt_deb_notif_prest')
			val_dt_fin_notif_prest = cleaned_data.get('zd_dt_fin_notif_prest')
			val_nat_prest = cleaned_data.get('zl_nat_prest')
			val_mont_prest_min = cleaned_data.get('zs_mont_prest_min')
			val_mont_prest_max = cleaned_data.get('zs_mont_prest_max')
			val_mode_taxe_prest = cleaned_data.get('zl_mode_taxe_prest')
			val_dep = cleaned_data.get('zl_dep')
			val_ajout_select_exist = cleaned_data.get('cb_ajout_select_exist')

		# Initialisation des conditions de la requête
		ands = {}

		# Préparation des conditions
		if val_org_prest : ands['id_prest__id_org_prest'] = val_org_prest
		if val_org_moa :
			ids = val_org_moa
			for m in val_org_moa :
				ids += [rm.id_org_moa_anc.pk for rm in TRegroupementsMoa.objects.filter(id_org_moa_fil = m)]
			ands['id_doss__id_org_moa__in'] = ids
		if val_progr : ands['id_doss__id_progr'] = val_progr
		if val_axe : ands['id_doss__num_axe'] = val_axe.split('_')[-1]
		if val_ss_axe : ands['id_doss__num_ss_axe'] = val_ss_axe.split('_')[-1]
		if val_act : ands['id_doss__num_act'] = val_act.split('_')[-1]
		if val_dt_deb_notif_prest : ands['id_prest__dt_notif_prest__gte'] = val_dt_deb_notif_prest
		if val_dt_fin_notif_prest : ands['id_prest__dt_notif_prest__lte'] = val_dt_fin_notif_prest
		if val_nat_prest : ands['id_prest__id_nat_prest'] = val_nat_prest
		if val_mont_prest_min : ands['mont_prest_doss__gte'] = val_mont_prest_min
		if val_mont_prest_max : ands['mont_prest_doss__lte'] = val_mont_prest_max
		if val_mode_taxe_prest : ands['id_doss__est_ttc_doss'] = { 0 : False, 1 : True }[int(val_mode_taxe_prest)]
		if val_dep : ands['id_prest__id_org_prest__num_dep'] = val_dep

		# Préparation du jeu de données des prestations
		qs_prest = TPrestationsDossier.objects.filter(**ands)

		# Suppression de variables
		del ands

		# Initialisation des balises <tr/>
		trs = []

		if self.kw_gby == False :

			# Réinitialisation de la variable "historique" si l'option "Ajouter à la sélection existante" n'est pas
			# cochée
			if not val_ajout_select_exist : _req.session['filtr_prest'] = []

			# Empilement de la variable "historique"
			_req.session['filtr_prest'] += [pd.pk for pd in qs_prest]

			# Initialisation du jeu de données des prestations
			_qs_prest = TPrestationsDossier.objects.filter(pk__in = _req.session.get('filtr_prest'))

			for pd in _qs_prest :

				# Obtention d'une instance VSuiviPrestationsDossier
				obj_spd = VSuiviPrestationsDossier.objects.get(pk = pd.pk)

				# Préparation des colonnes
				tds = [
					pd.id_doss,
					pd.id_doss.get_int_doss(),
					pd.id_prest.int_prest,
					pd.id_prest.ref_prest,
					pd.id_prest.id_nat_prest,
					pd.id_prest.id_org_prest,
					obt_mont(pd.mont_prest_doss),
					obj_spd.nb_aven,
					obt_mont(obj_spd.mont_aven_sum),
					obt_mont(obj_spd.mont_tot_prest_doss),
					obt_mont(obj_spd.mont_ht_fact_sum),
					obt_mont(obj_spd.mont_ttc_fact_sum),
					obt_mont(obj_spd.mont_raf),
					'TTC' if pd.id_doss.est_ttc_doss == True else 'HT',
					dt_fr(pd.id_prest.dt_notif_prest) or '-',
					dt_fr(pd.id_prest.dt_fin_prest) or '-',
					'<a href="{}" class="consult-icon pull-right" title="Consulter la prestation"></a>'.format(
						reverse('cons_prest', args = [pd.pk])
					)
				]

				# Empilement des balises <tr/>
				trs.append('<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tds])))

				# Suppression de variables
				del obj_spd, pd, tds

			# Détermination de la balise <tfoot/>
			if _qs_prest.count() > 0 :

				# Initialisation du jeu de données des prestations (vue)
				_qs_spd = VSuiviPrestationsDossier.objects.filter(pk__in = [pd.pk for pd in _qs_prest])

				tfoot = '''
				<tr>
					<td colspan="6">Total</td>
					<td>{}</td>
					<td>{}</td>
					<td>{}</td>
					<td>{}</td>
					<td>{}</td>
					<td>{}</td>
					<td colspan="5">{}</td>
				</tr>
				'''.format(
					obt_mont(sum([pd.mont_prest_doss for pd in _qs_prest])),
					sum([spd.nb_aven for spd in _qs_spd]),
					obt_mont(sum([spd.mont_aven_sum for spd in _qs_spd])),
					obt_mont(sum([spd.mont_tot_prest_doss for spd in _qs_spd])),
					obt_mont(sum([spd.mont_ht_fact_sum for spd in _qs_spd])),
					obt_mont(sum([spd.mont_ttc_fact_sum for spd in _qs_spd])),
					obt_mont(sum([spd.mont_raf for spd in _qs_spd]))
				)

				# Suppression de variables
				del _qs_spd

			else :
				tfoot = ''

			# Suppression de variables
			del qs_prest

			return '''
			<div class="my-table" id="t_select_prest">
				<table>
					<thead>
						<tr>
							<th>N° du dossier</th>
							<th>Intitulé du dossier</th>
							<th>Intitulé de la prestation</th>
							<th>Référence de la prestation</th>
							<th>Nature de la prestation</th>
							<th>Prestataire</th>
							<th>Montant de la prestation (en €)</th>
							<th>Nombre d'avenants</th>
							<th>Somme des avenants (en €)</th>
							<th>Montant total de la prestation (en €)</th>
							<th>Somme HT des factures émises (en €)</th>
							<th>Somme TTC des factures émises (en €)</th>
							<th>Reste à facturer (en €)</th>
							<th>Mode de taxe</th>
							<th>Date de notification de la prestation</th>
							<th>Date de fin de la prestation</th>
							<th></th>
						</tr>
					</thead>
					<tbody>{}</tbody>
					<tfoot id="za_tfoot_select_prest">{}</tfoot>
				</table>
			</div>
			'''.format(''.join(trs), tfoot)

		else :

			# Réinitialisation de la variable "historique"
			_req.session['filtr_prest'] = []

			_sum = 0

			# Initialisation des lignes du fichier CSV
			lgs_csv = []

			for p in TPrestataire.objects.all() :

				# Initialisation du jeu de données des prestations pour le prestataire courant
				qs_pop = qs_prest.filter(id_prest__id_org_prest = p)

				# Initialisation des jeux de données des prestations en cours et clôturées pour le prestataire courant
				qs_pop_ec = VSuiviPrestationsDossier.objects.filter(
					pk__in = [pop.pk for pop in qs_pop], mont_raf__gt = 0
				)
				qs_pop_clot = VSuiviPrestationsDossier.objects.filter(
					pk__in = [pop.pk for pop in qs_pop], mont_raf__lte = 0
				)

				# Calcul du montant total des prestations pour le prestataire courant (utile au calcul de l'indice de
				# contractualisation)
				mont_pdop__sum = sum([pop.mont_prest_doss for pop in qs_pop])

				# Calcul du montant total des prestations (utile au calcul de l'indice de contractualisation)
				mont_prest_doss__sum = sum([pd.mont_prest_doss for pd in qs_prest])

				# Calcul du pourcentage de contractualisation pour le prestataire courant
				pourc_contr = (mont_pdop__sum / mont_prest_doss__sum) * 100 if mont_prest_doss__sum > 0 else 0

				# Préparation des colonnes
				_tds = [
					str(p),
					qs_pop.count(),
					mont_pdop__sum,
					qs_pop_ec.count(),
					sum([pop.mont_prest_doss for pop in qs_pop_ec]),
					qs_pop_clot.count(),
					sum([pop.mont_prest_doss for pop in qs_pop_clot]),
					pourc_contr
				]
				tds = [
					_tds[0],
					_tds[1],
					obt_mont(_tds[2]),
					_tds[3],
					obt_mont(_tds[4]),
					_tds[5],
					obt_mont(_tds[6]),
					obt_pourc(_tds[7])
				]

				# Empilement des lignes du fichier CSV et des balises <tr/>
				if _tds[1] > 0 :
					lgs_csv.append(_tds)
					trs.append('<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tds])))

				# Calcul du total lié aux pourcentages de contractualisation (100 normalement)
				_sum += pourc_contr

				# Suppression de variables
				del mont_pdop__sum, mont_prest_doss__sum, p, pourc_contr, qs_pop, qs_pop_clot, qs_pop_ec, _tds, tds

			# Détermination de la balise <tfoot/>
			if len(trs) > 0 :

				# Initialisation des jeux de données des prestations en cours et clôturées
				qs_prest_ec = VSuiviPrestationsDossier.objects.filter(
					pk__in = [pd.pk for pd in qs_prest], mont_raf__gt = 0
				)
				qs_prest_clot = VSuiviPrestationsDossier.objects.filter(
					pk__in = [pd.pk for pd in qs_prest], mont_raf__lte = 0
				)

				tfoot = '''
				<tr>
					<td>Total</td>
					<td>{}</td>
					<td>{}</td>
					<td>{}</td>
					<td>{}</td>
					<td>{}</td>
					<td>{}</td>
					<td>{}</td>
				</tr>
				'''.format(
					qs_prest.count(),
					obt_mont(sum([pd.mont_prest_doss for pd in qs_prest])),
					qs_prest_ec.count(),
					obt_mont(sum([pd.mont_prest_doss for pd in qs_prest_ec])),
					qs_prest_clot.count(),
					obt_mont(sum([pd.mont_prest_doss for pd in qs_prest_clot])),
					obt_pourc(_sum)
				)

				# Suppression de variables
				del qs_prest_clot, qs_prest_ec

			else :
				tfoot = ''

			# Suppression de variables
			del qs_prest, _sum

			output = '''
			<div class="my-table" id="t_regr_prest">
				<table>
					<thead>
						<tr>
							<th>Prestataire</th>
							<th>Nombre de prestations</th>
							<th>Montant cumulé des prestations (en €)</th>
							<th>Nombre de prestations en cours</th>
							<th>Montant cumulé des prestations en cours (en €)</th>
							<th>Nombre de prestations clôturées</th>
							<th>Montant cumulé des prestations clôturées (en €)</th>
							<th>Indice de contractualisation (% du montant global des prestations)</th>
						</tr>
					</thead>
					<tbody>{}</tbody>
					<tfoot id="za_tfoot_regr_prest">{}</tfoot>
				</table>
			</div>
			'''.format(''.join(trs), tfoot)

			return output

class AvancementProgramme(forms.Form) :

	# Champs
	zl_progr = forms.ChoiceField(choices = [DEFAULT_OPTION], label = 'Programme', required = False)
	cbsm_org_moa = forms.MultipleChoiceField(
		label = 'Maître(s) d\'ouvrage(s)|Nom|__zcc__', required = False, widget = forms.SelectMultiple()
	)
	zl_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_ss_axe = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Sous-axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)
	zl_act = forms.ChoiceField(
		choices = [DEFAULT_OPTION],
		label = 'Action',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'hide-field' })
	)

	# Méthodes système

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TProgramme

		# Initialisation des arguments
		kw_prg = kwargs.pop('kw_prg', None)
		kw_axe = kwargs.pop('kw_axe', None)
		kw_ssa = kwargs.pop('kw_ssa', None)

		super().__init__(*args, **kwargs)

		init_mess_err(self)

		# Définition des programmes valides
		self.fields['zl_progr'].choices += [(prg.pk, prg) for prg in TProgramme.objects.filter(
			pk__in = [i[0] for i in self.__execute_sql(code = 'prg')[1]]
		)]
		
		# Définition des maîtres d'ouvrages valides
		self.fields['cbsm_org_moa'].choices = [
			[moa.pk, '|'.join([str(moa), '__zcc__'])] for moa in TMoa.objects.filter(
				pk__in =  [i[0] for i in self.__execute_sql(code = 'moa')[1]]
			)
		]

		# Définition des axes, sous-axes et actions valides
		if kw_prg :
			self.fields['zl_axe'].choices = [(axe.pk, axe) for axe in TAxe.objects.filter(id_progr = kw_prg)]
			if kw_axe :
				self.fields['zl_ss_axe'].choices = [(ssa.pk, ssa) for ssa in TSousAxe.objects.filter(id_axe = kw_axe)]
				if kw_ssa :
					self.fields['zl_act'].choices = [
						(act.pk, act) for act in TAction.objects.filter(id_ss_axe = kw_ssa)
					]

	# Méthodes privées

	def __execute_sql(self, code = None) :

		'''Exécution de la requête SQL'''

		# Imports
		from django.db import connection

		# Renvoi du couple entêtes/lignes sous forme de tableau ou d'un tableau vierge
		with connection.cursor() as c :
			try :
				c.execute(self.__get_sql(code = code))
				return [c.description, c.fetchall()]
			except :
				return []

	def __get_act(self) :
		'''Action'''
		return '.'.join(self.cleaned_data.get('zl_act').split('_')[1:]) if self.data else None

	def __get_axe(self) :
		'''Axe'''
		return '.'.join(self.cleaned_data.get('zl_axe').split('_')[1:]) if self.data else None

	def __get_moa(self) :
		'''Maître d'ouvrage'''
		return self.cleaned_data.get('cbsm_org_moa') if self.data else None

	def __get_prg(self) :
		'''Programme'''
		return self.cleaned_data.get('zl_progr') if self.data else None

	def __get_ssa(self) :
		'''Sous-axe'''
		return '.'.join(self.cleaned_data.get('zl_ss_axe').split('_')[1:]) if self.data else None

	def __get_sql(self, code) :

		'''Obtention de la requête SQL'''

		# Si code requête programme, alors...
		if code == 'prg' :
			sql = 'SELECT DISTINCT "Programme - ID" FROM "hors_public"."v_suivi_prg";'
		# Si code requête maître d'ouvrage, alors...
		elif code == 'moa' :
			sql = '''
			SELECT DISTINCT UNNEST(STRING_TO_ARRAY("Programme - Maître d'ouvrage - ID", ';'))
			FROM "hors_public"."v_suivi_prg";
			'''
		# Sinon...
		else :

			# Définition de la requête non-filtrée
			sql = 'SELECT * FROM "hors_public"."v_suivi_prg"'

			# Initialisation des filtres
			filters = []

			# Récupération des valeurs du formulaire
			prg = self.__get_prg()
			moa = self.__get_moa()
			axe = self.__get_axe()
			ssa = self.__get_ssa()
			act = self.__get_act()

			# Définition des filtres
			if prg :
				filters.append('"Programme - ID" = ' + str(prg))
			if moa :
				moa_filters = [
					str(i) \
					+ ' = ANY(STRING_TO_ARRAY("Programme - Maître d\'ouvrage - ID", \';\')::INTEGER[])' for i in moa
				] # Définition des filtres dédiés au champ des maîtres d'ouvrages
				filters.append('(' + ' OR '.join(moa_filters) + ')')
			if axe :
				filters.append('"Programme - Axe - Numéro" = \'' + str(axe) + '\'')
			if ssa :
				filters.append('"Programme - Sous-axe - Numéro" = \'' + str(ssa) + '\'')
			if act :
				filters.append('"Programme - Action - Numéro" = \'' + str(act) + '\'')

			# Intégration des filtres à la requête
			if filters :
				sql += ' WHERE ' + ' AND '.join(filters)

			# Intégration du point-virgule final
			sql += ';'

		return sql

	# Méthodes publiques

	def get_form(self, rq) :

		'''Obtention du formulaire'''

		# Initialisation des contrôles du formulaire
		form = init_f(self)

		return '''
		<form action="" method="post" name="f_avanc_prg" onsubmit="soum_f(event);">
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			<fieldset class="my-fieldset">
				<legend>Rechercher par</legend>
				<div>
					{}
					{}
					{}
					{}
					{}
					<div class="buttons-group">
						<button class="green-btn my-btn" type="reset">Réinitialiser</button>
						<button class="green-btn my-btn" type="submit">Valider</button>
					</div>
				</div>
			</fieldset>
		</form>
		'''.format(
			csrf(rq)['csrf_token'],
			form['zl_progr'],
			form['cbsm_org_moa'],
			form['zl_axe'],
			form['zl_ss_axe'],
			form['zl_act']
		)

	def get_datatable(self, *args, **kwargs) :

		'''Obtention d'une table de données'''

		# Exécution de la requête SQL
		sql = self.__execute_sql()

		return '''
		<div class="my-table" id="t_avanc_prg">
			<table>
				<thead>
					<tr>{}</tr>
				</thead>
				<tbody>{}</tbody>
			</table>
		</div>
		'''.format(
			''.join(['<th>{}</th>'.format(i[0]) for i in sql[0]]),
			''.join(['<tr>{}</tr>'.format(
				''.join('<td>{}</td>'.format(col if col is not None else '') for col in row)
			) for row in sql[1]])
		)