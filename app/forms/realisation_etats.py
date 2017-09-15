#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.constants import *
from app.functions import init_mess_err
from django import forms

class FiltrerDossiers(forms.ModelForm) :

	# Imports
	from app.models import TAvisCp
	from app.models import TFinanceur
	from app.models import TPrestataire
	from app.validators import val_mont_pos

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
	zs_mont_doss_min = forms.FloatField(
		label = '',
		required = False,
		validators = [val_mont_pos],
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : '0 par défaut' })
	)
	zs_mont_doss_max = forms.FloatField(
		label = '',
		required = False,
		validators = [val_mont_pos],
		widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro', 'placeholder' : 'infini par défaut' })
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

	class Meta :

		# Import
		from app.models import TDossier

		fields = [
			'id_av',
			'id_nat_doss',
			'id_progr',
			'id_sage',
			'id_techn',
			'id_type_doss',
		]
		model = TDossier

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

		# Imports
		from app.functions import init_f
		from app.models import TDossier
		from django.template.context_processors import csrf

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
					<button class="center-block green-btn my-btn" type="submit">Valider</button>
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
		from app.functions import obt_doss_regr
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
		from app.sql_views import VSuiviDossier
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
			val_doss_dep_nn_sold = cleaned_data.get('cb_doss_dep_nn_sold')
			val_doss_ddv_nn_sold = cleaned_data.get('cb_doss_ddv_nn_sold')
			val_org_fin = cleaned_data.get('zl_org_fin')
			val_org_prest = cleaned_data.get('zl_org_prest')
			val_integr_doss_ass = cleaned_data.get('cb_integr_doss_ass')
			val_ajout_select_exist = cleaned_data.get('cb_ajout_select_exist')
			val_gby = cleaned_data.get('zl_gby')

		# Initialisation du jeu de données des dossiers
		qs_doss = TDossier.objects.none()

		if val_org_moa :

			# Initialisation des conditions de la requête
			ands = {}

			# Préparation des conditions
			if val_progr : ands['id_progr'] = val_progr
			if val_axe : ands['num_axe'] = val_axe.split('_')[-1]
			if val_ss_axe : ands['num_ss_axe'] = val_ss_axe.split('_')[-1]
			if val_act : ands['num_act'] = val_act.split('_')[-1]
			if val_nat_doss : ands['id_nat_doss'] = val_nat_doss
			if val_type_doss : ands['id_type_doss'] = val_type_doss
			if val_techn : ands['id_techn'] = val_techn
			if val_av :
				ands['id_av__in'] = [val_av] + [a.pk for a in TAvancement.objects.filter(id_av_pere = val_av)]
			if val_dt_deb_delib_moa_doss : ands['dt_delib_moa_doss__gte'] = val_dt_deb_delib_moa_doss
			if val_dt_fin_delib_moa_doss : ands['dt_delib_moa_doss__lte'] = val_dt_fin_delib_moa_doss
			if val_av_cp : ands['id_av_cp'] = val_av_cp
			if val_dt_deb_av_cp_doss : ands['dt_av_cp_doss__gte'] = val_dt_deb_av_cp_doss
			if val_dt_fin_av_cp_doss : ands['dt_av_cp_doss__lte'] = val_dt_fin_av_cp_doss
			if val_mont_doss_min : ands['mont_doss__gte'] = val_mont_doss_min
			if val_mont_doss_max : ands['mont_doss__lte'] = val_mont_doss_max
			if val_org_fin : ands['tfinancement__id_org_fin'] = val_org_fin
			if val_org_prest : ands['tprestationsdossier__id_prest__id_org_prest'] = val_org_prest

			# Préparation du jeu de données des dossiers
			for m in val_org_moa : qs_doss |= obt_doss_regr(m).filter(**ands)

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

			for d in TDossier.objects.filter(pk__in = _req.session.get('filtr_doss')) :

				# Obtention d'une instance VSuiviDossier
				obj_sd = VSuiviDossier.objects.get(pk = d.pk)

				# Préparation des données de la colonne "Financement"
				fins = [obt_mont(obj_sd.mont_raf)]
				for f in TFinanceur.objects.all() :
					if TFinancement.objects.filter(id_doss = d, id_org_fin = f).count() > 0 :
						mont_part_fin = obt_mont(TFinancement.objects.get(id_doss = d, id_org_fin = f).mont_part_fin)
					else :
						mont_part_fin = 0
					fins.append(mont_part_fin)

				# Préparation des colonnes
				tds = [
					d,
					d.get_int_doss(),
					d.id_org_moa,
					d.id_progr,
					d.id_nat_doss,
					d.id_type_doss,
					obt_mont(d.mont_doss),
					obt_mont(d.mont_suppl_doss),
					obt_mont(obj_sd.mont_tot_doss),
					'TTC' if d.est_ttc_doss == True else 'HT',
					d.id_av_cp,
					dt_fr(d.dt_av_cp_doss) or '-',
					d.id_av,
					obt_mont(obj_sd.mont_tot_prest_doss),
					obt_mont(obj_sd.mont_fact_sum),
					*fins,
					'<a href="{0}" class="consult-icon pull-right" title="Consulter le dossier"></a>'.format(
						reverse('cons_doss', args = [d.pk])
					)
				]

				# Empilement des balises <tr/>
				trs.append('<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tds])))

			# Stockage des financeurs
			org_fins = ['<th>Autofinancement</th>'] + ['<th>{}</th>'.format(f) for f in TFinanceur.objects.all()]

			return '''
			<div class="my-table" id="t_select_doss">
				<table>
					<thead>
						<tr>
							<th rowspan="2">N° du dossier</th>
							<th rowspan="2">Intitulé du dossier</th>
							<th rowspan="2">Maître d'ouvrage</th>
							<th rowspan="2">Programme</th>
							<th rowspan="2">Nature du dossier</th>
							<th rowspan="2">Type de dossier</th>
							<th colspan="4">Montant du dossier</th>
							<th rowspan="2">Avis du comité de programmation - CD GEMAPI</th>
							<th rowspan="2">Date de l'avis du comité de programmation</th>
							<th rowspan="2">État d'avancement</th>
							<th rowspan="2">Montant commandé (en €)</th>
							<th rowspan="2">Montant payé (en €)</th>
							<th colspan="{}">Financement</th>
							<th rowspan="2"></th>
						</tr>
						<tr>
							<th>Présenté au CD GEMAPI (en €)</th>
							<th>Dépassement (en €)</th>
							<th>Total (en €)</th>
							<th>Mode de taxe</th>
							{}
						</tr>
					</thead>
					<tbody>{}</tbody>
				</table>
			</div>
			'''.format(len(org_fins), ''.join(org_fins), ''.join(trs))

		else :

			# Réinitialisation de la variable "historique"
			_req.session['filtr_doss'] = []

			# Initialisation des paramètres de regroupement
			params = {
				'AV_CP' : [TAvisCp.objects.all(), 'id_av_cp'],
				'NAT_DOSS' : [TNatureDossier.objects.all(), 'id_nat_doss'],
				'ORG_FIN' : [TFinanceur.objects.all(), 'tfinancement__id_org_fin'],
				'PROGR' : [TProgramme.objects.all(), 'id_progr'],
				'TYPE_DOSS' : [TTypeDossier.objects.all(), 'id_type_doss']
			}

			if val_gby in params : 

				# Initialisation des données de chaque balise <tr/>
				trs__untagged = []

				# Préparation des données de chaque balise <tr/>
				for elem in params[val_gby][0] :
					trs__untagged.append([str(elem), qs_doss.filter(**{ params[val_gby][1] : elem }).count()])

				# Ajout de la ligne "Autofinancement" et tri du tableau
				if val_gby == 'ORG_FIN' :
					trs__untagged.append([
						'Autofinancement',
						VSuiviDossier.objects.filter(pk__in = [d.pk for d in qs_doss], mont_raf__gt = 0).count()
					])
					trs__untagged = sorted(trs__untagged, key = lambda l : l[0])

				# Empilement des balises <tr/>
				for tr in trs__untagged :
					trs.append('<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tr])))

			else :
				if val_gby == 'ORG_MOA' :
					for m in TMoa.objects.filter(peu_doss = True, en_act_doss = True) :

						# Préparation des maîtres d'ouvrages père/fils
						ids = [rm.id_org_moa_anc.pk for rm in TRegroupementsMoa.objects.filter(id_org_moa_fil = m)] \
						+ [m.pk]

						# Empilement des balises <tr/>
						tds = [m, qs_doss.filter(id_org_moa__in = ids).count()]
						trs.append('<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tds])))

			output = '''
			<div class="my-table" id="t_regr_doss">
				<table>
					<thead>
						<tr>
							<th id="za_regr_doss_0">{}</th>
							<th>Nombre de dossiers</th>
						</tr>
					</thead>
					<tbody>{}</tbody>
				</table>
			</div>
			'''.format(dict(self.fields['zl_gby'].choices)[val_gby], ''.join(trs))

			# Empilement de la variable "historique"
			for lg in BeautifulSoup(output).find_all('tr') :
				_req.session['filtr_doss'].append([col.contents[0] for col in lg.find_all()])

			return output