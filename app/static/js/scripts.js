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

$(document).keydown(function(e)
{
	if (e.keyCode == 116)
	{
		//alert_util(e);
	}
})

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
 * Ce script permet de griser le champ relatif à la date de délibération au maître d'ouvrage d'un dossier si l'état d'
 * avancement choisi est "En projet".
 * e : Variable objet JavaScript
 */
$('select[id$="zl_av"]').change(function(e)
{
	// J'obtiens le préfixe du contrôle.
	var prefixe = ret_pref(e);

	if (isNaN($(this).val()) == false)
	{
		// Je récupère l'intitulé de l'état d'avancement sélectionné.
		var intitule_avancement = $('#id_' + prefixe + 'zl_av option:selected').text();
		
		// Je stocke l'objet lié à la date de délibération au maître d'ouvrage.
		var obj_date_deliberation_moa = $('#id_' + prefixe + 'zd_dt_delib_moa_doss');

		if (intitule_avancement == 'En projet')
		{
			// Je grise le champ relatif à la date de délibération au maître d'ouvrage d'un dossier.
			obj_date_deliberation_moa.val('');
			obj_date_deliberation_moa.attr('disabled', true);
		}
		else
		{
			// Je dégrise le champ relatif à la date de délibération au maître d'ouvrage d'un dossier.
			obj_date_deliberation_moa.removeAttr('disabled');
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
	var intitule_programme = $('#id_CreerDossier-zld_progr option:selected').text();

	// Je gère l'affichage du module PGRE.
	if (intitule_programme == 'PGRE')
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
$('input[name="cbsm_moa"]').change(function(e)
{
	ger_coch_cbsm(e, $('input[name="cbsm_moa"]'));
});