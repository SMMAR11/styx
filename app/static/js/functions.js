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
				$('#fw_' + t_ld_eff[i].substr(3)).hide();
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
						var div = $('#fw_' + t_ld_alim[i].substr(3));
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

			// Initialisation d'une nouvelle datatable dans la fenêtre
			// modale des détails d'un comité de programmation - CD
			// GEMAPI
			if (_s == 'cons_ddscdg') {
				new MyDataTable('cons_acpfinddscdg').set_datatable(
					{'exports': false}
				);
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
 * Cette procédure permet d'afficher une zone d'information relative à l'un des points d'un graphique.
 * _id : Identifiant de la zone d'information
 * _c : Contenu de la zone d'information
 */
function show_tooltip(_id, _c) {

	// Je récupère l'identifiant de l'objet "graphique".
	var id_graph = _id.split('_tooltip')[0];

	// J'initialise les coordonnées absolues de la zone d'information.
	var offset = $('#' + id_graph).offset();
	var x = offset.left;
	var y = offset.top + 8;

	// Je prépare et j'affiche la zone d'information relative à l'un des points du graphique.
	var div = $('<div/>', { class : 'graph-tooltip', 'id' : _id });
	div.css({ left : x, top : y, width : $('#' + id_graph).width() });
	div.appendTo('body');
	$('<div/>', { html : _c }).appendTo(div);
	div.show();
}

/**
 * Cette procédure permet de traiter un formulaire soumis.
 * _e : Objet DOM
 * _s : Styles post-traitement
 * _t : Tableau de paramètres indépendants du paramètre "_e".
 */
function soum_f(_e, _s = function(){}, _t = []) {

	// Je bloque le comportement par défaut du formulaire.
	_e.preventDefault();

	var est_conf = false;
	if (_t.length > 0) {
		if (_t.length == 2) {
			est_conf = true;
		}
		else {
			throw 'Le tableau n\'est pas conforme.';
		}
	}

	// Je pointe vers l'objet "formulaire".
	var o_f = $(_e.target);
	if (est_conf == true) {
		o_f = _t[0];
	}

	// J'assigne le suffixe lié au formulaire (utile pour manipuler les contrôles liés à celui-ci).
	var suff = o_f.attr('name').substring(2);

	// J'initialise l'URL traitant le formulaire.
	var act = o_f.attr('action');
	if (act == undefined) {
		act = '';
	}
	if (est_conf == true) {
		act += _t[1];
	}

	// Je stocke la valeur de l'attribut "onsubmit".
	var get_onsubmit = o_f.attr('onsubmit');

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

			// Je désactive la possibilité de soumettre le formulaire tant que la requête AJAX n'est pas terminée.
			if (get_onsubmit != undefined) {
				o_f.attr('onsubmit', 'return false;');
			}
		},
		success : function(data) {

			// Je retire toutes les erreurs du formulaire.
			if (!data['bypass'] || data['bypass'] == false) {
				$('#za_fe_' + suff).remove();
				o_f.find('.field-error').empty();
				ret_errs(o_f);
			}

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
					var div = $('<div/>', { 'class' : 'b green-color text-center', html : data['success']['message'] });
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

					var suff_datat = suff;
					if (data['success']['datatable_name']) {
						suff_datat = data['success']['datatable_name'];
					}

					// J'obtiens la table de données.
					var dtable = new MyDataTable(suff_datat).get_datatable();

					// Je vide la datatable.
					dtable.clear().draw();

					for (var i = 0; i < data['success']['datatable'].length; i += 1) {

						// Je stocke l'élément courant.
						var elem = data['success']['datatable'][i];

						// Je prépare les données de l'élément courant.
						var lg = [];
						for (var j = 0; j < elem.length; j += 1) {
							lg.push(elem[j]);
						}

						// J'ajoute une ligne à la datatable.
						dtable.row.add(lg).draw(true);
					}
				}

				// Remplacement de texte
				if (data['success']['replace']) {
					$(data['success']['replace'][0]).text(data['success']['replace'][1]);
				}

				// Surchargement d'éléments
				if (data['success']['elements']) {
					for (var i = 0; i < data['success']['elements'].length; i += 1) {

						// Stockage de l'élément courant
						var elem = data['success']['elements'][i];

						// Renommage de l'élément à supprimer
						var elem_to_remove = $(elem[0]).attr('id') + '__old';
						$(elem[0]).attr('id', elem_to_remove);

						// Insertion du nouvel élément
						$(elem[1]).insertAfter('#' + elem_to_remove);

						// Suppression de l'ancien élément
						$('#' + elem_to_remove).remove();
					}
				}

				// Je traite le cas où je dois effectuer une opération sans rafraîchissement (ajout, mise à jour).
				if (data['success']['message'] && data['success']['display']) {

					// Je cache le contenu de la fenêtre modale.
					$('#fm_' + suff).find('.close').hide();
					$('#za_' + suff).hide();

					// J'insère un nouveau contenu dans la fenêtre modale.
					var div = $('<div/>', { 'class' : 'b green-color text-center', html : data['success']['message'] });
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

				// Je traite le cas où je dois initialiser des tables de données dynamiques.
				if (data['success']['new_datatables']) {
					var dtables = data['success']['new_datatables'];
					for (var ndx in dtables) {
						var dtable = dtables[ndx];
						new MyDataTable(dtable[0]).set_datatable(dtable[1]);
					}
				}

				// J'applique les styles.
				_s();
			}
			else {
				var erreur_glob;
				for (var i in data) {
					if (i.indexOf('__all__') > -1) {

						// Définition du message d'erreur global
						erreur_glob = data[i][0];
					}
					else {

						// Je pointe vers le contrôle soumis à une erreur.
						var span = $('#fw_' + i).find('.field-error');

						// Je prépare le message d'erreur.
						var ul = $('<ul/>');
						var li = $('<li/>', { html : data[i][0] });

						// J'affiche l'erreur.
						span.append(ul);
						ul.append(li);
						aj_err($('#id_' + i));
					}
				}

				// Affichage du message d'erreur global si défini
				if (erreur_glob != undefined) {
					var div = $('<div/>', {
						'class' : 'custom-alert-danger row',
						'id' : 'za_fe_' + suff,
						html : erreur_glob
					});
					o_f.closest('.form-root').prepend(div);
				}
			}
		},
		error : function(xhr) {
			alert('Erreur ' + xhr.status);
		},
		complete : function() {

			// Je réactive la possibilité de soumettre le formulaire.
			if (get_onsubmit != undefined) {
				o_f.attr('onsubmit', get_onsubmit);
			}

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
					var div = $('<div/>', { 'class' : 'b green-color text-center', html : data['success']['message'] });
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
			else {

				// Je vide le contenu de la fenêtre modale.
				$('#za_' + suff).empty();

				// J'insère un nouveau contenu dans la fenêtre modale.
				var div = $('<div/>', { 'class' : 'b red-color text-center', html : data });
				$('#za_' + suff).append(div);

				// J'affiche la fenêtre modale.
				$('#fm_' + suff).modal();
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

/**
 * Cette fonction permet d'afficher un nombre avec des zéros non-siginificatifs.
 * _v : Valeur à convertir
 * _s : Taille souhaitée
 * Retourne une chaîne de caractères
 */
function zfill(_v, _s) {

	// Je convertis la donnée en chaîne de caractères.
	v = String(_v);

	// Je rajoute un zéro non-significatif à gauche tant que la longueur de la nouvelle chaîne de caractères n'est pas
	// égale à la taille souhaitée.
	while (v.length < _s) {
		v = '0' + v;
	}

	return v;
}

/**
 * Cette fonction permet d'afficher uniquement les sous-axes correspondant à l'axe selectionné.
 *
 */
function ShowRelated(id_parent, wrapper_child, id_child, attrs_parent) {

	var val_parent = document.getElementById(id_parent).value,
	wrapper = document.getElementById(wrapper_child);
	if (val_parent == "all") {
		wrapper.setAttribute("class", "hide");
	} else {
		wrapper.setAttribute("class", "show");
		var options = document.getElementById(id_child).children;

		for (var i = 0; i < options.length; i++){
      var val_related = options[i].getAttribute(attrs_parent);
			if (val_related == "all" || val_related == val_parent) {
				options[i].style.display = "block";
			} else {
				options[i].style.display = "none";
			}
		}
	}
}
