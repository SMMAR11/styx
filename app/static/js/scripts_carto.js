var map;
var editableLayers = new L.FeatureGroup();

var options = {
    position: 'topleft',
    draw: {
        polyline: {
            shapeOptions: {
                color: '#cf532d',
                weight: 5
            }
        },
        polygon: {
            shapeOptions: {
                color: '#2d58cf'
            }
        },
        circle: false, // Turns off this drawing tool
        rectangle: false//, // Turns off this drawing tool
    },
    edit: {
        featureGroup: editableLayers, //REQUIRED!!
        remove: true
    }
};

var drawControl = new L.Control.Draw(options);

window.addEventListener("map:init", function (e) {
    var detail = e.detail;
    map = detail.map;

    // Ajout du layer des géométries
    map.addLayer(editableLayers);

    // Ajout de la barre d'édition
    map.addControl(drawControl);

    // A l'évènement created du dessin, on sauve dans le layer
    map.on(L.Draw.Event.CREATED, function (e) {
        var type = e.layerType,
            layer = e.layer;

        editableLayers.addLayer(layer);
    });

    // Bouton de sauvegarde de la géométrie
    L.easyButton('fa-floppy-o', function (){
        // Extraction GeoJson du featureGroup
        var data = editableLayers.toGeoJSON().features;
        var p = [];
        for(var i=0; i<data.length ; i++){
            feat = data[i];
            p.push(JSON.stringify(feat.geometry));
        }

        // Maj du champ caché avec le GeoJson
        $('#edit-geom').val(p.join(';'));

        // Submit du form
        //$('#form_modifier_dossier_geom').submit();
        $('#btn-geom-submit').click();

    }).addTo(map);

}, false);


$(function() {

    $("body").on("shown.bs.tab", "#tabCarto", function() {
        // Calcul dynamique de la hauteur de la carto
        var _heightHeader = $('#header').height() + $('#navbar').height() + 130 + $('#menu_dossier').height();
        var _heightFooter = $('#pre-footer').height() + $('#footer').height();
        $("#styxmap").height($(window).height() - _heightHeader - _heightFooter);
        map.invalidateSize();

        // Les boutons des geoms non autorisées sont masqués
        if( $('#typegeom_doss').val().indexOf('marker') == -1)
            $(".leaflet-draw-draw-marker").css("display","none");

        if( $('#typegeom_doss').val().indexOf('polyline') == -1)
            $(".leaflet-draw-draw-polyline").css("display","none");

        if( $('#typegeom_doss').val().indexOf('polygon') == -1)
            $(".leaflet-draw-draw-polygon").css("display","none");
        
    });

});
