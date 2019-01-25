class MyDataTable {

	// Constructeur
	constructor(name) {
		this.id = '#t_' + name;
		this.name = name;
		this.obj = $('#t_' + name + ' table');
	}

	// Getters
	
	get get_id() {
		return this.id;
	}

	get get_name() {
		return this.name;
	}

	get get_obj() {
		return this.obj;
	}

	// Méthodes

	// Création d'un blob
	create_blob(content, apptype, extension = '') {

		// Ajout de zéros non-significatifs
		function pad(number, size = 2) {
			var str = number.toString();
			while (str.length < size) {
				str = '0' + str;
			}
			return str
		}

		// Instanciation d'un objet Blob
		var file = new Blob(['\ufeff', content], { type : apptype });

		// Instanciation d'un objet Date
		var now = new Date();

		// Retrait des blobs existants
		$('.my-blob').remove();

		// Ajout d'un blob dans le DOM
		var a = $('<a/>', {
			'class' : 'my-blob',
			'download' : [
				this.get_id.substring(1) + '_',
				pad(now.getDate()),
				pad(now.getMonth() + 1),
				pad(now.getFullYear(), 4).substring(2),
				pad(now.getHours()),
				pad(now.getMinutes()),
				pad(now.getSeconds()),
				extension
			].join(''),
			'href' : URL.createObjectURL(file)
		});
		a.appendTo('body');

		// Clic automatisé sur le blob ajouté
		a.get(0).click();

	}

	// Export vers un document au format CSV
	csv(delim) {

		// Obtention du texte d'une cellule
		function get_text(td) {
			return '"' + $.trim(td.text()).replace(/(\n)/gm, ' ').replace(/(\t)/gm, '') + '"';
		}

		// Stockage de la table
		var table = this.get_html_table(false);

		// Définition des délimiteurs
		var cdel = delim;
		var rdel = '\r\n';

		// Initialisation des lignes
		var rows = [];

		// Balise <thead/>

		$(table).find('tr:has(th)').each(function() {

			// Initialisation des colonnes
			var cols = [];

			$(table).find('th').each(function() {

				// Empilement des colonnes
				cols.push(get_text($(this)));

			});

			// Empilement des lignes
			rows.push(cols.join(cdel));

		});

		// Balise <tbody/>

		$(table).find('tr:has(td)').each(function() {

			// Initialisation des colonnes
			var cols = [];

			$(this).find('td').each(function() {

				// Empilement des colonnes
				cols.push(get_text($(this)));

			});

			// Empilement des lignes
			rows.push(cols.join(cdel));

		});

		// Mise en forme de la chaîne CSV
		var csv = rows.join(rdel);

		// Création d'un blob
		this.create_blob(csv, 'text/csv;charset=utf8', '.csv');

	}

	// Export vers un document Excel
	excel() {
		this.create_blob(this.get_html_table(), 'application/vnd.ms-excel');
	}

	// Obtention d'une datatable
	get_datatable() {
		return this.get_obj.DataTable();
	}

	// Obtention d'une table HTML sans mise en forme supplémentaire
	get_html_table(include_tfoot = true) {

		var trs = [this.get_obj.find('thead tr'), this.get_obj.find('tbody tr')];
		if (include_tfoot) {
			trs.push(this.get_obj.find('tfoot tr'));
		}

		// Mise en forme d'une table HTML sans mise en forme supplémentaire
		var html = '<table border="1">';
		for (var i in trs) {
			trs[i].each(function() {
				html += '<tr>' + $(this).html() + '</tr>';
			});
		}
		html += '</table>';

		// Retrait d'éléments indésirables
		html = html.replace(/<a[^>]*>|<\/a>/g, '');
		html = html.replace(/<img[^>]*>/gi, '');
		html = html.replace(/<input[^>]*>/gi, '');

		return html;
	}

	// Export vers un nouvel onglet
	html() {

		// Ouverture d'un nouvel onglet
		var wdow = window.open('', '', 'height=600,left=0,menubar=no,resizable=yes,scrollbars=yes,toolbar=0,top=0,width=800');

		// Mise en forme de la chaîne de caractères HTML
		var html = [
			'<!DOCTYPE html>',
			'<html lang="en">',
			'<head>',
			'<meta charset="utf-8">',
			'<meta http-equiv="X-UA-Compatible" content="IE=edge">',
			'<meta name="author" content="SMMAR">',
			'<meta name="rights" content="SMMAR">',
			'<meta name="viewport" content="width=device-width, initial-scale=1">',
			'<style>',
			'table { border: 1px solid; border-collapse: collapse; width: 100%; }',
			'</style>',
			'</head>',
			'<body>',
			this.get_html_table(),
			'</body>',
			'</html>'
		].join('');

		// Intégration de la chaîne de caractères HTML
		wdow.document.write(html);

		// Possibilité d'impression
		wdow.print();
		
	}

	// Définition d'une datatable
	set_datatable(kwargs = {}) {

		// Initialisation des arguments sous forme de dictionnaire
		var k = { 'autofit' : [], 'exports' : true, 'paging' : false, 'unbordered' : [], 'unsorting' : [] };
		$.extend(k, kwargs);

		// Calcul du nombre de colonnes
		var nbr = 0;
		this.get_obj.find('tr:first-child th').each(function() {
			var cspan = $(this).attr('colspan');
			if (!cspan) {
				cspan = 1;
			}
			nbr += Number(cspan);
		});

		// Initialisation des clés ayant pour valeur un tableau
		var keys = ['autofit', 'unbordered', 'unsorting'];

		// Réassignation des arguments si besoin pour chaque clé du dictionnaire "k"
		keys.forEach(function(i) {

			// Initialisation des indices
			var ndxs = [];
			for (var j in k[i]) {
				if (!Number.isInteger(k[i][j])) {

					// Récupération du couple préfixe/nombre de colonnes à traiter
					var spl = k[i][j].split(':');

					// Empilement des indices en partant du début
					if (spl[0] == 'FIRST') {
						for (var ndx = 0; ndx < nbr; ndx += 1) {
							if (Number(spl[1]) > ndx) {
								ndxs.push(ndx);
							}
						}
					}

					// Empilement des indices en partant de la fin
					if (spl[0] == 'LAST') {
						for (var ndx = 0; ndx < nbr; ndx += 1) {
							if (nbr - Number(spl[1]) <= ndx) {
								ndxs.push(ndx);
							}
						}
					}

				}
				else {
					ndxs.push(k[i][j]);
				}
			}

			// Réassignation des arguments
			k[i] = ndxs;

		});

		// Ajout de la classe CSS "unbordered" sur les balises "<td/>" concernées
		var aoColumns = [];
		for (var ndx = 0; ndx < nbr; ndx += 1) {
			aoColumns.push(($.inArray(ndx, k['unbordered']) > -1 ? { 'sClass' : 'autofit unbordered' } : null));
		}

		// Mise en forme du message d'information
		var info = '<span class="u">Nombre de résultats :</span> _TOTAL_';

		// Définition d'une datatable
		var dtable = this.get_obj.DataTable({
			'aoColumnDefs' : [
				{ 'aTargets' : k['unsorting'], 'bSortable' : false },
				{ className : 'autofit', 'targets' : k['autofit'] },
				{ className : 'unbordered', 'targets' : k['unbordered'] }
			],
			'aoColumns' : aoColumns,
			'autoWidth' : false,
			'dom': 'lfrtip' + (k['exports'] ? '<"toolbar">' : ''),
			'info' : true,
			'language' : {
				'emptyTable' : 'Aucun enregistrement',
				'lengthMenu': 'Afficher _MENU_ enregistrements',
				'paginate' : { 'next' : 'Suivant', 'previous' : 'Précédent' },
				'sInfo' : info,
				'sInfoEmpty' : info
			},
			'lengthMenu' : [[-1, 5, 10, 25, 50], ['---------', 5, 10, 25, 50]],
			'order' : [],
			'paging' : k['paging'],
			'searching' : false
		});
		
		if (k['exports']) {

			// Initialisation des contenus HTML
			var htmls = [
				'<span class="u">Exporter sous :</span>',
				' ',
				'<button class="excel my-btn-sm" onclick="new MyDataTable(\'' + this.get_name + '\').csv(\',\');" type="button">',
				'CSV (délimiteur virgule)',
				'</button>',
				' ',
				'<button class="excel my-btn-sm" onclick="new MyDataTable(\'' + this.get_name + '\').csv(\';\');" type="button">',
				'CSV (délimiteur point-virgule)',
				'</button>',
				' ',
				'<button class="excel my-btn-sm" onclick="new MyDataTable(\'' + this.get_name + '\').excel();" type="button">',
				'Excel',
				'</button>',
				' ',
				'<button class="html my-btn-sm" onclick="new MyDataTable(\'' + this.get_name + '\').html();" type="button">',
				'HTML',
				'</button>'
			];

			// Mise en forme de la chaîne de caractères HTML
			var html = ''
			for (var i in htmls) {
				html += htmls[i];
			}

			// Intégration de la chaîne de caractères HTML
			$(this.get_id + ' .toolbar').html(html);

		}

		return dtable;
	}

}