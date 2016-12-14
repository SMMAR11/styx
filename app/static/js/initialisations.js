/* Constantes globales */
const CONTACT_ADMIN = 'Veuillez contacter l\'administrateur de l\'application.';
const POURC_TVA = 1.2;

/* Variables globales */
var tab_datatables;
var timer = [];

/**
 * Ce script permet l'initialisation d'éléments dès la fin du chargement du DOM.
 */
$(document).ready(function()
{
	// J'initialise les datatables de l'application.
	tab_datatables =
	{
		'ajouter_dossier_associe' : init_datatable($('#tab_ajouter_dossier_associe'), [3]),
		'choisir_dossier' : init_datatable($('#tab_choisir_dossier'), [3]),
		'choisir_prestation' : init_datatable($('#tab_choisir_prestation'), [5]),
		'consulter_avenants' : init_datatable($('#tab_consulter_avenants'), []),
		'consulter_demandes_versement' : init_datatable($('#tab_consulter_demandes_versement'), [6]),
		'consulter_dossiers_associes' : init_datatable($('#tab_consulter_dossiers_associes'), [5]),
		'consulter_factures' : init_datatable($('#tab_consulter_factures'), [4]),
		'consulter_photos' : init_datatable($('#tab_consulter_photos'), [0, 4]),
		'consulter_financements' : init_datatable($('#tab_consulter_financements'), [4]),
		'consulter_prestations' : init_datatable($('#tab_consulter_prestations'), [6]),
		'consulter_dossiers_prestation' : init_datatable($('#tab_dossiers_prestation'), [2]),
		'selectionner_dossiers' : init_datatable($('#tab_selectionner_dossiers'), [6])
	}

	// J'initialise les zones de date de l'application.
	$(document).on('mousemove', function()
	{
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
	});

	$('form').each(function()
	{
		// J'ajoute une alerte à chaque élément du menu principal.
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

		// Je retire l'attribut "required" pour tous les champs de tous les formulaire de la page active.
		for (var i = 0; i < $(this).length; i ++)
		{
			var form = $(this)[i];
			for (var j = 0; j < form.length; j ++)
			{
				var balise = form[j];
				$(balise).removeAttr('required');
			}
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
			url : URL_APP_NAV,
			dataType : 'html',
			success : function(data)
			{
				$('#app-nav').find('a[href="' + data + '"]').parent().addClass('active');
				$(data).addClass('active in');
			}	
		});
	}
	catch (e)
	{

	}

	// Je désigne le fichier uploadé dans le cas d'une modification.
	$('.file-return').each(function()
	{
		// Je pointe vers l'objet "input".
		var obj_contr = $(this).prev().prev();

		// Je récupère le chemin du fichier uploadé.
		var chem_fich = obj_contr.attr('title');

		if (chem_fich != undefined)
		{
			// Je définis l'identifiant du bouton "Retirer".
			var id_span = obj_contr.attr('id').split('_');
			id_span[1] = id_span[1].slice(0, id_span[1].length - 2) + 'bt';
			id_span = id_span.join('_');

			// Je mets en forme le bouton "Retirer".
			var span = $('<span/>', { 'id' : id_span, html : 'Retirer' });

			// J'affiche le chemin du fichier uploadé ainsi que le bouton "Retirer".
			$(this).html(chem_fich + ' ');
			$(this).append(span);
		}
	});
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

/**
 * Ce script permet de passer le message de succès de la fenêtre modale.
 */
$(document).on('click', '.a-to-span', function()
{
	clearTimeout(timer[0]);
	window.location.href = timer[1];
});