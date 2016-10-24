/**
 * Cette procédure permet d'actualiser une datatable selon un formulaire de recherche.
 * e : Variable objet JavaScript
 * p_form : Formulaire de filtrage
 * p_datatable : Datatable à actualiser
 * p_styles : Procédure permettant de mettre en forme la datatable après actualisation
 * p_prefixe : Préfixe des différents contrôles du formulaire (utilisé car un contrôle peut être dupliqué sur une même
 * page d'où la nécessité d'un préfixe pour différencier les contrôles)
 */
function act_datatable(e, p_form, p_datatable, p_styles = function(){}, p_prefixe = '')
{
	// Je lance une requête AJAX.
	$.ajax(
	{
		type : 'post',
		url : p_form.attr('action') + '?action=filtrer-dossiers',
		data : serial_array(p_form),
		dataType : 'json',
		beforeSend : function()
		{
			// J'informe l'utilisateur qu'une requête AJAX se prépare.
			aff_loader_ajax(true);
		},
		success : function(data)
		{
			// Je vide tous les messages d'erreurs lié au formulaire soumis.
			p_form.find('.za_erreur').empty();

			// Je retire la mise en forme des erreurs.
			ret_errs(p_form);

			if (data['success'])
			{
				// Je vide la datatable pour la rafraîchir entièrement.
				p_datatable.clear().draw();

				for (var i = 0; i < data['success'].length; i ++)
				{
					// Je déclare un tableau vierge qui contiendra les données d'une ligne de la datatable actualisée.
					var ligne = [];

					for (var j = 0; j < data['success'][i].length; j ++)
					{
						// J'empile le tableau déclaré précédemment (cellule par cellule).
						ligne.push(data['success'][i][j]);
					}

					// J'ajoute une ligne à la datatable (ligne visible).
					p_datatable.row.add(ligne).draw(true);
				}

				// Je mets en forme la datatable (on imite la mise en forme initiale généralement).
				p_styles();
			}
			else
			{
				// Je parcours chaque contrôle soumis à une erreur.
				for (var i in data)
				{
					// Je pointe vers la zone d'erreur relative au contrôle à l'indice i.
					var span = select_cont($('#id_' + p_prefixe + i)).find('.za_erreur');

					// Je prépare l'erreur.
					var ul = $('<ul/>', { 'class' : 'errorlist c-attention' });
					var li = $('<li/>', { html : data[i][0] });

					// J'affiche l'erreur.
					span.append(ul);
					ul.append(li);

					// Je mets en forme le contrôle à l'indice i.
					ajout_err($('#id_' + p_prefixe + i));
				}
			}
		},
		error : function(xhr, ajaxOptions, thrownError)
		{
			var erreur = xhr.status + ' ' + thrownError;
			erreur += '\n';
			erreur += CONTACT_ADMIN;
			
			alert(erreur);
		},
		complete : function()
		{
			// J'informe l'utilisateur que la requête AJAX est terminée.
			aff_loader_ajax(false);
		}
	});
}

/**
 * Cette procédure permet d'afficher du code HTML dans une fenêtre modale.
 * e : Variable objet JavaScript
 * p_suffixe :  Suffixe de la fenêtre modale.
 */
function aff_html_ds_fm(e, p_suffixe)
{
	// Je peux désormais manipuler l'objet.
	var obj = e.target;

	// Je lance une requête AJAX.
	$.ajax(
	{
		type : 'post',
		url : $(obj).attr('action'),
		dataType : 'html',
		beforeSend : function()
		{
			// J'informe l'utilisateur qu'une requête AJAX se prépare.
			aff_loader_ajax(true);
		},
		success : function(data)
		{
			// J'affiche dans la fenêtre modale le contenu de la réponse AJAX.
			$('#za_' + p_suffixe).html(data);

			// J'affiche la fenêtre modale.
			$('#fm_' + p_suffixe).modal();
		},
		error : function(xhr, ajaxOptions, thrownError)
		{
			var erreur = xhr.status + ' ' + thrownError;
			erreur += '\n';
			erreur += CONTACT_ADMIN;
			
			alert(erreur);
		},
		complete : function()
		{
			// J'informe l'utilisateur que la requête AJAX est terminée.
			aff_loader_ajax(false);
		}
	});
}

/**
 * Cette procédure permet de gérer l'affichage d'un message pendant une requête AJAX.
 * p_affichage : Dois-je afficher ou non le message ?
 */
function aff_loader_ajax(p_affichage)
{
	if (p_affichage == true)
	{
		// J'initialise le bloc.
		var div = $('<div/>', {
			'class' : 'text-center',
			'id' : 'loader_ajax'
		});

		// J'initialise le message.
		var message = '<span class="glyphicon glyphicon-refresh spin"></span>';
		message += '<br />';
		message += 'Veuillez patienter...';

		// J'insère le message dans le bloc.
		div.append(message);

		// J'affiche le bloc.
		div.insertAfter('.container-fluid');
	}
	else
	{
		// Je retire le bloc.
		$('div#loader_ajax').remove();
	}
}

/**
 * Cette procédure permet de transmettre un numéro de dossier associé au formulaire de création d'un dossier.
 * e : Variable objet JavaScript
 */
function ajout_doss_ass(e)
{
	// Je récupère le numéro du dossier choisi.
	var numero_dossier = $(e.currentTarget).parent().parent().find($('td:first-child')).text();

	// Je transmets le numéro du dossier associé choisi au formulaire principal.
	$('input[name$="za_doss_ass"]').val(numero_dossier);

	// Je ferme la fenêtre modale relative au choix d'un dossier associé.
	$('#fm_choisir_dossier_associe').modal('hide');
};

/**
 * Cette procédure permet à l'utilisateur de visualiser les contrôles soumis à une erreur.
 * p_controle : Contrôle possédant une erreur
 */
function ajout_err(p_controle)
{
	p_controle.addClass('invalide');
}

/**
 * Cette procédure alerte l'utilisateur d'une possible redirection (utile en cas de saisie).
 */
function alert_util(e)
{
	// J'affiche une alerte de redirection de page à l'utilisateur.
	var msg_box = confirm('Es-tu sûr de vouloir quitter cette page ?');

	// Je ne suis pas redirigé si l'utilisateur choisi l'option "Annuler".
	if (msg_box == false)
	{
		e.preventDefault();
	}
}

/**
 * Cette procédure permet de gérer l'affichage des listes déroulantes suivantes : programmes, axes, sous-axes, actions
 * et types de dossiers.
 * e : Variable objet JavaScript
 * p_tab_params : Tableau de paramètres relatif à une future requête de type "GET"
 */
function alim_liste(e, p_tab_params)
{
	/**
	 * Cette procédure permet de désafficher une liste de listes déroulantes.
	 * e : Variable objet JavaScript
	 * p_tab_listes : Tableau de listes déroulantes à désafficher
	 */
	function desaff_liste(p_tab_listes)
	{
		for (var i = 0; i < p_tab_listes.length; i ++)
		{
			$(p_tab_listes[i] + ' > option').each(function()
			{
				if ($(this).val() != 'D' && $(this).val() != 'DBP')
				{
					// Je retire le choix de la liste déroulante.
					$(this).remove();
				}
				else
				{
					// Je réinitialise la valeur de l'option par défaut.
					$(this).val('D');
				}
			});

			if ($(p_tab_listes[i]).hasClass('hide-field'))
			{
				// Je désaffiche la liste déroulante.
				select_cont($(p_tab_listes[i])).hide();
			}
		}
	}

	// Je récupère l'identifiant de la liste déroulante.
	var id_liste = '#' + e.target.getAttribute('id');

	// Je stocke le préfixe du formulaire.
	var prefixe = ret_pref(e);

	// Je déclare un tableau de listes à deux dimensions.
	var tab_listes =
	{
		'alimenter' : new Array(),
		'effacer' : new Array(),
		'modifier_option_par_defaut' : new Array(
			'#id_' + prefixe + 'zld_axe', 
			'#id_' + prefixe + 'zld_ss_axe', 
			'#id_' + prefixe + 'zld_act'
		)
	};

	// J'initialise le tableau des listes.
	if (id_liste == '#id_' + prefixe + 'zld_progr')
	{
		tab_listes['alimenter'] = new Array(
			'#id_' + prefixe + 'zld_axe', 
			'#id_' + prefixe + 'zld_type_doss'
		);

		tab_listes['effacer'] = new Array(
			'#id_' + prefixe + 'zld_axe', 
			'#id_' + prefixe + 'zld_ss_axe', 
			'#id_' + prefixe + 'zld_act', 
			'#id_' + prefixe + 'zld_type_doss'
		);
	}

	if (id_liste == '#id_' + prefixe + 'zld_axe')
	{
		tab_listes['alimenter'] = new Array(
			'#id_' + prefixe + 'zld_ss_axe'
		);

		tab_listes['effacer'] = new Array(
			'#id_' + prefixe + 'zld_ss_axe', 
			'#id_' + prefixe + 'zld_act'
		);
	}

	if (id_liste == '#id_' + prefixe + 'zld_ss_axe')
	{
		tab_listes['alimenter'] = new Array(
			'#id_' + prefixe + 'zld_act'
		);

		tab_listes['effacer'] = new Array(
			'#id_' + prefixe + 'zld_act'
		);
	}

	if ($(id_liste).val() > -1)
	{
		// Je lance une requête AJAX.
		$.ajax(
		{
			type : 'post',
			url : '?' + p_tab_params.join('&'),
			data : { csrfmiddlewaretoken : $('input[name="csrfmiddlewaretoken"]').val() },
			dataType : 'json',
			beforeSend : function()
			{
				// J'informe l'utilisateur qu'une requête AJAX se prépare.
				aff_loader_ajax(true);
			},
			success : function(data)
			{
				// Je désaffiche une liste de listes déroulantes.
				desaff_liste(tab_listes['effacer']);

				for (var i = 0; i < tab_listes['alimenter'].length; i ++)
				{
					// Je récupère la clé du tableau JSON.
					var split = tab_listes['alimenter'][i].split('_');
					var cle_json = split.slice(2, split.length).join('_');

					// J'alimente la liste déroulante.
					for (var j = 0; j < data[cle_json].length; j ++)
					{
						$(tab_listes['alimenter'][i]).append(
							'<option value="' + data[cle_json][j][0] + '">' + data[cle_json][j][1] + '</option>'
						);
					}

					// J'affiche la liste déroulante si elle admet des choix et si le contrôle existe.
					if (data[cle_json].length > 0)
					{
						var bloc = select_cont($(tab_listes['alimenter'][i]));
						if (typeof(bloc) == 'object')
						{
							bloc.show();
						}	
					}
				}

				// Je mets à jour la valeur de l'option par défaut de chaque liste déroulante renseignée dans le 
				// tableau tab_listes['modifier_option_par_defaut'].
				for (var i = 0; i < tab_listes['modifier_option_par_defaut'].length; i ++)
				{
					$(tab_listes['modifier_option_par_defaut'][i] + ' > option').each(function()
					{
						if ($(this).val() == 'D' || $(this).val() == 'DBP')
						{
							if (select_cont($(tab_listes['modifier_option_par_defaut'][i])).is(':visible'))
							{
								$(this).val('D');
							}
							else
							{
								$(this).val('DBP');
							}
						}
					});
				}
			},
			error : function(xhr, ajaxOptions, thrownError)
			{
				var erreur = xhr.status + ' ' + thrownError;
				erreur += '\n';
				erreur += CONTACT_ADMIN;
				
				alert(erreur);
			},
			complete : function()
			{
				// J'informe l'utilisateur que la requête AJAX est terminée.
				aff_loader_ajax(false);
			}
		});
	}
	else
	{
		// Je désaffiche une liste de listes déroulantes.
		desaff_liste(tab_listes['effacer']);
	}
}

/**
 * Cette procédure permet de gérer une liste de cases à cocher.
 * e : Variable objet JavaScript
 * p_controle : Contrôle permettant de reconnaître la liste de cases à cocher
 */
function ger_coch_cbsm(e, p_controle)
{
	// Je stocke l'objet lié à la case cochée.
	var obj = e.target;

	// Je stocke la valeur de la case cochée.
	var cb_changee = $(obj).attr('value');

	if (isNaN(cb_changee) == true)
	{
		// Je coche toutes les cases à cocher si et seulement si je coche l'option "Tous/Toutes", sinon je les décoche
		// toutes si et seulement si je décoche l'option "Tous/Toutes".
		if ($(obj).is(':checked'))
		{
			p_controle.each(function()
			{
				this.checked = true;
			});
		}
		else
		{
			p_controle.each(function()
			{
				this.checked = false;
			});
		}
	}
	else
	{
		// Je décoche l'option "Tous/Toutes" si je coche ou décoche une case différente de l'option "Tous/Toutes".
		p_controle.each(function()
		{
			if (isNaN($(this).val()) == true)
			{
				this.checked = false;
			}
		});
	}
}

/**
 * Cette fonction retourne une datatable.
 * p_tab_html : Tableau HTML qui servira de datatable
 * p_tab_indices : Tableau d'indices de colonne auquel on interdira le tri sur celles-ci
 * p_extension : Dois-je ajouter l'extension qui permet de découper le tableau sur plusieurs tranches ?
 * Retourne une datatable
 */
function init_datatable(p_tab_html, p_tab_indices, p_extension = false)
{
	var datatable = p_tab_html.DataTable(
	{
		'order' : [],
		'paging' : p_extension,
		'info' : p_extension,
		'searching' : false,
		'aoColumnDefs' : [{
			'bSortable' : false,
			'aTargets' : p_tab_indices
		}]
	});

	return datatable;
}

/**
 * Cette procédure permet de retirer le style d'erreur aux contrôles soumis à une erreur.
 * p_form : Formulaire dont on doit retirer le style d'erreur aux contrôles soumis à une erreur.
 */
function ret_errs(p_form)
{
	p_form.find('.invalide').each(function()
	{
		$(this).removeClass('invalide');
	});
}

/**
 * Cette fonction retourne un préfixe via le nom d'un contrôle.
 * e : Variable objet JavaScript
 * Retourne un préfixe
 */
function ret_pref(e)
{
	// J'obtiens le nom du contrôle.
	var nom_controle = e.target.getAttribute('name');

	// J'effectue un découpage du nom du contrôle afin de récupérer le préfixe de celui-ci s'il existe.
	var split = nom_controle.split('-');

	// J'initialise la valeur du préfixe.
	var prefixe = '';
	if (split.length > 1)
	{
		prefixe = split[0] + '-';
	}

	return prefixe;
}

/**
 * Cette fonction retourne l'élément <div /> qui possède la classe field-wrapper, et lié à un contrôle spécifique.
 * p_contrôle : Contrôle dont on doit chercher l'élément <div /> qui possède la classe field-wrapper
 * Retourne un objet du DOM
 */
function select_cont(p_controle)
{
	// J'initialise la réponse de la fonction.
	var reponse;

	// Je récupère tous les parents du contrôle placé en paramètre.
	var tab_parents = p_controle.parents();
					
	for (var i = 0; i < tab_parents.length; i ++)
	{
		if ($(tab_parents[i]).hasClass('field-wrapper'))
		{
			// Je mets à jour la valeur de la variable réponse si le parent du contrôle placé en paramètre à l'indice i
			// possède la classe field-wrapper (classe située au sommet du champ).
			reponse = $(tab_parents[i]);
		}
	}

	return reponse;
}

/**
 * Cette fonction imite la méthode serializeArray() sauf qu'elle retire le préfixe de chacun des éléments du tableau 
 * "POST".
 * p_form : Formulaire "POST"
 */
function serial_array(p_form)
{
	// J'utilise la méthode serializeArray().
	var tab_post = p_form.serializeArray();

	// Je déclare et j'empile le tableau des cases à cocher cochées.
	var tab_cb_cochees = new Array();
	p_form.each(function()
	{
		// J'initialise le tableau des champs du formulaire.
		var tab_form = $(this)[0];

		for (var i = 0; i < tab_form.length; i ++)
		{
			if (tab_form[i].type == 'checkbox')
			{
				// Je stocke la valeur de certaines propriétés de la case à cocher courante.
				var id = tab_form[i].id;
				var nom = tab_form[i].name;
				var valeur = tab_form[i].value;

				if ($('#' + id).is(':checked') == true)
				{
					if (tab_cb_cochees[nom] == undefined)
					{
						tab_cb_cochees[nom] = valeur;
					}
					else
					{
						// Je déclare un tableau qui permet de stocker temporairement plusieurs valeurs en cas que 
						// plusieurs éléments possèdent la même clé.
						var temp = new Array();

						// J'empile le tableau des valeurs déjà existantes pour une même clé.
						for (var j = 0; j < tab_cb_cochees[nom].length; j ++)
						{
							temp.push(tab_cb_cochees[nom][j]);
						}

						// Je rajoute la dernière valeur pour la clé déjà existante.
						temp.push(valeur);

						tab_cb_cochees[nom] = temp;
					}
				}
			}
		}
	});

	// Je fusionne le tableau des cases à cocher avec celui où sont stockées les données "POST".
	tab_post = tab_post.concat(tab_cb_cochees);

	for (var i = 0; i < tab_post.length; i ++)
	{
		var cle = tab_post[i]['name'];
		var split = cle.split('-');
		var nouvelle_cle = split[split.length - 1];

		// Je renomme la clé sans le préfixe.
		if (nouvelle_cle != cle)
		{
			tab_post[i].name = nouvelle_cle;
		}
	}

	return tab_post;
}

/**
 * Cette procédure permet d'afficher un message dans une fenêtre modale après la suppression d'un élément dans la base
 * de données.
 * e : Variable objet JavaScript
 */
function suppr(e)
{
	// Je bloque le comportement par défaut du bouton.
	e.preventDefault();

	// Je peux désormais manipuler l'objet.
	var obj = e.target;

	// Je récupère le suffixe de la fenêtre modale.
	var obj_za = $(obj).parent().parent().parent().attr('id');
	var split = obj_za.split('_');
	var suffixe = split.slice(1).join('_');

	// Je lance une requête AJAX.
	$.ajax(
	{
		type : 'post',
		url : $(obj).attr('href'),
		dataType : 'json',
		beforeSend : function()
		{
			// J'informe l'utilisateur qu'une requête AJAX se prépare.
			aff_loader_ajax(true);
		},
		success : function(data)
		{
			if (data['success'])
			{
				// J'affiche le message de succès dans une fenêtre modale.
				$('#za_' + suffixe).html('<p class="text-center c-attention b">' + data['success'] + '</p>');

				// J'affiche la fenêtre modale (en retirant la croix de fermeture de celle-ci).
				$('#bt_fm_' + suffixe).remove();
				$('#fm_' + suffixe).modal();

				setTimeout(function()
				{
					// Je suis redirigé.
					window.location.href = data['redirect'];	
				},
				2000);
			}
		},
		error : function(xhr, ajaxOptions, thrownError)
		{
			var erreur = xhr.status + ' ' + thrownError;
			erreur += '\n';
			erreur += CONTACT_ADMIN;
			
			alert(erreur);
		},
		complete : function()
		{
			// J'informe l'utilisateur que la requête AJAX est terminée.
			aff_loader_ajax(false);
		}
	});
}

/**
 * Cette procédure permet de traiter un formulaire de saisie.
 * e : Variable objet JavaScript
 * p_prefixe : Préfixe des différents contrôles du formulaire (utilisé car un contrôle peut être dupliqué sur une même
 * page d'où la nécessité d'un préfixe pour différencier les contrôles)
 */
function trait_form(e, p_prefixe = '')
{
	// Je récupère le nom du formulaire.
	var nom_form = e.target.getAttribute('name');

	// Je stocke dans une variable l'objet "formulaire".
	var obj_form = $('form[name="' + nom_form + '"]');

	// Je récupère le suffixe lié au formulaire (utile pour manipuler les contrôles liés au formulaire).
	var suffixe = nom_form.substring(5);

	// Je lance une requête AJAX.
	$.ajax(
	{
		type : 'post',
		url : obj_form.attr('action'),
		data : serial_array(obj_form),
		dataType : 'json',
		beforeSend : function()
		{
			// J'informe l'utilisateur qu'une requête AJAX se prépare.
			aff_loader_ajax(true);

			// Je grise le bouton de soumission du formulaire.
			obj_form.find('button[type="submit"]').attr('disabled', true);
		},
		success : function(data)
		{
			// Je vide tous les messages d'erreurs lié au formulaire soumis.
			obj_form.find('.za_erreur').empty();

			// Je retire la mise en forme des erreurs.
			ret_errs(obj_form);

			if (data['success'])
			{
				// J'affiche le message de succès dans une fenêtre modale.
				$('#za_' + suffixe).html('<p class="text-center c-attention b">' + data['success'] + '</p>');

				// J'affiche la fenêtre modale (en retirant la croix de fermeture de celle-ci).
				$('#bt_fm_' + suffixe).remove();
				$('#fm_' + suffixe).modal();

				setTimeout(function()
				{
					// Je suis redirigé.
					window.location.href = data['redirect'];	
				},
				2000);
			}
			else
			{
				// Je parcours chaque contrôle soumis à une erreur.
				for (var i in data)
				{
					// Je pointe vers la zone d'erreur relative au contrôle à l'indice i.
					var span = select_cont($('#id_' + p_prefixe + i)).find('.za_erreur');

					// Je prépare l'erreur.
					var ul = $('<ul/>', { 'class' : 'errorlist c-attention' });
					var li = $('<li/>', { html : data[i][0] });

					// J'affiche l'erreur.
					span.append(ul);
					ul.append(li);

					// Je mets en forme le contrôle à l'indice i.
					ajout_err($('#id_' + p_prefixe + i));
				}
			}
		},
		error : function(xhr, ajaxOptions, thrownError)
		{
			var erreur = xhr.status + ' ' + thrownError;
			erreur += '\n';
			erreur += CONTACT_ADMIN;
			
			alert(erreur);
		},
		complete : function()
		{
			// Je dégrise le bouton de soumission du formulaire.
			obj_form.find('button[type="submit"]').removeAttr('disabled');

			// J'informe l'utilisateur que la requête AJAX est terminée.
			aff_loader_ajax(false);
		}
	});
}