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

    if (forbidden == false) {
        // J'ajoute la barre d'édition.
        map.addControl(drawControl);
    }

    // Je sauve la géométrie dans le layer lors de l'événement "CREATED" du dessin.
    map.on(L.Draw.Event.CREATED, function(e) {
        var type = e.layerType;
        var layer = e.layer;
        editableLayers.addLayer(layer);
    });

    if (forbidden == false) {
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

        }).addTo(map);
    }
}, false);

$(function() {
    $('body').on('shown.bs.tab', 'a[href="#ong_carto"]', function() {

        // Je calcule la hauteur de la carte.
        $('#styx-map').css('min-height', 'calc(100vh - 382px)');
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