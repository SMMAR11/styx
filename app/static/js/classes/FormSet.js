class FormSet {

	// Constructeur

	constructor(event) {
		this.event = event;
		this.wrapper = undefined;
	}

	// Méthodes "privées"

	__add_form() {

		// Insertion d'un formulaire au formulaire groupé

		// Récupération du champ formulaire groupé
		var wrap = $(this.event.target.closest('.field-wrapper'));

		// Récupération de l'identifiant
		var id = wrap.attr('id');

		// Initialisation des balises HTML <td/> composant la future
		// balise HTML <tr/>
		var tds = [];

		// Pour chaque balise <td/> composant la balise HTML <tr/> du
		// formulaire vierge, empilement des balises HTML <td/>
		// composant la future balise HTML <tr/>
		$('#' + id + '_empty_form tr td').each(function(ndx) {
			tds.push($(this).html());
		});

		// Intégration de la future balise HTML <tr/> dans le tableau
		// (formulaire groupé)
		var datatable = new MyDataTable(id.substr(3)).get_datatable();
		datatable.row.add(tds).draw(true);

		// Réindexage du formulaire groupé
		this.wrapper = wrap;
		this.__reindex();

		return true;

	}

	__reindex() {

		// Réindexage du formulaire groupé

		// Récupération du contrôle nombre de formulaires
		var total_formsInput = this.wrapper.find('input[name$=TOTAL_FORMS]');

		// Récupération du nombre de formulaires composant le
		// formulaire groupé
		var total_formsVal = total_formsInput.val();

		// Initialisation du sommet
		var ndx = -1;

		// Pour chaque balise <tr/> composant la balise <tbody/>, elle-
		// même composant la balise <table/>...
		this.wrapper.find('table tbody tr:not(.dataTables_empty)')
			.each(function() {

			// Incrémentation du sommet
			ndx += 1;

			// Pour chaque champ du formulaire...
			$(this)
				.find('.field-wrapper')
				.each(function() {
				
				// Remplacement de la chaîne de caractères "__prefix__"
				// par le sommet (en deux étapes)
				var name = $(this)
					.attr('id')
					.replace(/__prefix__/g, total_formsVal)
					.substr(3);
				name = name.replace(/\d+/g, ndx);

				// Mise à jour de la valeur de l'attribut "id" du
				// conteneur
				$(this).attr('id', 'fw_' + name);

				// Mise à jour de la valeur des attributs "id" et
				// "name" du champ
				var child = $(this).find('.field-control').children();
				child.first().attr({'id': 'id_' + name, 'name': name});

			});

		});

		// Définition du nombre de formulaires composant le formulaire
		// groupé
		total_formsInput.val(parseInt(ndx + 1));

		return true;

	}

	__remove_form() {

		// Suppression d'un formulaire du formulaire groupé

		// Récupération du champ formulaire groupé
		var wrap = $(this.event.target.closest('.field-wrapper'));

		// Récupération de la balise HTML <tr/> (c.-à-d. le formulaire)
		var tr = $(this.event.target.closest('tr'));

		// Suppression de la balise HTML <tr/> (c.-à-d. le formulaire)
		// du tableau (c.-à-d. le formulaire groupé)
		var datatable = new MyDataTable(wrap.attr('id').substr(3)).get_datatable();
		datatable.row(tr).remove().draw(true);

		// Réindexage du formulaire groupé
		this.wrapper = wrap;
		this.__reindex();

		return true;

	}

	// Méthodes "publiques"

	add_form() {
		// Insertion d'un formulaire au formulaire groupé
		return this.__add_form();
	}

	remove_form() {
		// Suppression d'un formulaire du formulaire groupé
		return this.__remove_form();
	}

}