#!/usr/bin/env python
#-*- coding: utf-8

'''
Cette fonction retourne un tableau de données.
request : Objet requête
Retourne un tableau associatif
'''
def alim_ld(request) :

	# Imports
	from app.models import TAction
	from app.models import TAxe
	from app.models import TProgramme
	from app.models import TSousAxe
	from app.models import TTypesProgrammesTypeDossier

	# J'initialise certaines valeurs du formulaire non-soumis.
	v_type_progr = ''
	v_progr = ''
	v_axe = ''
	v_ss_axe = ''
	try :
		v_progr = request.POST['id_progr']
	except :
		pass
	try :
		v_axe = request.POST['num_axe']
	except :
		pass
	try :
		v_ss_axe = request.POST['num_ss_axe']
	except :
		pass

	# Je déclare les tableaux de sortie.
	t_axes = []
	t_ss_axes = []
	t_act = []
	t_types_doss = []
	
	# Je prépare et mets en forme les données des tableaux de sortie.
	if v_progr :
		qs_axes = TAxe.objects.filter(id_progr = v_progr)
		for a in qs_axes :
			t_axes.append([a.pk, a.num_axe])
		try :
			v_type_progr = TProgramme.objects.get(pk = v_progr).id_type_progr
		except :
			pass
		qs_types_doss = TTypesProgrammesTypeDossier.objects.filter(id_type_progr = v_type_progr).order_by(
			'id_type_doss'
		)
		for td in qs_types_doss :
			t_types_doss.append([td.id_type_doss.pk, td.id_type_doss.int_type_doss])
		if v_axe :
			qs_ss_axes = TSousAxe.objects.filter(id_axe = v_axe)
			for sa in qs_ss_axes :
				t_ss_axes.append([sa.pk, sa.num_ss_axe])
			if v_ss_axe :
				qs_act = TAction.objects.filter(id_ss_axe = v_ss_axe)
				for a in qs_act :
					t_act.append([a.pk, a.num_act])

	return {
		'axe' : t_axes,
		'ss_axe' : t_ss_axes,
		'act' : t_act,
		'type_doss' : t_types_doss
	}

'''
Cette fonction retourne une date au format français.
_d : Date convertie
Retourne une chaîne de caractères
'''
def dt_fr(_d) :

	# Imports
	from datetime import datetime

	output = _d

	if _d :
		d = datetime.strptime(str(_d), '%Y-%m-%d')
		output = d.strftime('%d/%m/%Y')

	return output

'''
Cette fonction retourne un tableau de dossiers filtrés.
request : Objet requête
_d_excl : Dossier exclu du résultat de la requête.
Retourne un jeu de données
'''
def filtr_doss(request, _d_excl = None) :

	# Imports
	from app.forms.gestion_dossiers import ChoisirDossier
	from app.models import TAction
	from app.models import TAxe
	from app.models import TDossier
	from app.models import TRegroupementsMoa
	from app.models import TSousAxe
	from django.db.models import Q
	from functools import reduce
	import operator

	# Je soumets le formulaire.
	f_chois_doss = ChoisirDossier(request.POST, prefix = 'ChoisirDossier')

	# Je rajoute des choix valides pour certaines listes déroulantes (prévention d'erreurs).
	post_progr = request.POST['ChoisirDossier-zl_progr']
	post_axe = request.POST['ChoisirDossier-zl_axe']
	post_ss_axe = request.POST['ChoisirDossier-zl_ss_axe']
	if post_progr :
		t_axes = [(a.pk, a.pk) for a in TAxe.objects.filter(id_progr = post_progr)]
		f_chois_doss.fields['zl_axe'].choices = t_axes
		t_ss_axes = [(sa.pk, sa.pk) for sa in TSousAxe.objects.filter(id_axe = post_axe)]
		f_chois_doss.fields['zl_ss_axe'].choices = t_ss_axes
		t_act = [(a.pk, a.pk) for a in TAction.objects.filter(id_ss_axe = post_ss_axe)]
		f_chois_doss.fields['zl_act'].choices = t_act

	if f_chois_doss.is_valid() :

		# Je récupère les données du formulaire valide.
		cleaned_data = f_chois_doss.cleaned_data
		v_org_moa = cleaned_data.get('zl_org_moa')
		v_progr = cleaned_data.get('zl_progr')
		v_axe = cleaned_data.get('zl_axe')
		v_ss_axe = cleaned_data.get('zl_ss_axe')
		v_act = cleaned_data.get('zl_act')
		v_nat_doss = cleaned_data.get('zl_nat_doss')
		v_ann_delib_moa_doss = cleaned_data.get('zl_ann_delib_moa_doss')

		# J'initialise les conditions de la requête.
		t_sql = { 'and' : {}, 'or' : [] }
		if v_org_moa :
			for rm in TRegroupementsMoa.objects.filter(id_org_moa_fil = v_org_moa) :
				t_sql['or'].append(Q(**{ 'id_org_moa' : rm.id_org_moa_anc }))
			if len(t_sql['or']) > 0 :
				t_sql['or'].append(Q(**{ 'id_org_moa' : v_org_moa }))
			else :
				t_sql['and']['id_org_moa'] = v_org_moa
		if v_progr :
			t_sql['and']['id_progr'] = v_progr
			if v_axe :
				t_sql['and']['num_axe'] = v_axe.split('_')[-1]
				if v_ss_axe :
					t_sql['and']['num_ss_axe'] = v_ss_axe.split('_')[-1]
					if v_act :
						t_sql['and']['num_act'] = v_act.split('_')[-1]
		if v_nat_doss :
			t_sql['and']['id_nat_doss'] = v_nat_doss
		if v_ann_delib_moa_doss :
			t_sql['and']['dt_delib_moa_doss__year'] = v_ann_delib_moa_doss

		# J'initialise la requête.
		if len(t_sql['or']) > 0 :
			qs_doss = TDossier.objects.filter(reduce(operator.or_, t_sql['or']), **t_sql['and'])
		else :
			qs_doss = TDossier.objects.filter(**t_sql['and'])
		if _d_excl :
			qs_doss = qs_doss.exclude(pk = _d_excl)

	else :
		qs_doss = []
		
	return qs_doss

'''
Cette fonction génère une chaîne de caractères selon le datetime courant.
Retourne une chaîne de caractères
'''
def gen_cdc() :

	# Imports
	import hashlib
	import time

	# Je récupère le "datetime" courant.
	dt = time.strftime('%d%m%Y%H%M%S')

	# Je crypte le "datetime" courant selon la méthode de hashage "SHA1".
	dt_crypt = hashlib.sha1(dt.encode()).hexdigest()

	return dt_crypt

'''
Cette fonction retourne le formulaire d'ajout d'un avenant.
request : Objet requête
_pd : Objet TPrestationsDossier
_u : URL traitant le formulaire
Retourne une chaîne de caractères
'''
def gen_f_ajout_aven(request, _pd, _u) :

	# Imports
	from app.forms.gestion_dossiers import GererAvenant
	from app.functions import init_f
	from django.template.context_processors import csrf

	# J'instancie un objet "formulaire".
	f = GererAvenant(prefix = 'GererAvenant', k_prest_doss = _pd)

	# J'initialise le gabarit de chaque champ du formulaire.
	t = init_f(f)

	return '''
	<form action="{0}" enctype="multipart/form-data" name="f_ajout_aven" method="post" onsubmit="soum_f(event)">
		<input name="csrfmiddlewaretoken" type="hidden" value="{1}">
		<div class="row">
			<div class="col-sm-6">{2}</div>
			<div class="col-sm-6">{3}</div>
		</div>
		{4}
		{5}
		{6}
		{7}
		<button class="center-block green-btn my-btn" type="submit">Valider</button>
	</form>
	'''.format(
		_u,
		csrf(request)['csrf_token'],
		t['za_num_doss'],
		t['zl_prest'],
		t['int_aven'],
		t['dt_aven'],
		t['mont_aven'],
		t['comm_aven']
	)

'''
Cette fonction retourne un tableau HTML de dossiers.
request : Objet requête
_d_excl : Dossier exclu du résultat de la requête.
Retourne un tableau HTML
'''
def gen_t_ch_doss(request, _d_excl = None) :

	# Imports
	from app.forms.gestion_dossiers import ChoisirDossier
	from app.functions import dt_fr
	from app.functions import init_f
	from app.models import TDossier
	from django.template.context_processors import csrf

	# J'instancie un objet "formulaire".
	f_ch_doss = ChoisirDossier(prefix = 'ChoisirDossier')

	# J'initialise le gabarit de chaque champ du formulaire.
	t_ch_doss = init_f(f_ch_doss)

	# J'initialise la requête.
	qs_doss = TDossier.objects.all()
	if _d_excl :
		qs_doss = TDossier.objects.exclude(pk = _d_excl)

	# J'empile le tableau des lignes du tableau HTML.
	t_lg = []
	for d in qs_doss :
		lg = '''
		<tr>
			<td class="b">{0}</td>
			<td>{1}</td>
			<td>{2}</td>
			<td>{3}</td>
			<td><span class="choose-icon pointer pull-right" title="Choisir le dossier"></span></td>
		</tr>
		'''.format(
			d,
			'{0} - {1} - {2} - {3}'.format(d.id_nat_doss, d.id_type_doss, d.lib_1_doss, d.lib_2_doss),
			d.id_org_moa,
			dt_fr(d.dt_delib_moa_doss) or '-'
		)
		t_lg.append(lg)

	return '''
	<form action="?action=filtrer-dossiers" method="post" name="f_ch_doss">
		<input name="csrfmiddlewaretoken" type="hidden" value="{0}">
		<fieldset class="my-fieldset" style="padding-bottom: 0;">
			<legend>Rechercher par</legend>
			<div>
				<div class="row">
					<div class="col-xs-6">{1}</div>
					<div class="col-xs-6">{2}</div>
				</div>
				<div class="row">
					<div class="col-xs-6">{3}</div>
					<div class="col-xs-3">{4}</div>
					<div class="col-xs-3">{5}</div>
				</div>
				<div class="row">
					<div class="col-xs-6">{6}</div>
					<div class="col-xs-6">{7}</div>
				</div>
			</div>
		</fieldset>
	</form>
	<div class="br"></div>		
	<div class="my-table" id="t_ch_doss">
		<table>
			<thead>
				<tr>
					<th>N° du dossier</th>
					<th>Intitulé du dossier</th>
					<th>Maître d'ouvrage</th>
					<th>Date de délibération au maître d'ouvrage</th>
					<th></th>
				</tr>
			</thead>
			<tbody>{8}</tbody>
		</table>
	</div>
	'''.format(
		(csrf(request)['csrf_token']),
		t_ch_doss['zl_org_moa'],
		t_ch_doss['zl_progr'],
		t_ch_doss['zl_axe'],
		t_ch_doss['zl_ss_axe'],
		t_ch_doss['zl_act'],
		t_ch_doss['zl_nat_doss'],
		t_ch_doss['zl_ann_delib_moa_doss'],
		'\n'.join(t_lg)
	)

'''
Cette fonction retourne le tableau HTML des factures disponibles pour une demande de versement.
_f : Identifiant d'un objet TFinancement
_i : Instance TDemandeVersement
_c : Dois-je cocher les factures reliées à la demande de versement ?
Retourne une chaîne de caractères
'''
def gen_t_html_fact_doss(_f, _i = None, _c = False) :

	# Imports
	from app.functions import dt_fr
	from app.functions import obt_mont
	from app.models import TFacture
	from app.models import TFacturesDemandeVersement
	from app.models import TFinancement
	from itertools import chain

	# Je vérifie l'existence d'un objet TFinancement.
	try :
		o_fin = TFinancement.objects.get(pk = _f)
	except :
		o_fin = None

	# Je vérifie l'existence d'un objet TDossier.
	if o_fin :
		o_doss = o_fin.id_doss
	else :
		o_doss = None

	if o_doss :

		# Je définis si le montant du dossier est en HT ou en TTC.
		ht_ou_ttc = 'HT'
		if o_doss.est_ttc_doss == True :
			ht_ou_ttc = 'TTC'

		t_lg = []
		for index, f in enumerate(TFacture.objects.filter(id_doss = o_doss)) :

			# Je définis les factures cochées par défaut.
			checked = ''
			if _i and _c == True :
				try :
					TFacturesDemandeVersement.objects.get(id_ddv = _i, id_fact = f)
					checked = 'checked=""'
				except :
					pass

			# J'initialise le montant de la facture selon le mode de taxe du dossier.
			mont_fact = f.mont_ht_fact
			if o_doss.est_ttc_doss == True :
				mont_fact = f.mont_ttc_fact

			# Je définis les factures pouvant être encore liées à une demande de versement.
			peut_coch = False
			if len(TFacturesDemandeVersement.objects.filter(id_ddv__id_fin = o_fin, id_fact = f)) == 0 :
				peut_coch = True
			if _i :
				peut_coch = True
			if peut_coch == True :
				cb_fact = '''
				<input type="checkbox" class="pull-right" id="id_GererDemandeVersement-cbsm_fact_{0}" montant="{1}"
				name="GererDemandeVersement-cbsm_fact" pourcentage="{2}" taxe={3} value="{4}" {5}>
				'''.format(index, mont_fact, o_fin.pourc_elig_fin or '', ht_ou_ttc, f.pk, checked)
			else :
				cb_fact = ''

			lg = '''
			<tr>
				<td>{0}</td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
				<td>{4}</td>
			</tr>
			'''.format(
				f.id_prest,
				obt_mont(mont_fact),
				f.num_fact, 
				dt_fr(f.dt_mand_moa_fact), 
				cb_fact
			)

			# J'empile le tableau des lignes du tableau HTML.
			t_lg.append(lg)

		# Je prépare le tableau HTML.
		t_html = '''
		<div class="field-wrapper">
			<span class="field-label">
				Facture(s) pouvant être reliée(s) à la demande de versement
				<span class="field-remark"></span>
			</span>
			<div class="my-table" id="t_ch_fact_ddv">
				<table id="id_GererDemandeVersement-cbsm_fact">
					<thead>
						<tr>
							<th>Prestation</th>
							<th>Montant {0} (en €)</th>
							<th>N° de facture</th>
							<th>Date de mandatement par le maître d'ouvrage</th>
							<th></th>
						</tr>
					</thead>
					<tbody>{1}</tbody>
				</table>
			</div>
			<span class="field-error"></span>
		</div>
		'''.format(ht_ou_ttc, '\n'.join(t_lg))

	else :
		t_html = ''

	return t_html

'''
Cette procédure (ou fonction) permet de savoir si un utilisateur peut accéder ou non à une vue.
request : Objet requête
Retourne un booléen si le paramètre "_h" vaut False
_u : Utilisateur en cours
_d : Dossier cible (objet TDossier ou tableau)
_g : Dois-je vérifier l'accès en lecture ou en écriture ?
_h : Dois-je déclencher une erreur 403 en cas de non-permission ?
'''
def ger_droits(_u, _d, _g = True, _h = True) :

	# Imports
	from app.models import TDroit
	from app.models import TMoa
	from app.models import TTypeProgramme
	from django.core.exceptions import PermissionDenied

	t_coupl = []
	for d in TDroit.objects.filter(id_util = _u).order_by('-id_org_moa', '-id_type_progr') :

		# J'initialise le tableau des maîtres d'ouvrages (identifiants).
		if d.id_org_moa :
			t_org_moa = [d.id_org_moa.pk]
		else :
			t_org_moa = [m.pk for m in TMoa.objects.all()]

		# J'initialise le tableau des types de programmes (identifiants).
		if d.id_type_progr :
			t_type_progr = [d.id_type_progr.pk]
		else :
			t_type_progr = [tp.pk for tp in TTypeProgramme.objects.all()]

		# Je définis si je dois vérifier le droit en écriture ou en lecture.
		attr = d.en_lect
		if _g == False :
			attr = d.en_ecr

		# J'empile le tableau des couples valides.
		for i in range(0, len(t_org_moa)) :
			for j in range(0, len(t_type_progr)) :
				coupl = (t_org_moa[i], t_type_progr[j])
				if attr == True :
					t_coupl.append(coupl)
				else :
					if coupl in t_coupl :
						t_coupl.remove(coupl)

	# Je retire les doublons.
	t_coupl_uniq = set(t_coupl)

	# J'initialise le tuple correspondant au couple recherché selon l'instance du paramètre "_d".
	if isinstance(_d, list) == True :
		tupl = tuple(_d)
	else :
		tupl = (_d.id_org_moa.pk, _d.id_progr.id_type_progr.pk)

	# Je vérifie si l'utilisateur peut accéder à la vue.
	trouve = False
	if tupl in t_coupl_uniq :
		trouve = True

	if _h == True :
		if trouve == False :
			raise PermissionDenied
	else :
		return trouve
		
'''
Cette fonction retourne le gabarit de chaque champ d'un formulaire.
_f : Formulaire traité
Retourne un tableau associatif.
'''
def init_f(_f) :

	# Imports
	from django.template.defaultfilters import safe

	# Je déclare le tableau de sortie.
	t_champs = {}

	# Je parcours chaque champ du formulaire traité.
	for c in _f :

		# J'initialise le gabarit de base.
		gab_base = '''
		<div class="field-wrapper">
			<span class="field-label">{0}</span>
			<span class="field-control">{1}</span>
			<span class="field-error"></span>
		</div>
		'''
		
		# Je mets en place une variable qui va stocker le gabarit utilisé.
		gab = None

		# Je convertis le champ en code HTML.
		c_to_html = '{0}'.format(c)

		bal = '<{0}/>'.format(c_to_html.split('<')[1].split(' ')[0])
		if bal == '<a/>' :

			# Je récupère les différentes parties de la zone d'upload lors d'une modification.
			split = c_to_html.split('<')

			zu_fich = '<{0}'.format(split[len(split) - 1])
			fich_act = split[1].split('href="')[1].split('"')[0]

			if len(split) == 8 :
				label_eff_fich = '<{0}<{1}'.format(split[4], split[5])
				cb_eff_fich = '<{0}'.format(split[3])
				part_gab = '''
				<span class="delete-file">
					{0}
					{1}
				</span>
				'''.format(cb_eff_fich, label_eff_fich)
			else :
				part_gab = ''

			gab = '''
			<div class="field-wrapper">
				<span class="field-label">{0}</span>
				<div class="input-file-container">
					<span class="field-control">{1}</span>
					<span class="input-file-trigger">Parcourir</span>
					<div class="input-file-return">
						<span class="file-infos">
							{2}
						</span>
						{3}
					</div>
				</div>
				<span class="field-error"></span>
			</div>
			'''.format(c.label, zu_fich, fich_act, part_gab)

		if bal == '<input/>' :

			if 'type="checkbox"' in c_to_html :
				gab = gab_base.format(c.label, c)

			if 'type="email"' in c_to_html :
				c_maj = c_to_html.replace('type="email"', 'type="text"')
				gab = gab_base.format(c.label, c_maj)
			
			if 'type="file"' in c_to_html :
				gab = '''
				<div class="field-wrapper">
					<span class="field-label">{0}</span>
					<div class="input-file-container">
						<span class="field-control">{1}</span>
						<span class="input-file-trigger">Parcourir</span>
					</div>
					<span class="field-error"></span>
				</div>
				'''.format(c.label, c)

			if 'type="hidden"' in c_to_html :
				gab = gab_base.format(c.label, c)

			if 'type="number"' in c_to_html :
				c_maj = c_to_html.replace('type="number"', 'type="text"')
				c_maj = c_maj.replace(' step="any"', '')
				gab = gab_base.format(c.label, c_maj)

			if 'type="password"' in c_to_html or 'type="text"' in c_to_html :
				if c.name.startswith('zsac_') == True :
					gab = '''
					<div class="field-wrapper">
						<span class="field-label">{0}</span>
						<div class="typeahead__container">
							<div class="typeahead__field">
								<span class="typeahead__query">
									<span class="field-control">{1}</span>
								</span>
							</div>
						</div>
						<span class="field-error"></span>
					</div>
					'''.format(c.label, c)
				else :
					gab = gab_base.format(c.label, c)

		if bal == '<select/>' :
			gab = gab_base.format(c.label, c)

		if bal == '<textarea/>' :
			gab = gab_base.format(c.label, c)

		if bal == '<ul/>' :
			gab = gab_base.format(c.label, c)

		# J'empile le tableau de sortie s'il n'y a pas d'erreurs.
		if gab :
			t_champs[c.name] = safe(gab)
		else :
			raise ValueError('Aucun gabarit n\'est disponible pour le champ « {0} ».'.format(c.name))

	return t_champs

'''
Cette fonction retourne une fenêtre modale.
_s : Suffixe de reconnaissance pour chaque élément de la fenêtre modale
_h : En-tête de la fenêtre modale
_b : Corps de la fenêtre modale
Retourne une fenêtre modale
'''
def init_fm(_s, _h, _b = '') :

	# Imports
	from django.template.defaultfilters import safe

	fm = '''
	<div class="fade modal my-modal" data-backdrop="static" id="fm_{s}" role="dialog" tabindex="-1">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button class="close" data-dismiss="modal" type="button">&times;</button>
					<p class="modal-title">{h}</p>
				</div>
				<div class="modal-body">
					<span id="za_{s}">
						{b}
					</span>
					<div class="modal-padding-bottom"></div>
				</div>
			</div>
		</div>
	</div>
	'''.format(s = _s, h = _h, b = _b)

	return safe(fm)

'''
Cette fonction retourne le gabarit de chaque attribut d'une instance.
_t : Tableau d'attributs
Retourne un tableau associatif
'''
def init_pg_cons(_t) :

	# Imports
	from django.template.defaultfilters import safe
	from styx.settings import MEDIA_URL

	# Je déclare le tableau de sortie.
	t_attrs = {}

	for c, v in _t.items() :

		err = False

		if 'label' in v and 'value' in v :

			# J'initialise le contenu du conteneur.
			contr = '''
			<span class="attribute-label">{0}</span>
			<div class="attribute-control">{1}</div>
			'''.format(v['label'], v['value'])

			# Je surcharge le contenu du conteneur dans le cas d'un fichier PDF.
			if 'pdf' in v :
				if v['pdf'] == True :
					if v['value'] :
						contr = '''
						<a href="{0}{1}" target="blank" class="icon-link pdf-icon">{2}</a>
						'''.format(MEDIA_URL, v['value'], v['label'])
					else :
						contr = None
				else :
					err = True

			# Je complète le contenu du conteneur si besoin.
			if 'help-text' in v and contr != '' :
				contr += '''
				<span class="attribute-help-text">{0}</span>
				'''.format(v['help-text'])

			# J'initialise le gabarit.
			if contr :
				cont = '''
				<div class="attribute-wrapper">
					{0}
				</div>
				'''.format(contr)
			else :
				cont = ''
			
		else :
			err = True

		# J'empile le tableau de sortie s'il n'y a pas d'erreurs.
		if err == False :
			t_attrs[c] = safe(cont)
		else :
			raise ValueError('Aucun gabarit n\'est disponible pour l\'attribut « {0} ».'.format(c))

	return t_attrs
	
'''
Cette fonction retourne un entier ou un nombre décimal sous forme de montant.
_v : Valeur dont on veux avoir le montant
Retourne un entier ou un nombre décimal
'''
def obt_mont(_v) :

	output = _v

	if _v is not None :

		# Je convertis l'entier ou le nombre décimal sous forme de montant.
		output = '{:,.2f}'.format(_v)

		# Je retire les virgules.
		output = output.replace(',', ' ')

		# Je retire les zéros non-significatifs si besoin.
		if output.endswith('.00') :
			output = output[:-3]
		
	return output

'''
Cette fonction retourne un entier ou un nombre décimal sous forme de pourcentage.
_v : Valeur dont on veux avoir le pourcentage
Retourne un entier ou un nombre décimal
'''
def obt_pourc(_v) :

	output = _v

	if _v :

		# Je convertis l'entier ou le nombre décimal sous forme de pourcentage.
		output = '{0:.2f}'.format(_v)

		# Je retire les zéros non-significatifs si besoin.
		if output.endswith('.00') :
			output = output[:-3]
		if '.' in output and output.endswith('0') :
			output = output[:-1]
			
	return output

'''
Cette procédure permet de mettre à jour un fichier log.
_t : Tableau de données à renseigner dans le fichier log
'''
def rempl_fich_log(_t) :

	# Imports
	from styx.settings import MEDIA_ROOT
	import csv
	import time

	try :

		# J'ouvre (ou je créé) le fichier log.
		with open('{0}\log.csv'.format(MEDIA_ROOT), 'a', newline = '') as fich :

			# Je définis le délimiteur.
			writer = csv.writer(fich, delimiter = ';')

			# J'ajoute en fin de tableau la date et l'heure de l'opération.
			_t.append(time.strftime('%d/%m/%Y %H:%M:%S'))

			# J'ajoute une ligne au fichier log.
			writer.writerow(_t)

			# Je ferme le fichier log.
			fich.close()

	except :
		pass

'''
Cette fonction retourne une demande de confirmation de suppression d'un élément.
_v : Vue permettant la suppression
_m: Message d'alerte
Retourne une chaîne de caractères
'''
def suppr(_v, _m = '') :

	# Je mets en forme les lignes de la fenêtre modale.
	lg_princ = '''
	<div class="row">
		<div class="col-xs-6 text-center">
			<a href="{0}" class="green-btn my-btn" onclick="suppr(event);" style="display: inline-block;">Oui</a>
		</div>
		<div class="col-xs-6 text-center">
			<button class="green-btn my-btn" data-dismiss="modal" style="display: inline-block;">Non</button>
		</div>
	</div>
	'''.format(_v)

	lg_sec = '''
	<div class="row">
		<div class="col-xs-12 text-center">
			<span class="b red-color">
				<span class="u">Attention :</span> {0}
			</span>
		</div>
	</div>
	'''.format(_m)

	# J'initialise le tableau des lignes de la fenêtre modale.
	t_lg = [lg_princ]
	if _m != '' :
		t_lg.append(lg_sec)

	# J'inverse l'ordre du tableau des lignes de la fenêtre modale afin d'avoir le message d'alerte au début.
	t_lg.reverse()

	return '<div class="br"></div>'.join(t_lg)

'''
Cette fonction vérifie si l'extension d'un fichier uploadé est autorisée.
_v : Fichier uploadé
_e : Extension(s) autorisée(s)
Retourne un booléen
'''
def verif_ext_fich(_v, _e) :

	# Imports
	import os

	err = False

	# Je récupère l'extension du fichier.
	ext = os.path.splitext(_v.name)[1]

	if ext.lower() not in _e :
		err = True

	return err

'''
Cette fonction vérifie une valeur numérique saisie.
_v : Valeur saisie
_null : La valeur peut-elle être nulle ?
'''
def verif_mont(_v, _null) :

	err = False

	# Je vérifie que la valeur ne soit pas strictement négative.
	if _null == True and _v < 0 :
		err = True
	if _null == False and _v <= 0 :
		err = True

	# Je calcule le nombre de décimales.
	v_str = str(_v)
	i = v_str.index('.') + 1
	nb_dec = len(v_str) - i

	if nb_dec > 2 :
		err = True

	return err