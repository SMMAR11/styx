#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.constants import *
from django import forms

class GererDossier(forms.Form) :

	''' Imports '''
	from app.validators import valid_cdc, valid_mont, valid_nb

	# Je définis les champs du formulaire.
	za_num_doss = forms.CharField(
		label = 'Numéro du dossier',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zs_int_doss = forms.CharField(
		label = 'Intitulé du dossier',
		validators = [valid_cdc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zs_descr_doss = forms.CharField(
		label = 'Description du dossier et de ses objectifs',
		required = False,
		validators = [valid_cdc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	za_doss_ass = forms.CharField(
		label = 'Dossier associé',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zl_org_moa = forms.ChoiceField(
		label = 'Maître d\'ouvrage',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zld_progr = forms.ChoiceField(
		label = 'Programme',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zld_axe = forms.ChoiceField(
		label = 'Axe',
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_ss_axe = forms.ChoiceField(
		label = 'Sous-axe',
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_act = forms.ChoiceField(
		label = 'Action',
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_type_doss = forms.ChoiceField(
		label = 'Type du dossier',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zl_nat_doss = forms.ChoiceField(
		label = 'Nature du dossier',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zl_techn = forms.ChoiceField(
		label = 'Technicien',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zs_mont_ht_doss = forms.CharField(
		label = 'Montant HT du dossier (en €)',
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zs_mont_ttc_doss = forms.CharField(
		label = 'Montant TTC du dossier (en €)',
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zl_av = forms.ChoiceField(
		label = 'État d\'avancement du dossier',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zd_dt_delib_moa_doss = forms.DateField(
		label = 'Date de délibération au maître d\'ouvrage',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zl_av_cp = forms.ChoiceField(
		label = 'Avis du comité de programmation',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zd_dt_av_cp_doss = forms.DateField(
		label = 'Date de l\'avis du comité de programmation',
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zu_chem_dds_doss = forms.FileField(
		label = 'Fichier scanné du DDS',
		required = False,
		widget = forms.FileInput(attrs = { 'class' : 'input-file' })
	)

	za_chem_dds_doss = forms.CharField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True, 'type' : 'hidden' })
	)

	zs_comm_doss = forms.CharField(
		label = 'Commentaire',
		required = False,
		validators = [valid_cdc],
		widget = forms.Textarea(attrs = { 'class' : 'form-control', 'maxlength' : 255, 'rows' : 5 })
	)

	# Je définis les champs PGRE du formulaire.
	zs_quant_objs_pgre = forms.CharField(
		label = 'Quantification des objectifs',
		required = False,
		validators = [valid_nb],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_quant_real_pgre = forms.CharField(
		label = 'Réalisé',
		required = False,
		validators = [valid_nb],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zl_unit = forms.ChoiceField(
		label = 'Unité',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	cbsm_riv = forms.MultipleChoiceField(
		label = 'Rivières impactées',
		required = False,
		widget = forms.CheckboxSelectMultiple()
	)

	zl_port = forms.ChoiceField(
		label = 'Portée du dossier',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	def __init__(self, *args, **kwargs) :

		''' Imports '''
		from app.functions import float_to_int, integer, reecr_dt
		from app.models import TAction
		from app.models import TAvancement
		from app.models import TAvisCp
		from app.models import TAxe
		from app.models import TDossier
		from app.models import TMoa
		from app.models import TNatureDossier
		from app.models import TPgre
		from app.models import TPortee
		from app.models import TProgramme
		from app.models import TRiviere
		from app.models import TRivieresDossier
		from app.models import TSousAxe
		from app.models import TTechnicien
		from app.models import TTypeDossier
		from app.models import TUnite
		from styx.settings import MEDIA_URL

		# Je déclare les arguments.
		k_doss = kwargs.pop('k_doss', None)

		super(GererDossier, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += CHAMP_REQUIS 

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = None
		try :
			obj_doss = TDossier.objects.get(id_doss = k_doss)
		except :
			pass

		# Je définis les valeurs initiales du formulaire.
		if obj_doss is not None :
			self.fields['za_num_doss'].initial = obj_doss.num_doss
			self.fields['zs_int_doss'].initial = obj_doss.int_doss
			self.fields['zs_descr_doss'].initial = obj_doss.descr_doss

			# Je vérifie l'existence d'un objet TDossier lié au dossier associé.
			obj_doss_ass = None
			try :
				obj_doss_ass = TDossier.objects.get(id_doss = obj_doss.id_doss_ass.id_doss)
			except :
				pass

			if obj_doss_ass is not None :
				self.fields['za_doss_ass'].initial = obj_doss_ass.num_doss

			self.fields['zl_org_moa'].initial = obj_doss.id_org_moa.id_org_moa.id_org
			self.fields['zld_progr'].initial = obj_doss.id_progr.id_progr
			self.fields['zld_axe'].initial = obj_doss.num_axe
			self.fields['zld_ss_axe'].initial = obj_doss.num_ss_axe
			self.fields['zld_act'].initial = obj_doss.num_act
			self.fields['zld_type_doss'].initial = obj_doss.id_type_doss.id_type_doss
			self.fields['zl_nat_doss'].initial = obj_doss.id_nat_doss.id_nat_doss
			self.fields['zl_techn'].initial = obj_doss.id_techn.id_techn
			self.fields['zs_mont_ht_doss'].initial = float_to_int(obj_doss.mont_ht_doss)
			self.fields['zs_mont_ttc_doss'].initial = float_to_int(obj_doss.mont_ttc_doss)
			self.fields['zl_av'].initial = obj_doss.id_av.id_av
			self.fields['zd_dt_delib_moa_doss'].initial = reecr_dt(obj_doss.dt_delib_moa_doss)
			self.fields['zl_av_cp'].initial = obj_doss.id_av_cp.id_av_cp
			self.fields['zd_dt_av_cp_doss'].initial = reecr_dt(obj_doss.dt_av_cp_doss)
			self.fields['zs_comm_doss'].initial = obj_doss.comm_doss

			# J'initialise l'attribut "title" de la zone d'upload du fichier de DDS du dossier.
			if obj_doss.chem_dds_doss is not None :
				self.fields['zu_chem_dds_doss'].widget.attrs['title'] = MEDIA_URL + obj_doss.chem_dds_doss
				self.fields['za_chem_dds_doss'].initial = MEDIA_URL + obj_doss.chem_dds_doss

			# Je vérifie l'existence d'un objet TPgre.
			obj_doss_pgre = None
			try :
				obj_doss_pgre = TPgre.objects.get(id_pgre = k_doss)
			except :
				pass

			if obj_doss_pgre is not None :
				self.fields['zs_quant_objs_pgre'].initial = float_to_int(obj_doss_pgre.quant_objs_pgre, 0)
				self.fields['zs_quant_real_pgre'].initial = float_to_int(obj_doss_pgre.quant_real_pgre, 0)

				# Je vérifie l'existence d'un objet TUnite.
				obj_unit_doss_pgre = None
				try :
					obj_unit_doss_pgre = TUnite.objects.get(id_unit = obj_doss_pgre.id_unit.id_unit)
				except :
					pass

				if obj_unit_doss_pgre is not None :
					self.fields['zl_unit'].initial = obj_unit_doss_pgre.id_unit

				# Je stocke dans un tableau les identifiants des rivières impactées par l'objet TPgre.
				tab_riv = []
				for une_riv_doss in TRivieresDossier.objects.filter(id_pgre = obj_doss_pgre) :
					tab_riv.append(une_riv_doss.id_riv.id_riv)

				self.fields['cbsm_riv'].initial = tab_riv

				# Je vérifie l'existence d'un objet TPortee.
				obj_port_doss_pgre = None
				try :
					obj_port_doss_pgre = TPortee.objects.get(id_port = obj_doss_pgre.id_port.id_port)
				except :
					pass

				if obj_port_doss_pgre is not None :
					self.fields['zl_port'].initial = obj_port_doss_pgre.id_port

		# Je définis l'état du contrôle relatif à la date de délibération au maître d'ouvrage.
		if obj_doss is not None :
			if TAvancement.objects.get(id_av = obj_doss.id_av.id_av).int_av == 'En projet' :
				self.fields['zd_dt_delib_moa_doss'].widget.attrs['disabled'] = True

		# Je définis des parametres.
		if obj_doss is not None :
			p_org_moa = int(obj_doss.id_org_moa.id_org_moa.id_org)
			p_progr = int(obj_doss.id_progr.id_progr)
			p_axe = integer(obj_doss.num_axe)
			p_ss_axe = integer(obj_doss.num_ss_axe)
		else :
			p_org_moa = -1
			p_progr = -1
			p_axe = -1
			p_ss_axe = -1

		# J'alimente la liste déroulante des maîtres d'ouvrages selon l'opération en cours.
		if p_org_moa > 0 :

			# Je traite le cas où je modifie un dossier. Dans ce cas, je bloque la liste déroulante car je ne peux pas
			# changer le maître d'ouvrage.
			les_org_moa = list(
				[(i.id_org_moa.id_org, i.id_org_moa.n_org) for i in TMoa.objects.filter(id_org_moa = p_org_moa)]
			)

		else :

			# Je traite le cas où j'ajoute un dossier. Dans ce cas, je renseigne les maîtres d'ouvrages en activité.
			les_org_moa = list(OPTION_INITIALE)
			les_org_moa.extend(
				[(i.id_org_moa.id_org, i.id_org_moa.n_org) for i in TMoa.objects.filter(en_act = True).order_by(
					'id_org_moa__n_org'
				)]
			)

		self.fields['zl_org_moa'].choices = les_org_moa
		
		# J'alimente la liste déroulante des programmes selon l'opération en cours.
		if p_progr > 0 :

			# Je traite le cas où je modifie un dossier. Dans ce cas, je bloque la liste déroulante car je ne peux pas
			# changer le programme.
			les_progr = list([(i.id_progr, i.int_progr) for i in TProgramme.objects.filter(id_progr = p_progr)])

		else :

			# Je traite le cas où j'ajoute un dossier. Dans ce cas, je renseigne tous les programmes.
			les_progr = list(OPTION_INITIALE)
			les_progr.extend([(i.id_progr, i.int_progr) for i in TProgramme.objects.order_by('int_progr')])

		self.fields['zld_progr'].choices = les_progr

		# J'alimente la liste déroulante des axes.
		les_axes = list([(i.num_axe, i.num_axe) for i in TAxe.objects.filter(id_progr = p_progr).order_by('num_axe')])

		# Je gère la valeur de l'option par défaut.
		if len(les_axes) > 0 :

			# J'insère l'option par défaut.
			les_axes.insert(0, [OPTION_INITIALE[0][0], OPTION_INITIALE[0][1]])

			# J'ajoute la classe "show-field-temp" qui permet d'afficher la liste déroulante.
			self.fields['zld_axe'].widget.attrs['class'] += 'show-field-temp'

		else :

			# J'insère l'option par défaut qui permet de bypasser la validation du contrôle.
			les_axes.insert(0, ['DBP', OPTION_INITIALE[0][1]])

		self.fields['zld_axe'].choices = les_axes

		# J'alimente la liste déroulante des sous-axes.
		les_ss_axes = list([(i.num_ss_axe, i.num_ss_axe) for i in TSousAxe.objects.filter(
			id_axe = '{0}_{1}'.format(p_progr, p_axe)
		).order_by('num_ss_axe')])

		# Je gère la valeur de l'option par défaut.
		if len(les_ss_axes) > 0 :

			# J'insère l'option par défaut.
			les_ss_axes.insert(0, [OPTION_INITIALE[0][0], OPTION_INITIALE[0][1]])

			# J'ajoute la classe "show-field-temp" qui permet d'afficher la liste déroulante.
			self.fields['zld_ss_axe'].widget.attrs['class'] += 'show-field-temp'

		else :

			# J'insère l'option par défaut qui permet de bypasser la validation du contrôle.
			les_ss_axes.insert(0, ['DBP', OPTION_INITIALE[0][1]])

		self.fields['zld_ss_axe'].choices = les_ss_axes

		# J'alimente la liste déroulante des actions.
		les_act = list([(i.num_act, i.num_act) for i in TAction.objects.filter(
			id_ss_axe = '{0}_{1}_{2}'.format(p_progr, p_axe, p_ss_axe)
		).order_by('num_act')])

		# Je gère la valeur de l'option par défaut.
		if len(les_act) > 0 :

			# J'insère l'option par défaut.
			les_act.insert(0, [OPTION_INITIALE[0][0], OPTION_INITIALE[0][1]])

			# J'ajoute la classe "show-field-temp" qui permet d'afficher la liste déroulante.
			self.fields['zld_act'].widget.attrs['class'] += 'show-field-temp'

		else :

			# J'insère l'option par défaut qui permet de bypasser la validation du contrôle.
			les_act.insert(0, ['DBP', OPTION_INITIALE[0][1]])

		self.fields['zld_act'].choices = les_act

		# J'alimente la liste déroulante des types de dossiers.
		les_types_doss = list(OPTION_INITIALE)
		les_types_doss.extend([(i.id_type_doss, i.int_type_doss) for i in TTypeDossier.objects.filter(
			id_progr = p_progr
		).order_by('int_type_doss')])
		self.fields['zld_type_doss'].choices = les_types_doss

		# J'alimente la liste déroulante des natures de dossiers.
		les_nat_doss = list(OPTION_INITIALE)
		les_nat_doss.extend([(i.id_nat_doss, i.int_nat_doss) for i in TNatureDossier.objects.order_by('int_nat_doss')])
		self.fields['zl_nat_doss'].choices = les_nat_doss

		# J'alimente la liste déroulante des techniciens en activité.
		les_techn = list(OPTION_INITIALE)
		les_techn.extend([(i.id_techn, '{0} {1}'.format(i.n_techn, i.pren_techn)) for i in TTechnicien.objects.filter(
			en_act = 1
		).order_by('n_techn', 'pren_techn')])
		self.fields['zl_techn'].choices = les_techn

		# J'alimente la liste déroulante des états d'avancements.
		les_av = list(OPTION_INITIALE)
		les_av.extend([(i.id_av, i.int_av) for i in TAvancement.objects.order_by('int_av')])
		self.fields['zl_av'].choices = les_av

		# J'alimente la liste déroulante des avis du comité de programmation.
		les_av_cp = list(OPTION_INITIALE)
		les_av_cp.extend([(i.id_av_cp, i.int_av_cp) for i in TAvisCp.objects.order_by('int_av_cp')])
		self.fields['zl_av_cp'].choices = les_av_cp

		# J'alimente la liste déroulante des unités.
		les_unit = list(OPTION_INITIALE)
		les_unit.extend([(i.id_unit, i.int_unit) for i in TUnite.objects.order_by('int_unit')])
		self.fields['zl_unit'].choices = les_unit

		# J'alimente la liste déroulante des rivières.
		les_riv = list([(i.id_riv, i.n_riv) for i in TRiviere.objects.order_by('n_riv')])
		les_riv.extend([('T', 'Toutes')]);
		self.fields['cbsm_riv'].choices = les_riv

		# J'alimente la liste déroulante des portées du dossier.
		les_port = list(OPTION_INITIALE)
		les_port.extend([(i.id_port, i.int_port) for i in TPortee.objects.order_by('int_port')])
		self.fields['zl_port'].choices = les_port

	def clean(self) :

		''' Imports '''
		from app.functions import integer, nett_val, valid_zl
		from app.models import TAvancement
		from app.models import TProgramme
		from app.models import TUnite

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererDossier, self).clean()
		v_num_doss = nett_val(cleaned_data.get('za_num_doss'))
		v_doss_ass = nett_val(cleaned_data.get('za_doss_ass'))
		v_org_moa = cleaned_data.get('zl_org_moa')
		v_progr = cleaned_data.get('zld_progr')
		v_axe = cleaned_data.get('zld_axe')
		v_ss_axe = cleaned_data.get('zld_ss_axe')
		v_act = cleaned_data.get('zld_act')
		v_type_doss = cleaned_data.get('zld_type_doss')
		v_nat_doss = cleaned_data.get('zl_nat_doss')
		v_techn = cleaned_data.get('zl_techn')
		v_av_cp = cleaned_data.get('zl_av_cp')
		v_av = cleaned_data.get('zl_av')
		v_dt_delib_moa_doss = nett_val(cleaned_data.get('zd_dt_delib_moa_doss'))
		v_obj_dds_doss = nett_val(cleaned_data.get('zu_chem_dds_doss'))
		v_quant_objs_pgre = nett_val(cleaned_data.get('zs_quant_objs_pgre'))
		v_quant_real_pgre = nett_val(cleaned_data.get('zs_quant_real_pgre'))
		v_unit = integer(cleaned_data.get('zl_unit'))

		# Je vérifie la valeur de chaque liste déroulante obligatoire du formulaire.
		v_org_moa = valid_zl(self, 'zl_org_moa', v_org_moa)
		v_progr = valid_zl(self, 'zld_progr', v_progr)
		v_axe = valid_zl(self, 'zld_progr', v_progr, 'zld_axe', v_axe)
		v_ss_axe = valid_zl(self, 'zld_axe', v_axe, 'zld_ss_axe', v_ss_axe)
		v_act = valid_zl(self, 'zld_ss_axe', v_ss_axe, 'zld_act', v_act)
		v_type_doss = valid_zl(self, 'zld_type_doss', v_type_doss)
		v_nat_doss = valid_zl(self, 'zl_nat_doss', v_nat_doss)
		v_techn = valid_zl(self, 'zl_techn', v_techn)
		v_av_cp = valid_zl(self, 'zl_av_cp', v_av_cp)
		v_av = valid_zl(self, 'zl_av', v_av)

		# Je renvoie une erreur lorsque la date de délibération au maître d'ouvrage d'un dossier dont l'état d'
		# avancement est différent de "En projet" n'est pas renseignée.
		if v_av > -1 :
			if TAvancement.objects.get(id_av = v_av).int_av != 'En projet' and v_dt_delib_moa_doss is None :
				self.add_error('zd_dt_delib_moa_doss', MESSAGES['required'])

		# Je vérifie l'existence d'un objet TProgramme.
		obj_progr = None
		try :
			obj_progr = TProgramme.objects.get(id_progr = v_progr)
		except :
			pass

		# Je gère l'affichage des erreurs liées à la partie "PGRE" si et seulement si ce programme a été choisi.
		if obj_progr is not None and obj_progr.int_progr == 'PGRE' :
			if v_quant_objs_pgre is None :
				if v_unit > 0 or v_quant_real_pgre is not None:
					self.add_error('zs_quant_objs_pgre', MESSAGES['required'])
			else :
				if v_unit < 0 :
					self.add_error('zl_unit', MESSAGES['required'])
				else :
					if v_quant_real_pgre is not None :
						if float(v_quant_real_pgre) > float(v_quant_objs_pgre) :
							self.add_error(
								'zs_quant_real_pgre', 
								'La quantification réalisée doit être inférieure ou égale à {0} {1}.'.format(
									v_quant_objs_pgre, TUnite.objects.get(id_unit = v_unit).int_unit
								)
							)

		# Je renvoie une erreur si le dossier associé choisi correspond au dossier en cours de modification.
		if v_num_doss is not None :
			if v_num_doss == v_doss_ass :
				self.add_error('za_doss_ass', 'Veuillez choisir un autre dossier associé.')

		# Je vérifie l'extension du fichier de DDS du dossier.
		if v_obj_dds_doss is not None :
			if v_obj_dds_doss.name.endswith('.pdf') == False :
				self.add_error('zu_chem_dds_doss', 'Veuillez choisir un fichier au format PDF.')

class GererDossier_Reglementation(forms.Form) :

	''' Imports '''
	from app.validators import valid_cdc

	# Je définis le champ du formulaire.
	zs_comm_regl_doss = forms.CharField(
		label = 'Commentaire',
		required = False,
		validators = [valid_cdc],
		widget = forms.Textarea(attrs = { 'class' : 'form-control', 'maxlength' : 255, 'rows' : 5 })
	)

	def __init__(self, *args, **kwargs) :

		''' Imports '''
		from app.models import TDossier

		# Je déclare les éléments du tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)

		super(GererDossier_Reglementation, self).__init__(*args, **kwargs)

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = None
		try :
			obj_doss = TDossier.objects.get(id_doss = k_doss)
		except :
			pass

		# Je définis la valeur initiale du formulaire.
		if obj_doss is not None :
			self.fields['zs_comm_regl_doss'].initial = obj_doss.comm_regl_doss

class ChoisirDossier(forms.Form) :

	# Je définis les champs du formulaire.
	zl_org_moa = forms.ChoiceField(
		label = 'Maître d\'ouvrage',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zld_progr = forms.ChoiceField(
		label = 'Programme',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zld_axe = forms.ChoiceField(
		choices = list(OPTION_INITIALE),
		label = 'Axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_ss_axe = forms.ChoiceField(
		choices = list(OPTION_INITIALE),
		label = 'Sous-axe',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_act = forms.ChoiceField(
		choices = list(OPTION_INITIALE),
		label = 'Action',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zl_nat_doss = forms.ChoiceField(
		label = 'Nature du dossier',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zl_ann_delib_moa_doss = forms.ChoiceField(
		label = 'Année de délibération au maître d\'ouvrage du dossier',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	def __init__(self, *args, **kwargs) :

		''' Imports '''
		from app.functions import init_tab_annees
		from app.models import TAction
		from app.models import TAxe
		from app.models import TMoa
		from app.models import TNatureDossier
		from app.models import TProgramme
		from app.models import TSousAxe
		
		super(ChoisirDossier, self).__init__(*args, **kwargs)

		# J'alimente la liste déroulante des maîtres d'ouvrages en activité.
		les_org_moa = list(OPTION_INITIALE)
		les_org_moa.extend([(i.id_org_moa.id_org, i.id_org_moa.n_org) for i in TMoa.objects.filter(
			en_act = 1
		).order_by('id_org_moa__n_org')])
		self.fields['zl_org_moa'].choices = les_org_moa
		
		# J'alimente la liste déroulante des programmes.
		les_progr = list(OPTION_INITIALE)
		les_progr.extend([(i.id_progr, i.int_progr) for i in TProgramme.objects.order_by('int_progr')])
		self.fields['zld_progr'].choices = les_progr

		# J'alimente la liste déroulante des natures de dossiers.
		les_nat_doss = list(OPTION_INITIALE)
		les_nat_doss.extend([(i.id_nat_doss, i.int_nat_doss) for i in TNatureDossier.objects.order_by('int_nat_doss')])
		self.fields['zl_nat_doss'].choices = les_nat_doss

		# J'alimente la liste déroulante des années de délibération au maître d'ouvrage.
		les_ann_delib_moa_doss = list(OPTION_INITIALE)
		les_ann_delib_moa_doss.extend([(i, i) for i in init_tab_annees()])
		self.fields['zl_ann_delib_moa_doss'].choices = les_ann_delib_moa_doss

class GererPhoto(forms.Form) :

	''' Imports '''
	from app.validators import valid_cdc

	# Je définis les champs du formulaire.
	za_num_doss = forms.CharField(
		label = 'Numéro du dossier',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zs_int_ph = forms.CharField(
		label = 'Intitulé de la photo',
		validators = [valid_cdc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zs_descr_ph = forms.CharField(
		label = 'Description de la photo',
		required = False,
		validators = [valid_cdc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zl_ppv_ph = forms.ChoiceField(
		label = 'Période de la prise de vue de la photo',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zd_dt_pv_ph = forms.DateField(
		label = 'Date de la prise de vue de la photo',
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zu_chem_ph = forms.FileField(
		label = 'Photo',
		widget = forms.FileInput(attrs = { 'class' : 'input-file' })
	)

	za_chem_ph = forms.CharField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True, 'type' : 'hidden' })
	)

	def __init__(self, *args, **kwargs) :

		''' Imports '''
		from app.functions import reecr_dt
		from app.models import TDossier, TPeriodePriseVuePhoto, TPhoto
		from styx.settings import MEDIA_URL

		# Je déclare les éléments du tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)
		k_ph = kwargs.pop('k_ph', None)
		k_modif = kwargs.pop('k_modif', False)

		super(GererPhoto, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += CHAMP_REQUIS 

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = None
		try :
			obj_doss = TDossier.objects.get(id_doss = k_doss)
		except :
			pass

		# Je vérifie l'existence d'un objet TPhoto.
		obj_ph = None
		try :
			obj_ph = TPhoto.objects.get(id_ph = k_ph)
		except :
			pass

		# Je définis les valeurs initiales du formulaire.
		if obj_doss is not None :
			self.fields['za_num_doss'].initial = obj_doss.num_doss

		if obj_ph is not None :
			self.fields['za_num_doss'].initial = obj_ph.id_doss.num_doss
			self.fields['zs_int_ph'].initial = obj_ph.int_ph
			self.fields['zs_descr_ph'].initial = obj_ph.descr_ph
			self.fields['zl_ppv_ph'].initial = obj_ph.id_ppv_ph.id_ppv_ph
			self.fields['zd_dt_pv_ph'].initial = reecr_dt(obj_ph.dt_pv_ph)

			# J'initialise l'attribut "title" de la zone d'upload de la photo.
			if obj_ph.chem_ph is not None :
				self.fields['zu_chem_ph'].widget.attrs['title'] = MEDIA_URL + obj_ph.chem_ph
				self.fields['za_chem_ph'].initial = MEDIA_URL + obj_ph.chem_ph

		if k_modif == True :
			self.fields['zu_chem_ph'].required = False

		# J'alimente la liste déroulante des périodes de prise de vue d'une photo.
		les_ppv_ph = list(OPTION_INITIALE)
		les_ppv_ph.extend([(i.id_ppv_ph, i.int_ppv_ph) for i in TPeriodePriseVuePhoto.objects.order_by(
			'int_ppv_ph')]
		)
		self.fields['zl_ppv_ph'].choices = les_ppv_ph

	def clean(self) :

		''' Imports '''
		from app.functions import nett_val, valid_zl
		from app.models import TDossier

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererPhoto, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_ppv_ph = cleaned_data.get('zl_ppv_ph')
		v_obj_ph = nett_val(cleaned_data.get('zu_chem_ph'))
		v_ph = nett_val(cleaned_data.get('za_chem_ph'))

		# Je vérifie l'existence d'un objet TDossier.
		try :
			TDossier.objects.get(num_doss = v_num_doss)
		except :
			self.add_error('za_num_doss', MESSAGES['invalid'])

		# Je vérifie la valeur de chaque liste déroulante obligatoire du formulaire.
		v_ppv_ph = valid_zl(self, 'zl_ppv_ph', v_ppv_ph)

		if v_obj_ph is not None :

			# Je vérifie l'extension du fichier image.
			if v_obj_ph.name.endswith(('.bmp', '.gif', '.jpg', '.jpeg', '.png')) == False :
				self.add_error('zu_chem_ph', 'Les formats autorisés sont BMP, GIF, JPG, JPEG et PNG.')

			# Je vérifie le poids du fichier image.
			POIDS_IMG_MO = 3
			if v_obj_ph.size > 1048576 * POIDS_IMG_MO :
				self.add_error('zu_chem_ph', 'Veuillez choisir un fichier de moins de {0} Mo.'.format(POIDS_IMG_MO))

		else :
			if v_ph is None :

				# Je vérifie le renseignement du fichier image dans le cas d'une modification. Je demande le 
				# renseignement du champ si et seulement si j'ai appuyé sur le bouton "Retirer".
				self.add_error('zu_chem_ph', MESSAGES['required'])

class GererArrete(forms.Form) :

	''' Imports '''
	from app.validators import valid_int

	# Je définis les champs du formulaire.
	za_num_doss = forms.CharField(
		label = 'Numéro du dossier',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	za_int_type_decl = forms.CharField(
		label = 'Intitulé de l\'arrêté',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zl_type_av_arr = forms.ChoiceField(
		label = 'Avancement',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zs_num_arr = forms.CharField(
		label = 'Numéro de l\'arrêté',
		validators = [valid_int],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zd_dt_sign_arr = forms.DateField(
		label = 'Date de signature de l\'arrêté',
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zd_dt_lim_encl_trav_arr = forms.DateField(
		label = 'Date limite d\'enclenchement des travaux',
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zu_chem_pj_arr = forms.FileField(
		label = 'Fichier scanné de l\'arrêté',
		widget = forms.FileInput(attrs = { 'class' : 'input-file' })
	)

	za_chem_pj_arr = forms.CharField(
		label = '',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True, 'type' : 'hidden' })
	)

	def __init__(self, *args, **kwargs) :

		''' Imports '''
		from app.functions import reecr_dt
		from app.models import TArretesDossier, TDossier, TTypeAvancementArrete, TTypeDeclaration
		from styx.settings import MEDIA_URL

		# Je déclare les éléments du tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)
		k_arr = kwargs.pop('k_arr', None)
		k_modif = kwargs.pop('k_modif', False)

		super(GererArrete, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += CHAMP_REQUIS

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = None
		try :
			obj_doss = TDossier.objects.get(id_doss = k_doss)
		except :
			pass

		# Je vérifie l'existence d'un objet TTypeDeclaration.
		obj_arr = None
		try :
			obj_arr = TTypeDeclaration.objects.get(id_type_decl = k_arr)
		except :
			pass

		# Je vérifie l'existence d'un objet TArretesDossier.
		obj_arr_doss = None
		try :
			obj_arr_doss = TArretesDossier.objects.get(id_doss = obj_doss, id_type_decl = obj_arr)
		except :
			pass

		# Je définis les valeurs initiales du formulaire.
		if obj_doss is not None and obj_arr is not None :
			self.fields['za_num_doss'].initial = obj_doss.num_doss
			self.fields['za_int_type_decl'].initial = obj_arr.int_type_decl

		if obj_arr_doss is not None :
			self.fields['zl_type_av_arr'].initial = obj_arr_doss.id_type_av_arr.id_type_av_arr
			self.fields['zs_num_arr'].initial = obj_arr_doss.num_arr
			self.fields['zd_dt_sign_arr'].initial = reecr_dt(obj_arr_doss.dt_sign_arr)
			self.fields['zd_dt_lim_encl_trav_arr'].initial = reecr_dt(obj_arr_doss.dt_lim_encl_trav_arr)

			# J'initialise l'attribut "title" de la zone d'upload du fichier scanné de l'arrêté.
			if obj_arr_doss.chem_pj_arr is not None :
				self.fields['zu_chem_pj_arr'].widget.attrs['title'] = MEDIA_URL + obj_arr_doss.chem_pj_arr
				self.fields['za_chem_pj_arr'].initial = MEDIA_URL + obj_arr_doss.chem_pj_arr

		if k_modif == True :
			self.fields['zu_chem_pj_arr'].required = False

		# J'alimente la liste déroulante des types d'avancements d'un arrêté.
		les_type_av_arr = list(OPTION_INITIALE)
		les_type_av_arr.extend([(i.id_type_av_arr, i.int_type_av_arr) for i in TTypeAvancementArrete.objects.order_by(
			'int_type_av_arr')]
		)
		self.fields['zl_type_av_arr'].choices = les_type_av_arr

	def clean(self) :

		''' Imports '''
		from app.functions import nett_val, valid_zl

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererArrete, self).clean()
		v_type_av_arr = cleaned_data.get('zl_type_av_arr')
		v_obj_arr = nett_val(cleaned_data.get('zu_chem_pj_arr'))
		v_arr = nett_val(cleaned_data.get('za_chem_pj_arr'))

		# Je vérifie la valeur de chaque liste déroulante obligatoire du formulaire.
		v_type_av_arr = valid_zl(self, 'zl_type_av_arr', v_type_av_arr)

		if v_obj_arr is not None :

			# Je vérifie l'extension du fichier de l'arrêté.
			if v_obj_arr.name.endswith('.pdf') == False :
				self.add_error('zu_chem_pj_arr', 'Veuillez choisir un fichier au format PDF.')

		else :
			if v_arr is None :

				# Je vérifie le renseignement du fichier scanné de l'arrêté dans le cas d'une modification. Je demande
				# le renseignement du champ si et seulement si j'ai appuyé sur le bouton "Retirer".
				self.add_error('zu_chem_pj_arr', MESSAGES['required'])

class GererFinancement(forms.Form) :

	''' Imports '''
	from app.validators import valid_cdc, valid_int, valid_mont, valid_pourc

	# Je définis les champs du formulaire.
	za_num_doss = forms.CharField(
		label = 'Numéro du dossier',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zl_org_fin = forms.ChoiceField(
		label = 'Organisme financeur',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zs_int_fin = forms.CharField(
		label = 'Intitulé du financement',
		validators = [valid_cdc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zs_mont_ht_elig_fin = forms.CharField(
		label = 'Montant HT de l\'assiette éligible de la subvention',
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_mont_ttc_elig_fin = forms.CharField(
		label = 'Montant TTC de l\'assiette éligible de la subvention',
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_pourc_elig_fin = forms.CharField(
		label = 'Pourcentage de l\'assiette éligible',
		validators = [valid_pourc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_mont_ht_tot_subv_fin = forms.CharField(
		label = 'Montant HT total de la subvention',
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_mont_ttc_tot_subv_fin = forms.CharField(
		label = 'Montant TTC total de la subvention',
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zd_dt_deb_elig_fin = forms.DateField(
		label = 'Date de début d\'éligibilité',
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zs_duree_valid_fin = forms.CharField(
		label = 'Durée de validité (en mois)',
		validators = [valid_int],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zs_duree_pror_fin = forms.CharField(
		label = 'Durée de la prorogation (en mois)',
		required = False,
		validators = [valid_int],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zd_dt_lim_deb_oper_fin = forms.DateField(
		label = 'Date limite du début de l\'opération',
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zd_dt_lim_prem_ac_fin = forms.DateField(
		label = 'Date limite du premier acompte',
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zl_paiem_prem_ac = forms.ChoiceField(
		label = 'Premier acompte payé en fonction de',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zs_pourc_real_fin = forms.CharField(
		label = 'Pourcentage de réalisation des travaux',
		required = False,
		validators = [valid_pourc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zu_chem_pj_fin = forms.FileField(
		label = 'Fichier PDF de l\'arrêté de subvention',
		required = False,
		widget = forms.FileInput(attrs = { 'class' : 'input-file' })
	)

	zs_comm_fin = forms.CharField(
		label = 'Commentaire',
		required = False,
		validators = [valid_cdc],
		widget = forms.Textarea(attrs = {'class' : 'form-control', 'maxlength' : 255, 'rows' : 5 })
	)

	def __init__(self, *args, **kwargs) :

		''' Imports '''
		from app.models import TDossier, TFinanceur, TPaiementPremierAcompte

		# Je déclare les éléments du tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)
		k_fin = kwargs.pop('k_fin', None)

		super(GererFinancement, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += CHAMP_REQUIS

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = None
		try :
			obj_doss = TDossier.objects.get(id_doss = k_doss)
		except :
			pass

		# Je définis la valeur initiale du formulaire.
		if obj_doss is not None :
			self.fields['za_num_doss'].initial = obj_doss.num_doss

		# J'alimente la liste déroulante des financeurs.
		les_org_fin = list(OPTION_INITIALE)
		les_org_fin.extend([(i.id_org_fin.id_org, i.id_org_fin.n_org) for i in TFinanceur.objects.order_by(
			'id_org_fin__n_org')
		])
		self.fields['zl_org_fin'].choices = les_org_fin

		# J'alimente la liste déroulante des types de paiements du premier acompte.
		les_paiem_prem_ac = list(OPTION_INITIALE)
		les_paiem_prem_ac.extend([(i.id_paiem_prem_ac, i.int_paiem_prem_ac)
			for i in TPaiementPremierAcompte.objects.order_by('int_paiem_prem_ac')]
		)
		self.fields['zl_paiem_prem_ac'].choices = les_paiem_prem_ac

	def clean(self) :

		''' Imports '''
		from app.functions import float_to_int, nett_val, valid_zl
		from app.models import TDossier, TFinancement
		from app.sql_views import VSuiviDossier

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererFinancement, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_org_fin = cleaned_data.get('zl_org_fin')
		v_mont_ht_elig_fin = cleaned_data.get('zs_mont_ht_elig_fin')
		v_mont_ttc_elig_fin = cleaned_data.get('zs_mont_ttc_elig_fin')
		v_pourc_elig_fin = cleaned_data.get('zs_pourc_elig_fin')
		v_mont_ht_tot_subv_fin = cleaned_data.get('zs_mont_ht_tot_subv_fin')
		v_mont_ttc_tot_subv_fin = cleaned_data.get('zs_mont_ttc_tot_subv_fin')
		v_paiem_prem_ac = cleaned_data.get('zl_paiem_prem_ac')
		v_obj_fin = nett_val(cleaned_data.get('zu_chem_pj_fin'))

		# Je vérifie la valeur de chaque liste déroulante obligatoire du formulaire.
		v_org_fin = valid_zl(self, 'zl_org_fin', v_org_fin)
		v_paiem_prem_ac = valid_zl(self, 'zl_paiem_prem_ac', v_paiem_prem_ac)

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = None
		try :
			obj_doss = TDossier.objects.get(num_doss = v_num_doss)
		except :
			self.add_error('za_num_doss', MESSAGES['invalid'])

		if obj_doss is not None :

			# Je récupère les restes à financer.
			obj_suivi_doss = VSuiviDossier.objects.get(id_doss = obj_doss.id_doss)
			v_mont_ht_raf = obj_suivi_doss.mont_ht_raf
			v_mont_ttc_raf = obj_suivi_doss.mont_ttc_raf

			# Je gère la contrainte suivante : le montant éligible doit être inférieur ou égal à la différence du montant
			# du dossier et de la somme des montants éligibles.
			if v_mont_ht_elig_fin is not None :
				if float(v_mont_ht_elig_fin) > float(v_mont_ht_raf) :
					self.add_error(
						'zs_mont_ht_elig_fin',
						'Veuillez saisir un montant HT inférieur ou égal à {0} €.'.format(float_to_int(v_mont_ht_raf))
					)

			if v_mont_ttc_elig_fin is not None :
				if float(v_mont_ttc_elig_fin) > float(v_mont_ttc_raf) :
					self.add_error(
						'zs_mont_ttc_elig_fin',
						'Veuillez saisir un montant TTC inférieur ou égal à {0} €.'.format(float_to_int(v_mont_ttc_raf))
					)

			# Je gère la contrainte suivante : le montant de la subvention ne peut être supérieur au montant éligible.
			if v_pourc_elig_fin is not None :
				if float(v_mont_ht_tot_subv_fin) > float(v_mont_ht_elig_fin) :
					self.add_error(
						'zs_mont_ht_tot_subv_fin',
						'Le montant HT total de la subvention ne peut être supérieur au montant HT éligible.'
					)

				if float(v_mont_ttc_tot_subv_fin) > float(v_mont_ttc_elig_fin) :
					self.add_error(
						'zs_mont_ttc_tot_subv_fin',
						'Le montant TTC total de la subvention ne peut être supérieur au montant TTC éligible.'
					)

			# Je vérifie que le financeur sélectionné ne participe pas déjà au montage financier.
			if v_org_fin > 0 :
				try :
					TFinancement.objects.get(id_doss = obj_doss.id_doss, id_org_fin = v_org_fin)
					self.add_error(
						'zl_org_fin',
						'Le financeur participe déjà au montage financier.'
					)
				except :
					pass

			# Je vérifie l'extension du fichier de l'arrêté.
			if v_obj_fin is not None :
				if v_obj_fin.name.endswith('.pdf') == False :
					self.add_error('zu_chem_pj_fin', 'Veuillez choisir un fichier au format PDF.')

class GererPrestation(forms.Form) :

	''' Imports '''
	from app.validators import valid_cdc, valid_mont, valid_siret

	# Je définis les champs du formulaire.
	za_num_doss = forms.CharField(
		label = 'Numéro du dossier',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zs_siret_org_prest = forms.CharField(
		label = 'Numéro SIRET du prestataire',
		validators = [valid_siret],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 14 })
	)

	zs_int_prest = forms.CharField(
		label = 'Intitulé de la prestation',
		validators = [valid_cdc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'maxlength' : 255 })
	)

	zs_mont_ht_tot_prest = forms.CharField(
		label = 'Montant HT total de la prestation',
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_mont_ttc_tot_prest = forms.CharField(
		label = 'Montant TTC total de la prestation',
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zd_dt_notif_prest = forms.DateField(
		label = 'Date de notification de la prestation',
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zd_dt_fin_prest = forms.DateField(
		label = 'Date de fin de la prestation',
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	za_mont_ht_raf = forms.CharField(
		label = 'Montant HT restant à facturer',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	za_mont_ttc_raf = forms.CharField(
		label = 'Montant TTC restant à facturer',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zl_nat_prest = forms.ChoiceField(
		label = 'Nature de la prestation',
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zu_chem_pj_prest = forms.FileField(
		label = 'Fichier PDF de la prestation',
		required = False,
		widget = forms.FileInput(attrs = { 'class' : 'input-file' })
	)

	zs_comm_prest = forms.CharField(
		label = 'Commentaire',
		required = False,
		validators = [valid_cdc],
		widget = forms.Textarea(attrs = {
			'class' : 'form-control',
			'maxlength' : 255,
			'rows' : 5
		})
	)

	def __init__(self, *args, **kwargs) :

		''' Imports '''
		from app.models import TDossier, TNaturePrestation

		# Je déclare les éléments du tableau des arguments.
		k_doss = kwargs.pop('k_doss', None)

		super(GererPrestation, self).__init__(*args, **kwargs)

		# J'ajoute un astérisque au label de chaque champ obligatoire. De plus, je définis les messages d'erreurs
		# personnalisés à chaque champ.
		for cle, valeur in self.fields.items() :
			self.fields[cle].error_messages = MESSAGES
			if self.fields[cle].required == True :
				self.fields[cle].label += CHAMP_REQUIS

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = None
		try :
			obj_doss = TDossier.objects.get(id_doss = k_doss)
		except :
			pass

		# Je définis la valeur initiale du formulaire.
		if obj_doss is not None :
			self.fields['za_num_doss'].initial = obj_doss.num_doss

		# J'alimente la liste déroulante des natures de prestations.
		les_nat_prest = list(OPTION_INITIALE)
		les_nat_prest.extend([(i.id_nat_prest, i.int_nat_prest) for i in TNaturePrestation.objects.all().order_by(
			'int_nat_prest')
		])
		self.fields['zl_nat_prest'].choices = les_nat_prest

	def clean(self) :

		''' Imports '''
		from app.functions import float_to_int, valid_zl
		from app.models import TDossier, TPrestataire
		from app.sql_views import VSuiviDossier

		# Je récupère certaines données du formulaire pré-valide.
		cleaned_data = super(GererPrestation, self).clean()
		v_num_doss = cleaned_data.get('za_num_doss')
		v_siret_org_prest = cleaned_data.get('zs_siret_org_prest')
		v_mont_ht_tot_prest = cleaned_data.get('zs_mont_ht_tot_prest')
		v_mont_ttc_tot_prest = cleaned_data.get('zs_mont_ttc_tot_prest')
		v_nat_prest = cleaned_data.get('zl_nat_prest')

		# Je vérifie la valeur de chaque liste déroulante obligatoire du formulaire.
		v_nat_prest = valid_zl(self, 'zl_nat_prest', v_nat_prest)

		# Je vérifie l'existence d'un objet TDossier.
		obj_doss = None
		try :
			obj_doss = TDossier.objects.get(num_doss = v_num_doss)
		except :
			self.add_error('za_num_doss', MESSAGES['invalid'])

		if obj_doss is not None :

			# Je récupère les restes à utiliser.
			obj_suivi_doss = VSuiviDossier.objects.get(id_doss = obj_doss.id_doss)
			v_mont_ht_rau = obj_suivi_doss.mont_ht_rau
			v_mont_ttc_rau = obj_suivi_doss.mont_ttc_rau

			# Je renvoie une erreur si le numéro SIRET saisi appartient à aucun objet TPrestataire.
			try :
				TPrestataire.objects.get(siret_org_prest = v_siret_org_prest)
			except :
				self.add_error(
					'zs_siret_org_prest',
					'Le numéro SIRET appartient à aucun prestataire.'
				)

			# Je gère la contrainte suivante : le montant total de la prestation doit être inférieur ou égal au reste 
			# à utiliser du dossier.
			if v_mont_ht_tot_prest is not None :
				if float(v_mont_ht_tot_prest) > float(v_mont_ht_rau) :
					self.add_error(
						'zs_mont_ht_tot_prest',
						'Veuillez saisir un montant HT inférieur ou égal à {0} €.'.format(float_to_int(v_mont_ht_rau))
					)

			if v_mont_ttc_tot_prest is not None :
				if float(v_mont_ttc_tot_prest) > float(v_mont_ttc_rau) :
					self.add_error(
						'zs_mont_ttc_tot_prest',
						'Veuillez saisir un montant TTC inférieur ou égal à {0} €.'.format(float_to_int(v_mont_ttc_rau))
					)