var bloc_carte;
var carte;

try
{
	var bloc_carte = L.map('map', { attributionControl: false }).setView([0, 0], 15);
	var carte = L.tileLayer('http://korona.geog.uni-heidelberg.de/tiles/roads/x={x}&y={y}&z={z}').addTo(bloc_carte);
}
catch (e)
{
	
}