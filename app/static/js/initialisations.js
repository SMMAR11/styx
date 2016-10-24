/* Constante globale */
const CONTACT_ADMIN = 'Veuillez contacter l\'administrateur de l\'application.';

/* Variable globale */
var tab_datatables;

/**
 * Ce script permet l'initialisation d'éléments dès la fin du chargement du DOM.
 */
$(document).ready(function()
{
	// J'initialise les datatables de l'application.
	tab_datatables =
	{
		'ajouter_dossier_associe' : init_datatable($('#tab_ajouter_dossier_associe'), [4], true),
		'choisir_dossier' : init_datatable($('#tab_choisir_dossier'), [4], true),
		'consulter_demandes_versement' : init_datatable($('#tab_consulter_demandes_versement'), [6]),
		'consulter_dossiers_associes' : init_datatable($('#tab_consulter_dossiers_associes'), [6]),
		'consulter_factures' : init_datatable($('#tab_consulter_factures'), [4]),
		'consulter_photos' : init_datatable($('#tab_consulter_photos'), [0, 4]),
		'consulter_plan_financement' : init_datatable($('#tab_consulter_plan_financement'), [5]),
		'consulter_prestations' : init_datatable($('#tab_consulter_prestations'), [5]),
		'selectionner_dossiers' : init_datatable($('#tab_selectionner_dossiers'), [7], true)
	}

	// J'initialise les zones de date de l'application.
	$('.date').datepicker(
	{
		language : 'fr',
		format : 'dd/mm/yyyy',
		weekStart : 1,
		autoclose : true,
		orientation : 'bottom left',
		startDate : '01/01/1900',
		endDate : '31/12/9999'
	});

	// J'ajoute une alerte à chaque élément du menu principal.
	$('form').each(function()
	{
		if ($(this).hasClass('alert-user'))
		{
			$('#menu_principal').find('.alert-user').each(function()
			{
				// Je définis un événement onclick sur l'élément courant du menu principal.
				$(this).attr('onclick', 'alert_util(event)');

				// Je retire la classe temporaire "alert-user" de l'élément courant.
				$(this).removeClass('alert-user');
			});

			// Je retire la classe "alert-user" du formulaire courant.
			$(this).removeClass('alert-user');
		}
	});

	// Je cache chaque liste déroulante qui possède la classe hide-field.
	$('.hide-field').each(function()
	{
		// Je récupère le bloc qui possède la classe "field-wrapper" du champ à cacher.
		var id_liste = $(this).attr('id');
		var bloc = select_cont($('#' + id_liste));

		// Je cache le bloc.
		bloc.hide();
	});

	// J'affiche chaque liste déroulante qui possède la classe temporaire show-field-temp.
	$('.show-field-temp').each(function()
	{
		// Je récupère le bloc qui possède la classe "field-wrapper" du champ à afficher.
		var id_liste = $(this).attr('id');
		var bloc = select_cont($('#' + id_liste));

		// J'affiche le bloc.
		bloc.show();

		// Je retire la classe temporaire.
		$(this).removeClass('show-field-temp');
	});

	// Je définis l'onglet actif du menu de consultation d'un dossier.
	try
	{
		// Je lance une requête AJAX.
		$.ajax(
		{
			type : 'post',
			url : '/retourner-onglet-actif.html',
			dataType : 'html',
			success : function(data)
			{
				$('#menu_dossier').find('a[href="' + data + '"]').parent().addClass('active');
				$(data).addClass('in active');
			}	
		});
	}
	catch (e)
	{

	}
});

/**
 * Ce script permet d'afficher la page web dès la fin du chargement de celle-ci.
 */
$(window).load(function()
{
	setTimeout(function()
	{
		// Je cache le loader.
		$('div#loader_page').hide();

		// J'affiche la page.
		$('body').removeAttr('style');
		$('div.container-fluid').removeAttr('style');

		// Je retire le loader.
		$('div#loader_page').remove();

	}, 250);
});