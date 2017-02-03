#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.constants import *
from django import forms

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
		label = 'Dossier associé', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
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
	zl_type_doss = forms.ChoiceField(choices = [DEFAULT_OPTION], label = 'Type de dossier', widget = forms.Select())
	zl_techn = forms.ChoiceField(label = 'Agent responsable', widget = forms.Select())
	rb_est_ttc_doss = forms.ChoiceField(
		choices = [(True, 'Oui'), (False, 'Non')],
		initial = False,
		label = 'Le montant est-il en TTC ?',
		required = False,
		widget = forms.RadioSelect()
	)

	class Meta :

		# Imports
		from app.models import TDossier

		exclude = [
			'comm_regl_doss', 
			'dt_int_doss', 
			'est_ttc_doss', 
			'id_fam',
			'id_org_moa',
			'id_progr',
			'id_techn',
			'id_type_doss', 
			'num_doss', 
			'type_decl'
		]
		fields = '__all__'
		model = TDossier

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TAction
		from app.models import TAxe
		from app.models import TMoa
		from app.models import TProgramme
		from app.models import TSousAxe
		from app.models import TTechnicien

		# Je déclare le tableau des arguments.
		self.k_util = kwargs.pop('k_util', None)

		super(GererDossier, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED

		# J'ajoute un double astérisque au label de certains champs.
		self.fields['dt_delib_moa_doss'].label += REMARK
		self.fields['mont_doss'].label += REMARK
		self.fields['mont_suppl_doss'].label += REMARK
		self.fields['dt_av_cp_doss'].label += REMARK

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		t_org_moa = [(m.pk, m) for m in TMoa.objects.filter(en_act_org_moa = True)]
		t_org_moa.insert(0, DEFAULT_OPTION)
		self.fields['zl_org_moa'].choices = t_org_moa

		# J'alimente la liste déroulante des programmes.
		t_progr = [(p.pk, p) for p in TProgramme.objects.filter(en_act_progr = True)]
		t_progr.insert(0, DEFAULT_OPTION)
		self.fields['zl_progr'].choices = t_progr

		# J'alimente la liste déroulante des techniciens.
		t_techn = [(t.pk, t) for t in TTechnicien.objects.filter(en_act_techn = True)]
		t_techn.insert(0, DEFAULT_OPTION)
		self.fields['zl_techn'].choices = t_techn

		# Je passe en lecture seule le champ relatif à la date de l'avis du comité de programmation car "En attente"
		# est l'avis du comité de programmation sélectionné par défaut.
		self.fields['dt_av_cp_doss'].widget.attrs['readonly'] = True

		i = self.instance

		# J'exclus le champ relatif aux dépenses supplémentaires lorsque je veux créer un dossier.
		if not i.pk :
			del self.fields['mont_suppl_doss']

		if i.pk :

			# Je réinitialise le tableau des choix de certaines listes déroulantes.
			self.fields['zl_org_moa'].choices = [(i.id_org_moa.pk, i.id_org_moa)]
			self.fields['zl_progr'].choices = [(i.id_progr.pk, i.id_progr)]
			self.fields['zl_type_doss'].choices = [(i.id_type_doss.pk, i.id_type_doss)]
			if i.id_techn.en_act_techn == False :
				self.fields['zl_techn'].choices += [(i.id_techn.pk, i.id_techn)]

			# J'affiche la valeur initiale de chaque champ personnalisé.
			self.fields['za_num_doss'].initial = i
			self.fields['za_doss_ass'].initial = i.id_doss_ass
			self.fields['zl_type_doss'].initial = i.id_type_doss.pk
			self.fields['zl_techn'].initial = i.id_techn.pk
			self.fields['rb_est_ttc_doss'].initial = i.est_ttc_doss

			if i.num_axe is not None :

				# J'alimente la liste déroulante des axes.
				t_axe = [(a.pk, a.num_axe) for a in TAxe.objects.filter(id_progr = i.id_progr)]
				t_axe.insert(0, DEFAULT_OPTION)
				self.fields['zl_axe'].choices = t_axe

				# Je pointe vers l'objet TAxe.
				o_axe = TAxe.objects.get(id_progr = i.id_progr, num_axe = i.num_axe).pk

				# J'affiche le contrôle en sélectionnant l'axe de l'instance.
				self.fields['zl_axe'].initial = o_axe
				self.fields['zl_axe'].widget.attrs['class'] += ' show-field'

				if i.num_ss_axe is not None :

					# J'alimente la liste déroulante des sous-axes.
					t_ss_axe = [(sa.pk, sa.num_ss_axe) for sa in TSousAxe.objects.filter(id_axe = o_axe)]
					t_ss_axe.insert(0, DEFAULT_OPTION)
					self.fields['zl_ss_axe'].choices = t_ss_axe

					# Je pointe vers l'objet TSousAxe.
					o_ss_axe = TSousAxe.objects.get(id_axe = o_axe, num_ss_axe = i.num_ss_axe).pk

					# J'affiche le contrôle en sélectionnant le sous-axe de l'instance.
					self.fields['zl_ss_axe'].initial = o_ss_axe
					self.fields['zl_ss_axe'].widget.attrs['class'] += ' show-field'

					if i.num_act is not None :

						# J'alimente la liste déroulante des actions.
						t_act = [(a.pk, a.num_act) for a in TAction.objects.filter(id_ss_axe = o_ss_axe)]
						t_act.insert(0, DEFAULT_OPTION)
						self.fields['zl_act'].choices = t_act

						# Je pointe vers l'objet TAction.
						o_act = TAction.objects.get(id_ss_axe = o_ss_axe, num_act = i.num_act).pk

						# J'affiche le contrôle en sélectionnant l'action de l'instance.
						self.fields['zl_act'].initial = o_act
						self.fields['zl_act'].widget.attrs['class'] += ' show-field'

			# Je vérifie si certains champs doivent bénéficier ou non de la lecture seule.
			if i.id_av.int_av == 'En projet' :
				self.fields['dt_delib_moa_doss'].widget.attrs['readonly'] = True
			if i.id_av_cp.int_av_cp in ['Accordé', 'Refusé'] :
				self.fields['dt_av_cp_doss'].widget.attrs['readonly'] = False
			if i.id_av_cp.int_av_cp == 'Accordé' :
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
		from app.sql_views import VSuiviDossier
		from django.db.models import Max
		from django.db.models import Sum

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
		v_av_cp = cleaned_data.get('id_av_cp')
		v_av_cp_doss = cleaned_data.get('dt_av_cp_doss')

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
			if v_av.int_av != 'En projet' and not v_dt_delib_moa_doss :
				self.add_error('dt_delib_moa_doss', ERROR_MESSAGES['required'])

		# Je rends obligatoire la date de l'avis du comité de programmation si celui-ci est en attente ou sans objet.
		if v_av_cp :
			if not v_av_cp.int_av_cp in ['En attente', 'Sans objet'] and not v_av_cp_doss :
				self.add_error('dt_av_cp_doss', ERROR_MESSAGES['required'])

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
			if ger_droits(self.k_util, [o_org_moa.pk, o_progr.id_type_progr.pk], False, False) == False :
				self.add_error('zl_org_moa', None)
				self.add_error(
					'zl_progr',
					'''
					Vous n\'avez pas les permissions requises pour créer un dossier du programme « {0} » pour le maître
					d\'ouvrage « {1} ».
					'''.format(o_progr, o_org_moa)
				)

		if i.pk :

			# Je récupère trois valeurs : le montant de l'assiette éligible maximum, la somme des montants de la 
			# participation et la somme des prestations.
			qs_fin_aggr = TFinancement.objects.filter(id_doss = i).aggregate(
				Max('mont_elig_fin'), Sum('mont_part_fin')
			)
			mont_elig_fin_max = qs_fin_aggr['mont_elig_fin__max'] or 0
			mont_part_fin_sum = qs_fin_aggr['mont_part_fin__sum'] or 0
			mont_tot_prest_doss = VSuiviDossier.objects.get(pk = i.pk).mont_tot_prest_doss

			# Je trie les deux valeurs dans l'ordre afin de récupérer le montant minimum du dossier.
			t_mont_doss = sorted([mont_elig_fin_max, mont_part_fin_sum, mont_tot_prest_doss])

			# Je gère la contrainte suivante : les montants du dossier dépendent des éléments comptables de celui-ci.
			if v_mont_doss is not None and v_mont_suppl_doss is not None :
				if v_av_cp :
					if v_av_cp.int_av_cp == 'Accordé' :
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
			if v_av and v_av.int_av == 'En projet' :
				mess = None
				if len(TFinancement.objects.filter(id_doss = i)) > 0 :
					mess = 'Un financement a déjà été déclaré pour ce dossier.' 
				if len(TPrestationsDossier.objects.filter(id_doss = i)) > 0 :
					mess = 'Une prestation a déjà été lancée pour ce dossier.'
				if mess :
					self.add_error('id_av', mess)

			# Je renvoie une erreur si le montant de dépassement d'un dossier dont l'avis du comité de programmation
			# est différent de "Accordé" est strictement positif.
			if v_av_cp and v_av_cp.int_av_cp != 'Accordé' :
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
			v_act = None

		o.num_act = v_act

		# J'initialise le numéro de l'axe.
		try :
			v_axe = TAxe.objects.get(pk = self.cleaned_data.get('zl_axe')).num_axe
		except :
			v_axe = None

		o.num_axe = v_axe

		# J'initialise le numéro du sous-axe.
		try :
			v_ss_axe = TSousAxe.objects.get(pk = self.cleaned_data.get('zl_ss_axe')).num_ss_axe
		except :
			v_ss_axe = None

		o.num_ss_axe = v_ss_axe

		# Je vérifie l'existence d'un objet TDossier.
		try :
			o_doss = TDossier.objects.get(num_doss = self.cleaned_data.get('za_doss_ass'))
		except :
			o_doss = None

		o.id_doss_ass = o_doss
		o.id_progr = TProgramme.objects.get(pk = self.cleaned_data.get('zl_progr'))
		o.id_org_moa = TMoa.objects.get(pk = self.cleaned_data.get('zl_org_moa'))
		o.id_techn = TTechnicien.objects.get(pk = self.cleaned_data.get('zl_techn'))
		o.id_type_doss = TTypeDossier.objects.get(pk = self.cleaned_data.get('zl_type_doss'))

		if commit :
			o.save()

		return o

class ChoisirDossier(forms.ModelForm) :

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

	class Meta :

		# Imports
		from app.models import TDossier

		fields = []
		model = TDossier

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TMoa
		from app.models import TNatureDossier
		from app.models import TProgramme
		from datetime import date

		# Je déclare le tableau des arguments.
		k_org_moa = kwargs.pop('k_org_moa', None)

		super(ChoisirDossier, self).__init__(*args, **kwargs)

		# Je définis les messages d'erreurs personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES

		if k_org_moa :
			self.fields['zl_org_moa'].initial = k_org_moa

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		t_org_moa = [(m.pk, m) for m in TMoa.objects.filter(en_act_org_moa = True)]
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
		t_ann_delib_moa_doss = [(i, i) for i in range(1999, date.today().year + 1)]
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

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions import obt_pourc

		# Je déclare le tableau des arguments.
		instance = kwargs.get('instance', None)
		k_doss = kwargs.pop('k_doss', None)

		# Je mets en forme certaines données.
		'''
		if instance :
			kwargs.update(initial = {
				'pourc_elig_fin' : obt_pourc(instance.pourc_elig_fin),
				'pourc_real_fin' : obt_pourc(instance.pourc_real_fin)
			})
		'''

		super(GererFinancement, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED

		# J'ajoute un double astérisque au label de certains champs.
		self.fields['mont_elig_fin'].label += REMARK
		self.fields['pourc_elig_fin'].label += REMARK
		self.fields['dt_deb_elig_fin'].label += REMARK
		self.fields['pourc_real_fin'].label += REMARK

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
			if i.mont_elig_fin and i.pourc_elig_fin :
				self.fields['mont_part_fin'].widget.attrs['readonly'] = True
			if i.id_paiem_prem_ac :
				if i.id_paiem_prem_ac.int_paiem_prem_ac == 'Pourcentage de réalisation des travaux' :
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
		from app.sql_views import VFinancement
		from app.sql_views import VSuiviDossier

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
					qs_fin = qs_fin.exclude(pk = i.pk)
				if len(qs_fin) > 0 :
					self.add_error('id_org_fin', 'Le financeur participe déjà au montage financier.')

			# Je gère la contrainte suivante : le montant de l'assiette éligible de la subvention doit toujours être 
			# inférieur ou égal au montant du dossier.
			if v_mont_elig_fin and float(v_mont_elig_fin) > o_doss.mont_doss :
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
			if v_mont_part_fin and float(v_mont_part_fin) > mont_part_fin_max :
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
				o_fin = VFinancement.objects.get(pk = i.pk)
				if v_mont_part_fin and float(v_mont_part_fin) < o_fin.mont_ddv_sum :
					self.add_error(
						'mont_part_fin',
						'Veuillez saisir un montant supérieur ou égal à {0} €.'.format(obt_mont(o_fin.mont_ddv_sum))
					)

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
	from app.validators import val_mont_pos
	from app.validators import val_siret

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
	zsac_siret_org_prest = forms.CharField(
		label = 'Numéro SIRET du prestataire', 
		validators = [val_siret], 
		widget = forms.TextInput(attrs = { 'autocomplete' : 'off', 'maxlength' : 14 })
	)
	zs_mont_prest = forms.FloatField(
		label = 'Montant [ht_ou_ttc] de la prestation', 
        validators = [val_mont_pos],
        widget = forms.TextInput()
    )

	class Meta :

		# Imports
		from app.models import TPrestation

		exclude = ['doss', 'id_org_prest']
		fields = '__all__'
		model = TPrestation

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TPrestationsDossier

		# Je déclare le tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)

		super(GererPrestation, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED

		# J'initialise la variable liée au mode de taxe par précaution.
		ht_ou_ttc = 'HT'

		i = self.instance
		if i.pk :
			self.fields['zsac_siret_org_prest'].initial = i.id_org_prest.siret_org_prest
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

		# J'exclus le champ personnalisé lié au montant de la prestation lorsque je suis en phase de modification.
		if i.pk :
			del self.fields['zs_mont_prest']

	def clean(self) :

		# Imports
		from app.functions import dt_fr
		from app.functions import obt_mont
		from app.models import TAvenant
		from app.models import TDossier
		from app.models import TPrestataire
		from app.sql_views import VSuiviDossier
		from django.db.models import Min

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererPrestation, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_siret_org_prest = cleaned_data.get('zsac_siret_org_prest')
		v_mont_prest = cleaned_data.get('zs_mont_prest')
		v_dt_fin_prest = cleaned_data.get('dt_fin_prest')

		i = self.instance

		# Je gère la contrainte suivante : le numéro SIRET doit exister dans la base de données afin de le relier à un
		# prestataire.
		if len(TPrestataire.objects.filter(siret_org_prest = v_siret_org_prest)) == 0 :
			self.add_error('zsac_siret_org_prest', 'Le numéro SIRET appartient à aucun prestataire.')

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
			if v_mont_prest and float(v_mont_prest) > o_suivi_doss.mont_rae :
				self.add_error(
					'zs_mont_prest', 
					'Veuillez saisir un montant inférieur ou égal à {0} €.'.format(obt_mont(o_suivi_doss.mont_rae))
				)

		# Je renvoie une erreur si la date de fin de prestation est supérieure à la date du premier avenant.
		if i.pk :
			qs_aven_aggr = TAvenant.objects.filter(id_prest = i).aggregate(Min('dt_aven'))
			dt_aven_min = qs_aven_aggr['dt_aven__min']
			if v_dt_fin_prest and dt_aven_min and v_dt_fin_prest > dt_aven_min :
				self.add_error(
					'dt_fin_prest',
					'''
					Veuillez saisir une date antérieure ou égale au {0} (date de fin du premier avenant).
					'''.format(dt_fr(dt_aven_min))
				)

	def save(self, commit = True) :

		# Imports
		from app.models import TDossier
		from app.models import TPrestataire

		o = super(GererPrestation, self).save(commit = False)
		o.id_org_prest = TPrestataire.objects.get(siret_org_prest = self.cleaned_data.get('zsac_siret_org_prest'))
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

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED

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

		fields = ['mont_prest_doss']
		model = TPrestationsDossier

	def __init__(self, *args, **kwargs) :

		# Je déclare le tableau des arguments.
		self.k_doss = kwargs.pop('k_doss', None)
		self.k_prest = kwargs.pop('k_prest', None)
		
		super(RedistribuerPrestation, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES

		# Je supprime le label lié au montant du couple prestation/dossier.
		self.fields['mont_prest_doss'].label = ''

	def clean(self) :

		# Imports
		from app.functions import obt_mont
		from app.sql_views import VSuiviDossier
		from app.sql_views import VSuiviPrestationsDossier

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
		if v_mont_prest_doss and not mont_prest_doss_min <= float(v_mont_prest_doss) <= mont_prest_doss_max :

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
		choices = [DEFAULT_OPTION, ('Acompte', 'Acompte'), ('Solde', 'Solde')],
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

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TFacturesDemandeVersement
		from app.models import TPrestationsDossier

		# Je déclare le tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)

		super(GererFacture, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED

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
			v_suivi_fact = 'Acompte'
			if i.suivi_fact == 'Solde' :
				v_suivi_fact = 'Solde'
			self.fields['zl_suivi_fact'].initial = v_suivi_fact

			if len(TFacturesDemandeVersement.objects.filter(id_fact = i)) > 0 :
				self.fields['mont_ht_fact'].widget.attrs['readonly'] = True
				self.fields['mont_ttc_fact'].widget.attrs['readonly'] = True

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
		from app.sql_views import VSuiviPrestationsDossier

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererFacture, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_prest = cleaned_data.get('zl_prest')
		v_mont_ht_fact = cleaned_data.get('mont_ht_fact')
		v_mont_ttc_fact = cleaned_data.get('mont_ttc_fact')
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
				if float(valeur) > mont_raf_max :
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

			# Je renvoie une erreur si le montant de la facture est modifié.
			if v_mont_ht_fact and i.pk and float(v_mont_ht_fact) != i.mont_ht_fact :
				self.add_error(
					'mont_ht_fact', 
					'''
					Vous ne pouvez pas modifier le montant HT de la facture car elle est reliée à une demande de
					versement.
					'''
				)
			if v_mont_ttc_fact and i.pk and float(v_mont_ttc_fact) != i.mont_ttc_fact :
				self.add_error(
					'mont_ttc_fact', 
					'''
					Vous ne pouvez pas modifier le montant TTC de la facture car elle est reliée à une demande de 
					versement.
					'''
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
		if commit :
			o.save()

		return o

class GererDemandeVersement(forms.ModelForm) :

	za_num_doss = forms.CharField(
		label = 'Numéro du dossier', required = False, widget = forms.TextInput(attrs = { 'readonly' : True })
	)
	zl_fin = forms.ChoiceField(label = 'Partenaire financier', widget = forms.Select())
	cbsm_fact = forms.MultipleChoiceField(label = '', required = False, widget = forms.CheckboxSelectMultiple())

	class Meta :

		# Imports
		from app.models import TDemandeVersement

		exclude = ['fact', 'id_fin']
		fields = '__all__'
		model = TDemandeVersement

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TFacture
		from app.models import TFinancement

		# Je déclare le tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)

		super(GererDemandeVersement, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED

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

		# J'ajoute un astérisque au label du champ de montant obligatoire.
		if num_doss :
			if num_doss.est_ttc_doss == True :
				self.fields['mont_ttc_ddv'].label += REQUIRED
			else :
				self.fields['mont_ht_ddv'].label += REQUIRED

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
			self.fields['zl_fin'].initial = i.id_fin
			self.fields['cbsm_fact'].choices = [(f.pk, f) for f in TFacture.objects.filter(id_doss = i.id_fin.id_doss)]

	def clean(self) :

		# Imports
		from app.functions import obt_mont
		from app.models import TDemandeVersement
		from app.models import TDossier
		from app.sql_views import VFinancement

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererDemandeVersement, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_fin = cleaned_data.get('zl_fin')
		v_type_vers = cleaned_data.get('id_type_vers')
		v_fact = cleaned_data.get('cbsm_fact')

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
			o_suivi_fin = VFinancement.objects.get(pk = v_fin)
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
			if i.pk and o_suivi_fin.pk == i.id_fin.pk :
				if 'ht' in cle :
					mont_rad += i.mont_ht_ddv
				if 'ttc' in cle :
					mont_rad += i.mont_ttc_ddv
			if valeur :
				if float(valeur) > mont_rad :
					self.add_error(
						cle, 
						'Veuillez saisir un montant inférieur ou égal à {0} €.'.format(obt_mont(mont_rad))
					)
			else :
				self.add_error(cle, ERROR_MESSAGES['required'])

			# Je renvoie une erreur si aucune facture n'a été reliée à une demande de versement dont le type de 
			# versement est différent de "Avance forfaitaire".
			if v_type_vers :
				if v_type_vers.int_type_vers in ['Acompte', 'Solde'] and not v_fact :
					self.add_error('cbsm_fact', ERROR_MESSAGES['required'])

			# Je récupère les demandes de versements soldées du financement.
			qs_ddv = TDemandeVersement.objects.filter(
				id_fin = o_suivi_fin.pk, 
				id_type_vers__int_type_vers = 'Solde'
			)

			# Je renvoie une erreur si un financement admet déjà une demande de versement soldée.
			err = False
			if v_type_vers :
				if not i.pk :
					if len(qs_ddv) > 0 :
						err = True
				else :
					qs_ddv = qs_ddv.exclude(pk = i.pk)
					if len(qs_ddv) > 0 and v_type_vers.int_type_vers == 'Solde' :
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

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TArretesDossier
		from app.models import TTypeDeclaration

		# Je déclare le tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)

		super(GererArrete, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED

		# J'ajoute un double astérisque au label de certains champs.
		self.fields['num_arr'].label += REMARK
		self.fields['dt_sign_arr'].label += REMARK
		self.fields['dt_lim_encl_trav_arr'].label += REMARK
		self.fields['chem_pj_arr'].label += REMARK

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
			if v_type_av_arr and v_type_av_arr.int_type_av_arr == 'Validé' :
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

	def __init__(self, *args, **kwargs) :

		# Je déclare le tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)

		super(GererPhoto, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED

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

	def __init__(self, *args, **kwargs) :

		# Je déclare le tableau des arguments.
		k_prest_doss = kwargs.pop('k_prest_doss', None)

		super(GererAvenant, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED

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
		from app.sql_views import VSuiviDossier
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
			self.add_error('za_num_doss', ERROR_MESSAGES['invalid'])
			self.add_error('zl_prest', '')

		if o_prest_doss and o_suivi_doss :

			# Je gère le bon renseignement de la date de fin de l'avenant.
			if v_dt_aven :
				if i.pk :

					# Je stocke le jeu de données des avenants du couple prestation/dossier.
					qs_aven = TAvenant.objects.filter(
						id_doss = o_prest_doss.id_doss, id_prest = o_prest_doss.id_prest
					).order_by('num_aven')

					# Je récupère l'index de l'avenant.
					ind = None
					for index, a in enumerate(qs_aven) :
						if a.pk == i.pk :
							ind = index

					# J'initialise la date de fin minimale de l'avenant.
					if ind == 0 :
						dt_aven_min = o_prest_doss.id_prest.dt_fin_prest
					else :
						dt_aven_min = qs_aven[ind - 1].dt_aven

					# J'initialise la date de fin maximale de l'avenant.
					if ind == len(qs_aven) - 1 :
						dt_aven_max = None
					else :
						dt_aven_max = qs_aven[ind + 1].dt_aven

					# Je renvoie une erreur si la date de fin de l'avenant n'est pas conforme.
					if dt_aven_max :
						if not dt_aven_min <= v_dt_aven <= dt_aven_max : 
							self.add_error(
								'dt_aven',
								'''
								La date de fin de l\'avenant doit être comprise entre le {0} et le {1}.
								'''.format(dt_fr(dt_aven_min), dt_fr(dt_aven_max))
							)
					else :
						if v_dt_aven < dt_aven_min :
							self.add_error(
								'dt_aven', 
								'''
								La date de fin de l\'avenant doit être postérieure ou égale au {0}.
								'''.format(dt_fr(dt_aven_min))
							)

				else :

					# Je récupère la date de fin de la prestation (soit celle indiquée lors de la création de celle-ci, soit la
					# date de l'avenant la plus grande).
					num_aven_max = TAvenant.objects.filter(
						id_doss = o_prest_doss.id_doss, id_prest = o_prest_doss.id_prest
					).aggregate(Max('num_aven'))['num_aven__max']

					if num_aven_max :
						dt_fin_prest = TAvenant.objects.get(
							id_doss = o_prest_doss.id_doss, id_prest = o_prest_doss.id_prest, num_aven = num_aven_max
						).dt_aven
					else :
						dt_fin_prest = o_prest_doss.id_prest.dt_fin_prest

					# Je renvoie une erreur si la date de fin de l'avenant n'est pas conforme.
					if v_dt_aven < dt_fin_prest :
						self.add_error(
							'dt_aven',
							'''
							La date de fin de l\'avenant doit être postérieure ou égale au {0}.
							'''.format(dt_fr(dt_fin_prest))
						)

			# Je renvoie une erreur si le montant de l'avenant est supérieur au reste à engager du dossier.
			mont_rae = o_suivi_doss.mont_rae
			if i.pk :
				mont_rae += i.mont_aven
			if v_mont_aven and float(v_mont_aven) > mont_rae :
				self.add_error(
					'mont_aven',
					'Veuillez saisir un montant inférieur ou égal à {0} €.'.format(obt_mont(mont_rae))
				)

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

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = ERROR_MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += REQUIRED