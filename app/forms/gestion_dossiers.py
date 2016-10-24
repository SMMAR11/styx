from app.constants import *
from app.functions import *
from app.models import *
from app.validators import *
from django import forms

class ChoisirDossier(forms.Form) :

	# Je définis les champs du formulaire.
	zl_moa = forms.ChoiceField(
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

	zl_annee_delib_moa_doss = forms.ChoiceField(
		label = 'Année de délibération au maître d\'ouvrage du dossier',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	def __init__(self, *args, **kwargs) :
		
		super(ChoisirDossier, self).__init__(*args, **kwargs)

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		les_moa = list(OPTION_INITIALE)
		les_moa.extend([(i.id_org_moa.id_org, i.id_org_moa.n_org) 
			for i in TMoa.objects.filter(en_act = 1).order_by('id_org_moa__n_org')]
		)
		self.fields['zl_moa'].choices = les_moa
		
		# J'alimente la liste déroulante des programmes.
		les_programmes = list(OPTION_INITIALE)
		les_programmes.extend([(i.id_progr, i.int_progr) 
			for i in TProgramme.objects.order_by('int_progr')]
		)
		self.fields['zld_progr'].choices = les_programmes

		# J'alimente la liste déroulante des natures de dossier.
		les_natures_dossier = list(OPTION_INITIALE)
		les_natures_dossier.extend([(i.id_nat_doss, i.int_nat_doss) 
			for i in TNatureDossier.objects.order_by('int_nat_doss')]
		)
		self.fields['zl_nat_doss'].choices = les_natures_dossier

		# J'alimente la liste déroulante des années.
		les_annees_creation_dossier = list(OPTION_INITIALE)
		les_annees_creation_dossier.extend([(i, i) 
			for i in init_tab_annees()]
		)
		self.fields['zl_annee_delib_moa_doss'].choices = les_annees_creation_dossier

class GererDossier(forms.Form) :

	# Je définis les champs du formulaire.
	za_num_doss = forms.CharField(
		error_messages = MESSAGES,
		label = 'Numéro du dossier',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zs_int_doss = forms.CharField(
		error_messages = MESSAGES,
		label = 'Intitulé du dossier' + CHAMP_REQUIS,
		validators = [valid_cdc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_descr_doss = forms.CharField(
		error_messages = MESSAGES,
		label = 'Description du dossier et de ses objectifs',
		required = False,
		validators = [valid_cdc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	za_doss_ass = forms.CharField(
		error_messages = MESSAGES,
		label = 'Dossier associé',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zl_moa = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Maître d\'ouvrage' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zld_progr = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Programme' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zld_axe = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Axe' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_ss_axe = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Sous-axe' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_act = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Action' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control hide-field' })
	)

	zld_type_doss = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Type du dossier' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zl_nat_doss = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Nature du dossier' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zl_techn = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Technicien' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zs_mont_ht_doss = forms.CharField(
		error_messages = MESSAGES,
		label = 'Montant HT du dossier (en €)' + CHAMP_REQUIS,
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_mont_ttc_doss = forms.CharField(
		error_messages = MESSAGES,
		label = 'Montant TTC du dossier (en €)' + CHAMP_REQUIS,
		validators = [valid_mont],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zl_av = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'État d\'avancement du dossier' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zd_dt_delib_moa_doss = forms.DateField(
		error_messages = MESSAGES,
		label = 'Date de délibération au maître d\'ouvrage',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zl_av_cp = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Avis du comité de programmation' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zd_dt_av_cp_doss = forms.DateField(
		error_messages = MESSAGES,
		label = 'Date de l\'avis du comité de programmation' + CHAMP_REQUIS,
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zu_chem_dds_doss = forms.FileField(
		error_messages = MESSAGES,
		label = 'Fichier scanné du DDS',
		required = False,
		widget = forms.FileInput(attrs = {'class' : 'input-file'})
	)

	zs_comm_doss = forms.CharField(
		label = 'Commentaire',
		required = False,
		validators = [valid_cdc],
		widget = forms.Textarea(attrs = {
			'class' : 'form-control',
			'rows' : '5'
		})
	)

	# Je définis les champs PGRE du formulaire.
	zs_quant_objs_pgre = forms.CharField(
		error_messages = MESSAGES,
		label = 'Quantification des objectifs',
		required = False,
		validators = [valid_nb],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_quant_real_pgre = forms.CharField(
		error_messages = MESSAGES,
		label = 'Réalisé',
		required = False,
		validators = [valid_nb],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zl_unit = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Unité',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	cbsm_riv = forms.MultipleChoiceField(
		error_messages = MESSAGES,
		label = 'Rivières impactées',
		required = False,
		widget = forms.CheckboxSelectMultiple()
	)

	zl_port = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Portée du dossier',
		required = False,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	def __init__(self, *args, **kwargs) :

		# Je déclare les éléments du tableau des arguments.
		k_dossier = kwargs.pop('k_dossier', None)
		k_intitule_dossier = kwargs.pop('k_intitule_dossier', None)
		k_description_dossier = kwargs.pop('k_description_dossier', None)
		k_dossier_associe = kwargs.pop('k_dossier_associe', None)
		k_moa = kwargs.pop('k_moa', -1)
		k_programme = kwargs.pop('k_programme', -1)
		k_axe = kwargs.pop('k_axe', -1)
		k_sous_axe = kwargs.pop('k_sous_axe', -1)
		k_action = kwargs.pop('k_action', -1)
		k_type_dossier = kwargs.pop('k_type_dossier', -1)
		k_nature_dossier = kwargs.pop('k_nature_dossier', -1)
		k_technicien = kwargs.pop('k_technicien', -1)
		k_montant_ht_dossier = kwargs.pop('k_montant_ht_dossier', None)
		k_montant_ttc_dossier = kwargs.pop('k_montant_ttc_dossier', None)
		k_avancement = kwargs.pop('k_avancement', -1)
		k_date_deliberation_moa_dossier = kwargs.pop('k_date_deliberation_moa_dossier', None)
		k_avis_cp = kwargs.pop('k_avis_cp', -1)
		k_date_avis_cp_dossier = kwargs.pop('k_date_avis_cp_dossier', None)
		k_commentaire_dossier = kwargs.pop('k_commentaire_dossier', None)
		k_quantification_objectifs = kwargs.pop('k_quantification_objectifs', None)
		k_quantification_realisee = kwargs.pop('k_quantification_realisee', None)
		k_unite = kwargs.pop('k_unite', -1)
		k_portee = kwargs.pop('k_portee', -1)

		super(GererDossier, self).__init__(*args, **kwargs)

		# Je définis les valeurs par défaut des champs du formulaire.
		self.fields['za_num_doss'].initial = k_dossier
		self.fields['zs_int_doss'].initial = k_intitule_dossier
		self.fields['zs_descr_doss'].initial = k_description_dossier
		self.fields['za_doss_ass'].initial = k_dossier_associe
		self.fields['zl_moa'].initial = k_moa
		self.fields['zld_progr'].initial = k_programme
		self.fields['zld_axe'].initial = k_axe
		self.fields['zld_ss_axe'].initial = k_sous_axe
		self.fields['zld_act'].initial = k_action
		self.fields['zld_type_doss'].initial = k_type_dossier
		self.fields['zl_nat_doss'].initial = k_nature_dossier
		self.fields['zl_techn'].initial = k_technicien
		self.fields['zs_mont_ht_doss'].initial = float_to_int(k_montant_ht_dossier)
		self.fields['zs_mont_ttc_doss'].initial = float_to_int(k_montant_ttc_dossier)
		self.fields['zl_av'].initial = k_avancement
		self.fields['zd_dt_delib_moa_doss'].initial = reecr_dt(k_date_deliberation_moa_dossier)
		self.fields['zl_av_cp'].initial = k_avis_cp
		self.fields['zd_dt_av_cp_doss'].initial = reecr_dt(k_date_avis_cp_dossier)
		self.fields['zs_comm_doss'].initial = k_commentaire_dossier
		self.fields['zs_quant_objs_pgre'].initial = float_to_int(k_quantification_objectifs, 0)
		self.fields['zs_quant_real_pgre'].initial = float_to_int(k_quantification_realisee, 0)
		self.fields['zl_unit'].initial = k_unite
		self.fields['zl_port'].initial = k_portee

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		if k_moa > 0 :
			les_moa = list([(i.id_org_moa.id_org, i.id_org_moa.n_org) 
				for i in TMoa.objects.filter(id_org_moa = k_moa)])
		else :
			les_moa = list(OPTION_INITIALE)
			les_moa.extend([(i.id_org_moa.id_org, i.id_org_moa.n_org) 
				for i in TMoa.objects.filter(en_act = 1).order_by('id_org_moa__n_org')]
			)	
		self.fields['zl_moa'].choices = les_moa
		
		# J'alimente la liste déroulante des programmes.
		if k_programme > 0 :
			les_programmes = list([(i.id_progr, i.int_progr) 
				for i in TProgramme.objects.filter(id_progr = k_programme)])
		else :
			les_programmes = list(OPTION_INITIALE)
			les_programmes.extend([(i.id_progr, i.int_progr) 
				for i in TProgramme.objects.order_by('int_progr')]
			)
		self.fields['zld_progr'].choices = les_programmes

		# Je commence à alimenter la liste déroulante des axes.
		les_axes = list([(i.id_axe, i.id_axe) 
			for i in TAxe.objects.filter(id_progr = k_programme).order_by('id_axe')]
		)

		# Je gère la valeur de l'option par défaut de la liste déroulante des axes ainsi que l'affichage de celle-ci.
		if len(les_axes) > 0 :

			# J'insère l'option par défaut.
			les_axes.insert(0, [
				OPTION_INITIALE[0][0],
				OPTION_INITIALE[0][1]
			])

			# J'ajoute la classe show-field-temp qui permet d'afficher la liste déroulante des axes.
			self.fields['zld_axe'].widget.attrs['class'] += ' show-field-temp'

		else :

			# J'insère l'option par défaut qui permet de bypasser la validation du contrôle (car la liste déroulante
			# des axes n'admet aucune option).
			les_axes.insert(0, [
				'DBP',
				OPTION_INITIALE[0][1]
			])

		self.fields['zld_axe'].choices = les_axes

		# Je commence à alimenter la liste déroulante des sous-axes.
		les_sous_axes = list([(i.id_ss_axe, i.id_ss_axe) 
			for i in TSousAxe.objects.filter(id_progr = k_programme, id_axe = k_axe).order_by('id_ss_axe')]
		)

		# Je gère la valeur de l'option par défaut de la liste déroulante des sous-axes ainsi que l'affichage de 
		# celle-ci.
		if len(les_sous_axes) > 0 :

			# J'insère l'option par défaut.
			les_sous_axes.insert(0, [
				OPTION_INITIALE[0][0],
				OPTION_INITIALE[0][1]
			])

			# J'ajoute la classe show-field-temp qui permet d'afficher la liste déroulante des sous-axes.
			self.fields['zld_ss_axe'].widget.attrs['class'] += ' show-field-temp'

		else :

			# J'insère l'option par défaut qui permet de bypasser la validation du contrôle (car la liste déroulante
			# des sous-axes n'admet aucune option).
			les_sous_axes.insert(0, [
				'DBP',
				OPTION_INITIALE[0][1]
			])

		self.fields['zld_ss_axe'].choices = les_sous_axes

		# Je commence à alimenter la liste déroulante des actions.
		les_actions = list([(i.id_act, i.id_act) 
			for i in TAction.objects.all().filter(
				id_progr = k_programme,
				id_axe = k_axe,
				id_ss_axe = k_sous_axe
			).order_by('id_act')]
		)

		# Je gère la valeur de l'option par défaut de la liste déroulante des actions ainsi que l'affichage de 
		# celle-ci.
		if len(les_actions) > 0 :

			# J'insère l'option par défaut.
			les_actions.insert(0, [
				OPTION_INITIALE[0][0],
				OPTION_INITIALE[0][1]
			])

			# J'ajoute la classe show-field-temp qui permet d'afficher la liste déroulante des actions.
			self.fields['zld_act'].widget.attrs['class'] += ' show-field-temp'

		else :

			# J'insère l'option par défaut qui permet de bypasser la validation du contrôle (car la liste déroulante
			# des actions n'admet aucune option).
			les_actions.insert(0, [
				'DBP',
				OPTION_INITIALE[0][1]
			])

		self.fields['zld_act'].choices = les_actions

		# J'alimente la liste déroulante des types de dossiers.
		les_types_dossier = list(OPTION_INITIALE)
		les_types_dossier.extend([(i.id_type_doss, i.int_type_doss) 
			for i in TTypeDossier.objects.filter(id_progr = k_programme).order_by('int_type_doss')]
		)
		self.fields['zld_type_doss'].choices = les_types_dossier

		# J'alimente la liste déroulante des natures de dossiers.
		les_natures_dossier = list(OPTION_INITIALE)
		les_natures_dossier.extend([(i.id_nat_doss, i.int_nat_doss) 
			for i in TNatureDossier.objects.order_by('int_nat_doss')]
		)
		self.fields['zl_nat_doss'].choices = les_natures_dossier

		# J'alimente la liste déroulante des techniciens.
		les_techniciens = list(OPTION_INITIALE)
		les_techniciens.extend([(i.id_techn, i.n_techn + ' ' + i.pren_techn) 
			for i in TTechnicien.objects.filter(en_act = 1).order_by('n_techn', 'pren_techn')]
		)
		self.fields['zl_techn'].choices = les_techniciens

		# J'alimente la liste déroulante des états d'avancement.
		les_avancements = list(OPTION_INITIALE)
		les_avancements.extend([(i.id_av, i.int_av) 
			for i in TAvancement.objects.order_by('int_av')]
		)
		self.fields['zl_av'].choices = les_avancements

		# J'alimente la liste déroulante des avis du comité de programmation.
		les_avis_cp = list(OPTION_INITIALE)
		les_avis_cp.extend([(i.id_av_cp, i.int_av_cp)
			for i in TAvisCp.objects.order_by('int_av_cp')]
		)
		self.fields['zl_av_cp'].choices = les_avis_cp

		# J'alimente la liste déroulante des unités.
		les_unites = list(OPTION_INITIALE)
		les_unites.extend([(i.id_unit, i.int_unit) 
			for i in TUnite.objects.order_by('int_unit')]
		)
		self.fields['zl_unit'].choices = les_unites

		# J'alimente la liste déroulante des rivières.
		les_rivieres = list([(i.id_riv, i.n_riv) 
			for i in TRiviere.objects.order_by('n_riv')]
		)
		les_rivieres.extend([('T', 'Toutes')]);
		self.fields['cbsm_riv'].choices = les_rivieres

		# Je vérifie l'existence d'un objet TProgramme.
		obj_programme = None
		try :
			obj_programme = TProgramme.objects.get(id_progr = k_programme)
		except :
			pass

		# Je coche les cases à cochées relatives aux rivières impactées par le dossier PGRE.
		if obj_programme is not None and obj_programme.int_progr == 'PGRE' :

			# Je stocke dans un tableau les rivières impactées par le dossier PGRE.
			obj_dossier_pgre = TPgre.objects.filter(id_pgre = TDossier.objects.get(num_doss = k_dossier).id_doss)
			les_rivieres_dossier = TRivieresDossier.objects.filter(id_pgre = obj_dossier_pgre)

			# Je créé un tableau contenant les identifiants des rivières impactées par le dossier PGRE.
			tab_cb_cochees = []
			for une_riviere_dossier in les_rivieres_dossier :
				tab_cb_cochees.append(une_riviere_dossier.id_riv.id_riv)

			# Je définis la valeur par défaut du champ "Rivières impactées".
			self.fields['cbsm_riv'].initial = tab_cb_cochees

		# J'alimente la liste déroulante des portées du dossier.
		les_portees = list(OPTION_INITIALE)
		les_portees.extend([(i.id_port, i.int_port)
			for i in TPortee.objects.order_by('int_port')]
		)
		self.fields['zl_port'].choices = les_portees

		# J'initialise l'état du contrôle lié à la date de délibération au maître d'ouvrage du dossier.
		if k_avancement > 0 :
			if TAvancement.objects.get(id_av = k_avancement).int_av == 'En projet' :
				self.fields['zd_dt_delib_moa_doss'].widget.attrs['disabled'] = True

	def clean(self) :

		# Je récupère les données utiles du formulaire pré-valide.
		tab_donnees = super(GererDossier, self).clean()
		v_dossier = nett_val(tab_donnees.get('za_num_doss'))
		v_dossier_associe = nett_val(tab_donnees.get('za_doss_ass'))
		v_moa = tab_donnees.get('zl_moa')
		v_programme = tab_donnees.get('zld_progr')
		v_axe = tab_donnees.get('zld_axe')
		v_sous_axe = tab_donnees.get('zld_ss_axe')
		v_action = tab_donnees.get('zld_act')
		v_type_dossier = tab_donnees.get('zld_type_doss')
		v_nature_dossier = tab_donnees.get('zl_nat_doss')
		v_technicien = tab_donnees.get('zl_techn')
		v_avis_cp = tab_donnees.get('zl_av_cp')
		v_avancement = tab_donnees.get('zl_av')
		v_date_deliberation_moa_dossier = tab_donnees.get('zd_dt_delib_moa_doss')
		v_quantification_objectifs = nett_val(tab_donnees.get('zs_quant_objs_pgre'))
		v_quantification_realisee = nett_val(tab_donnees.get('zs_quant_real_pgre'))
		v_unite = nett_val(integer(tab_donnees.get('zl_unit')))

		# Je vérifie la valeur de chaque liste déroulante du formulaire obligatoire.
		v_moa = valid_zl(self,'zl_moa', v_moa)
		v_programme = valid_zl(self, 'zld_progr', v_programme)
		v_axe = valid_zl(self, 'zld_progr', v_programme, 'zld_axe', v_axe)
		v_sous_axe = valid_zl(self, 'zld_axe', v_axe, 'zld_ss_axe', v_sous_axe)
		v_action = valid_zl(self, 'zld_ss_axe', v_sous_axe, 'zld_act', v_action)
		v_type_dossier = valid_zl(self, 'zld_type_doss', v_type_dossier)
		v_nature_dossier = valid_zl(self, 'zl_nat_doss', v_nature_dossier)
		v_technicien = valid_zl(self, 'zl_techn', v_technicien)
		v_avis_cp = valid_zl(self, 'zl_av_cp', v_avis_cp)
		v_avancement = valid_zl(self, 'zl_av', v_avancement)

		if v_avancement > -1 :
			if TAvancement.objects.get(id_av = v_avancement).int_av != 'En projet' :

				# Je renvoie une erreur lorsque la date de délibération au maître d'ouvrage d'un dossier dont l'état d'
				# avancement est différent de "En projet" n'est pas renseigné.
				if v_date_deliberation_moa_dossier is None :
					self.add_error('zd_dt_delib_moa_doss', MESSAGES['required'])

		# Je vérifie l'existence d'un objet TProgramme.
		obj_programme = None
		try :
			obj_programme = TProgramme.objects.get(id_progr = v_programme)
		except :
			pass

		# Je gère l'affichage des erreurs liées à la partie "quantification" si et seulement si le pagramme choisi est
		# "PGRE".
		if obj_programme is not None and obj_programme.int_progr == 'PGRE' :
			if v_quantification_objectifs is None :
				if v_unite > 0 or v_quantification_realisee is not None:
					self.add_error('zs_quant_objs_pgre', MESSAGES['required'])
			else :
				if v_unite < 0 :
					self.add_error('zl_unit', MESSAGES['required'])
				else :
					if v_quantification_realisee is not None :
						if float(v_quantification_realisee) > float(v_quantification_objectifs) :
							self.add_error(
								'zs_quant_real_pgre', 
								'La quantification des objectifs réalisée doit être inférieure ou égale à {0} {1}.'.format(
									v_quantification_objectifs,
									TUnite.objects.get(id_unit = v_unite).int_unit
								)
							)

		# Je renvoie une erreur si le dossier associé choisi correspond au dossier en cours de modification.
		if v_dossier is not None :
			if v_dossier == v_dossier_associe :
				self.add_error('za_doss_ass', 'Veuillez choisir un autre dossier associé.')

class GererDossier_Reglementation(forms.Form) :

	# Je définis le champ du formulaire.
	zs_comm_regl_doss = forms.CharField(
		label = 'Commentaire',
		required = False,
		validators = [valid_cdc],
		widget = forms.Textarea(attrs = {
			'class' : 'form-control',
			'rows' : '5'
		})
	)

	def __init__(self, *args, **kwargs) :

		# Je déclare les éléments du tableau des arguments.
		k_commentaire = kwargs.pop('k_commentaire', None)

		super(GererDossier_Reglementation, self).__init__(*args, **kwargs)

		# Je définis la valeur par défaut du champ du formulaire.
		self.fields['zs_comm_regl_doss'].initial = k_commentaire

class GererPhoto(forms.Form) :

	# Je définis les champs du formulaire.
	za_doss = forms.CharField(
		label = 'Numéro du dossier',
		required = False,
		widget = forms.TextInput(attrs = { 'class' : 'form-control', 'readonly' : True })
	)

	zl_ppv_ph = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Période de la prise de vue de la photo' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zs_int_ph = forms.CharField(
		error_messages = MESSAGES,
		label = 'Intitulé de la photo' + CHAMP_REQUIS,
		validators = [valid_cdc],
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zd_dt_pv_ph = forms.DateField(
		error_messages = MESSAGES,
		label = 'Date de la prise de vue de la photo' + CHAMP_REQUIS,
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zu_chem_ph = forms.FileField(
		error_messages = MESSAGES,
		label = 'Photo <span class="c-attention i">(fichier image de moins de 3 Mo)</span>' + CHAMP_REQUIS,
		widget = forms.FileInput(attrs = {'class' : 'input-file'})
	)

	def __init__(self, *args, **kwargs) :

		# Je déclare les éléments du tableau des arguments.
		k_dossier = kwargs.pop('k_dossier', None)

		super(GererPhoto, self).__init__(*args, **kwargs)

		try :
			v_numero_dossier = TDossier.objects.get(id_doss = k_dossier).num_doss
		except :
			v_numero_dossier = k_dossier

		# Je définis les valeurs par défaut des champs du formulaire.
		self.fields['za_doss'].initial = v_numero_dossier

		# J'alimente la liste déroulante des maîtres d'ouvrages.
		les_periodes_prise_vue_photo = list(OPTION_INITIALE)
		les_periodes_prise_vue_photo.extend([(i.id_ppv_ph, i.int_ppv_ph) 
			for i in TPeriodePriseVuePhoto.objects.all().order_by('int_ppv_ph')]
		)
		self.fields['zl_ppv_ph'].choices = les_periodes_prise_vue_photo

	def clean(self) :

		# Je récupère les données utiles du formulaire pré-valide.
		tab_donnees = super(GererPhoto, self).clean()
		v_periode_prise_vue_photo = tab_donnees.get('zl_ppv_ph')

		# Je vérifie la valeur de chaque liste déroulante du formulaire.
		v_periode_prise_vue_photo = valid_zl(self, 'zl_ppv_ph', v_periode_prise_vue_photo)

class GererReglementation(forms.Form) :

	# Je définis les champs du formulaire.
	zl_type_av_arr = forms.ChoiceField(
		error_messages = MESSAGES,
		label = 'Avancement' + CHAMP_REQUIS,
		widget = forms.Select(attrs = { 'class' : 'form-control' })
	)

	zd_dt_arr = forms.DateField(
		error_messages = MESSAGES,
		label = 'Date de l\'arrêté' + CHAMP_REQUIS,
		widget = forms.TextInput(attrs = { 'class' : 'date form-control' })
	)

	zu_chem_pj_arr = forms.FileField(
		error_messages = MESSAGES,
		label = 'Fichier PDF de l\'arrêté',
		required = False,
		widget = forms.FileInput(attrs = {'class' : 'input-file'})
	)

	def __init__(self, *args, **kwargs) :

		# Je déclare les éléments du tableau des arguments.
		k_avancement = kwargs.pop('k_avancement', -1)
		k_date_arrete = kwargs.pop('k_date_arrete', None)

		super(GererReglementation, self).__init__(*args, **kwargs)

		# Je définis les valeurs par défaut des champs du formulaire.
		self.fields['zl_type_av_arr'].initial = k_avancement
		self.fields['zd_dt_arr'].initial = reecr_dt(k_date_arrete)

		# J'alimente la liste déroulante des types d'avancements d'un arrêté.
		les_avancements = list(OPTION_INITIALE)
		les_avancements.extend([(i.id_type_av_arr, i.int_type_av_arr) 
			for i in TTypeAvancementArrete.objects.all().order_by('int_type_av_arr')]
		)
		self.fields['zl_type_av_arr'].choices = les_avancements

	def clean(self) :

		# Je récupère les données utiles du formulaire pré-valide.
		tab_donnees = super(GererReglementation, self).clean()
		v_avancement = tab_donnees.get('zl_type_av_arr')

		# Je vérifie la valeur de chaque liste déroulante du formulaire.
		v_avancement = valid_zl(self, 'zl_type_av_arr', v_avancement)