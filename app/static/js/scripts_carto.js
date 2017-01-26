var map;
var editableLayers = new L.FeatureGroup();
var options = {
    position : 'topleft',
    draw : {
        polyline : {
            shapeOptions : {
                color : '#CF532D',
                weight : 5
            }
        },
        polygon : {
            shapeOptions : {
                color : '#2D58CF'
            }
        },
        circle : false,
        rectangle : false
    },
    edit : {
        featureGroup : editableLayers,
        remove : true
    }
};

if (forbidden == false) {
    var drawControl = new L.Control.Draw(options);
}

window.addEventListener('map:init', function(e) {
    var detail = e.detail;
    map = detail.map;

    // J'ajoute la couche des géométries.
    map.addLayer(editableLayers);

    // J'ajoute la barre d'édition.
    if (forbidden == false) {
        map.addControl(drawControl);
    }

    // Je sauve la géométrie dans le layer lors de l'événement "CREATED" du dessin.
    map.on(L.Draw.Event.CREATED, function(e) {
        var type = e.layerType;
        var layer = e.layer;
        editableLayers.addLayer(layer);
    });

    if (forbidden == false) {

        // J'ajoute le bouton de sauvegarde de la géométrie.
        L.easyButton('fa-floppy-o', function() {

            // J'extrais le GeoJSON du FeatureGroup.
            var data = editableLayers.toGeoJSON().features;
            var p = [];
            for(var i = 0; i < data.length ; i += 1) {
                var feat = data[i];
                p.push(JSON.stringify(feat.geometry));
            }

            // Je mets à jour le champ caché via le GeoJSON.
            $('#edit-geom').val(p.join(';'));

            // Je soumets le formulaire.
            $('form[name="f_modif_carto"]').submit();

        }, 'Mettre à jour la géométrie du dossier').addTo(map);
    }

    // J'ajoute un bouton permettant d'agrandir ou de réduire la hauteur de la carte.
    L.easyButton({
        position : 'topright',
        states : [{
            stateName : 'normal-map',
            icon : 'glyphicon glyphicon-resize-full',
            title : 'Agrandir la carte',
            onClick : function(_c) {
                $('#styx-map').css('min-height', '768px');
                map.invalidateSize();
                _c.state('large-map');
            }
        },{
            stateName : 'large-map',
            icon : 'glyphicon glyphicon-resize-small',
            title : 'Réduire la carte',
            onClick : function(_c) {
                $('#styx-map').css('min-height', '300px');
                map.invalidateSize();
                _c.state('normal-map');
            }
        }]
    }).addTo(map);

}, false);

$(function() {
    $('body').on('shown.bs.tab', 'a[href="#ong_carto"]', function() {

        map.invalidateSize();

        // Je centre la carte sur les objets géométriques.
        if (editableLayers.getBounds().getNorthEast() != undefined) {
            map.fitBounds(editableLayers.getBounds());
        }

        // Je cache les boutons non-autorisés.
        if($('#types_geom_doss').val().indexOf('marker') == -1) {
            $('.leaflet-draw-draw-marker').remove();
        }
        if($('#types_geom_doss').val().indexOf('polyline') == -1) {
            $('.leaflet-draw-draw-polyline').remove();
        }
        if($('#types_geom_doss').val().indexOf('polygon') == -1) {
            $('.leaflet-draw-draw-polygon').remove();
        }
    });
});