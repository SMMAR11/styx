/**
 * Cette procédure permet de gérer l'affichage d'un loader pendant une requête AJAX.
 * _a : Dois-je afficher ou non le loader ?
 */
function aff_load_ajax(_a)
{
	if (_a == true) {

		// J'initialise le contenu du loader.
		var o_ajax_loader = $('<div/>', { 'class' : 'text-center', 'id' : 'ajax-loader' });
		var t_ajax_loader = [
			$('<span/>', { 'class' : 'glyphicon glyphicon-refresh spin' }),
			$('<br/>'),
			'Veuillez patienter...'
		];

		// Je prépare le contenu du loader.
		for (var i = 0; i < t_ajax_loader.length; i += 1) {
			o_ajax_loader.append(t_ajax_loader[i]);
		}

		// J'affiche le loader.
		o_ajax_loader.insertAfter('.container-fluid');
	}
	else {

		// Je supprime le loader.
		$('#ajax-loader').remove();
	}
}

/**
 * Cette fonction affiche une ou plusieurs listes déroulantes dépendantes d'une autre liste déroulante.
 * _e : Objet DOM
 * _t : Tableau de listes global
 * _f : Formulaire à soumettre
 * Retourne un booléen qui déterminera si je dois soumettre le formulaire ou non par la suite
 */
function alim_ld(_e, _t, _f = undefined) {

	/**
	 * Cette procédure cache les listes déroulantes inutiles.
	 * _t : Tableau de listes global
	 */
	function desalim_ld(_t) {

		// J'initialise le tableau des listes déroulantes à effacer (listes déroulantes à partir du niveau
		// supérieur).
		t_ld_eff = [];
		for (var i = c_o + 1; i < _t.length; i += 1) {
			if ($.isArray(_t[i])) {
				for (var j = 0; j < _t[i].length; j += 1) {
					t_ld_eff.push(_t[i][j]);
				}
			}
			else {
				t_ld_eff.push(_t[i]);
			}
		}

		for (var i = 0; i < t_ld_eff.length; i += 1) {

			// Je remets à zéro la liste déroulante.
			$('#' + t_ld_eff[i] + ' > option').each(function() {
				if ($(this).val() != '') {
					$(this).remove();
				}
			});

			// Je cache la liste déroulante.
			if ($('#' + t_ld_eff[i]).hasClass('hide-field')) {
				point_fw($('#' + t_ld_eff[i])).hide();
			}
		}
	}

	if (_t.length != 4) {
		throw 'Le tableau n\'est pas conforme.';
	}

	// Je prépare la valeur de sortie.
	var submit = true;
	if (_f == undefined) {
		submit = false;
	}

	// Je stocke les identifiants de chaque liste déroulante concernée par niveau.
	var t_ld = [_t[0], _t[1], _t[2], _t[3]];

	// Je pointe vers l'objet DOM affecté par l'événement "onchange".
	var o = $(_e.target);

	// Je récupère la clé du tableau "t_ld[]".
	var c_o;
	$.each(t_ld, function(_c, _v) {
		if ($.isArray(_v)) {
			for (var i = 0; i < _v.length; i += 1) {
				if (o.attr('id') == _v[i]) {
					c_o = _c
				}
			}
		}
		else {
			if (o.attr('id') == _v) {
				c_o = _c
			}
		}
	});

	if (o.val() != '') {
		$.ajax({
			type : 'post',
			url : '?action=alimenter-listes',
			data : {
				csrfmiddlewaretoken : $('input[name="csrfmiddlewaretoken"]').val(),
				id_progr : $('#' + _t[0]).val(),
				num_axe : $('#' + _t[1][0]).val(),
				num_ss_axe : $('#' + _t[2]).val()
			},
			dataType : 'json',
			beforeSend : function() {
				aff_load_ajax(true);
			},
			success : function(data) {
				desalim_ld(t_ld);
				
				// J'initialise le tableau des listes déroulantes à alimenter (listes déroulantes du niveau supérieur).
				var c_sup = c_o + 1;
				var v_sup = t_ld[c_sup];
				if ($.isArray(v_sup)) {
					t_ld_alim = v_sup;
				}
				else {
					t_ld_alim = [v_sup];
				}

				for (var i = 0; i < t_ld_alim.length; i += 1) {

					// Je récupère la clé de la liste déroulante à alimenter.
					var split = t_ld_alim[i].split('_');
					var c_ld_alim = split.slice(2, split.length).join('_');

					var t_donn = data[c_ld_alim];

					// J'alimente la liste déroulante.
					for (var j = 0; j < t_donn.length; j += 1) {
						var opt = $('<option/>', { 'value' : t_donn[j][0], html : t_donn[j][1]});
						$('#' + t_ld_alim[i]).append(opt);
					}

					// J'essaie d'afficher la liste déroulante si elle admet des choix.
					if (t_donn.length > 0) {
						var div = point_fw($('#' + t_ld_alim[i]));
						if ($.type(div) == 'object') {
							div.show();
						}	
					}
				}
			},
			error : function(xhr) {
				alert('Erreur ' + xhr.status);
			},
			complete : function() {
				aff_load_ajax(false);
			}
		}).done(function() {
			if (submit == true) {
				_f.submit();
			}
		});
	}
	else {
		desalim_ld(t_ld);
		if (submit == true) {
			_f.submit();
		}
	}

	return submit;
}

/**
 * Cette procédure permet à l'utilisateur de visualiser les contrôles soumis à une erreur.
 * _c : Contrôle soumis à une erreur
 */
function aj_err(_c) {
	_c.addClass('invalid-field');
}

/**
 * Cette procédure permet d'afficher du code HTML dans une fenêtre modale.
 * _e : Objet DOM
 * _s :  Suffixe de la fenêtre modale.
 */
function html_ds_fm(_e, _s)
{
	// Je pointe vers l'objet.
	var o = _e.target;

	// Je lance une requête AJAX.
	$.ajax({
		type : 'post',
		url : $(o).attr('action'),
		dataType : 'html',
		beforeSend : function() {
			aff_load_ajax(true);
		},
		success : function(data)
		{
			// J'insère un nouveau contenu dans la fenêtre modale.
			$('#za_' + _s).html(data);

			// J'affiche la fenêtre modale.
			$('#fm_' + _s).modal();
		},
		error : function(xhr) {
			alert('Erreur ' + xhr.status);
		},
		complete : function() {
			aff_load_ajax(false);
		}
	});
}

/**
 * Cette fonction permet l'initialisation d'une datatable.
 * _d : Datatable à initialiser
 * _t : Tableau de colonnes dont on ne veut pas trier
 * Retourne un objet "datatable"
 */
function init_datat(_d, _t) {
	return _d.find('table').DataTable({
		'aoColumnDefs' : [{
			'aTargets' : _t,
			'bSortable' : false
		}],
		'autoWidth' : false,
		'info' : false,
		'language' : {
			'emptyTable' : 'Aucun enregistrement'
		},
		'order' : [],
		'paging' : false,
		'searching' : false
	});
}

/**
 * Cette fonction permet de pointer vers le bloc "origine" d'un contrôle.
 * _c : Contrôle dont l'origine doit être trouvée
 * Retourne un objet
 */
function point_fw(_c) {

	var output;

	// Je cherche à trouver l'origine du conteneur (élément <div/> avec la classe "field-wrapper") parmi tous les
	// parents du champ.
	var t_par = _c.parents();
	for (var i = 0; i < t_par.length; i += 1) {
		o = $(t_par[i]);
		if (o.hasClass('field-wrapper')) {
			output = o;
		}
	}

	// Je renvoie une erreur si la variable de retour n'est pas définie.
	if (output == undefined) {
		throw 'Le champ est inclus dans aucun conteneur.'
	}

	return output;
}

/**
 * Cette procédure permet de retirer les erreurs d'un formulaire afin de le remettre à zéro.
 * _f : Formulaire dont on doit retirer les erreurs
 */
function ret_errs(_f) {
	_f.find('.invalid-field').each(function() {
		$(this).removeClass('invalid-field');
	});
}

/**
 * Cette procédure permet de traiter un formulaire soumis.
 * _e : Objet DOM
 * _s : Styles post-traitement
 * _u : URL traitant le formulaire
 */
function soum_f(_e, _s = function(){}, _u = null) {

	// Je bloque le comportement par défaut du formulaire.
	_e.preventDefault();

	// Je récupère la valeur de l'attribut "name".
	var get_f_name = $(_e.target).attr('name');

	// Je pointe vers l'objet "formulaire".
	var o_f = $('form[name="' + get_f_name + '"]');

	// J'assigne le suffixe lié au formulaire (utile pour manipuler les contrôles liés à celui-ci).
	var suff = get_f_name.substring(2);

	// J'initialise l'URL traitant le formulaire.
	var act = o_f.attr('action');
	if (_u != null) {
		act += _u;
	}

	// Je lance une requête AJAX.
	$.ajax({
		type : 'post',
		url : act,
		data : new FormData(o_f.get(0)),
		dataType : 'json',
		processData : false,
		contentType : false,
		beforeSend : function() {
			aff_load_ajax(true);
			o_f.find('button[type="submit"]').addClass('to-block');
		},
		success : function(data) {

			// Je retire toutes les erreurs du formulaire.
			o_f.find('.field-error').empty();
			o_f.find('.form-grouped-error').empty();
			ret_errs(o_f);

			if (data['success']) {

				// Je traite le cas où je dois effectuer une opération avec rafraîchissement (ajout, mise à jour).
				if (data['success']['message'] && data['success']['redirect']) {

					var suff_modal = suff;
					if (data['success']['modal']) {
						suff_modal = data['success']['modal'];
					}

					// Je vide le contenu de la fenêtre modale.
					$('#za_' + suff_modal).empty();

					// J'insère un nouveau contenu dans la fenêtre modale.
					var div = $('<div/>', { 'class' : 'b red-color text-center', html : data['success']['message'] });
					$('#za_' + suff_modal).append(div);

					// J'affiche la fenêtre modale.
					$('#fm_' + suff_modal).find('.close').remove();
					$('#fm_' + suff_modal).modal();

					// Je suis redirigé.
					setTimeout(function() {
						window.location.href = data['success']['redirect'];
					}, 2000);
				}

				// Je traite le cas où je dois actualiser une datatable.
				if (data['success']['datatable']) {

					// Je vide la datatable ("t_datat[]" est issue des variables globales de l'application).
					t_datat[suff].clear().draw();

					for (var i = 0; i < data['success']['datatable'].length; i += 1) {

						// Je stocke l'élément courant.
						var elem = data['success']['datatable'][i];

						// Je prépare les données de l'élément courant.
						var lg = [];
						for (var j = 0; j < elem.length; j += 1) {
							lg.push(elem[j]);
						}

						// J'ajoute une ligne à la datatable.
						t_datat[suff].row.add(lg).draw(true);
					}

					// J'applique les styles.
					_s();
				}

				// Je traite le cas où je dois afficher un nouveau formulaire.
				if (data['success']['next']) {

					// Je retire le formulaire de l'étape actuelle.
					$('#za_' + suff + '_next').remove();

					// Je cache le formulaire de l'étape précédente.
					o_f.hide();

					// J'affiche le nouveau formulaire.
					var div = $('<div/>', { 'id' : 'za_' + suff + '_next' });
					$(div).append(data['success']['next']);
					$(div).insertAfter('form[name="' + get_f_name + '"]');

					// J'initialise la nouvelle datatable.
					var datat = init_datat($('#t_' + suff + '_next'), []);
				}

				// Je traite le cas où je dois effectuer une opération sans rafraîchissement (ajout, mise à jour).
				if (data['success']['message'] && data['success']['display']) {

					// Je cache le contenu de la fenêtre modale.
					$('#fm_' + suff).find('.close').hide();
					$('#za_' + suff).hide();

					// J'insère un nouveau contenu dans la fenêtre modale.
					var div = $('<div/>', { 'class' : 'b red-color text-center', html : data['success']['message'] });
					$(div).insertAfter($('#za_' + suff));

					// Je transvase une donnée de l'instance créée vers le formulaire principal si besoin.
					$(data['success']['display'][0]).val(data['success']['display'][1]);

					setTimeout(function() {

						// Je ferme la fenêtre modale.
						$('#fm_' + suff).modal('hide');

						// Je vide le formulaire.
						o_f[0].reset();

						// Je reviens à l'état initial du sous-formulaire.
						div.remove();
						$('#fm_' + suff).find('.close').show();
						$('#za_' + suff).show();
					}, 2000);
				}
			}
			else {
				if (data['errors']) {

					// Je prépare le message d'erreur.
					var ul = $('<ul/>');
					var li = $('<li/>', { html : data['errors'][0] });

					// J'affiche l'erreur.
					o_f.find('.form-grouped-error').append(ul);
					ul.append(li);
				}
				else {
					for (var i in data) {

						// Je pointe vers le contrôle soumis à une erreur.
						var span = point_fw($('#id_' + i)).find('.field-error');

						// Je prépare le message d'erreur.
						var ul = $('<ul/>');
						var li = $('<li/>', { html : data[i][0] });

						// J'affiche l'erreur.
						span.append(ul);
						ul.append(li);
						aj_err($('#id_' + i));

						// Je cache le message d'erreur si et seulement si un message d'erreur porte sur plusieurs champs à
						// la fois (cas exceptionnel).
						if (data[i][0] == 'None') {
							li.css('visibility', 'hidden');
						}
					}
				}
			}
		},
		error : function(xhr) {
			alert('Erreur ' + xhr.status);
		},
		complete : function() {
			o_f.find('button[type="submit"]').removeClass('to-block');
			aff_load_ajax(false);
		}
	});
}

/**
 * Cette procédure permet d'afficher un message après la suppression d'un élément.
 * _e : Objet DOM
 */
function suppr(_e)
{
	// Je bloque le comportement par défaut du bouton.
	_e.preventDefault();

	// Je pointe vers l'objet.
	var o = $(_e.target);

	// Je récupère le suffixe de la fenêtre modale.
	var o_za = o.parent().parent().parent().attr('id');
	var split = o_za.split('_');
	var suff = split.slice(1).join('_');

	// Je lance une requête AJAX.
	$.ajax({
		type : 'post',
		url : o.attr('href'),
		dataType : 'json',
		beforeSend : function() {
			aff_load_ajax(true);
		},
		success : function(data) {
			if (data['success']) {
				if (data['success']['message'] && data['success']['redirect']) {

					// Je vide le contenu de la fenêtre modale.
					$('#za_' + suff).empty();

					// J'insère un nouveau contenu dans la fenêtre modale.
					var div = $('<div/>', { 'class' : 'b red-color text-center', html : data['success']['message'] });
					$('#za_' + suff).append(div);

					// J'affiche la fenêtre modale.
					$('#fm_' + suff).find('.close').remove();
					$('#fm_' + suff).modal();

					// Je suis redirigé.
					setTimeout(function() {
						window.location.href = data['success']['redirect'];
					}, 2000);
				}
			}
		},
		error : function(xhr) {
			alert('Erreur ' + xhr.status);
		},
		complete : function() {
			aff_load_ajax(false);
		}
	});
}