#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from app.views import autres, gestion_dossiers, handlers, portail_carto, realisation_etats, session
from django.conf import settings
from django.conf.urls import handler403, handler404, include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', session.index, name = 'index'),
	url(r'^index.html$', session.index, name = 'index'),
	url(r'^deconnecter.html$', session.deconnecter, name = 'deconnecter'),
    url(r'^modules/gestion-compte/consulter-compte/$', session.consulter_compte, name = 'consulter_compte'),
    url(r'^modules/portail-cartographique/$', portail_carto.index, name = 'portail_carto'),
	url(r'^modules/gestion-dossiers/$', gestion_dossiers.index, name = 'gestion_dossiers'),
	url(r'^modules/gestion-dossiers/creer-dossier/$', gestion_dossiers.creer_dossier, name = 'creer_dossier'),
    url(
        r'^modules/gestion-dossiers/modifier-dossier/([0-9]+)/$',
        gestion_dossiers.modifier_dossier,
        name = 'modifier_dossier'
    ),
    url(
        r'^modules/gestion-dossiers/supprimer-dossier/([0-9]+)/$',
        gestion_dossiers.supprimer_dossier,
        name = 'supprimer_dossier'
    ),
    url(r'^modules/gestion-dossiers/choisir-dossier/$', gestion_dossiers.choisir_dossier, name = 'choisir_dossier'),
    url(
        r'^modules/gestion-dossiers/consulter-dossier/([0-9]+)/$',
        gestion_dossiers.consulter_dossier,
        name = 'consulter_dossier'
    ),
    url(
        r'^modules/gestion-dossiers/consulter-cartographie/([0-9]+)/$',
        portail_carto.consulter_carto,
        name = 'consulter_carto'
    ),
    url(
        r'^modules/gestion-dossiers/ajouter-financement/$',
        gestion_dossiers.ajouter_financement,
        name = 'ajouter_financement'
    ),
    url(
        r'^modules/gestion-dossiers/ajouter-prestation/$',
        gestion_dossiers.ajouter_prestation,
        name = 'ajouter_prestation'
    ),
    url(
        r'^modules/gestion-dossiers/consulter-prestation/([0-9]+)/$',
        gestion_dossiers.consulter_prestation,
        name = 'consulter_prestation'
    ),
    url(
        r'^modules/gestion-dossiers/ajouter-facture/$', gestion_dossiers.ajouter_facture, name = 'ajouter_facture'
    ),
    url(
        r'^modules/gestion-dossiers/ajouter-demande-versement/$',
        gestion_dossiers.ajouter_demande_versement,
        name = 'ajouter_demande_versement'
    ),
    url(
        r'^modules/gestion-dossiers/ajouter-arrete/([0-9]+)/([0-9]+)/$',
        gestion_dossiers.ajouter_arrete,
        name = 'ajouter_arrete'
    ),
    url(
        r'^modules/gestion-dossiers/modifier-arrete/([0-9]+)/([0-9]+)/$',
        gestion_dossiers.modifier_arrete,
        name = 'modifier_arrete'
    ),
     url(
        r'^modules/gestion-dossiers/supprimer-arrete/$',
        gestion_dossiers.supprimer_arrete,
        name = 'supprimer_arrete'
    ),
    url(r'^modules/gestion-dossiers/ajouter-photo/$', gestion_dossiers.ajouter_photo, name = 'ajouter_photo'),
    url(
        r'^modules/gestion-dossiers/modifier-photo/([0-9]+)/$',
        gestion_dossiers.modifier_photo,
        name = 'modifier_photo'
    ),
    url(r'^modules/gestion-dossiers/supprimer-photo/$', gestion_dossiers.supprimer_photo, name = 'supprimer_photo'),
    
    url(r'^modules/realisation-etats/$', realisation_etats.index, name = 'realisation_etats'),
    url(
        r'^modules/realisation-etats/selectionner-dossiers/$',
        realisation_etats.selectionner_dossiers,
        name = 'selectionner_dossiers'
    ),
    url(
        r'^modules/realisation-etats/selectionner-dossiers/exporter-csv-non-complet/$',
        realisation_etats.exporter_csv_selectionner_dossiers, { 'p_complet' : False },
        name = 'exporter_csv_selectionner_dossiers_non_complet'
    ),
    url(
        r'^modules/realisation-etats/selectionner-dossiers/exporter-csv-complet/$',
        realisation_etats.exporter_csv_selectionner_dossiers, { 'p_complet' : True },
        name = 'exporter_csv_selectionner_dossiers_complet'
    ),
    url(r'^retourner-onglet-actif.html$', autres.retourner_onglet_actif, name = 'retourner_onglet_actif'),
    url(r'^autocompleter.html$', autres.autocompleter, name = 'autocompleter')
]

# Je modifie les templates relatifs aux codes HTTP.
handler403 = handlers.handler_403
handler404 = handlers.handler_404

if settings.DEBUG is True :
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)