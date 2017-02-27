// Variables globales
var t_datat = {
	'alert' : init_datat($('#t_alert'), [0]),
	'ch_act_pgre' : init_datat($('#t_ch_act_pgre'), [6]),
	'ch_cbsm_atel_pgre' : init_datat($('#t_ch_cbsm_atel_pgre'), [1]),
	'ch_cbsm_org_moa' : init_datat($('#t_ch_cbsm_org_moa'), [1]),
	'ch_doss' : init_datat($('#t_ch_doss'), [4]),
	'ch_fact_ddv' : init_datat($('#t_ch_fact_ddv'), [4]),
	'ch_prest' : init_datat($('#t_ch_prest'), [5]),
	'cons_arr' : init_datat($('#t_cons_arr'), [5]),
	'cons_aven' : init_datat($('#t_cons_aven'), [4]),
	'cons_ddv' : init_datat($('#t_cons_ddv'), [6]),
	'cons_doss_fam' : init_datat($('#t_cons_doss_fam'), [4]),
	'cons_doss_prest' : init_datat($('#t_cons_doss_prest'), [3]),
	'cons_droit' : init_datat($('#t_cons_droit'), [0, 1, 2, 3]),
	'cons_fact' : init_datat($('#t_cons_fact'), [7]),
	'cons_fact_ddv' : init_datat($('#t_cons_fact_ddv'), [4]),
	'cons_fin' : init_datat($('#t_cons_fin'), [8]),
	'cons_pdc' : init_datat($('#t_cons_pdc'), [2]),
	'cons_ph' : init_datat($('#t_cons_ph'), [0, 4]),
	'cons_prest' : init_datat($('#t_cons_prest'), [6]),
	'modif_prest_doss' : init_datat($('#t_modif_prest_doss'), [0, 1, 2, 3, 4])
};
var submit = false;
var pt_prec = null;
var est_init = false;

/**
 * Ce script permet l'affichage d'un loader dès la fin du chargement du DOM.
 */
$(document).ready(function() {

	// Je cache la page HTML.
	$('.container-fluid').hide();
	$('body').css('background-color', '#FFF');

	// J'initialise le contenu du loader principal.
	var o_main_loader = $('<div/>', { 'id' : 'main-loader' });
	var t_main_loader = [
		$('<span/>', { 'class' : 'glyphicon glyphicon-refresh spin' }),
		$('<br/>'),
		'Chargement de la page'
	];

	// Je prépare le contenu du loader principal.
	for (var i = 0; i < t_main_loader.length; i += 1) {
		o_main_loader.append(t_main_loader[i]);
	}

	// J'affiche le loader principal.
	$('body').prepend(o_main_loader);
});

/**
 * Ce script permet l'affichage d'une page web dès la fin du chargement de celle-ci.
 */
$(window).load(function() {
	setTimeout(function() {

		// Je supprime le loader principal.
		$('#main-loader').remove();

		// Je montre la page HTML chargée.
		$('body').removeAttr('style');
		$('.container-fluid').removeAttr('style');
	}, 250);
});

/**
 * Ce script permet de retirer le focus du sous-menu sélectionné si et seulement je ferme celui-ci.
 */
$('#main-nav .dropdown').on('click', function() {
	if ($(this).hasClass('open')) {
		$('#main-nav .dropdown-toggle').blur();
	}
});

/**
 * Ce script permet la mise en place automatique d'un système permettant la visibilité d'un mot de passe saisi.
 */
$(document).ready(function() {
	$('input[name*="password"]').each(function() {
		var span = $('<span/>', { 'class' : 'glyphicon glyphicon-eye-close showable-password'});
		$(this).parent().append(span);
	});
});

/**
 * Ce script permet l'utilisation du système permettant la visibilité d'un mot de passe saisi.
 */
$(document).on('click', '.showable-password', function() {
	var o_password = $(this).prev();
	if (o_password.attr('type') == 'password') {
		$(this).removeClass('glyphicon-eye-close');
		$(this).addClass('glyphicon-eye-open');
		o_password.attr('type', 'text');
	}
	else {
		$(this).removeClass('glyphicon-eye-open');
		$(this).addClass('glyphicon-eye-close');
		o_password.attr('type', 'password');
	}
});

/**
 * Ce script permet de bloquer le comportement par défaut d'un élément cliqué qui possède la classe "to-block".
 * _e : Objet DOM
 */
$(document).on('click', '.to-block', function(_e) {
	_e.preventDefault();
})

// Gestion des dossiers

/**
 * Ce script permet l'affichage de la fenêtre modale d'ajout d'un dossier associé/de correspondance.
 */
$('#id_GererDossier-rb_doss_ass_0, #id_GererActionPgre-rb_doss_corr_0').on('click', function() {
	$('#fm_ch_doss').modal();
});

/**
 * Ce script permet de récupérer le numéro d'un dossier que l'on souhaite associer.
 */
$(document).on('click', '#t_ch_doss .choose-icon', function() {

	// Je réinitialise tous les pictogrammes.
	$('#t_ch_doss .chosen-icon').each(function() {
		$(this).removeClass('chosen-icon');
		$(this).addClass('choose-icon pointer');
		$(this).attr('title', 'Choisir le dossier');
	});

	// Je montre à l'utilisateur le pictogramme sélectionné.
	$(this).removeClass('choose-icon pointer');
	$(this).removeAttr('title');
	$(this).addClass('chosen-icon');

	// Je stocke le numéro du dossier sélectionné.
	var v_num_doss = $(this).parent().parent().find($('td:first-child')).text();

	// Je transmets le numéro du dossier sélectionné au formulaire principal.
	$('#id_GererDossier-za_doss_ass').val(v_num_doss);
	$('#id_GererActionPgre-za_doss_corr').val(v_num_doss);

	// Je ferme la fenêtre modale.
	$('#fm_ch_doss').modal('hide');
});

/**
 * Ce script permet de réinitialiser la valeur du dossier associé/de correspondance.
 */
$('#id_GererDossier-rb_doss_ass_1, #id_GererActionPgre-rb_doss_corr_1, #bt_suppr_doss_ass, #bt_suppr_doss_corr').on(
	'click', function() {

	// Je réinitialise tous les pictogrammes.
	$('#t_ch_doss .chosen-icon').each(function() {
		$(this).removeClass('chosen-icon');
		$(this).addClass('choose-icon pointer');
		$(this).attr('title', 'Choisir le dossier');
	});
	
	$('#id_GererDossier-za_doss_ass').val('');
	$('#id_GererActionPgre-za_doss_corr').val('');
});

/**
 * Ce script permet de cacher chaque liste déroulante possédant la classe hide-field.
 */
$('.hide-field').each(function() {
	point_fw($('#' + $(this).attr('id'))).hide();
});

/**
 * Ce script permet d'afficher chaque liste déroulante possédant la classe show-field.
 */
$('.show-field').each(function() {
	point_fw($('#' + $(this).attr('id'))).show();
	$(this).removeClass('show-field');
});

/**
 * Ce script permet de gérer l'affichage et les données des listes déroulantes des axes, des sous-axes, des actions et
 * des types de dossiers du formulaire de choix d'un dossier.
 * _e : Objet DOM
 */
$('#id_ChoisirDossier-zl_progr, #id_ChoisirDossier-zl_axe, #id_ChoisirDossier-zl_ss_axe').on('change', function(_e) {
	submit = alim_ld(
		_e,
		[
			'id_ChoisirDossier-zl_progr',
			['id_ChoisirDossier-zl_axe'],
			'id_ChoisirDossier-zl_ss_axe',
			'id_ChoisirDossier-zl_act'
		],
		$('form[name="f_ch_doss"]')
	);
});

/**
 * Ce script permet de simuler la soumission du formulaire de choix d'un dossier.
 */
$('form[name="f_ch_doss"]').on('change', function() {
	if (submit == false) {
		$(this).submit();
	}
	else {
		submit = false;
	}
});

/**
 * Ce script permet de traiter le formulaire de choix d'un dossier.
 * _e : Objet DOM
 */
$('form[name="f_ch_doss"]').on('submit', function(_e) {
	soum_f(
		_e,
		function() {
			$('#t_ch_doss tbody > tr').each(function() {
				if ($(this).find('td:first-child').attr('class') != 'dataTables_empty') {
					$(this).find('td:first-child').addClass('b');
				}				
			});
		}
	);
});

/**
 * Ce script permet de gérer l'affichage et les données des listes déroulantes des axes, des sous-axes, des actions et
 * des types de dossiers des formulaires de gestion d'un dossier.
 * _e : Objet DOM
 */
$('#id_GererDossier-zl_progr, #id_GererDossier-zl_axe, #id_GererDossier-zl_ss_axe').on('change', function(_e) {
	submit = alim_ld(
		_e,
		[
			'id_GererDossier-zl_progr',
			['id_GererDossier-zl_axe', 'id_GererDossier-zl_type_doss'],
			'id_GererDossier-zl_ss_axe',
			'id_GererDossier-zl_act'
		]
	);
});

/**
 * Ce script gère l'état des contrôles "date" des formulaires de gestion des caractéristiques d'un dossier.
 * _e : Objet DOM
 */
$('#id_GererDossier-id_av, #id_GererDossier-id_av_cp').on('change', function(_e) {
	if (isNaN($(this).val()) == false) {

		// Je récupère les intitulés.
		var v_int_av = $('#id_GererDossier-id_av option:selected').text();
		var v_int_av_cp = $('#id_GererDossier-id_av_cp option:selected').text();

		// Je pointe vers les objets "date".
		var o_dt_delib_moa_doss = $('#id_GererDossier-dt_delib_moa_doss');
		var o_dt_av_cp_doss = $('#id_GererDossier-dt_av_cp_doss');

		if (v_int_av == EP_STR) {
			o_dt_delib_moa_doss.val('');
			o_dt_delib_moa_doss.attr('readonly', true);

			$('#id_GererDossier-id_av_cp option').each(function() {
				if ($(this).text() == EA_STR) {
					$('#id_GererDossier-id_av_cp').val($(this).val());
				}
			});
		}
		else {
			o_dt_delib_moa_doss.removeAttr('readonly');
		}

		if (v_int_av == EP_STR || $.inArray(v_int_av_cp, [EA_STR, SO_STR]) > -1) {
			o_dt_av_cp_doss.val('');
			o_dt_av_cp_doss.attr('readonly', true);
		}
		else {
			o_dt_av_cp_doss.removeAttr('readonly');
		}
	}
});

/**
 * Ce script permet le calcul automatique du montant de la participation.
 */
$('#id_GererFinancement-mont_elig_fin, #id_GererFinancement-pourc_elig_fin').on('input', function() {

	// Je récupère le montant de l'assiette éligible ainsi que le pourcentage éligible.
	var v_mont_elig_fin = $('#id_GererFinancement-mont_elig_fin').val();
	var v_pourc_elig_fin = $('#id_GererFinancement-pourc_elig_fin').val();

	// Je calcule le montant de la participation.
	var v_mont_part_fin = '';
	if (isNaN(v_mont_elig_fin) == false && isNaN(v_pourc_elig_fin) == false) {
		if (v_mont_elig_fin != '' && v_pourc_elig_fin != '') {
			v_mont_part_fin = v_mont_elig_fin * (v_pourc_elig_fin / 100);
			v_mont_part_fin = Math.round(v_mont_part_fin * 100) / 100;
		}
	}

	// J'affiche le montant de la participation.
	$('#id_GererFinancement-mont_part_fin').val(v_mont_part_fin);

	/*
	var t = new Array(v_mont_elig_fin, v_pourc_elig_fin);
	var readonly = true;

	// Je vérifie s'il y a une erreur de saisie.
	for (var i = 0; i < t.length; i += 1) {
		if (isNaN(t[i]) == true || t[i].length == 0) {
			readonly = false;
		}
	}

	var o_mont_part_fin = $('#id_GererFinancement-mont_part_fin');
	if (readonly == true) {
		o_mont_part_fin.attr('readonly', true);	
	}
	else {
		o_mont_part_fin.removeAttr('readonly');
	}
	*/
});

/**
 * Ce script permet d'activer ou de désactiver la lecture seule du contrôle lié au pourcentage de réalisation des 
 * travaux.
 */
$('#id_GererFinancement-id_paiem_prem_ac').on('change', function() {

	// Je récupère le libellé du paiement du premier acompte.
	var v_paiem_prem_ac = $('#' + $(this).attr('id') + ' option:selected').text();

	// J'active ou je désactive la lecture seule du contrôle lié au pourcentage de réalisation des travaux.
	var o_pourc_real_fin = $('#id_GererFinancement-pourc_real_fin');
	if (v_paiem_prem_ac == PRT_STR) {
		o_pourc_real_fin.removeAttr('readonly');
	}
	else {
		o_pourc_real_fin.attr('readonly', true);
		o_pourc_real_fin.val('');
	}
});

/**
 * Ce script permet de retirer l'attribut "required" pour tous les champs de tous les formulaires de la page active.
 */
$(document).on('mousemove', function() {
	$('form').each(function() {
		for (var i = 0; i < $(this).length; i += 1) {
			var f = $(this)[i];
			for (var j = 0; j < f.length; j += 1) {
				var bal = f[j];
				$(bal).removeAttr('required');
			}
		}
	});
});

/**
 * Ce script permet de retirer chaque élément possédant la classe "forbidden" (restriction de droits).
 */
if (forbidden == true) {
	$('.forbidden').each(function() {
		$(this).remove();
	});
}

/**
 * Ce script permet de gérer l'affichage des formulaires lors de la procédure d'ajout ou de reliage d'une prestation.
 */
$('input[name="GererPrestation-rb_prest_exist"]').on('change', function() {
	if ($(this).val() == 1) {
		$('#za_nvelle_prest').hide();
		$('#za_red_prest_etape_1').show();
	}
	else {
		$('#za_red_prest_etape_1').hide();
		$('#za_nvelle_prest').show();
	}
});

/**
 * Ce script permet d'afficher le formulaire de redistribution d'une prestation.
 */
$(document).on('click', '#t_ch_prest .choose-icon', function() {

	// Je garde en mémoire la prestation choisie.
	var o_prest = $(this);
	
	// Je lance une requête AJAX.
	$.ajax({
		type : 'post',
		url : $(this).attr('action'),
		dataType : 'html',
		beforeSend : function() {
			aff_load_ajax(true);
		},
		success : function(data) {

			// Je réinitialise tous les pictogrammes.
			$('#t_ch_prest .chosen-icon').each(function() {
				$(this).removeClass('chosen-icon');
				$(this).addClass('choose-icon pointer');
				$(this).attr('title', 'Choisir la prestation');
			});

			// Je montre à l'utilisateur le pictogramme sélectionné.
			o_prest.removeClass('choose-icon pointer');
			o_prest.removeAttr('title');
			o_prest.addClass('chosen-icon');

			// Je retire le précédent formulaire de redistribution d'une prestation.
			$('#za_red_prest_etape_2').remove();

			// J'affiche le formulaire de redistribution d'une prestation.
			$(data).insertAfter($('#t_ch_prest'));

			// J'initialise la datatable.
			var datat = init_datat($('#t_red_prest'), [0, 1, 2, 3, 4]);
		},
		error : function(xhr) {
			alert('Erreur ' + xhr.status);

			// Je réinitialise tous les pictogrammes.
			$('#t_ch_prest .chosen-icon').each(function() {
				$(this).removeClass('chosen-icon');
				$(this).addClass('choose-icon pointer');
				$(this).attr('title', 'Choisir la prestation');
			});

			// Je retire le précédent formulaire de redistribution d'une prestation.
			$('#za_red_prest_etape_2').remove();
		},
		complete : function() {
			aff_load_ajax(false);
		}
	});
});

/**
 * Ce script permet de simuler la soumission du formulaire de choix d'une prestation.
 */
$('form[name="f_ch_prest"]').on('change', function() {
	$(this).submit();
});

/**
 * Ce script permet de traiter le formulaire de choix d'une prestation.
 * _e : Objet DOM
 */
$('form[name="f_ch_prest"]').on('submit', function(_e) {
	soum_f(
		_e,
		function() {

			// Je retire le précédent formulaire de redistribution d'une prestation.
			$('#za_red_prest_etape_2').remove();
		}
	);
});

/**
 * Ce script permet l'autocomplétion via les numéros SIRET existants dans la base de données selon un critère de
 * recherche.
 */
$.typeahead({
    debug: true,
    delay : 500,
    dynamic : true,
    emptyTemplate : 'Aucun résultat pour {{query}}',
    input : '#id_GererPrestation-zsac_siret_org_prest',
    minLength : 1,
    source : {
        org_prest : {
            display : 'siret_org_prest',
            data : [],
            ajax : function(query) {
            	return {
                    type : 'GET',
                    url : URL_AUTOCOMPL,
                    path : 'data.org_prest',
                    data : {
                    	action : 'autocompleter-siret',
                        q : '{{query}}'
                    }
                };
            },
        }
    },
    template : function(query, item) {
    	var tpl = [
    		'{{siret_org_prest}}',
    		'<br />',
    		'<span class="small">',
    		'{{n_org}}',
    		'</span>'
    	];
        return tpl.join('\n'); 
    }
});

/**
 * Ce script permet de retourner le nom d'un fichier uploadé.
 */
$(document).on('change', 'input[type="file"]', function() {

	// Je pointe vers la racine du contrôle.
	var fw = point_fw($(this));

	// Je retire l'élément HTML retournant le fichier uploadé.
	fw.find('.input-file-return').remove();

	// Je prépare l'élément HTML retournant le nouveau fichier uploadé.
	var div = $('<div/>', { 'class' : 'input-file-return' });
	var span = $('<span/>', { 'class' : 'file-infos', html : ' ' + $(this).val() });

	// J'affiche l'élément HTML retournant le nouveau fichier uploadé.
	div.append(span);
	div.insertAfter(fw.find('.input-file-trigger'));

	// J'applique un style CSS.
	fw.find('.input-file-trigger').css('margin-right', '3.5px');
});

/**
 * Ce script permet d'afficher ou non le tableau HTML des factures disponibles pour une demande de versement.
 */
$('#id_GererDemandeVersement-zl_fin, #id_GererDemandeVersement-id_type_vers').on('change', function() {

	// Je mets en place un booléen déterminant si je dois afficher le tableau des factures.
	var aff_t = 0;

	var v_type_vers = $('#id_GererDemandeVersement-id_type_vers').val();
	if (v_type_vers != '' && isNaN(v_type_vers) == false) {
		var v_int_type_vers = $('#id_GererDemandeVersement-id_type_vers option:selected').text();
		if ($.inArray(v_int_type_vers, [ACOMPT_STR, SOLD_STR]) > -1) {
			aff_t += 1;
		}
	}

	var v_fin = $('#id_GererDemandeVersement-zl_fin').val();
	if (v_fin != '' && isNaN(v_fin) == false) {
		aff_t += 1;
	}

	// Je pointe vers la datatable.
	var datat = t_datat['ch_fact_ddv'];

	if (aff_t == 2) {

		// Je pointe vers l'objet "formulaire".
		var o_f = $('form[name="f_ger_ddv"]');

		// Je lance une requête AJAX.
		$.ajax({
			type : 'post',
			url : o_f.attr('action') + '?action=filtrer-factures',
			data : new FormData(o_f.get(0)),
			dataType : 'html',
			processData : false,
			contentType : false,
			beforeSend : function() {
				aff_load_ajax(true);
			},
			success : function(data)
			{
				// Je retire le tableau des factures.
				try {
					point_fw($('#t_ch_fact_ddv')).remove();
				}
				catch (e) {

				}
				
				// J'affiche le tableau des factures.
				$(data).insertAfter(point_fw($('#id_GererDemandeVersement-int_ddv')));

				// J'initialise la datatable.
				var datab = init_datat($('#t_ch_fact_ddv'), [4]);
			},
			error : function(xhr) {
				alert('Erreur ' + xhr.status);
			},
			complete : function() {
				aff_load_ajax(false);
			}
		});
	}
	else {

		// Je retire le tableau des factures.
		try {
			point_fw($('#t_ch_fact_ddv')).remove();
		}
		catch (e) {

		}
	}
});

/**
 * Ce script permet de gérer l'état de certains champs relatif à une demande de versement.
 */
$('#id_GererDemandeVersement-dt_vers_ddv').on('input', function() {
	if ($(this).val() != '') {
		$('#id_GererDemandeVersement-num_bord_ddv').removeAttr('readonly');
		$('#id_GererDemandeVersement-num_titre_rec_ddv').removeAttr('readonly');
	}
	else {
		$('#id_GererDemandeVersement-num_bord_ddv').attr('readonly', true);
		$('#id_GererDemandeVersement-num_titre_rec_ddv').attr('readonly', true);
		$('#id_GererDemandeVersement-num_bord_ddv').val('');
		$('#id_GererDemandeVersement-num_titre_rec_ddv').val('');
	}
});

/** 
 * Ce script permet de pré-calculer automatiquement le montant d'une demande de versement.
 */
$(document).on('change', 'input[name="GererDemandeVersement-cbsm_fact"]', function() {

	// J'initialise le montant de la demande de versement.
	var mont_ddv = 0;

	// J'initialise certaines variables "compteurs".
	var cpt = 0;
	var cpt_ht = 0;
	var cpt_ttc = 0;

	$('input[name="GererDemandeVersement-cbsm_fact"]').each(function() {
		if ($(this).is(':checked')) {

			// Je mets en forme le montant de la facture.
			var v_mont_fact = $(this).attr('montant');
			if (v_mont_fact == '' || isNaN(v_mont_fact) == true) {
				v_mont_fact = 0;
			}

			// Je mets en forme le pourcentage éligible du financement.
			var v_pourc_elig_fin = $(this).attr('pourcentage');
			if (v_pourc_elig_fin != '' && isNaN(v_pourc_elig_fin) == false) {
				v_pourc_elig_fin = v_pourc_elig_fin / 100;
			}
			else {
				v_pourc_elig_fin = 1;
			}

			// Je calcule le montant de la demande de versement.
			mont_ddv += v_mont_fact * v_pourc_elig_fin;
		}

		// Je vérifie que toutes les cases à cocher ont le même mode de taxe.
		cpt += 1;
		if ($(this).attr('taxe') == 'HT') {
			cpt_ht += 1;
		}
		if ($(this).attr('taxe') == 'TTC') {
			cpt_ttc += 1;
		}
	});

	// Je mets en forme le montant de la demande de versement.
	if (mont_ddv == 0) {
		mont_ddv = '';
	}
	else {
		mont_ddv = mont_ddv.toFixed(2);
	}
	
	// J'affiche le montant de la demande de versement.
	if (cpt == cpt_ht) {
		$('#id_GererDemandeVersement-mont_ht_ddv').val(mont_ddv);
	}
	if (cpt == cpt_ttc) {
		$('#id_GererDemandeVersement-mont_ttc_ddv').val(mont_ddv);
	}
});

/**
 * Ces deux scripts permettent la gestion d'affichage des fenêtres modales d'ajout d'une prestation et d'un 
 * prestataire.
 */
$('#bt_ajout_org_prest').on('click', function() {
	$('#fm_ajout_prest').modal('hide');
	$('#fm_ajout_org_prest').modal('show');
});

$('#fm_ajout_org_prest').on('hidden.bs.modal', function() {
	$('#fm_ajout_prest').modal('show');
});

/**
 * Ce script permet de gérer l'état des contrôles relatifs à un montant du formulaire de modification d'un dossier.
 */
$('form[name="f_modif_doss"] #id_GererDossier-id_av_cp').on('change', function() {
	var v_int_av_cp = $('#id_GererDossier-id_av_cp option:selected').text();
	if (v_int_av_cp == ACC_STR) {
		$('#id_GererDossier-mont_doss').attr('readonly', true);
		$('#id_GererDossier-mont_suppl_doss').removeAttr('readonly');
	}
	else {
		$('#id_GererDossier-mont_doss').removeAttr('readonly');
		$('#id_GererDossier-mont_suppl_doss').attr('readonly', true);
		$('#id_GererDossier-mont_suppl_doss').val(0);
	}
});

/**
 * Ce script permet de cocher/décocher automatiquement un groupe de cases à cocher.
 */
$('input[type="checkbox"]').on('change', function() {
	var o = $(this);
	if (o.val() == 'all') {
		var name = o.attr('id').substr(3);
		name = name.substr(0, name.length - 5);
		$('input[name="' + name + '"]').each(function() {
			if (o.is(':checked')) {
				this.checked = true;
			}
			else {
				this.checked = false;
			}
		});
	}
	else {
		if ($(this).is(':checked') == false) {
			$('#id_' + $(this).attr('name') + '__all').attr('checked', false);
		}
	}
});

/**
 * Ce script permet de mettre à jour la datatable relative aux ateliers concernés par une instance de concertation
 * sélectionnée.
 * _e : Objet DOM
 */
$('#id_GererActionPgre-id_ic_pgre').on('change', function(_e) {
	soum_f(
		_e, 
		function() {
			$('#id_GererActionPgre-cbsm_atel_pgre__all').attr('checked', false);
		},
		[$('form[name="f_ger_act_pgre"]'), '?action=filtrer-ateliers']
	);
});

/**
 * Ce script permet de déterminer l'état d'alerte du compte.
 */
$(window).load(function() {
	$.getJSON(URL_ALERT + '?action=compter-alertes', function(_d) {
		if (_d > 0) {
			$('#za_alert').css('background-color', '#FF0921');
		}
		else {
			$('#za_alert').css('background-color', '#94C054');
		}
	});
});

/**
 * Ce script permet l'initialisation du graphique relatif à la variation de l'économie de la ressource en eau.
 */
$(function() {
    $('body').on('shown.bs.tab', 'a[href="#ong_pdc"]', function() {
    	if (est_init == false) {
    		est_init = true;
	    	$.post('?action=initialiser-graphique', function(_d) {
	    		try {
		    		$.plot('#zg_pdc', [{
		    			color : '#FF0921',
		    			data : _d[1],
		    			hoverable : false,
		    			label : 'Objectifs d\'économie de la ressource en eau (en m<sup>3</sup>)',
		    			points : { show : false },
		    			shadowSize : 0
		    		}, {
		    			color : '#F8B862',
		    			data : _d[0],
		    			label : 'Économie de la ressource en eau réalisée (en m<sup>3</sup>)',
		    			shadowSize : 0
		    		}], {
		    			grid: { backgroundColor : '#FFF', borderWidth: 1, color : '#555', hoverable : true },
		    			legend : { container : $('#zg_pdc').next(), show : true },
			    		series : {
			    			lines : { show : true },
			    			points : { show : true }
			    		},
			    		xaxis : {
			    			minTickSize: [1, 'day'],
			    			mode : 'time',
			    			timeformat : '%d/%m'
			    		}
		    		});
		    	}
		    	catch (e) {
		    		
		    	}
	    	});
	    }
    });
});

/**
 * Ce script permet l'affichage de la zone d'information relative à l'un des points du graphique des points de 
 * contrôle.
 */
$('#zg_pdc').bind('plothover', function(_e, _p, item) {

	// Je mets en forme l'identifiant de la zone d'information.
	var id = $(_e.target).attr('id') + '_tooltip';

	// Je retire la zone d'information.
	$('#' + id).remove();

	if (item) {
		if (pt_prec != item.datapoint) {
			pt_prec = item.datapoint;

			// Je prépare la date du point de contrôle.
			var o_dt = new Date(item.datapoint[0]);
			var dt = zfill(o_dt.getDate(), 2) + '/' + zfill(o_dt.getMonth() + 1, 2) + '/' + zfill(o_dt.getFullYear(), 4);

			// J'affiche la zone d'information.
			show_tooltip(id, item.datapoint[1] + ' m<sup>3</sup> économisé(s) au ' + dt);
		}
	}
	else {
		pt_prec = null;
	}
});

/**
 * Ce script permet de simuler la soumission du formulaire de choix d'une action PGRE.
 */
$('form[name="f_ch_act_pgre"]').on('change', function() {
	$(this).submit();
});

/**
 * Ce script permet de traiter le formulaire de choix d'une action PGRE.
 * _e : Objet DOM
 */
$('form[name="f_ch_act_pgre"]').on('submit', function(_e) {
	soum_f(
		_e,
		function() {
			$('#t_ch_act_pgre tbody > tr').each(function() {
				if ($(this).find('td:first-child').attr('class') != 'dataTables_empty') {
					$(this).find('td:first-child').addClass('b');
				}				
			});
		}
	);
});