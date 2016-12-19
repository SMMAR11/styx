/**
 * Ce script permet de bloquer le comportement par défaut de l'élément cliqué.
 * e : Variable objet JavaScript
 */
$('.to-block').click(function(e)
{
	e.preventDefault();
});

/**
 * Ce script permet de retirer le focus lié à l'élément cliqué.
 */
$('.to-unfocus').click(function()
{
	$(this).blur();
});

/**
 * Ce script permet le traitement lié à l'identification.
 * e : Variable objet JavaScript
 */
$('form[name="form_identification"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'identification.
	trait_form(e);
});

/**
 * Ce script permet le traitement lié à la demande de réinitialisation du mot de passe.
 * e : Variable objet JavaScript
 */
$('form[name="form_oublier_mdp"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire de demande de réinitialisation du mot de passe.
	trait_form(e);
});

/**
 * Ce script permet de gérer les champs liés à état d'avancement du dossier ainsi que ceux liés au comité de
 * programmation.
 * e : Variable objet JavaScript
 */
$('select[id$="zl_av"], select[id$="zl_av_cp"]').change(function(e)
{
	// J'obtiens le préfixe du contrôle.
	var prefixe = ret_pref(e);

	if (isNaN($(this).val()) == false)
	{
		// Je récupère les intitulés.
		var int_av = $('#id_' + prefixe + 'zl_av option:selected').text();
		var int_av_cp = $('#id_' + prefixe + 'zl_av_cp option:selected').text();

		// Je pointe vers les contrôles de type "date".
		var obj_dt_delib_moa_doss = $('#id_' + prefixe + 'zd_dt_delib_moa_doss');
		var obj_dt_av_cp_doss = $('#id_' + prefixe + 'zd_dt_av_cp_doss');

		if (int_av == 'En projet')
		{
			// Je grise le champ relatif à la date de délibération au maître d'ouvrage d'un dossier.
			obj_dt_delib_moa_doss.val('');
			obj_dt_delib_moa_doss.attr('disabled', true);

			// Je sélectionne par défaut l'option "En attente".
			$('#id_' + prefixe + 'zl_av_cp option').each(function()
			{
				if ($(this).text() == 'En attente')
				{
					$('#id_' + prefixe + 'zl_av_cp').val($(this).val());
				}
			});
		}
		else
		{
			// Je dégrise le champ relatif à la date de délibération au maître d'ouvrage d'un dossier.
			obj_dt_delib_moa_doss.removeAttr('disabled');
		}

		if (int_av == 'En projet' || int_av_cp == 'En attente' || int_av_cp == 'Sans objet')
		{
			// Je grise le champ relatif à la date de l'avis du comité de programmation.
			obj_dt_av_cp_doss.val('');
			obj_dt_av_cp_doss.attr('disabled', true);
		}
		else
		{
			// Je dégrise le champ relatif à la date de l'avis du comité de programmation.
			obj_dt_av_cp_doss.removeAttr('disabled');
		}
	}
});

/**
 * Ce script permet d'obtenir la liste des axes et des types de dossier relatifs au programme choisi dans la liste 
 * déroulante des programmes.
 * e : Variable objet JavaScript
 */
$('select[id$="zld_progr"]').change(function(e)
{
	var tab_params = new Array(
		'programme=' + $(this).val()
	);

	alim_liste(e, tab_params);
});

/**
 * Ce script permet d'obtenir la liste des sous-axes relatifs au programme choisi dans la liste déroulante des 
 * programmes et à l'axe choisi dans la liste déroulante des axes.
 * e : Variable objet JavaScript
 */
$('select[id$="zld_axe"]').change(function(e)
{
	// J'obtiens le préfixe de la liste déroulante.
	var prefixe = ret_pref(e);

	var tab_params = new Array(
		'programme=' + $('#id_' + prefixe + 'zld_progr').val(),
		'axe=' + $(this).val()
	);

	alim_liste(e, tab_params);
});

/**
 * Ce script permet d'obtenir la liste des actions relatives au programme choisi dans la liste déroulante des 
 * programmes, à l'axe choisi dans la liste déroulante des axes et au sous-axe choisi dans la liste déroulante des 
 * sous-axes.
 * e : Variable objet JavaScript
 */
$('select[id$="zld_ss_axe"]').change(function(e)
{
	// J'obtiens le préfixe de la liste déroulante.
	var prefixe = ret_pref(e);

	var tab_params = new Array(
		'programme=' + $('#id_' + prefixe + 'zld_progr').val(),
		'axe=' + $('#id_' + prefixe + 'zld_axe').val(),
		'sous_axe=' + $(this).val()
	);

	alim_liste(e, tab_params);
});

/**
 * Ce script permet d'actualiser la datatable relative à l'ajout d'un dossier associé.
 * e : Variable objet JavaScript
 */
$('form[name="form_ajouter_dossier_associe"]').change(function(e)
{
	// J'actualise la datatable.
	act_datatable(
		e, 
		$('form[name="form_ajouter_dossier_associe"]'), 
		tab_datatables['ajouter_dossier_associe'],
		function()
		{
			// J'imite la mise en forme initiale de la datatable.
			$('#tab_ajouter_dossier_associe').find('tbody').find('tr').each(function()
			{
				if ($(this).find('td:first-child').attr('class') != 'dataTables_empty')
				{
					$(this).find('td:first-child').addClass('b');
				}				
			});
		},
		'ChoisirDossier-'
	);
});

/**
 * Ce script permet de transmettre un numéro de dossier associé au formulaire de création d'un dossier.
 */
$('#tab_ajouter_dossier_associe').on('click', '.bt-choisir', function()
{
	// Je récupère le numéro du dossier choisi.
	var num_doss = $(this).parent().parent().find($('td:first-child')).text();

	// Je transmets le numéro du dossier associé choisi au formulaire principal.
	$('input[name$="za_doss_ass"]').val(num_doss);

	// Je ferme la fenêtre modale relative au choix d'un dossier associé.
	$('#fm_choisir_dossier_associe').modal('hide');
});

/**
 * Ce script permet la réinitialisation de la valeur de la zone d'affichage liée au dossier associé lorsqu'on se trouve
 * sur la page de création d'un dossier si et seulement si l'option "Non" est cochée.
 */
$('input[name="rb_doss_ass"]').change(function()
{
	if ($(this).val() == 0)
	{
		$('#id_CreerDossier-za_doss_ass').val('');
	}
});

/**
 * Ce script permet la gestion de l'affichage du module PGRE.
 */
$('#id_CreerDossier-zld_progr').change(function(e)
{
	// Je récupère l'intitulé du programme sélectionné.
	var int_progr = $('#id_CreerDossier-zld_progr option:selected').text();

	// Je gère l'affichage du module PGRE.
	if (int_progr == 'PGRE')
	{
		$('#za_form_pgre').show();
	}
	else
	{
		$('#za_form_pgre').hide();
	}
});

/**
 * Ce script permet de gérer la valeur de chaque case à cocher liées à une rivière lors du renseignement d'un dossier
 * dont le programme est "PGRE".
 */
$('input[name$="cbsm_riv"]').change(function(e)
{
	ger_coch_cbsm(e, $('input[name$="cbsm_riv"]'));
});

/**
 * Ce script permet le traitement d'une requête d'insertion d'un dossier dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_creer_dossier"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'insertion d'un dossier.
	trait_form(e, 'CreerDossier-');
});

/**
 * Ce script permet la réinitialisation de la valeur de la zone d'affichage liée au dossier associé lorsqu'on se trouve
 * sur la page de modification d'un dossier.
 */
$('#bt_supprimer_dossier_associe').click(function()
{
	$('#id_ModifierDossier-za_doss_ass').val('');
});

/**
 * Ce script permet le traitement d'une requête de modification d'un dossier dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_modifier_dossier"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire de modification d'un dossier.
	trait_form(e, 'ModifierDossier-');
});

/**
 * Ce script permet d'afficher la demande de confirmation de suppression d'un dossier.
 * e : Variable objet JavaScript
 */
$('#bt_supprimer_dossier').click(function(e)
{
	aff_html_ds_fm(e, 'supprimer_dossier');
});

/**
 * Ce script permet d'actualiser la datatable relative au choix d'un dossier.
 * e : Variable objet JavaScript
 */
$('form[name="form_choisir_dossier"]').change(function(e)
{
	// J'actualise la datatable.
	act_datatable(
		e, 
		$('form[name="form_choisir_dossier"]'),
		tab_datatables['choisir_dossier'],
		function()
		{
			// J'imite la mise en forme initiale de la datatable.
			$('#tab_choisir_dossier').find('tbody').find('tr').each(function()
			{
				if ($(this).find('td:first-child').attr('class') != 'dataTables_empty')
				{
					$(this).find('td:first-child').addClass('b');
				}				
			});
		}
	);
});

/**
 * Ce script permet d'afficher les informations relatives à une photo d'un dossier.
 */
$('#tab_consulter_photos').find('img').click(function(e)
{
	aff_html_ds_fm(e, 'afficher_photo');
});

/**
 * Ce script permet de retourner le nom d'un fichier prêt à être uploadé.
 */
$('input[name*="zu_"]').change(function(e)
{
	// J'affiche le nom du fichier sélectionné.
	$(this).parent().find('.file-return').html($(this).val());
});

/**
 * Ce script permet le traitement d'une requête d'insertion d'une photo dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_ajouter_photo"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'insertion d'une photo.
	trait_form(e, 'AjouterPhoto-');
});

/**
 * Ce script permet le traitement d'une requête de modification d'une photo dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_modifier_photo"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire de modification d'une photo.
	trait_form(e, 'ModifierPhoto-');
});

/**
 * Ce script permet d'afficher la demande de confirmation de suppression d'une photo.
 * e : Variable objet JavaScript
 */
$('#tab_consulter_photos').find('.bt-supprimer').click(function(e)
{
	aff_html_ds_fm(e, 'supprimer_photo');
});

/**
 * Ce script permet d'actualiser la datatable relative à la réalisation d'un état en sélectionnant des dossiers.
 * e : Variable objet JavaScript
 */
$('form[name="form_selectionner_dossiers"]').submit(function(e)
{
	e.preventDefault();

	// J'actualise la datatable.
	act_datatable(
		e, 
		$('form[name="form_selectionner_dossiers"]'),
		tab_datatables['selectionner_dossiers'],
		function()
		{
			// J'imite la mise en forme initiale de la datatable.
			$('#tab_selectionner_dossiers').find('tbody').find('tr').each(function()
			{
				if ($(this).find('td:first-child').attr('class') != 'dataTables_empty')
				{
					$(this).find('td:first-child').addClass('b');
				}				
			});
		}
	);
});

/**
 * Ce script permet de gérer la valeur de chaque case à cocher liées au maître d'ouvrage lors du renseignement du
 * formulaire de réalisation d'un état en sélectionnant des dossiers.
 */
$('input[name="cbsm_org_moa"]').change(function(e)
{
	ger_coch_cbsm(e, $('input[name="cbsm_org_moa"]'));
});

/**
 * Ce script permet le traitement d'une requête d'insertion d'un financement dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_ajouter_financement"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'insertion d'un financement.
	trait_form(e, 'AjouterFinancement-');
});

/**
 * Ce script permet le calcul des montants HT et TTC de participation, ainsi que l'ajout ou non de l'attribut 
 * "readonly" sur certains champs.
 */
$('input[name$="zs_mont_ht_elig_fin"], input[name$="zs_mont_ttc_elig_fin"], input[name$="zs_pourc_elig_fin"]').on(
	'input', function()
	{
		/**
		 * Cette fonction permet de calculer un montant de participation.
		 * p_mont : Montant éligible
		 * p_pourc : Pourcentage éligible
		 */
		function calc_mont(p_mont, p_pourc)
		{
			// J'initialise le montant total.
			var mont_tot = '';

			if (isNaN(p_mont) == false && isNaN(p_pourc) == false)
			{
				if (p_mont != '' && p_pourc != '')
				{
					// Je calcule le montant total (arrondi au centième).
					mont_tot = p_mont * (p_pourc / 100);
					mont_tot = Math.round(mont_tot * 100) / 100;
				}
			}

			return mont_tot;
		}

		// Je récupère les montants éligibles ainsi que le pourcentage éligible.
		var mont_ht_elig_fin = $('input[name$="zs_mont_ht_elig_fin"]').val();
		var mont_ttc_elig_fin = $('input[name$="zs_mont_ttc_elig_fin"]').val();
		var pourc_elig_fin = $('input[name$="zs_pourc_elig_fin"]').val();

		// Je calcule le montant éligible TTC afin de prévenir un bug si et seulement si le contrôlé altéré est celui
		// appartenant au montant éligible HT.
		if ($(this).attr('name').indexOf('zs_mont_ht_elig_fin') > -1)
		{
			mont_ttc_elig_fin = (mont_ht_elig_fin * POURC_TVA).toFixed(2);
		}

		// J'affiche les montants de participation.
		$('input[name$="zs_mont_ht_part_fin"]').val(calc_mont(mont_ht_elig_fin, pourc_elig_fin));
		$('input[name$="zs_mont_ttc_part_fin"]').val(calc_mont(mont_ttc_elig_fin, pourc_elig_fin));

		// Je prépare les variables qui vont me permettre de savoir si je dois ajouter l'attribut "readonly" aux champs
		// liés à la participation.
		var tab_val = new Array(mont_ht_elig_fin, mont_ttc_elig_fin, pourc_elig_fin);
		var readonly = true;

		// Je vérifie s'il y a une erreur de saisie.
		for (var i = 0; i < tab_val.length; i ++)
		{
			if (isNaN(tab_val[i]) == true)
			{
				readonly = false;
			}

			if (tab_val[i].length == 0)
			{
				readonly = false;
			}
		}

		if (readonly == true)
		{
			$('input[name$="zs_mont_ht_part_fin"]').attr('readonly', true);
			$('input[name$="zs_mont_ttc_part_fin"]').attr('readonly', true);
		}
		else
		{
			$('input[name$="zs_mont_ht_part_fin"]').removeAttr('readonly');
			$('input[name$="zs_mont_ttc_part_fin"]').removeAttr('readonly');
		}
	}
);

/**
 * Ce script permet la gestion du champ lié au pourcentage de réalisation des travaux.
 */
$('select[id$="zl_paiem_prem_ac"').change(function()
{
	// Je pointe vers l'objet souhaité.
	obj_pourc_real_fin = $('input[name$="zs_pourc_real_fin"]');

	if ($('select[id$="zl_paiem_prem_ac"] option:selected').text() == 'Pourcentage de réalisation des travaux')
	{
		obj_pourc_real_fin.removeAttr('readonly');
	}
	else
	{
		obj_pourc_real_fin.val('');
		obj_pourc_real_fin.attr('readonly', true);
	}
});

/**
 * Ce script permet le traitement d'une requête d'insertion d'un arrêté dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_ajouter_arrete"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'insertion d'un arrêté.
	trait_form(e, 'AjouterArrete-');
});

/**
 * Ce script permet d'afficher la demande de confirmation de suppression d'un arrêté.
 * e : Variable objet JavaScript
 */
$('#bt_supprimer_arrete').click(function(e)
{
	aff_html_ds_fm(e, 'supprimer_arrete');
});

/**
 * Ce script permet le traitement d'une requête de modification d'un arrêté dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_modifier_arrete"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire de modification d'un arrêté.
	trait_form(e, 'ModifierArrete-');
});

/**
 * Ce script permet le traitement d'une requête d'insertion d'une prestation dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_ajouter_prestation"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'insertion d'une prestation.
	trait_form(e, 'AjouterPrestation-');
});

/**
 * Ce script permet la gestion de l'affichage du formulaire d'insertion d'une prestation.
 */
$('input[name="rb_prest_exist"]').change(function()
{
	if ($(this).val() == 1)
	{
		$('#za_prest_nvelle').hide();
		$('#za_prest_exist').show();
	}
	else
	{
		$('#za_prest_nvelle').show();
		$('#za_prest_exist').hide();
	}
});

/**
 * Ce script permet la "suppression" d'un fichier uploadé.
 */
$('.file-return').on('click', 'span', function()
{
	// Je récupère l'identifiant de la zone d'affichage du fichier uploadé.
	var id = $(this).attr('id').split('_');
	id[1] = id[1].slice(0, id[1].length - 2) + 'za';
	id = id.join('_');

	// Je retire le chemin du fichier uploadé.
	$('#' + id).val('');

	// Je réinitialise la zone d'upload.
	$(this).parent().prev().prev().removeAttr('title');
	$(this).parent().empty();
});

/**
 * Ce script permet le traitement d'une requête d'insertion d'un avenant dans la base de données.
 * e : Variable objet JavaScript
 */
 $(document).on('submit', 'form[name="form_ajouter_avenant"]', function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'insertion d'un avenant.
	trait_form(e, 'AjouterAvenant-');
});

/**
 * Ce script permet d'actualiser la datatable relative à la consultation des avenants d'un couple prestation/dossier.
 * e : Variable objet JavaScript
 */
$('form[name="form_rechercher_avenants"]').change(function(e)
{
	// J'actualise la datatable.
	act_datatable(
		e, 
		$('form[name="form_rechercher_avenants"]'), 
		tab_datatables['consulter_avenants'],
		function(){},
		'RechercherAvenants-'
	);

	// Je récupère l'identifiant du dossier choisi.
	var id_doss = $('#id_RechercherAvenants-zl_doss').val();

	// J'initialise le contenu de la zone d'affichage liée au dossier affecté par le futur avenant.
	var result = '';
	if (isNaN(id_doss) == false)
	{
		result = $('#id_RechercherAvenants-zl_doss option:selected').text();
	}

	// J'affiche le contenu dans la zone d'affichage.
	$('#id_AjouterAvenant-za_num_doss').val(result);
});

/**
 * Ce script permet le traitement d'une requête d'insertion d'une facture dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_ajouter_facture"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'insertion d'une facture.
	trait_form(e, 'AjouterFacture-');
});

/**
 * Ce script permet l'autocomplétion via les numéros SIRET existants dans la base de données selon un critère de
 * recherche.
 */
$.typeahead({
    input : 'input[name$="zsac_siret_org_prest"]',
    minLength : 1,
    order : 'asc',
    dynamic : true,
    delay : 500,
    template : function(query, item)
    {
    	tpl = [
    		'{{siret_org_prest}}',
    		'<br />',
    		'<span class="description">',
    		'{{n_org}}',
    		'</span>'
    	];

        return tpl.join('\n'); 
    },
    emptyTemplate : 'Aucun résultat pour {{query}}',
    source :
    {
        org_prest :
        {
            display : 'siret_org_prest',
            data : [],
            ajax : function(query)
            {
            	return {
                    type : 'GET',
                    url : URL_AUTOCOMPL,
                    path : 'data.org_prest',
                    data :
                    {
                    	action : 'lister-siret',
                        q : '{{query}}'
                    },
                    beforeSend : function()
					{
						// J'informe l'utilisateur qu'une requête AJAX se prépare.
						aff_loader_ajax(true);
					},
					complete : function()
					{
						// J'informe l'utilisateur que la requête AJAX est terminée.
						aff_loader_ajax(false);
					}
                };
            },
        }
    },
    debug: true
});

/**
 * Ce script permet d'actualiser la datatable relative au choix d'une prestation.
 * e : Variable objet JavaScript
 */
$('form[name="form_choisir_prestation"]').change(function(e)
{
	// J'actualise la datatable.
	act_datatable(
		e, 
		$('form[name="form_choisir_prestation"]'), 
		tab_datatables['choisir_prestation'],
		function()
		{
			// Je réinitialise la zone d'affichage consacrée à la redistribution des montants de la prestation.
			$('#za_tab_montants_prestation').remove();
		},
		'ChoisirPrestation-'
	);
});

/**
 * Ce script permet d'afficher le tableau de redistribution des montants d'une prestation.
 */
$('#tab_choisir_prestation').on('click', '.bt-choisir', function()
{
	// Je garde en mémoire la prestation choisie.
	var _this = $(this);
	
	// Je lance une requête AJAX.
	$.ajax(
	{
		type : 'post',
		url : $(this).attr('action'),
		dataType : 'html',
		beforeSend : function()
		{
			// J'informe l'utilisateur qu'une requête AJAX se prépare.
			aff_loader_ajax(true);
		},
		success : function(data)
		{
			// Je réinitialise la source du bouton de choix d'une prestation.
			$('#tab_choisir_prestation').find('.bt-choisir-actif').each(function()
			{
				$(this).removeClass('bt-choisir-actif');
				$(this).addClass('bt-choisir');
			});

			// Je montre à l'utilisateur la prestation choisie.
			_this.removeClass('bt-choisir');
			_this.addClass('bt-choisir-actif');

			// Je réinitialise la zone d'affichage consacrée à la redistribution des montants de la prestation.
			$('#za_tab_montants_prestation').remove();

			// J'affiche la zone d'affichage.
			$(data).insertAfter($('#tab_choisir_prestation').parent().parent());

			// Je mets en forme les zones de saisies pré-remplies consacrées aux montants.
			$('#za_tab_montants_prestation').find('.field-wrapper').each(function()
			{
				$(this).css('margin-bottom', 0);
			});

			// J'initialise la datatable.
			var dt = init_datatable($('#tab_montants_prestation'), [0, 1, 2, 3, 4]);
		},
		error : function(xhr, ajaxOptions, thrownError)
		{
			var err = xhr.status + ' ' + thrownError;
			err += '\n';
			err += CONTACT_ADMIN;
			
			alert(err);
		},
		complete : function()
		{
			// J'informe l'utilisateur que la requête AJAX est terminée.
			aff_loader_ajax(false);
		}
	});
});

/**
 * Ce script permet le traitement d'une requête de modification avancée d'une prestation dans la base de données.
 * e : Variable objet JavaScript
 */
$(document).on('submit', 'form[name="form_relier_prestation"]', function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'insertion d'une facture.
	trait_form(e, 'RepartirMontantsPrestation-');
});

/**
 * Ce script permet le calcul automatique d'un montant TTC via un pourcentage de TVA défini préalablement, et à partir
 * d'un montant HT.
 */
$(document).on('keyup', 'input[name*="_ht_"]', function()
{
	// Je pointe vers les zones de saisies liées.
	var obj_ht = $(this).attr('name');
	var obj_ttc = obj_ht.replace('_ht_', '_ttc_');

	// Je stocke les montants HT et TTC.
	var v_ht = $(this).val();
	var v_ttc = (v_ht * POURC_TVA).toFixed(2);

	if (isNaN(v_ht) == true || v_ht.length == 0)
	{
		v_ttc = '';
	}

	// J'affiche le montant TTC.
	$('input[name="' + obj_ttc + '"]').val(v_ttc);
});

/**
 * Ce script permet d'afficher les informations relatives à une photo d'un dossier.
 */
$('#tab_consulter_prestations').find('span[data-target="#fm_ajouter_avenant"]').click(function(e)
{
	aff_html_ds_fm(e, 'ajouter_avenant');
});

/**
 * Ce script permet le traitement d'une requête d'insertion d'une demande de versement dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_ajouter_ddv"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire d'insertion d'une demande de versement.
	trait_form(e, 'AjouterDemandeDeVersement-');
});

/**
 * Ce script permet le traitement d'une requête de modification de la géométrie d'un dossier dans la base de données.
 * e : Variable objet JavaScript
 */
$('form[name="form_modifier_carto"]').submit(function(e)
{
	// Je bloque l'envoi du formulaire.
	e.preventDefault();

	// Je vérifie la validité des données transmises via le formulaire de modification de la géométrie d'un dossier.
	trait_form(e);
});

/**
 * Ce script permet la gestion du tableau des factures selon le type de versement sélectionné et le financeur 
 * sélectionné.
 * e : Variable objet JavaScript
 */
$('select[id$="zl_type_vers"], select[id$="zl_org_fin"]').change(function(e)
{
	// J'obtiens le préfixe du contrôle.
	var prefixe = ret_pref(e);

	// Je mets en place un indicateur déterminant si je dois afficher le tableau des factures.
	var tab = false;

	if (isNaN($('#id_' + prefixe + 'zl_type_vers').val()) == false)
	{
		// Je récupère l'intitulé du type de versement sélectionné.
		var int_type_vers = $('#id_' + prefixe + 'zl_type_vers option:selected').text();

		if (int_type_vers == 'Acompte' || int_type_vers == 'Solde')
		{
			tab = true;
		}
	}

	// Je pointe vers la datatable relative.
	var dtab = tab_datatables['choisir_factures_ddv'];

	if (tab == true)
	{
		// Je pointe vers le formulaire d'ajout d'une demande de versement.
		var obj_form = $('form[name="form_ajouter_ddv"]');

		// Je lance une requête AJAX.
		$.ajax(
		{
			type : 'post',
			url : obj_form.attr('action') + '?action=filtrer-factures',
			data : recup_post(obj_form),
			dataType : 'json',
			processData : false,
			contentType : false,
			beforeSend : function()
			{
				// J'informe l'utilisateur qu'une requête AJAX se prépare.
				aff_loader_ajax(true);
			},
			success : function(data)
			{
				// Je vide la datatable pour la rafraîchir entièrement.
				dtab.clear().draw();

				for (var i = 0; i < data.length; i ++)
				{
					// Je déclare un tableau vierge qui contiendra les données d'une ligne de la datatable actualisée.
					var lg = [];

					for (var j = 0; j < data[i].length; j ++)
					{
						// J'empile le tableau déclaré précédemment (cellule par cellule).
						lg.push(data[i][j]);
					}

					// J'ajoute une ligne à la datatable (ligne visible).
					dtab.row.add(lg).draw(true);
				}
			},
			error : function(xhr, ajaxOptions, thrownError)
			{
				var err = xhr.status + ' ' + thrownError;
				err += '\n';
				err += CONTACT_ADMIN;
				
				alert(err);
			},
			complete : function()
			{
				// J'informe l'utilisateur que la requête AJAX est terminée.
				aff_loader_ajax(false);
			}
		});

		$('#za_tab_factures_ddv').show();
	}
	else
	{
		// Je vide la datatable.
		dtab.clear().draw();
		
		$('#za_tab_factures_ddv').hide();
	}
});

/**
 * Ce script permet l'affichage des montants HT et TTC pré-calculés d'une demande de versement.
 */
$(document).on('change', 'input[name="cbsm_fact"]', function()
{
	// Je pointe vers le formulaire d'ajout d'une demande de versement.
	var obj_form = $('form[name="form_ajouter_ddv"]');

	// Je lance une requête AJAX.
	$.ajax(
	{
		type : 'post',
		url : obj_form.attr('action') + '?action=calculer-montants',
		data : recup_post(obj_form),
		dataType : 'json',
		processData : false,
		contentType : false,
		beforeSend : function()
		{
			// J'informe l'utilisateur qu'une requête AJAX se prépare.
			aff_loader_ajax(true);
		},
		success : function(data)
		{
			if (data['status'] == true)
			{
				// J'affiche les montants HT et TTC pré-calculés de la demande de versement.
				$('input[name$="zs_mont_ht_ddv"]').val(data['success'][0].toFixed(2));
				$('input[name$="zs_mont_ttc_ddv"]').val(data['success'][1].toFixed(2));
			}
			else
			{
				$('input[name$="zs_mont_ht_ddv"]').val('');
				$('input[name$="zs_mont_ttc_ddv"]').val('');
			}
		},
		error : function(xhr, ajaxOptions, thrownError)
		{
			var err = xhr.status + ' ' + thrownError;
			err += '\n';
			err += CONTACT_ADMIN;
			
			alert(err);
		},
		complete : function()
		{
			// J'informe l'utilisateur que la requête AJAX est terminée.
			aff_loader_ajax(false);
		}
	});
});

/**
 * Ce script permet l'affichage des informations relatives à une photo.
 */
$(document).on('click', '#bt_afficher_infos_photo', function()
{
	// Je retire le bouton du DOM.
	$(this).parent().remove();

	// J'affiche les informations de la photo.
	$('#za_infos_photo').show();
});