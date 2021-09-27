#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.constants import *
from app.functions import init_mess_err
from django import forms
from django.forms import BaseFormSet

class GererDossier(forms.ModelForm) :

	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	rb_doss_ass = forms.ChoiceField(
		choices = [(True, 'Oui'), (False, 'Non')],
		initial = False,
		label = 'Ce dossier est-il lié à un autre dossier ?',
		required = False,
		widget = forms.RadioSelect()
	)
	za_doss_ass = forms.CharField(
		label = 'Dossier associé et/ou contrepartie',
		required = False,
		widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	zl_progr = forms.ChoiceField(label = 'Programme', widget = forms.Select())
	zl_org_moa = forms.ChoiceField(label = 'Maître d\'ouvrage', widget = forms.Select())
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
	zl_nat_doss = forms.ChoiceField(label = 'Nature du dossier', widget = forms.Select())
	zl_type_doss = forms.ChoiceField(choices = [DEFAULT_OPTION], label = 'Type de dossier', widget = forms.Select())
	zl_techn = forms.ChoiceField(label = 'Agent responsable', widget = forms.Select())
	rb_est_ttc_doss = forms.ChoiceField(
		choices = [(True, 'Oui'), (False, 'Non')],
		initial = False,
		label = 'Le montant est-il en TTC ?',
		required = False,
		widget = forms.RadioSelect()
	)
	est_autofin_doss = forms.ChoiceField(
		choices=[(True, 'Oui'), (False, 'Non')],
		initial=False,
		label='Le dossier est-il en autofinancement ?',
		required=False,
		widget=forms.RadioSelect()
	)
	est_pec_ds_bilan_doss = forms.ChoiceField(
		choices=[(True, 'Oui'), (False, 'Non')],
		initial=False,
        label='''
        Le dossier doit-il être pris en compte dans les bilans de
        programmation ? <span class="field-complement">(si et seulement
        si non-accordé en comité de programmation - CD GEMAPI)</span>
        ''',
		required=False,
		widget=forms.RadioSelect()
    )

	class Meta :

		# Imports
		from app.models import TDossier

		exclude = [
			'comm_regl_doss',
			'dt_int_doss',
			'est_ttc_doss',
			'id_fam',
			'id_nat_doss',
			'id_org_moa',
			'id_progr',
			'id_techn',
			'id_type_doss',
			'num_doss',
			'type_decl'
		]
		fields = '__all__'
		model = TDossier
		widgets = {
			'dt_delib_moa_doss' : forms.DateInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_depot_doss' : forms.DateInput(attrs = { 'input-group-addon' : 'date' }),
			'mont_doss' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' }),
			'mont_suppl_doss' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' })
		}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TAction
		from app.models import TAxe
		from app.models import TFinancement
		from app.models import TMoa
		from app.models import TNatureDossier
		from app.models import TPrestationsDossier
		from app.models import TProgramme
		from app.models import TSousAxe
		from app.models import TTechnicien
		from app.models import VSuiviDossier
		from styx.settings import T_DONN_BDD_STR

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		self.k_util = kwargs.pop('k_util', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'mont_doss' : '{:0.2f}'.format(instance.mont_doss),
				'mont_suppl_doss' : '{:0.2f}'.format(instance.mont_suppl_doss)
			})

		super(GererDossier, self).__init__(*args, **kwargs)
		init_mess_err(self)
		self.fields['zl_axe'].label += REQUIRED
		self.fields['zl_ss_axe'].label += REQUIRED
		self.fields['zl_act'].label += REQUIRED
		self.fields['dt_delib_moa_doss'].label += MAY_BE_REQUIRED

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		t_org_moa = [(m.pk, m) for m in TMoa.objects.filter(peu_doss = True, en_act_doss = True)]
		t_org_moa.insert(0, DEFAULT_OPTION)
		self.fields['zl_org_moa'].choices = t_org_moa

		# J'alimente la liste déroulante des programmes.
		t_progr = [(p.pk, p) for p in TProgramme.objects.filter(en_act = True)]
		t_progr.insert(0, DEFAULT_OPTION)
		self.fields['zl_progr'].choices = t_progr

		# J'alimente la liste déroulante des natures de dossiers.
		t_nat_doss = [(nd.pk, nd) for nd in TNatureDossier.objects.filter(peu_doss = True)]
		t_nat_doss.insert(0, DEFAULT_OPTION)
		self.fields['zl_nat_doss'].choices = t_nat_doss

		# J'alimente la liste déroulante des techniciens.
		t_techn = [(t.pk, t) for t in TTechnicien.objects.filter(en_act = True)]
		t_techn.insert(0, DEFAULT_OPTION)
		self.fields['zl_techn'].choices = t_techn

		i = self.instance

		# Intégration du type de taxe du dossier dans les divers champs
		# montant
		if (
			i.pk
		) and (
			TFinancement.objects.filter(id_doss=i.pk).exists() or \
			TPrestationsDossier.objects.filter(id_doss=i.pk).exists()
		):
			ht_ttc = ' ' + VSuiviDossier.objects.get(pk=i.pk).type_mont_doss
		else:
			ht_ttc = ''
		self.fields['mont_doss'].label = self.fields['mont_doss'].label.replace('[ht_ou_ttc]', ht_ttc)
		self.fields['mont_suppl_doss'].label = self.fields['mont_suppl_doss'].label.replace('[ht_ou_ttc]', ht_ttc)

		# J'exclus le champ relatif aux dépenses supplémentaires lorsque je veux créer un dossier.
		if not i.pk :
			del self.fields['mont_suppl_doss']

		if i.pk :

			# Je réinitialise le tableau des choix de certaines listes déroulantes.
			self.fields['zl_org_moa'].choices = [(i.id_org_moa.pk, i.id_org_moa)]
			self.fields['zl_progr'].choices = [(i.id_progr.pk, i.id_progr)]
			if i.id_nat_doss.peu_doss == False :
				self.fields['zl_nat_doss'].choices += [(i.id_nat_doss.pk, i.id_nat_doss)]
			self.fields['zl_type_doss'].choices = [(i.id_type_doss.pk, i.id_type_doss)]
			if i.id_techn.en_act == False :
				self.fields['zl_techn'].choices += [(i.id_techn.pk, i.id_techn)]

			# J'affiche la valeur initiale de chaque champ personnalisé.
			self.fields['za_num_doss'].initial = i
			self.fields['za_doss_ass'].initial = i.id_doss_ass
			self.fields['zl_nat_doss'].initial = i.id_nat_doss.pk
			self.fields['zl_type_doss'].initial = i.id_type_doss.pk
			self.fields['zl_techn'].initial = i.id_techn.pk
			self.fields['rb_est_ttc_doss'].initial = i.est_ttc_doss

			# Stockage des axes du programme
			axes = [(a.pk, a.num_axe) for a in TAxe.objects.filter(id_progr = i.id_progr)]

			if len(axes) > 0 :

				# Définition des choix de la liste déroulante des axes
				axes.insert(0, DEFAULT_OPTION)
				self.fields['zl_axe'].choices = axes

				# Affichage de la liste déroulante
				self.fields['zl_axe'].widget.attrs['class'] += ' show-field'

				if i.num_axe :

					# Obtention d'une instance TAxe
					obj_axe = TAxe.objects.get(id_progr = i.id_progr, num_axe = i.num_axe)

					# Affichage de la valeur initiale
					self.fields['zl_axe'].initial = obj_axe.pk

					# Stockage des sous-axes de l'axe
					ss_axes = [(sa.pk, sa.num_ss_axe) for sa in TSousAxe.objects.filter(id_axe = obj_axe)]

					if len(ss_axes) > 0 :

						# Définition des choix de la liste déroulante des sous-axes
						ss_axes.insert(0, DEFAULT_OPTION)
						self.fields['zl_ss_axe'].choices = ss_axes

						# Affichage de la liste déroulante
						self.fields['zl_ss_axe'].widget.attrs['class'] += ' show-field'

						if i.num_ss_axe :

							# Obtention d'une instance TSousAxe
							obj_ss_axe = TSousAxe.objects.get(id_axe = obj_axe, num_ss_axe = i.num_ss_axe)

							# Affichage de la valeur initiale
							self.fields['zl_ss_axe'].initial = obj_ss_axe.pk

							# Stockage des actions du sous-axe
							acts = [(a.pk, a.num_act) for a in TAction.objects.filter(id_ss_axe = obj_ss_axe)]

							if len(acts) > 0 :

								# Définition des choix de la liste déroulante des actions
								acts.insert(0, DEFAULT_OPTION)
								self.fields['zl_act'].choices = acts

								# Affichage de la liste déroulante
								self.fields['zl_act'].widget.attrs['class'] += ' show-field'

								# Affichage de la valeur initiale
								if i.num_act :
									obj_act = TAction.objects.get(id_ss_axe = obj_ss_axe, num_act = i.num_act)
									self.fields['zl_act'].initial = obj_act.pk

			# Récupération d'une instance VSuiviDossier
			voDds = VSuiviDossier.objects.get(pk=i.pk)

			# Je vérifie si certains champs doivent bénéficier ou non de la lecture seule.
			if i.id_av.int_av in [T_DONN_BDD_STR['AV_EP'], T_DONN_BDD_STR['AV_ABAND']] :
				self.fields['dt_delib_moa_doss'].widget.attrs['readonly'] = True
			if voDds.id_av_cp.int_av_cp == T_DONN_BDD_STR['AV_CP_ACC'] :
				self.fields['mont_doss'].widget.attrs['readonly'] = True
			else :
				self.fields['mont_suppl_doss'].widget.attrs['readonly'] = True

	def clean(self) :

		# Imports
		from app.functions import ger_droits
		from app.functions import obt_mont
		from app.models import TDossier
		from app.models import TFinancement
		from app.models import TMoa
		from app.models import TPrestationsDossier
		from app.models import TProgramme
		from app.models import VSuiviDossier
		from django.db.models import Max
		from django.db.models import Sum
		from styx.settings import T_DONN_BDD_STR

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererDossier, self).clean()
		v_doss_ass = cleaned_data.get('za_doss_ass')
		v_org_moa = cleaned_data.get('zl_org_moa')
		v_progr = cleaned_data.get('zl_progr')
		v_axe = cleaned_data.get('zl_axe')
		v_ss_axe = cleaned_data.get('zl_ss_axe')
		v_act = cleaned_data.get('zl_act')
		v_type_doss = cleaned_data.get('zl_type_doss')
		v_mont_doss = cleaned_data.get('mont_doss')
		v_mont_suppl_doss = cleaned_data.get('mont_suppl_doss')
		v_av = cleaned_data.get('id_av')
		v_dt_delib_moa_doss = cleaned_data.get('dt_delib_moa_doss')

		i = self.instance

		if v_doss_ass :

			# Je renvoie une erreur si le numéro du dossier associé n'existe pas.
			try :
				TDossier.objects.get(num_doss = v_doss_ass)
			except :
				self.add_error('za_doss_ass', 'Le dossier {0} n\'existe pas.'.format(v_doss_ass))

			# Je renvoie une erreur si le numéro du dossier associé et le numéro du dossier de l'instance sont
			# identiques.
			if i.pk and i.num_doss == v_doss_ass :
				self.add_error('za_doss_ass', 'Veuillez choisir un autre dossier associé.')

		# Je rends obligatoire la date de délibération au maître d'ouvrage si l'état d'avancement du dossier n'est pas
		# en projet.
		if v_av :
			if v_av.int_av not in [T_DONN_BDD_STR['AV_EP'], T_DONN_BDD_STR['AV_ABAND']] and not v_dt_delib_moa_doss :
				self.add_error('dt_delib_moa_doss', ERROR_MESSAGES['required'])

		# Je rends obligatoire l'axe, le sous-axe, l'action et le type de dossier sous certaines conditions.
		if v_progr :
			if v_axe :
				if v_ss_axe :
					if not v_act and len(self.fields['zl_act'].choices) > 0 :
						self.add_error('zl_act', ERROR_MESSAGES['required'])
				else :
					if len(self.fields['zl_ss_axe'].choices) > 0 :
						self.add_error('zl_ss_axe', ERROR_MESSAGES['required'])
			else :
				if len(self.fields['zl_axe'].choices) > 0 :
					self.add_error('zl_axe', ERROR_MESSAGES['required'])
			if not v_type_doss :
				self.add_error('zl_type_doss', ERROR_MESSAGES['required'])

		# Je renvoie une erreur si l'utilisateur n'a pas les droits pour créer un dossier spécifique.
		if not i.pk and v_org_moa and v_progr :
			o_org_moa = TMoa.objects.get(pk = v_org_moa)
			o_progr = TProgramme.objects.get(pk = v_progr)
			if ger_droits(self.k_util, [(o_org_moa.pk, o_progr.id_type_progr.pk)], False, False) == False :
				self.add_error(
					'__all__',
					'''
					Vous n\'avez pas les permissions requises pour créer un dossier du programme « {0} » pour le maître
					d\'ouvrage « {1} ».
					'''.format(o_progr, o_org_moa)
				)

		if i.pk :

			# Récupération d'une instance VSuiviDossier
			voDds = VSuiviDossier.objects.get(pk=i.pk)

			# Je récupère trois valeurs : le montant de l'assiette éligible maximum, la somme des montants de la
			# participation et la somme des prestations.
			qs_fin_aggr = TFinancement.objects.filter(id_doss = i).aggregate(
				Max('mont_elig_fin'), Sum('mont_part_fin')
			)
			mont_elig_fin_max = qs_fin_aggr['mont_elig_fin__max'] or 0
			mont_part_fin_sum = qs_fin_aggr['mont_part_fin__sum'] or 0
			mont_tot_prest_doss = voDds.mont_tot_prest_doss

			# Je trie les deux valeurs dans l'ordre afin de récupérer le montant minimum du dossier.
			t_mont_doss = sorted([mont_elig_fin_max, mont_part_fin_sum, mont_tot_prest_doss])

			# Je gère la contrainte suivante : les montants du dossier dépendent des éléments comptables de celui-ci.
			if v_mont_doss is not None and v_mont_suppl_doss is not None :
				if voDds.id_av_cp :
					if voDds.id_av_cp.int_av_cp == T_DONN_BDD_STR['AV_CP_ACC'] :
						if t_mont_doss[2] > i.mont_doss :
							mont_min = t_mont_doss[2] - i.mont_doss
							if float(v_mont_suppl_doss) < mont_min :
								self.add_error(
									'mont_suppl_doss',
									'Veuillez saisir un montant supérieur ou égal à {0} €.'.format(obt_mont(mont_min))
								)
					else :
						if float(v_mont_doss) < t_mont_doss[2] :
							self.add_error(
								'mont_doss',
								'Veuillez saisir un montant supérieur ou égal à {0} €.'.format(obt_mont(t_mont_doss[2]))
							)

			# Je renvoie une erreur si je passe un dossier en projet alors que des éléments comptables ont déjà été
			# saisis.
			if v_av and v_av.int_av == T_DONN_BDD_STR['AV_EP'] :
				if len(TPrestationsDossier.objects.filter(id_doss = i)) > 0 :
					self.add_error('id_av', 'Une prestation a déjà été lancée pour ce dossier.')

			# Je renvoie une erreur si le montant de dépassement d'un dossier dont l'avis du comité de programmation
			# est différent de "Accordé" est strictement positif.
			if voDds.id_av_cp and voDds.id_av_cp.int_av_cp != T_DONN_BDD_STR['AV_CP_ACC'] :
				if v_mont_suppl_doss and float(v_mont_suppl_doss) > 0 :
					self.add_error('mont_suppl_doss', ERROR_MESSAGES['invalid'])
			else :
				if v_mont_doss and v_mont_doss != i.mont_doss :
					self.add_error('mont_doss', ERROR_MESSAGES['invalid'])

	def save(self, commit = True) :

		# Imports
		from app.models import TAction
		from app.models import TAxe
		from app.models import TDossier
		from app.models import TMoa
		from app.models import TNatureDossier
		from app.models import TProgramme
		from app.models import TSousAxe
		from app.models import TTechnicien
		from app.models import TTypeDossier

		o = super(GererDossier, self).save(commit = False)

		v_est_ttc_doss = self.cleaned_data.get('rb_est_ttc_doss')
		if v_est_ttc_doss and v_est_ttc_doss == 'True' :
			o.est_ttc_doss = True
		if v_est_ttc_doss and v_est_ttc_doss == 'False' :
			o.est_ttc_doss = False

		# J'initialise le numéro de l'action.
		try :
			v_act = TAction.objects.get(pk = self.cleaned_data.get('zl_act')).num_act
		except :
			v_act = ''

		o.num_act = v_act

		# J'initialise le numéro de l'axe.
		try :
			v_axe = TAxe.objects.get(pk = self.cleaned_data.get('zl_axe')).num_axe
		except :
			v_axe = ''

		o.num_axe = v_axe

		# J'initialise le numéro du sous-axe.
		try :
			v_ss_axe = TSousAxe.objects.get(pk = self.cleaned_data.get('zl_ss_axe')).num_ss_axe
		except :
			v_ss_axe = ''

		o.num_ss_axe = v_ss_axe

		# Je vérifie l'existence d'un objet TDossier.
		try :
			o_doss = TDossier.objects.get(num_doss = self.cleaned_data.get('za_doss_ass'))
		except :
			o_doss = None

		o.id_doss_ass = o_doss
		o.id_nat_doss = TNatureDossier.objects.get(pk = self.cleaned_data.get('zl_nat_doss'))
		o.id_progr = TProgramme.objects.get(pk = self.cleaned_data.get('zl_progr'))
		o.id_org_moa = TMoa.objects.get(pk = self.cleaned_data.get('zl_org_moa'))
		o.id_techn = TTechnicien.objects.get(pk = self.cleaned_data.get('zl_techn'))
		o.id_type_doss = TTypeDossier.objects.get(pk = self.cleaned_data.get('zl_type_doss'))

		if commit :
			o.save()

		return o

class ChoisirDossier(forms.ModelForm) :

	zs_num_doss = forms.CharField(label='N° du dossier', required=False)
	zl_org_moa = forms.ChoiceField(label = 'Maître d\'ouvrage', required = False, widget = forms.Select())
	zl_progr = forms.ChoiceField(label = 'Programme', required = False, widget = forms.Select())
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
	zl_nat_doss = forms.ChoiceField(label = 'Nature du dossier', required = False, widget = forms.Select())
	zl_ann_delib_moa_doss = forms.ChoiceField(
		label = 'Année de délibération au maître d\'ouvrage', required = False, widget = forms.Select()
	)
	rb_doss_sold = forms.ChoiceField(
		choices=[('solde', 'Oui'), ('non_solde', 'Non')],
		initial='solde',
		label='Afficher les dossiers soldés ?',
		required=False,
		widget=forms.RadioSelect()
	)
	rb_doss_term = forms.ChoiceField(
		choices=[('termine', 'Oui'), ('non_termine', 'Non')],
		initial='termine',
		label='Afficher les dossiers terminés ?',
		required=False,
		widget=forms.RadioSelect()
	)
	rb_doss_archi = forms.ChoiceField(
		choices=[('archive', 'Oui'), ('non_archive', 'Non')],
		initial='archive',
		label='Afficher les dossiers archivés ?',
		required=False,
		widget=forms.RadioSelect()
	)
	rb_doss_aband = forms.ChoiceField(
		choices=[('abandonne', 'Oui'), ('non_abandonne', 'Non')],
		initial='abandonne',
		label='Afficher les dossiers abandonnés ?',
		required=False,
		widget=forms.RadioSelect()
	)

	class Meta :

		# Imports
		from app.models import TDossier

		fields = []
		model = TDossier

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TDossier
		from app.models import TMoa
		from app.models import TNatureDossier
		from app.models import TProgramme

		# Je déclare le tableau des arguments.
		k_org_moa = kwargs.pop('k_org_moa', None)

		super(ChoisirDossier, self).__init__(*args, **kwargs)
		init_mess_err(self, False)

		if k_org_moa :
			self.fields['zl_org_moa'].initial = k_org_moa

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		t_org_moa = [(m.pk, m) for m in TMoa.objects.filter(peu_doss = True, en_act_doss = True)]
		t_org_moa.insert(0, DEFAULT_OPTION)
		self.fields['zl_org_moa'].choices = t_org_moa

		# J'alimente la liste déroulante des programmes.
		t_progr = [(p.pk, p) for p in TProgramme.objects.all()]
		t_progr.insert(0, DEFAULT_OPTION)
		self.fields['zl_progr'].choices = t_progr

		# J'alimente la liste déroulante des natures de dossiers.
		t_nat_doss = [(nd.pk, nd) for nd in TNatureDossier.objects.all()]
		t_nat_doss.insert(0, DEFAULT_OPTION)
		self.fields['zl_nat_doss'].choices = t_nat_doss

		# J'alimente la liste déroulante des années.
		t_ann_delib_moa_doss = TDossier.objects.get_years(mdl_column = 'dt_delib_moa_doss')
		t_ann_delib_moa_doss.insert(0, DEFAULT_OPTION)
		self.fields['zl_ann_delib_moa_doss'].choices = t_ann_delib_moa_doss

class GererFinancement(forms.ModelForm) :

	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)

	class Meta :

		# Imports
		from app.models import TFinancement

		exclude = ['id_doss']
		fields = '__all__'
		model = TFinancement
		widgets = {
			'dt_deb_elig_fin' : forms.DateInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_decision_aide_fin' : forms.DateInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_lim_deb_oper_fin' : forms.DateInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_lim_prem_ac_fin' : forms.DateInput(attrs = { 'input-group-addon' : 'date' }),
			'mont_elig_fin' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' }),
			'mont_part_fin' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' })
		}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import obt_pourc
		from styx.settings import T_DONN_BDD_STR

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		k_doss = kwargs.pop('k_doss', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'mont_elig_fin' : '{:0.2f}'.format(instance.mont_elig_fin) if instance.mont_elig_fin else None,
				'mont_part_fin' : '{:0.2f}'.format(instance.mont_part_fin)
			})

		super(GererFinancement, self).__init__(*args, **kwargs)
		init_mess_err(self)
		self.fields['mont_elig_fin'].label += MAY_BE_REQUIRED
		self.fields['pourc_elig_fin'].label += MAY_BE_REQUIRED
		self.fields['pourc_real_fin'].label += MAY_BE_REQUIRED
		self.fields['dt_deb_elig_fin'].label += MAY_BE_REQUIRED

		# Je passe en lecture seule le champ relatif au pourcentage de réalisation des travaux.
		self.fields['pourc_real_fin'].widget.attrs['readonly'] = True

		# J'initialise certaines variables par précaution.
		num_doss = None
		ht_ou_ttc = 'HT'

		i = self.instance
		if i.pk :
			num_doss = i.id_doss
			if i.id_doss.est_ttc_doss == True :
				ht_ou_ttc = 'TTC'
			'''
			if i.mont_elig_fin and i.pourc_elig_fin :
				self.fields['mont_part_fin'].widget.attrs['readonly'] = True
			'''
			if i.id_paiem_prem_ac :
				if i.id_paiem_prem_ac.int_paiem_prem_ac == T_DONN_BDD_STR['PPA_PRT'] :
					self.fields['pourc_real_fin'].widget.attrs['readonly'] = False
		else :
			if k_doss :
				num_doss = k_doss
				if k_doss.est_ttc_doss == True :
					ht_ou_ttc = 'TTC'

		# J'affiche le numéro du dossier lié au financement (ou prochainement lié).
		self.fields['za_num_doss'].initial = num_doss

		# Je complète le label de chaque champ demandant un montant.
		lab_mont_elig_fin = self.fields['mont_elig_fin'].label.replace('[ht_ou_ttc]', ht_ou_ttc)
		self.fields['mont_elig_fin'].label = lab_mont_elig_fin
		lab_mont_part_fin = self.fields['mont_part_fin'].label.replace('[ht_ou_ttc]', ht_ou_ttc)
		self.fields['mont_part_fin'].label = lab_mont_part_fin

	def clean(self) :

		# Imports
		from app.functions import obt_mont
		from app.models import TDossier
		from app.models import VFinancement
		from app.models import VSuiviDossier

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererFinancement, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_org_fin = cleaned_data.get('id_org_fin')
		v_mont_elig_fin = cleaned_data.get('mont_elig_fin')
		v_pourc_elig_fin = cleaned_data.get('pourc_elig_fin')
		v_mont_part_fin = cleaned_data.get('mont_part_fin')
		v_dt_deb_elig_fin = cleaned_data.get('dt_deb_elig_fin')
		v_duree_valid_fin = cleaned_data.get('duree_valid_fin')
		v_duree_pror_fin = cleaned_data.get('duree_pror_fin')
		v_dt_lim_deb_oper_fin = cleaned_data.get('dt_lim_deb_oper_fin')
		v_a_inf_fin = cleaned_data.get('a_inf_fin')

		i = self.instance

		# Je vérifie l'existence d'un objet TDossier.
		try :
			if i.pk :
				o_doss = i.id_doss
			else :
				o_doss = TDossier.objects.get(num_doss = v_num_doss)
			o_suivi_doss = VSuiviDossier.objects.get(pk = o_doss.pk)
		except :
			o_doss = None
			o_suivi_doss = None
			self.add_error('za_num_doss', 'Le dossier n\'existe pas.')

		if o_doss and o_suivi_doss :

			# Je gère la contrainte suivante : un financeur ne peut participer plusieurs fois au plan de financement d'
			# un dossier.
			if v_org_fin :
				qs_fin = VFinancement.objects.filter(id_org_fin = v_org_fin, id_doss = o_doss)
				if i.pk :
					qs_fin = qs_fin.exclude(id_fin = i.pk)
				if len(qs_fin) > 0 :
					self.add_error('id_org_fin', 'Le financeur participe déjà au montage financier.')

			# Je gère la contrainte suivante : le montant de l'assiette éligible de la subvention doit toujours être
			# inférieur ou égal au montant du dossier.
			if v_mont_elig_fin and float(v_mont_elig_fin) > float(o_doss.mont_doss) :
				self.add_error(
					'mont_elig_fin',
					'Veuillez saisir un montant inférieur ou égal à {0} €.'.format(obt_mont(o_doss.mont_doss))
				)

			# Je gère la contrainte suivante : le couple montant de l'assiette éligible/pourcentage éligible doit être
			# conforme.
			if v_mont_elig_fin and v_pourc_elig_fin is None :
				self.add_error('pourc_elig_fin', ERROR_MESSAGES['required'])
			if v_pourc_elig_fin and v_mont_elig_fin is None :
				self.add_error('mont_elig_fin', ERROR_MESSAGES['required'])

			# Je stocke la valeur du reste à financer du dossier.
			mont_part_fin_max = o_suivi_doss.mont_raf
			if i.pk :
				mont_part_fin_max += i.mont_part_fin

			# Je gère la contrainte suivante : le montant de la participation doit être inférieur ou égal au reste à
			# financer du dossier.
			if v_mont_part_fin and float(v_mont_part_fin) > float(mont_part_fin_max) :
				self.add_error(
					'mont_part_fin',
					'Veuillez saisir un montant inférieur ou égal à {0} €.'.format(obt_mont(mont_part_fin_max))
				)

			# Je gère la contrainte suivante : le couple date de début d'éligibilité/durée de la validité et/ou de la
			# prorogation doit être conforme.
			if not v_dt_deb_elig_fin :
				if v_duree_valid_fin and v_duree_valid_fin > 0 :
					self.add_error('dt_deb_elig_fin', ERROR_MESSAGES['required'])
				if v_duree_pror_fin and v_duree_pror_fin > 0 :
					self.add_error('dt_deb_elig_fin', ERROR_MESSAGES['required'])

			# Je gère la contrainte suivante : le montant de la participation doit être supérieur ou égal à la somme
			# des demandes de versements effectuées sur ce financement.
			if i.pk :
				o_fin = VFinancement.objects.get(id_fin = i.pk)
				if v_mont_part_fin and float(v_mont_part_fin) < o_fin.mont_ddv_sum :
					self.add_error(
						'mont_part_fin',
						'Veuillez saisir un montant supérieur ou égal à {0} €.'.format(obt_mont(o_fin.mont_ddv_sum))
					)

			# Je gère la contrainte liée à la date limite du début de l'opération.
			if v_dt_lim_deb_oper_fin :
				if v_a_inf_fin == 'Sans objet' :
					self.add_error('a_inf_fin', ERROR_MESSAGES['invalid'])
			else :
				if v_a_inf_fin != 'Sans objet' :
					self.add_error('a_inf_fin', ERROR_MESSAGES['invalid'])

	def save(self, commit = True) :

		# Imports
		from app.models import TDossier

		o = super(GererFinancement, self).save(commit = False)
		if not self.instance.pk :
			o.id_doss = TDossier.objects.get(num_doss = self.cleaned_data.get('za_num_doss'))
		if commit :
			o.save()

		return o

class GererPrestation(forms.ModelForm) :

	# Imports
	from app.classes.FFEuroField import Class as FFEuroField

	rb_prest_exist = forms.ChoiceField(
		choices = [(1, 'Oui'), (0, 'Non')],
		initial = 0,
		label = 'La prestation est-elle déjà existante dans un autre dossier ?',
		required = False,
		widget = forms.RadioSelect()
	)
	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	zs_siret_org_prest = forms.CharField(
		label = 'Numéro SIRET du prestataire',
		widget = forms.TextInput(attrs = { 'autocomplete' : 'off', 'maxlength' : 14, 'typeahead' : 'on' })
	)
	zs_mont_prest = FFEuroField(
		label = 'Montant [ht_ou_ttc] de la prestation',
		min_value = 0.01,
        widget = forms.NumberInput(attrs = { 'input-group-addon' : 'euro' })
    )
	zs_duree_prest = forms.IntegerField(
		initial = 0, label = 'Durée de la prestation (en nombre de jours ouvrés)', min_value = 0
	)

	class Meta :

		# Imports
		from app.models import TPrestation

		exclude = ['doss', 'id_org_prest']
		fields = '__all__'
		model = TPrestation
		widgets = {
			'dt_fin_prest' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_notif_prest' : forms.TextInput(attrs = { 'input-group-addon' : 'date' })
		}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr
		from app.models import TPrestationsDossier

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		k_doss = kwargs.pop('k_doss', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'dt_fin_prest' : dt_fr(instance.dt_fin_prest) if instance.dt_fin_prest else None,
				'dt_notif_prest' : dt_fr(instance.dt_notif_prest) if instance.dt_notif_prest else None
			})

		super(GererPrestation, self).__init__(*args, **kwargs)
		init_mess_err(self)

		# J'initialise la variable liée au mode de taxe par précaution.
		ht_ou_ttc = 'HT'

		i = self.instance
		if i.pk :
			self.fields['zs_siret_org_prest'].initial = i.id_org_prest.siret_org_prest
			for pd in TPrestationsDossier.objects.filter(id_prest = i) :
				if pd.id_doss.est_ttc_doss == True :
					ht_ou_ttc = 'TTC'
		else :
			if k_doss :
				self.fields['za_num_doss'].initial = k_doss
				if k_doss.est_ttc_doss == True :
					ht_ou_ttc = 'TTC'

		# Je complète le label de chaque champ demandant un montant.
		lab_mont_prest = self.fields['zs_mont_prest'].label.replace('[ht_ou_ttc]', ht_ou_ttc)
		self.fields['zs_mont_prest'].label = lab_mont_prest

		# J'exclus les champs personnalisés liés à la durée et au montant de la prestation lorsque je suis en phase
		# de modification.
		if i.pk :
			del self.fields['zs_duree_prest']
			del self.fields['zs_mont_prest']

	def clean(self) :

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont
		from app.models import TAvenant
		from app.models import TDossier
		from app.models import TPrestataire
		from app.models import VSuiviDossier
		from django.db.models import Min

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererPrestation, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_siret_org_prest = cleaned_data.get('zs_siret_org_prest')
		v_mont_prest = cleaned_data.get('zs_mont_prest')
		v_dt_fin_prest = cleaned_data.get('dt_fin_prest')

		i = self.instance

		# Je gère la contrainte suivante : le numéro SIRET doit exister dans la base de données afin de le relier à un
		# prestataire.
		if len(TPrestataire.objects.filter(siret_org_prest = v_siret_org_prest)) == 0 :
			self.add_error('zs_siret_org_prest', 'Le numéro SIRET appartient à aucun prestataire.')

		# Je vérifie l'existence d'un objet TDossier.
		o_doss = None
		o_suivi_doss = None
		if not i.pk :
			try :
				o_doss = TDossier.objects.get(num_doss = v_num_doss)
				o_suivi_doss = VSuiviDossier.objects.get(pk = o_doss.pk)
			except :
				self.add_error('za_num_doss', 'Le dossier n\'existe pas.')

		# Je gère la contrainte suivante : le montant initial de la prestation ne doit pas être supérieur au reste à
		# engager du dossier.
		if o_doss and o_suivi_doss :
			if v_mont_prest and float(v_mont_prest) > float(o_suivi_doss.mont_rae) :
				self.add_error(
					'zs_mont_prest',
					'Veuillez saisir un montant inférieur ou égal à {0} €.'.format(obt_mont(o_suivi_doss.mont_rae))
				)

		# Je renvoie une erreur si la date de fin de prestation est supérieure à la date du premier avenant de date.
		if i.pk :
			qs_aven_aggr = TAvenant.objects.filter(id_prest = i).aggregate(Min('dt_aven'))
			dt_aven_min = qs_aven_aggr['dt_aven__min']
			if v_dt_fin_prest and dt_aven_min and v_dt_fin_prest > dt_aven_min :
				self.add_error(
					'dt_fin_prest',
					'''
					Veuillez saisir une date antérieure ou égale au {0} (date de fin du premier avenant de date).
					'''.format(dt_fr(dt_aven_min))
				)

	def save(self, commit = True) :

		# Imports
		from app.models import TDossier
		from app.models import TPrestataire

		o = super(GererPrestation, self).save(commit = False)
		o.id_org_prest = TPrestataire.objects.get(siret_org_prest = self.cleaned_data.get('zs_siret_org_prest'))
		if commit :
			o.save()

		return o

class ChoisirPrestation(forms.Form) :

	zl_progr = forms.ChoiceField(label = 'Programme', required = False, widget = forms.Select())
	za_org_moa = forms.CharField(
		label = 'Maître d\'ouvrage', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	zl_org_prest = forms.ChoiceField(label = 'Prestataire', required = False, widget = forms.Select())

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TPrestataire
		from app.models import TProgramme

		# Je déclare le tableau des arguments.
		k_org_moa = kwargs.pop('k_org_moa', None)

		super(ChoisirPrestation, self).__init__(*args, **kwargs)
		init_mess_err(self, False)

		# J'alimente la liste déroulante des programmes.
		t_progr = [(p.pk, p) for p in TProgramme.objects.all()]
		t_progr.insert(0, DEFAULT_OPTION)
		self.fields['zl_progr'].choices = t_progr

		# J'alimente la liste déroulante des prestataires.
		t_org_prest = [(p.pk, p) for p in TPrestataire.objects.all()]
		t_org_prest.insert(0, DEFAULT_OPTION)
		self.fields['zl_org_prest'].choices = t_org_prest

		# J'affiche la valeur initiale de certains champs personnalisés.
		self.fields['za_org_moa'].initial = k_org_moa

class RedistribuerPrestation(forms.ModelForm) :

	class Meta :

		# Imports
		from app.models import TPrestationsDossier

		fields = ['duree_prest_doss', 'mont_prest_doss']
		model = TPrestationsDossier
		widgets = {'mont_prest_doss' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' })}

	def __init__(self, *args, **kwargs) :

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		self.k_doss = kwargs.pop('k_doss', None)
		self.k_prest = kwargs.pop('k_prest', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'mont_prest_doss' : '{:0.2f}'.format(instance.mont_prest_doss)
			})

		super(RedistribuerPrestation, self).__init__(*args, **kwargs)
		init_mess_err(self, False)

		# Je supprime le label lié à la durée et au montant du couple prestation/dossier.
		self.fields['duree_prest_doss'].label = ''
		self.fields['mont_prest_doss'].label = ''

	def clean(self) :

		# Imports
		from app.functions import obt_mont
		from app.models import VSuiviDossier
		from app.models import VSuiviPrestationsDossier

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(RedistribuerPrestation, self).clean()
		v_mont_prest_doss = cleaned_data.get('mont_prest_doss')

		i = self.instance
		if i.pk :

			# Je pointe vers les objets VSuiviPrestationsDossier et VSuiviDossier.
			o_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(pk = i.pk)
			o_suivi_doss = VSuiviDossier.objects.get(pk = i.id_doss.pk)

			# J'initialise la somme des factures émises selon le mode de taxe du dossier.
			v_mont_fact_sum = o_suivi_prest_doss.mont_ht_fact_sum
			if o_suivi_doss.est_ttc_doss == True :
				v_mont_fact_sum = o_suivi_prest_doss.mont_ttc_fact_sum

			# Je définis les montants minimum et maximum.
			mont_prest_doss_min = v_mont_fact_sum - o_suivi_prest_doss.mont_aven_sum
			if mont_prest_doss_min < 0 :
				mont_prest_doss_min = 0
			mont_prest_doss_max = i.mont_prest_doss + o_suivi_doss.mont_rae

		else :

			# Je pointe vers l'objet VSuiviDossier.
			o_suivi_doss = VSuiviDossier.objects.get(pk = self.k_doss.pk)

			# Je définis les montants minimum et maximum.
			mont_prest_doss_min = 0
			mont_prest_doss_max = o_suivi_doss.mont_rae

		# Je renvoie une erreur si le montant saisi n'est pas inclus dans l'intervalle de valeurs autorisées.
		if v_mont_prest_doss and not float(mont_prest_doss_min) <= float(v_mont_prest_doss) <= float(mont_prest_doss_max) :

			err_mess = '''
			Veuillez saisir un montant compris entre {0} € et {1} €.
			'''.format(obt_mont(mont_prest_doss_min), obt_mont(mont_prest_doss_max))

			if mont_prest_doss_min == 0 :
				err_mess = '''
				Veuillez saisir un montant inférieur ou égal à {0} €.
				'''.format(obt_mont(mont_prest_doss_max))

			if mont_prest_doss_min == mont_prest_doss_max :
				err_mess = 'Veuillez saisir un montant égal à {0} €.'.format(obt_mont(mont_prest_doss_max))

			self.add_error('mont_prest_doss', err_mess)

	def save(self, commit = True) :

		o = super(RedistribuerPrestation, self).save(commit = False)
		if not self.instance.pk :
			o.id_doss = self.k_doss
			o.id_prest = self.k_prest
		if commit :
			o.save()

		return o

class GererFacture(forms.ModelForm) :

	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	zl_prest = forms.ChoiceField(label = 'Prestation', widget = forms.Select())
	zl_suivi_fact = forms.ChoiceField(
		choices = [
			DEFAULT_OPTION,
			('Acompte', 'Acompte'),
			('Avance', 'Avance'),
			('Solde', 'Solde')
		],
		label = 'Suivi de la facturation',
		required = True,
		widget = forms.Select()
	)

	class Meta :

		# Imports
		from app.models import TFacture

		exclude = ['id_doss', 'id_prest', 'suivi_fact']
		fields = '__all__'
		model = TFacture
		widgets = {
			'dt_mand_moa_fact' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_emiss_fact' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_rec_fact' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }),
			'mont_ht_fact' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' }),
			'mont_ttc_fact' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' })
		}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr
		from app.models import TFacturesDemandeVersement
		from app.models import TPrestationsDossier

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		k_doss = kwargs.pop('k_doss', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial={
				'dt_emiss_fact': dt_fr(instance.dt_emiss_fact) if instance.dt_emiss_fact else None,
				'dt_mand_moa_fact': dt_fr(instance.dt_mand_moa_fact) if instance.dt_mand_moa_fact else None,
				'dt_rec_fact': dt_fr(instance.dt_rec_fact) if instance.dt_rec_fact else None,
				'mont_ht_fact': '{:0.2f}'.format(instance.mont_ht_fact) if instance.mont_ht_fact else None,
				'mont_ttc_fact': '{:0.2f}'.format(instance.mont_ttc_fact) if instance.mont_ttc_fact else None,
			})

		super(GererFacture, self).__init__(*args, **kwargs)
		init_mess_err(self)

		# J'initialise certaines variables par précaution.
		num_doss = None

		i = self.instance
		if i.pk :
			num_doss = i.id_doss
		else :
			if k_doss :
				num_doss = k_doss

		# J'affiche le numéro du dossier lié à la facture (ou prochainement lié).
		self.fields['za_num_doss'].initial = num_doss

		# J'ajoute un astérisque au label du champ de montant obligatoire.
		if num_doss :
			if num_doss.est_ttc_doss == True :
				self.fields['mont_ttc_fact'].label += REQUIRED
			else :
				self.fields['mont_ht_fact'].label += REQUIRED

		if i.pk :

			# J'affiche la valeur initiale de chaque champ personnalisé.
			self.fields['zl_prest'].initial = i.id_prest.pk
			self.fields['zl_suivi_fact'].initial = i.suivi_fact

			# Interdiction de modifier le montant de la facture si reliée à une demande de versement
			if TFacturesDemandeVersement.objects.filter(id_fact = i).count() > 0 :
				if i.id_doss.est_ttc_doss == True :
					cle = 'mont_ttc_fact'
				else :
					cle = 'mont_ht_fact'
				self.fields[cle].widget.attrs['readonly'] = True

		# J'alimente la liste déroulante des prestations du dossier.
		t_prest_doss = [(pd.id_prest.pk, pd.id_prest) for pd in TPrestationsDossier.objects.filter(
			id_doss = num_doss
		).order_by('id_prest')]
		t_prest_doss.insert(0, DEFAULT_OPTION)
		self.fields['zl_prest'].choices = t_prest_doss

	def clean(self) :

		# Imports
		from app.functions import obt_mont
		from app.models import TDossier
		from app.models import TFacture
		from app.models import TFacturesDemandeVersement
		from app.models import VSuiviPrestationsDossier

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererFacture, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_prest = cleaned_data.get('zl_prest')
		v_suivi_fact = cleaned_data.get('zl_suivi_fact')

		i = self.instance

		# Je vérifie l'existence d'un objet TDossier.
		try :
			if i.pk :
				o_doss = i.id_doss
			else :
				o_doss = TDossier.objects.get(num_doss = v_num_doss)
		except :
			o_doss = None
			self.add_error('za_num_doss', 'Le dossier {0} n\'existe pas.'.format(v_num_doss))

		# Je vérifie l'existence d'un objet VSuiviPrestationsDossier.
		o_suivi_prest_doss = None
		if o_doss :
			try :
				o_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(id_doss = o_doss, id_prest = v_prest)
			except :
				self.add_error('zl_prest', ERROR_MESSAGES['invalid'])

		if o_suivi_prest_doss :

			# Je stocke la clé et la valeur du contrôle relatif au montant HT ou TTC de la facture.
			cle = 'mont_ht_fact'
			if o_suivi_prest_doss.id_doss.est_ttc_doss == True :
				cle = 'mont_ttc_fact'
			valeur = cleaned_data.get(cle)

			# Je détermine le reste à facturer de la prestation.
			mont_raf_max = o_suivi_prest_doss.mont_raf
			if i.pk and o_suivi_prest_doss.id_prest == i.id_prest :
				if 'ht' in cle :
					mont_raf_max += i.mont_ht_fact
				if 'ttc' in cle :
					mont_raf_max += i.mont_ttc_fact

			# Je gère la contrainte suivante : le montant de la facture ne doit pas être supérieur au reste à facturer
			# de la prestation.
			if valeur :
				if float(valeur) > float(mont_raf_max) :
					self.add_error(
						cle,
						'Veuillez saisir un montant inférieur ou égal à {0} €.'.format(obt_mont(mont_raf_max))
					)
			else :
				self.add_error(cle, ERROR_MESSAGES['required'])

			# Je récupère les factures soldées du couple prestation/dossier.
			qs_fact = TFacture.objects.filter(
				id_doss = o_suivi_prest_doss.id_doss,
				id_prest = o_suivi_prest_doss.id_prest,
				suivi_fact = 'Solde'
			)

			# Je gère la contrainte suivante : un couple prestation/dossier ne peut avoir deux factures soldées.
			err = False
			if v_suivi_fact :
				if not i.pk :
					if len(qs_fact) > 0 :
						err = True
				else :
					qs_fact = qs_fact.exclude(pk = i.pk)
					if len(qs_fact) > 0 and v_suivi_fact == 'Solde' :
						err = True
				if err == True :
					self.add_error('zl_suivi_fact', 'Vous avez déjà émis une facture soldée pour cette prestation.')

			# Interdiction de modifier le montant de la facture si reliée à une demande de versement
			if i.pk :

				# Stockage du montant de la facture
				if 'ht' in cle :
					mont_fact = i.mont_ht_fact
				if 'ttc' in cle :
					mont_fact = i.mont_ttc_fact

				nb_fact_ddv = TFacturesDemandeVersement.objects.filter(id_fact = i.pk).count()
				if valeur and nb_fact_ddv > 0 and float(valeur) != mont_fact :
					self.add_error(
						cle,
						'''
						Vous ne pouvez pas modifier le montant {} de la facture car elle est reliée à une demande de
						versement.
						'''.format('TTC' if 'ttc' in cle else 'HT')
					)

	def save(self, commit = True) :

		# Imports
		from app.models import TDossier
		from app.models import TPrestation

		o = super(GererFacture, self).save(commit = False)
		i = self.instance

		if i.pk :
			o.id_doss = i.id_doss
		else :
			o.id_doss = TDossier.objects.get(num_doss = self.cleaned_data.get('za_num_doss'))
		o.id_prest = TPrestation.objects.get(pk = self.cleaned_data.get('zl_prest'))
		o.suivi_fact = self.cleaned_data.get('zl_suivi_fact')
		if commit :
			o.save()

		return o

class GererDemandeVersement(forms.ModelForm) :

	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	zl_fin = forms.ChoiceField(label = 'Partenaire financier', widget = forms.Select())
	cbsm_fact = forms.MultipleChoiceField(
		label = '|'.join([
			'Facture(s) pouvant être reliée(s) à la demande de versement',
			'Prestation',
			'Montant [ht_ou_ttc] (en €)',
			'N° de facture',
			'Date de mandatement par le maître d\'ouvrage',
			'__zcc__'
		]),
		required = False,
		widget = forms.SelectMultiple()
	)

	class Meta :

		# Imports
		from app.models import TDemandeVersement

		exclude = ['fact', 'id_fin']
		fields = '__all__'
		model = TDemandeVersement
		widgets = {
			'dt_ddv' : forms.DateInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_vers_ddv' : forms.DateInput(attrs = { 'input-group-addon' : 'date' }),
			'mont_ht_ddv' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' }),
			'mont_ttc_ddv' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' }),
			'mont_ht_verse_ddv' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' }),
			'mont_ttc_verse_ddv' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' })
		}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont
		from app.models import TDemandeVersement
		from app.models import TFacture
		from app.models import TFacturesDemandeVersement
		from app.models import TFinancement
		from styx.settings import T_DONN_BDD_STR

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		k_doss = kwargs.pop('k_doss', None)
		k_fin = kwargs.pop('k_fin', None)
		k_init = kwargs.pop('k_init', False)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'mont_ht_ddv' : '{:0.2f}'.format(instance.mont_ht_ddv) if instance.mont_ht_ddv else None,
				'mont_ttc_ddv' : '{:0.2f}'.format(instance.mont_ttc_ddv) if instance.mont_ttc_ddv else None,
				'mont_ht_verse_ddv' : '{:0.2f}'.format(
					instance.mont_ht_verse_ddv
				) if instance.mont_ht_verse_ddv else None,
				'mont_ttc_verse_ddv' : '{:0.2f}'.format(
					instance.mont_ttc_verse_ddv
				) if instance.mont_ttc_verse_ddv else None
			})

		super(GererDemandeVersement, self).__init__(*args, **kwargs)
		init_mess_err(self)

		# J'initialise le numéro du dossier par précaution.
		num_doss = None

		i = self.instance
		if i.pk :
			num_doss = i.id_fin.id_doss
		else :
			if k_doss :
				num_doss = k_doss

		# J'affiche le numéro du dossier lié à l'arrêté (ou prochainement lié).
		self.fields['za_num_doss'].initial = num_doss

		if num_doss :
			if num_doss.est_ttc_doss == True :
				self.fields['mont_ttc_ddv'].label += REQUIRED
			else :
				self.fields['mont_ht_ddv'].label += REQUIRED

			# Mise à jour du label (ajout du mode de taxe du dossier)
			split = self.fields['cbsm_fact'].label.split('|')
			split[2] = split[2].replace('[ht_ou_ttc]', 'TTC' if num_doss.est_ttc_doss == True else 'HT')
			self.fields['cbsm_fact'].label = '|'.join(split)

		# J'alimente la liste déroulante des financements du dossier.
		o_doss = num_doss
		if o_doss :
			t_fin = [(f.pk, f.id_org_fin) for f in TFinancement.objects.filter(id_doss = o_doss).order_by(
				'id_org_fin'
			)]
			t_fin.insert(0, DEFAULT_OPTION)
			self.fields['zl_fin'].choices = t_fin

		# Je prépare les valeurs initiales des champs personalisés.
		if i.pk :
			self.fields['zl_fin'].initial = i.id_fin.pk

		# Je gère l'état des champs suivants : numéro de bordereau et numéro de titre de recette.
		ro = False
		if not i.pk :
			ro = True
		else :
			if not i.num_bord_ddv and not i.num_titre_rec_ddv :
				ro = True
		if ro == True :
			self.fields['num_bord_ddv'].widget.attrs['readonly'] = True
			self.fields['num_titre_rec_ddv'].widget.attrs['readonly'] = True

		if k_fin :

			# Déclaration du tableau des choix (initiaux ou non)
			tab_fact_ddv = []
			tab_fact_ddv_checked = []

			for f in TFacture.objects.filter(id_doss = k_fin.id_doss) :

				# Initialisation des cases à cocher
				est_zcc = False
				if TFacturesDemandeVersement.objects.filter(id_ddv__id_fin = k_fin, id_fact = f).count() == 0 :
					est_zcc = True
				if TFacturesDemandeVersement.objects.filter(
					id_ddv = i, id_ddv__id_fin = k_fin, id_fact = f
				).count() == 1 :
					est_zcc = True
					tab_fact_ddv_checked.append(f.pk)

				# Stockage des avances
				qsDev = TDemandeVersement.objects.filter(
					id_fin=k_fin.pk,
					id_type_vers__int_type_vers='Avance forfaitaire'
				)
				if qsDev.count() > 0:
					avances = sum([
						oDev.mont_ttc_ddv \
						if k_fin.id_doss.est_ttc_doss == True \
						else oDev.mont_ht_ddv\
						for oDev in qsDev
					])
				else:
					avances = 0

				# Préparation du tableau des factures
				tab_fact_ddv.append([f.pk, '|'.join([
					str(f.id_prest),
					obt_mont(f.mont_ttc_fact) if k_fin.id_doss.est_ttc_doss == True else obt_mont(f.mont_ht_fact),
					f.num_fact,
					dt_fr(f.dt_mand_moa_fact) or '-',
					'__zcc__$montant:{}$pourcentage:{}$taxe:{}$avances:{}'.format(
						f.mont_ttc_fact or '' if k_fin.id_doss.est_ttc_doss == True else f.mont_ht_fact or '',
						k_fin.pourc_elig_fin or '',
						'TTC' if k_fin.id_doss.est_ttc_doss == True else 'HT',
						avances
					) if est_zcc == True else ''
				])])

			# Destruction des tableaux en cas d'avance forfaitaire
			if i.pk and i.id_type_vers.int_type_vers == T_DONN_BDD_STR['TVERS_AF'] and k_init == True :
				tab_fact_ddv = []
				tab_fact_ddv_checked = []

			# ALimentation du champ lié au tableau des factures
			self.fields['cbsm_fact'].choices = tab_fact_ddv
			self.fields['cbsm_fact'].initial = tab_fact_ddv_checked

	def clean(self) :

		# Imports
		from app.functions import obt_mont
		from app.models import TDemandeVersement
		from app.models import TDossier
		from app.models import VFinancement
		from styx.settings import T_DONN_BDD_STR

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererDemandeVersement, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_fin = cleaned_data.get('zl_fin')
		v_type_vers = cleaned_data.get('id_type_vers')

		i = self.instance

		# Je vérifie l'existence d'un objet TDossier.
		try :
			if i.pk :
				o_doss = i.id_fin.id_doss
			else :
				o_doss = TDossier.objects.get(num_doss = v_num_doss)
		except :
			o_doss = None
			self.add_error('za_num_doss', 'Le dossier {0} n\'existe pas.'.format(v_num_doss))

		if v_fin :
			o_suivi_fin = VFinancement.objects.get(id_fin = v_fin)
		else :
			o_suivi_fin = None

		if o_doss and o_suivi_fin :

			# Je stocke la clé et la valeur du contrôle relatif au montant HT ou TTC de la demande de versement.
			cle = 'mont_ht_ddv'
			if o_suivi_fin.id_doss.est_ttc_doss == True :
				cle = 'mont_ttc_ddv'
			valeur = cleaned_data.get(cle)

			# Je gère la contrainte suivante : le montant de la demande de versement ne doit pas être supérieur au
			# reste à demander du financement.
			mont_rad = o_suivi_fin.mont_rad
			if i.pk and o_suivi_fin.id_fin.pk == i.id_fin.pk :
				if 'ht' in cle :
					mont_rad += i.mont_ht_ddv
				if 'ttc' in cle :
					mont_rad += i.mont_ttc_ddv
			if valeur :
				if float(valeur) > float(mont_rad) :
					self.add_error(
						cle,
						'Veuillez saisir un montant inférieur ou égal à {0} €.'.format(obt_mont(mont_rad))
					)
			else :
				self.add_error(cle, ERROR_MESSAGES['required'])

			# Je récupère les demandes de versements soldées du financement.
			qs_ddv = TDemandeVersement.objects.filter(
				id_fin = o_suivi_fin.id_fin.pk,
				id_type_vers__int_type_vers = T_DONN_BDD_STR['TVERS_SOLDE']
			)

			# Je renvoie une erreur si un financement admet déjà une demande de versement soldée.
			err = False
			if v_type_vers :
				if not i.pk :
					if len(qs_ddv) > 0 :
						err = True
				else :
					qs_ddv = qs_ddv.exclude(pk = i.pk)
					if len(qs_ddv) > 0 and v_type_vers.int_type_vers == T_DONN_BDD_STR['TVERS_SOLDE'] :
						err = True
				if err == True :
					self.add_error(
						'id_type_vers', 'Vous avez déjà émis une demande de versement soldée pour ce financeur.'
					)

	def save(self, commit = True) :

		# Imports
		from app.models import TFinancement

		o = super(GererDemandeVersement, self).save(commit = False)
		i = self.instance

		o.id_fin = TFinancement.objects.get(pk = self.cleaned_data.get('zl_fin'))
		if commit :
			o.save()

		return o

class GererArrete(forms.ModelForm) :

	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	zl_type_decl = forms.ChoiceField(label = 'Type de déclaration', widget = forms.Select())

	class Meta :

		# Imports
		from app.models import TArretesDossier

		exclude = ['id_doss', 'id_type_decl']
		fields = '__all__'
		model = TArretesDossier
		widgets = {
			'dt_lim_encl_trav_arr' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }),
			'dt_sign_arr' : forms.TextInput(attrs = { 'input-group-addon' : 'date' })
		}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr
		from app.models import TArretesDossier
		from app.models import TTypeDeclaration

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		k_doss = kwargs.pop('k_doss', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'dt_lim_encl_trav_arr' : dt_fr(
					instance.dt_lim_encl_trav_arr
				) if instance.dt_lim_encl_trav_arr else None,
				'dt_sign_arr' : dt_fr(instance.dt_sign_arr) if instance.dt_sign_arr else None
			})

		super(GererArrete, self).__init__(*args, **kwargs)
		init_mess_err(self)
		self.fields['num_arr'].label += MAY_BE_REQUIRED
		self.fields['dt_sign_arr'].label += MAY_BE_REQUIRED
		self.fields['dt_lim_encl_trav_arr'].label += MAY_BE_REQUIRED
		self.fields['chem_pj_arr'].label += MAY_BE_REQUIRED

		# J'initialise le numéro du dossier par précaution.
		num_doss = None

		i = self.instance
		if i.pk :
			num_doss = i.id_doss
		else :
			if k_doss :
				num_doss = k_doss

		# J'affiche le numéro du dossier lié à l'arrêté (ou prochainement lié).
		self.fields['za_num_doss'].initial = num_doss

		# J'alimente la liste déroulante des types de déclarations.
		if not i.pk :
			t_type_decl = [(td.pk, td) for td in TTypeDeclaration.objects.exclude(
				pk__in = TArretesDossier.objects.filter(id_doss = num_doss).values_list('id_type_decl', flat = True)
			)]
			t_type_decl.insert(0, DEFAULT_OPTION)
		else :
			t_type_decl = [(i.id_type_decl.pk, i.id_type_decl)]
		self.fields['zl_type_decl'].choices = t_type_decl

	def clean(self) :

		# Imports
		from app.models import TArretesDossier
		from app.models import TDossier
		from styx.settings import T_DONN_BDD_STR

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererArrete, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_type_decl = cleaned_data.get('zl_type_decl')
		v_type_av_arr = cleaned_data.get('id_type_av_arr')
		v_num_arr = cleaned_data.get('num_arr')
		v_dt_sign_arr = cleaned_data.get('dt_sign_arr')
		v_dt_lim_encl_trav_arr = cleaned_data.get('dt_lim_encl_trav_arr')
		v_chem_pj_arr = cleaned_data.get('chem_pj_arr')

		i = self.instance

		# Je vérifie l'existence d'un objet TDossier.
		try :
			if i.pk :
				o_doss = i.id_doss
			else :
				o_doss = TDossier.objects.get(num_doss = v_num_doss)
		except :
			o_doss = None
			self.add_error('za_num_doss', 'Le dossier {0} n\'existe pas.'.format(v_num_doss))

		if o_doss :

			# Je rends certains champs obligatoires si et seulement si l'avancement de l'arrêté est "Validé".
			if v_type_av_arr and v_type_av_arr.int_type_av_arr == T_DONN_BDD_STR['TAV_ARR_VALIDE'] :
				if not v_num_arr :
					self.add_error('num_arr', ERROR_MESSAGES['required'])
				if not v_dt_sign_arr :
					self.add_error('dt_sign_arr', ERROR_MESSAGES['required'])
				if not v_dt_lim_encl_trav_arr :
					self.add_error('dt_lim_encl_trav_arr', ERROR_MESSAGES['required'])
				if not v_chem_pj_arr :
					self.add_error('chem_pj_arr', ERROR_MESSAGES['required'])

			# Je renvoie une erreur si un type de déclaration déjà déclare pour un dossier essaie d'être à nouveau
			# déclaré.
			if not i.pk and v_type_decl :
				if len(TArretesDossier.objects.filter(id_doss = o_doss, id_type_decl = v_type_decl)) > 0 :
					self.add_error('zl_type_decl', ERROR_MESSAGES['invalid'])

	def save(self, commit = True) :

		# Imports
		from app.models import TDossier
		from app.models import TTypeDeclaration

		o = super(GererArrete, self).save(commit = False)
		i = self.instance

		if i.pk :
			o.id_doss = i.id_doss
		else :
			o.id_doss = TDossier.objects.get(num_doss = self.cleaned_data.get('za_num_doss'))
		o.id_type_decl = TTypeDeclaration.objects.get(pk = self.cleaned_data.get('zl_type_decl'))
		if commit :
			o.save()

		return o

class GererDossier_Reglementations(forms.ModelForm) :

	class Meta :

		# Imports
		from app.models import TDossier

		fields = ['comm_regl_doss']
		model = TDossier

class GererPhoto(forms.ModelForm) :

	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)

	class Meta :

		# Imports
		from app.models import TPhoto

		exclude = ['id_doss']
		fields = '__all__'
		model = TPhoto
		widgets = { 'dt_pv_ph' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }) }

	def __init__(self, *args, **kwargs) :

		# Je déclare le tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)

		super(GererPhoto, self).__init__(*args, **kwargs)
		init_mess_err(self)

		i = self.instance
		if not i.pk :
			self.fields['za_num_doss'].initial = k_doss
		else :
			self.fields['za_num_doss'].initial = i.id_doss

	def clean(self) :

		# Imports
		from app.models import TDossier

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererPhoto, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')

		# Je vérifie l'existence d'un objet TDossier.
		if not self.instance.pk :
			try :
				TDossier.objects.get(num_doss = v_num_doss)
			except :
				self.add_error('za_num_doss', 'Le dossier n\'existe pas.')

	def save(self, commit = True) :

		# Imports
		from app.models import TDossier

		o = super(GererPhoto, self).save(commit = False)
		i = self.instance
		if i.pk :
			o.id_doss = i.id_doss
		else :
			o.id_doss = TDossier.objects.get(num_doss = self.cleaned_data.get('za_num_doss'))
		if commit :
			o.save()

		return o

class GererAvenant(forms.ModelForm) :

	za_num_doss = forms.CharField(label = 'Numéro du dossier', widget = forms.TextInput(attrs = { 'readonly' : True }))
	zl_prest = forms.ChoiceField(label = 'Prestation', widget = forms.Select())

	class Meta :

		# Imports
		from app.models import TAvenant

		exclude = ['id_doss', 'id_prest', 'num_aven']
		fields = '__all__'
		model = TAvenant
		widgets = {
			'dt_aven' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }),
			'mont_aven' : forms.NumberInput(attrs = { 'input-group-addon' : 'euro' })
		}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		k_prest_doss = kwargs.pop('k_prest_doss', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'dt_aven' : dt_fr(instance.dt_aven),
				'mont_aven' : '{:0.2f}'.format(instance.mont_aven) if instance.mont_aven else None
			})

		super(GererAvenant, self).__init__(*args, **kwargs)
		init_mess_err(self)
		self.fields['dt_aven'].label += MAY_BE_REQUIRED
		self.fields['mont_aven'].label += MAY_BE_REQUIRED

		# J'initialise certaines variables par précaution.
		num_doss = None
		prest = None
		ht_ou_ttc = 'HT'

		i = self.instance
		if i.pk :
			num_doss = i.id_doss
			prest = i.id_prest
			if i.id_doss.est_ttc_doss == True :
				ht_ou_ttc = 'TTC'
		else :
			if k_prest_doss :
				num_doss = k_prest_doss.id_doss
				prest = k_prest_doss.id_prest
				if k_prest_doss.id_doss.est_ttc_doss == True :
					ht_ou_ttc = 'TTC'

		# J'affiche le numéro du dossier ainsi que la prestation liés à l'avenant (ou prochainement liés).
		self.fields['za_num_doss'].initial = num_doss
		if prest :
			self.fields['zl_prest'].choices = [(prest.pk, prest)]

		# Je complète le label de chaque champ demandant un montant.
		lab_mont_aven = self.fields['mont_aven'].label.replace('[ht_ou_ttc]', ht_ou_ttc)
		self.fields['mont_aven'].label = lab_mont_aven

	def clean(self) :

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont
		from app.models import TAvenant
		from app.models import TPrestationsDossier
		from app.models import VSuiviDossier
		from app.models import VSuiviPrestationsDossier
		from django.db.models import Max

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererAvenant, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_prest = cleaned_data.get('zl_prest')
		v_dt_aven = cleaned_data.get('dt_aven')
		v_mont_aven = cleaned_data.get('mont_aven')

		i = self.instance

		# Je vérifie l'existence d'un objet TPrestationsDossier.
		try :
			if i.pk :
				o_prest_doss = TPrestationsDossier.objects.get(id_doss = i.id_doss, id_prest = i.id_prest)
			else :
				o_prest_doss = TPrestationsDossier.objects.get(id_doss__num_doss = v_num_doss, id_prest = v_prest)
			o_suivi_doss = VSuiviDossier.objects.get(pk = o_prest_doss.id_doss.pk)
		except :
			o_prest_doss = None
			o_suivi_doss = None
			self.add_error('__all__', 'Le couple prestation/dossier est invalide.')

		if o_prest_doss and o_suivi_doss :

			if not v_dt_aven and not v_mont_aven :
				self.add_error('__all__', 'Veuillez renseigner au minimum une date ou un montant strictement positif.')

			# Je gère le bon renseignement de la date de fin de l'avenant.
			if v_dt_aven :
				if i.pk :

					# Stockage du numéro de l'avenant
					v_num_aven = i.num_aven

					# Obtention de l'avenant de date i-1 et i+1
					qs_aven_dt = TAvenant.objects.filter(
						id_doss = o_prest_doss.id_doss, id_prest = o_prest_doss.id_prest
					).exclude(dt_aven = None)
					obj_aven_min = qs_aven_dt.filter(num_aven__lt = v_num_aven).last()
					obj_aven_max = qs_aven_dt.filter(num_aven__gt = v_num_aven).first()

					# Définition de la date minimale d'un avenant
					if obj_aven_min :
						v_dt_aven_min = obj_aven_min.dt_aven
					else :
						v_dt_aven_min = o_prest_doss.id_prest.dt_fin_prest or None

					# Définition de la date maximale d'un avenant
					if obj_aven_max :
						v_dt_aven_max = obj_aven_max.dt_aven
					else :
						v_dt_aven_max = None

					# Vérification du champ "date"
					erreur = False
					if v_dt_aven_min and v_dt_aven < v_dt_aven_min :
						erreur = True
					if v_dt_aven_max and v_dt_aven > v_dt_aven_max :
						erreur = True

					# Définition du message d'erreur
					if erreur == True :
						if v_dt_aven_min and v_dt_aven_max :
							if v_dt_aven_min == v_dt_aven_max :
								mess = 'La date de fin de l\'avenant est obligatoirement le {0}.'.format(v_dt_aven_min)
							else :
								mess = '''
								La date de fin de l'avenant doit être comprise entre le {0} et le {1}.
								'''.format(dt_fr(v_dt_aven_min), dt_fr(v_dt_aven_max))
						elif v_dt_aven_min and not v_dt_aven_max :
							mess = '''
							La date de fin de l'avenant doit être postérieure ou égale au {0}.
							'''.format(dt_fr(v_dt_aven_min))
						elif not v_dt_aven_min and v_dt_aven_max :
							mess = '''
							La date de fin de l'avenant doit être antérieure ou égale au {0}.
							'''.format(dt_fr(v_dt_aven_max))
						self.add_error('dt_aven', mess)

				else :

					# Je récupère la date minimale d'un avenant.
					dt_aven_max = TAvenant.objects.filter(
						id_doss = o_prest_doss.id_doss, id_prest = o_prest_doss.id_prest
					).aggregate(Max('dt_aven'))['dt_aven__max'] or o_prest_doss.id_prest.dt_fin_prest

					# Je renvoie une erreur si la date de fin de l'avenant n'est pas conforme.
					if dt_aven_max and v_dt_aven < dt_aven_max :
						self.add_error(
							'dt_aven',
							'La date de fin de l\'avenant doit être postérieure ou égale au {0}.'.format(dt_fr(dt_aven_max))
						)

			# Vérification du champ "montant"
			erreur = False

			# Stockage du montant de l'avenant souhaité
			v_mont_aven = v_mont_aven or 0

			# Calcul du reste à engager du dossier
			mont_rae = o_suivi_doss.mont_rae
			if i.pk and i.mont_aven :
				mont_rae += i.mont_aven

			# Erreur si le montant de l'avenant est supérieur au reste à engager du dossier
			if float(v_mont_aven) > mont_rae :
				erreur = True

			# Erreur si le montant de l'avenant entraîne un reste à facturer négatif
			mont_aven_min = 0
			o_suivi_prest_doss = VSuiviPrestationsDossier.objects.get(pk = o_prest_doss.pk)
			if i.pk and i.mont_aven and i.mont_aven > o_suivi_prest_doss.mont_raf :
				mont_aven_min = abs(o_suivi_prest_doss.mont_raf - i.mont_aven)
				if v_mont_aven < mont_aven_min :
					erreur = True

			# Définition du message d'erreur
			tab_bornes_mont_aven = [mont_aven_min, mont_rae]
			if erreur == True :
				mess = '''
				Le montant de l'avenant est obligatoirement de {0} €.
				'''.format(obt_mont(tab_bornes_mont_aven[0]))
				if tab_bornes_mont_aven[0] and tab_bornes_mont_aven[1] :
					if tab_bornes_mont_aven[0] == tab_bornes_mont_aven[1] :
						mess = '''
						Le montant de l'avenant est obligatoirement de {0} €.
						'''.format(obt_mont(tab_bornes_mont_aven[0]))
					else :
						mess = '''
						Le montant de l'avenant doit être compris entre {0} € et {1} €.
						'''.format(obt_mont(tab_bornes_mont_aven[0]), obt_mont(tab_bornes_mont_aven[1]))
				elif tab_bornes_mont_aven[0] and not tab_bornes_mont_aven[1] :
					mess = '''
					Le montant de l'avenant doit être supérieur ou égal à {0} €.
					'''.format(obt_mont(tab_bornes_mont_aven[0]))
				elif not tab_bornes_mont_aven[0] and tab_bornes_mont_aven[1] :
					mess = '''
					Le montant de l'avenant doit être inférieur ou égal à {0} €.
					'''.format(obt_mont(tab_bornes_mont_aven[1]))
				self.add_error('mont_aven', mess)

	def save(self, commit = True) :

		# Imports
		from app.models import TPrestationsDossier

		o = super(GererAvenant, self).save(commit = False)
		i = self.instance
		if i.pk :
			o.id_doss = i.id_doss
			o.id_prest = i.id_prest
		else :
			o_prest_doss = TPrestationsDossier.objects.get(
				id_doss__num_doss = self.cleaned_data.get('za_num_doss'), id_prest = self.cleaned_data.get('zl_prest')
			)
			o.id_doss = o_prest_doss.id_doss
			o.id_prest = o_prest_doss.id_prest
		if commit :
			o.save()

		return o

class AjouterPrestataire(forms.ModelForm) :

	class Meta :

		# Imports
		from app.models import TPrestataire

		fields = ['comm_org', 'n_org', 'num_dep', 'siret_org_prest']
		model = TPrestataire

	def __init__(self, *args, **kwargs) :

		super(AjouterPrestataire, self).__init__(*args, **kwargs)
		init_mess_err(self)

class GererFicheVie(forms.ModelForm) :

	# Champs
	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)

	class Meta :

		# Imports
		from app.models import TFicheVie

		fields = ['comm_fdv', 'd_fdv', 'lib_fdv', 'chem_pj_fdv']
		model = TFicheVie
		widgets = { 'd_fdv' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }) }

	# Méthodes publiques

	def get_form(self, rq) :

		'''Mise en forme du formulaire'''

		# Imports
		from app.functions import init_f
		from django.template.context_processors import csrf

		form = init_f(self) # Initialisation des contrôles

		# Définition du conteni du formulaire
		content = '''
		{}
		<div class="row">
			<div class="col-sm-6">{}</div>
			<div class="col-sm-6">{}</div>
		</div>
		{}
		{}
		<button class="center-block green-btn my-btn" type="submit">Valider</button>
		'''.format(
			form['za_num_doss'],
			form['lib_fdv'],
			form['d_fdv'],
			form['comm_fdv'],
			form['chem_pj_fdv']
		)

		return '''
		<form action="{}" name="f_gerfdv" enctype="multipart/form-data" method="post" onsubmit="soum_f(event)">
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			{}
		</form>
		'''.format(
			'' if self.instance.pk else '?action=ajouter-fdv',
			csrf(rq)['csrf_token'],
			'''
			<fieldset class="my-fieldset">
				<legend>Modifier un événement</legend>
				<div>{}</div>
			</fieldset>
			'''.format(content) if self.instance.pk else content
		)

	# Méthodes système

	def __init__(self, *args, **kwargs) :
		self.k_doss = kwargs.pop('k_doss') # Définition des arguments
		super().__init__(*args, **kwargs)
		init_mess_err(self) # Définition des messages d'erreurs personnalisés

		# Définition de la valeur initiale du champ "za_num_doss"
		self.fields['za_num_doss'].initial = self.k_doss.num_doss

	def save(self, commit = True) :
		fdv = super().save(commit = False)
		fdv.id_doss = self.k_doss # Définition du dossier
		if commit : fdv.save()
		return fdv


class PrintDoss(forms.Form):
	caracteristiques = forms.BooleanField(label='Caractéristiques', initial=True, required=False)
	av_doss = forms.BooleanField(label='Avancement du dossier', initial=True, required=False)
	fiche_vie = forms.BooleanField(label='Fiche de vie', initial=True, required=False)
	plan_fnc = forms.BooleanField(label='Plan de financement', initial=True, required=False)
	prestation = forms.BooleanField(label='Prestations', initial=True, required=False)
	facture = forms.BooleanField(label='Factures', initial=True, required=False)
	versement = forms.BooleanField(label='Demandes de versements', initial=True, required=False)

class GererOrdreService(forms.ModelForm) :

	# Champs
	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	za_num_os = forms.CharField(
		label='Numéro de l\'ordre de service',
		required=False,
		widget=forms.TextInput(attrs={'readonly': True})
	)

	class Meta :

		# Imports
		from app.models import TOrdreService

		fields = ['comm_os', 'd_emiss_os', 'duree_w_os', 'obj_os', 'id_prest', 'id_type_os']
		model = TOrdreService
		widgets = { 'd_emiss_os' : forms.TextInput(attrs = { 'input-group-addon' : 'date' }) }

	# Méthodes privées

	def __get_pd(self) :
		from app.models import TPrestationsDossier
		return self.k_pd or TPrestationsDossier.objects.get(
			id_doss = self.instance.id_doss, id_prest = self.instance.id_prest
		)

	# Méthodes publiques

	def get_form(self, rq, racc = False) :

		'''Mise en forme du formulaire'''

		# Imports
		from app.functions import init_f
		from django.core.urlresolvers import reverse
		from django.template.context_processors import csrf

		form = init_f(self) # Initialisation des contrôles

		# Définition du contenu du formulaire
		content = '''
		<div class="row">
			<div class="col-sm-6">{}</div>
			<div class="col-sm-6">{}</div>
		</div>
		{}
		<div class="row">
			<div class="col-sm-6">{}</div>
			<div class="col-sm-6">{}</div>
		</div>
		{}
		{}
		{}
		<button class="center-block green-btn my-btn" type="submit">Valider</button>
		'''.format(
			form['za_num_doss'],
			form['id_prest'],
			form['za_num_os'] if self.instance.pk else '',
			form['id_type_os'],
			form['d_emiss_os'],
			form['obj_os'],
			form['duree_w_os'],
			form['comm_os']
		)

		return '''
		<form action="{}" name="f_geros" method="post" onsubmit="soum_f(event)">
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			{}
		</form>
		'''.format(
			reverse('modif_os', args = [self.instance.pk]) if self.instance.pk else reverse(
				'ajout_os_racc' if racc else 'ajout_os', args = [self.__get_pd().pk]
			),
			csrf(rq)['csrf_token'],
			'''
			<fieldset class="my-fieldset">
				<legend>Modifier un ordre de service</legend>
				<div>{}</div>
			</fieldset>
			'''.format(content) if self.instance.pk else content
		)

	# Méthodes système

	def __init__(self, *args, **kwargs) :
		self.k_pd = kwargs.pop('k_pd', None) # Définition des arguments
		super().__init__(*args, **kwargs)
		init_mess_err(self) # Définition des messages d'erreurs personnalisés

		# Définition de la valeur initiale du champ "za_num_doss"
		self.fields['za_num_doss'].initial = self.__get_pd().id_doss.num_doss

		# Définition de la valeur initiale du champ "za_num_os"
		if self.instance.pk:
			self.fields['za_num_os'].initial = self.instance.num_os

		# Redéfinition du champ "id_prest"
		self.fields['id_prest'].empty_label = None
		self.fields['id_prest'].queryset = self.fields['id_prest'].queryset.filter(pk = self.__get_pd().id_prest.pk)

	def clean(self) :

		# Initialisation des erreurs
		errors = {}

		# Récupération des données du formulaire
		cleaned_data = super().clean()
		val_duree_w_os = cleaned_data.get('duree_w_os')
		val_id_type_os = cleaned_data.get('id_type_os')

		if (val_duree_w_os) \
		and (val_id_type_os) \
		and (not val_id_type_os.nom_type_os.startswith(('Arrêt', 'Fin'))) :
			errors['duree_w_os'] = '''
			La valeur ne peut être strictement positive que pour un OS d'arrêt ou de fin de mission.
			'''

		# Ajout des erreurs
		for key, val in errors.items() : self.add_error(key, val)

	def save(self, commit=True):

		# Imports
		from app.models import TPrestationsDossier

		# Définition du type de requête (INSERT ou UPDATE)
		if self.instance.pk:
			is_create_mode = False
		else:
			is_create_mode = True

		# Pré-enregistrement d'un objet TOrdreService
		os = super().save(commit=False)

		# Définition du dossier
		os.id_doss = self.__get_pd().id_doss

		# Si type de requête INSERT, alors...
		if is_create_mode:

			# Définition du numéro de l'OS
			os.num_os = self.__get_pd().seq_os_prest_doss

			# Mise à jour du séquentiel OS
			self.__get_pd().seq_os_prest_doss += 1
			self.__get_pd().save()

		# Enregistrement d'un objet TOrdreService
		if commit:
			os.save()

		return os

class GererDdsCdg(forms.ModelForm) :

	class Meta :

		# Imports
		from app.models import TDdsCdg

		fields = ['cdg_id']
		model = TDdsCdg

	# Méthodes publiques

	def get_form(self, rq) :

		'''Mise en forme du formulaire'''

		# Imports
		from app.functions import init_f
		from django.core.urlresolvers import reverse
		from django.template.context_processors import csrf

		# Initialisation des contrôles
		form = init_f(self)

		return '''
		<form action="{}" name="f_ajout_ddscdg" method="post" onsubmit="soum_f(event)">
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			{}
			<button class="center-block green-btn my-btn" type="submit">Valider</button>
		</form>
		'''.format(
			reverse('ajout_ddscdg', args=[self.dds.pk]),
			csrf(rq)['csrf_token'],
			form['cdg_id']
		)

	# Méthodes Django

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import dt_fr
		from app.models import TCDGemapiCdg
		from app.models import TDdsCdg
		from datetime import date

		# Initialisation des arguments
		self.dds = kwargs.pop('kwarg_dds')

		super().__init__(*args, **kwargs)

		# Définition des messages d'erreurs personnalisés
		init_mess_err(self)

		# Récupération du champ "cdg_id"
		cdg_id = self.fields['cdg_id']

		# Récupération du CD GEMAPI le plus proche de la date du jour
		oCdg = TCDGemapiCdg.objects \
			.filter(cdg_date__gte=date.today()) \
			.exclude(pk__in=TDdsCdg.objects \
				.filter(dds_id=self.dds.pk) \
				.values_list('cdg_id', flat=True)
			) \
			.order_by('cdg_date') \
			.first()

		# Initialisation des arguments du champ surchargé "cdg_id"
		cdg_id_kwargs = {
			'initial': oCdg.pk if oCdg else None,
			'label': cdg_id.label,
			'required': cdg_id.required
		}

		# Initialisation du tableau des options possibles pour le champ
		# surchargé "cdg_id"
		cdg_id_choices = []
		# Pour chaque année...
		for date in TCDGemapiCdg.objects \
			.filter(cdg_date__gte=date.today()) \
			.dates('cdg_date', 'year', order='DESC'):
			# Récupération des dates dont le dossier peut être présenté
			qsCdgs = TCDGemapiCdg.objects \
				.filter(
					cdg_date__gte=date.today(),
					cdg_date__year=date.year
				) \
				.exclude(pk__in=TDdsCdg.objects \
					.filter(dds_id=self.dds.pk) \
					.values_list('cdg_id', flat=True)
				) \
				.order_by('cdg_date')
			# Si une date au minimum est repérée, alors...
			if qsCdgs.exists():
				# Initialisation des dates relatives à l'année
				cdgs = []
				# Pour chaque date...
				for iCdg in qsCdgs:
					# Empilement des dates relatives à l'année
					cdg = [iCdg.pk, dt_fr(iCdg.cdg_date)]
					cdgs.append(cdg)
				# Empilement du tableau des options possibles pour le
				# champ surchargé "cdg_id"
				cdg_id_choices.append([date.year, cdgs])
		# Insertion d'une option nulle
		cdg_id_choices.insert(0, [u'', '---------'])
		# Empilement des arguments du champ surchargé "cdg_id"
		cdg_id_kwargs['choices'] = cdg_id_choices

		# Redéfinition du champ "cdg_id"
		self.fields['cdg_id'] = forms.ChoiceField(**cdg_id_kwargs)

	def clean_cdg_id(self):

		# Imports
		from app.models import TCDGemapiCdg

		# Récupération de la valeur du champ surchargé "cdg_id"
		cdg_id = self.cleaned_data['cdg_id'] or None

		return TCDGemapiCdg.objects.filter(pk=cdg_id).first()

	def save(self, commit=True) :
		ddscdg = super().save(commit=False)
		ddscdg.dds_id = self.dds # Définition du dossier
		if commit:
			ddscdg.save()
		return ddscdg

class ManagePpi(forms.ModelForm):

	# Imports
	from app.classes.FFEuroField import Class as FFEuroField

	# Champs

	za_num_doss = forms.CharField(
		label='Numéro du dossier',
		required=False,
		widget=forms.TextInput(attrs={'readonly': True})
	)

	za_mont_ttc_tot_doss = forms.CharField(
		label='Montant TTC total du dossier (en €)',
		required=False,
		widget=forms.TextInput(attrs={'readonly': True})
	)

	za_mont_part_fin_sum = forms.CharField(
		label='Montant [ht_ou_ttc] total des subventions du dossier (en €)',
		required=False,
		widget=forms.TextInput(attrs={'readonly': True})
	)

	class Meta:

		# Imports
		from app.models import TPlanPluriannuelInvestissementPpi

		exclude = ['dds_id']
		model = TPlanPluriannuelInvestissementPpi
		widgets = {
			'ppi_budget_an_dps_ttc': forms.NumberInput(attrs={'input-group-addon': 'euro'}),
			'ppi_budget_an_vsm_previ': forms.NumberInput(attrs={'input-group-addon': 'euro'}),
			'ppi_real_an_pcdt_dps_ttc': forms.NumberInput(attrs={'input-group-addon': 'euro'}),
			'ppi_real_an_pcdt_vsm_previ': forms.NumberInput(attrs={'input-group-addon': 'euro'})
		}

	# Méthodes Django

	def __init__(self, *args, **kwargs):

		# Imports
		from app.functions import obt_mont

		# Variables globales
		self.iDds = kwargs.pop('kwarg_dds', None)
		self.rq = kwargs.pop('kwarg_rq', None)

		super().__init__(*args, **kwargs)

		# -------------------------------------------------------------
		# Méthodes locales
		# -------------------------------------------------------------

		def get_papFormset(self):

			"""
			Instanciation/soumission d'un objet formulaire groupé
			ManagePapFormSet
			"""

			# Imports
			from app.classes import FormSet

			# Gestion de l'attribut "initial"
			if self.instance.pk:
				initial = [{
					'pap_an': iPap.pap_an,
					'pap_dps_eli_fctva': iPap.pap_dps_eli_fctva,
					'pap_dps_ttc_rp': iPap.pap_dps_ttc_rp,
					'pap_vsm_previ_rp': iPap.pap_vsm_previ_rp
				} for iPap in self.instance \
					.tprospectiveannuelleppipap_set \
					.all()]
			else:
				initial = []

			return FormSet(
				columns=[
					'pap_an',
					'pap_dps_ttc_rp',
					'pap_vsm_previ_rp',
					'pap_dps_eli_fctva'
				],
				form=ManagePap,
				formset=ManagePapFormSet,
				label='',
				name='pap',
				rq=self.rq,
				formset_kwargs={'initial': initial}
			)

		# -------------------------------------------------------------

		# Variables globales
		self.papFormset = get_papFormset(self=self)

		# Définition des messages d'erreurs personnalisés
		init_mess_err(self)

		# Définition de la valeur initiale des champs non-issus du
		# modèle
		self.fields['za_num_doss'].initial = self.iDds.num_doss
		self.fields['za_mont_ttc_tot_doss'].initial \
			= obt_mont(self.iDds.get_view_object().mont_ttc_tot_doss)
		self.fields['za_mont_part_fin_sum'].initial \
			= obt_mont(self.iDds.get_view_object().mont_part_fin_sum)

		self.fields['za_mont_part_fin_sum'].label \
			= self.fields['za_mont_part_fin_sum'].label.replace(
				'[ht_ou_ttc]', self.iDds.get_view_object().type_mont_doss
			)

	def clean_ppi_an(self):

		# Imports
		from django.core.exceptions import ValidationError

		# Récupération de l'année renseignée
		ppi_an = self.cleaned_data['ppi_an']

		# CAS DE FIGURE : ajout d'un PPI
		if not self.instance.pk:
			# Renvoi d'une erreur si un PPI a déjà été renseigné pour
			# l'année renseignée
			if self.iDds \
				.tplanpluriannuelinvestissementppi_set \
				.filter(ppi_an=ppi_an) \
				.exists():
				raise ValidationError(
					'''
					Un PPI a déjà été renseigné pour l'année {}.
					'''.format(ppi_an)
				)

		return ppi_an

	def save(self, commit=True):

		# Pré-enregistrement
		iPpi = super().save(commit=False)

		# Définition du dossier
		iPpi.dds_id = self.iDds

		# Enregistrement
		if commit:
			iPpi.save()
			self.papFormset.save(iPpi=iPpi)

		return iPpi

	# Méthodes privées

	def __get_errors(self):

		"""
		Récupération des erreurs de formulaire
		"""

		# Initialisation des erreurs
		errors = {}

		# Si le formulaire est invalide, alors empilement des erreurs
		if not self.is_valid():
			errors.update(self.errors)

		# Empilement des erreurs (formulaire groupé)
		errors.update(self.papFormset.get_errors())

		return errors

	def __get_form(self, rq, has_fieldset):

		"""
		Mise en forme du formulaire
		"""

		# Imports
		from app.functions import init_f
		from django.core.urlresolvers import reverse
		from django.template.context_processors import csrf

		# Initialisation des contrôles
		form = init_f(self)

		# Récupération du couple formulaire groupé/formulaire vierge
		formset, empty_form = self.papFormset.display_formset()

		# Mise en forme du contenu du formulaire
		inner_form = '''
		{}
		<div class="row">
			<div class="col-sm-6">{}</div>
			<div class="col-sm-6">{}</div>
		</div>
		{}
		<div class="title-1">Réalisé au 31/12 de l'année précédente du PPI hors RAR</div>
		<div class="row">
			<div class="col-sm-6">{}</div>
			<div class="col-sm-6">{}</div>
		</div>
		<div class="title-1">Budget de l'année du PPI (RAR + nouvelles propositions)</div>
		<div class="row">
			<div class="col-sm-6">{}</div>
			<div class="col-sm-6">{}</div>
		</div>
		<div class="title-1">Prospective annuelle</div>
		{}
		<div class="title-1">Autres</div>
		{}
		<button
			class="center-block green-btn my-btn"
			type="submit"
		>Valider</button>
		'''.format(
			form['za_num_doss'],
			form['za_mont_ttc_tot_doss'],
			form['za_mont_part_fin_sum'],
			form['ppi_an'],
			form['ppi_real_an_pcdt_dps_ttc'],
			form['ppi_real_an_pcdt_vsm_previ'],
			form['ppi_budget_an_dps_ttc'],
			form['ppi_budget_an_vsm_previ'],
			formset,
			form['ppi_ntr_dps']
		)

		# Intégration d'une balise <fieldset/> si besoin
		if has_fieldset:
			inner_form = '''
			<fieldset class="my-fieldset">
				<legend>Mettre à jour un PPI</legend>
				<div>{}</div>
			</fieldset>
			'''.format(inner_form)

		return '''
		<form
			action="{}"
			method="post"
			name="f_manppi"
			onsubmit="soum_f(event)"
		>
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			{}
		</form>
		{}
		'''.format(
			(reverse('insppi') + '?dds=' + str(self.iDds.pk)) if not self.instance.pk else '',
			csrf(self.rq)['csrf_token'],
			inner_form,
			empty_form
		)

	# Méthodes publiques

	def get_errors(self):
		"""
		Récupération des erreurs de formulaire
		"""
		return self.__get_errors()

	def get_form(self, has_fieldset=False):
		"""
		Mise en forme du formulaire
		"""
		return self.__get_form(self, has_fieldset)

class ManagePapFormSet(BaseFormSet):

	"""
	Formulaire groupé de gestion des instances TProspectiveAnnuellePpiPap
	"""

	# Méthodes Django

	def save(self, iPpi):

		# Initialisation des ids
		pks = []

		# Pour chaque formulaire...
		for form in self.forms:

			# Enregistrement
			iPap = form.save(iPpi=iPpi)

			# Empilement desids
			pks.append(iPap.pk)

		# Suppression des instances obsolètes
		iPpi.tprospectiveannuelleppipap_set.exclude(pk__in=pks).delete()

		return True

class ManagePap(forms.ModelForm):

	"""
	Formulaire de gestion des instances TProspectiveAnnuellePpiPap
	"""

	class Meta:

		# Imports
		from app.models import TProspectiveAnnuellePpiPap

		exclude = ['ppi_id']
		model = TProspectiveAnnuellePpiPap
		'''
		widgets = {
			'pap_dps_eli_fctva': forms.NumberInput(attrs={'input-group-addon': 'euro'}),
			'pap_dps_ttc_rp': forms.NumberInput(attrs={'input-group-addon': 'euro'}),
			'pap_vsm_previ_rp': forms.NumberInput(attrs={'input-group-addon': 'euro'})
		}
		'''

	# Constructeur

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		# Définition des messages d'erreurs personnalisés
		init_mess_err(self)

		self.empty_permitted = False

	# Méthodes Django

	def save(self, iPpi):

		# Enregistrement de l'instance
		iPap, created = self._meta.model.objects.update_or_create(
			ppi_id=iPpi,
			pap_an=self.cleaned_data.get('pap_an'),
			defaults={
				'pap_dps_eli_fctva': self.cleaned_data.get('pap_dps_eli_fctva'),
				'pap_dps_ttc_rp': self.cleaned_data.get('pap_dps_ttc_rp'),
				'pap_vsm_previ_rp': self.cleaned_data.get('pap_vsm_previ_rp')
			}
		)

		return iPap