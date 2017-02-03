# Imports
from app.views import gestion_dossiers
from app.views import main
from django.conf import settings
from django.conf.urls import handler403
from django.conf.urls import handler404
from django.conf.urls import handler500
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', main.index, name = 'index'),
    url(r'^index.html$', main.index, name = 'index'),
    url(r'^deconnecter.html$', main.deconnect, name = 'deconnect'),
    url(r'^modifier-compte.html$', main.modif_util, name = 'modif_util'),
    url(r'^autocompleter.html$', main.autocompl, name = 'autocompl'),
    url(r'^modules/gestion-dossiers/$', gestion_dossiers.index, name = 'gest_doss'),
    url(r'^modules/gestion-dossiers/creer-dossier/$', gestion_dossiers.cr_doss, name = 'cr_doss'),
    url(r'^modules/gestion-dossiers/modifier-dossier/([0-9]+)/$', gestion_dossiers.modif_doss, name = 'modif_doss'),
    url(r'^modules/gestion-dossiers/supprimer-dossier/([0-9]+)/$', gestion_dossiers.suppr_doss, name = 'suppr_doss'),
    url(r'^modules/gestion-dossiers/choisir-dossier/$', gestion_dossiers.ch_doss, name = 'ch_doss'),
    url(r'^modules/gestion-dossiers/consulter-dossier/([0-9]+)/$', gestion_dossiers.cons_doss, name = 'cons_doss'),
    url(r'^modules/gestion-dossiers/imprimer-dossier/([0-9]+)/$', gestion_dossiers.impr_doss, name = 'impr_doss'),
    url(r'^modules/gestion-dossiers/ajouter-financement/$', gestion_dossiers.ajout_fin, name = 'ajout_fin'),
    url(r'^modules/gestion-dossiers/modifier-financement/([0-9]+)/$', gestion_dossiers.modif_fin, name = 'modif_fin'),
    url(r'^modules/gestion-dossiers/supprimer-financement/([0-9]+)/$', gestion_dossiers.suppr_fin, name = 'suppr_fin'),
    url(r'^modules/gestion-dossiers/consulter-financement/([0-9]+)/$', gestion_dossiers.cons_fin, name = 'cons_fin'),
    url(r'^modules/gestion-dossiers/ajouter-prestation/$', gestion_dossiers.ajout_prest, name = 'ajout_prest'),
    url(
        r'^modules/gestion-dossiers/modifier-prestation/([0-9]+)/$', gestion_dossiers.modif_prest, name = 'modif_prest'
    ),
    url(r'^modules/gestion-dossiers/consulter-prestation/([0-9]+)/$', gestion_dossiers.cons_prest, name = 'cons_prest'),
    url(
        r'^modules/gestion-dossiers/ajouter-avenant/$', 
        gestion_dossiers.ajout_aven, 
        { '_r' : 'cons_prest' }, 
        name = 'ajout_aven'
    ),
    url(
        r'^modules/gestion-dossiers/ajouter-avenant-raccourci/$', 
        gestion_dossiers.ajout_aven, 
        { '_r' : 'cons_doss' }, 
        name = 'ajout_aven_racc'
    ),
    url(r'^modules/gestion-dossiers/modifier-avenant/([0-9]+)/$', gestion_dossiers.modif_aven, name = 'modif_aven'),
    url(r'^modules/gestion-dossiers/consulter-avenant/([0-9]+)/$', gestion_dossiers.cons_aven, name = 'cons_aven'),
    url(r'^modules/gestion-dossiers/ajouter-facture/$', gestion_dossiers.ajout_fact, name = 'ajout_fact'),
    url(r'^modules/gestion-dossiers/modifier-facture/([0-9]+)/$', gestion_dossiers.modif_fact, name = 'modif_fact'),
    url(r'^modules/gestion-dossiers/consulter-facture/([0-9]+)/$', gestion_dossiers.cons_fact, name = 'cons_fact'),
    url(r'^modules/gestion-dossiers/ajouter-demande-de-versement/$', gestion_dossiers.ajout_ddv, name = 'ajout_ddv'),
    url(
        r'^modules/gestion-dossiers/modifier-demande-de-versement/([0-9]+)/$',
        gestion_dossiers.modif_ddv,
        name = 'modif_ddv'
    ),
    url(
        r'^modules/gestion-dossiers/consulter-demande-de-versement/([0-9]+)/$', 
        gestion_dossiers.cons_ddv, 
        name = 'cons_ddv'
    ),
    url(r'^modules/gestion-dossiers/ajouter-arrete/$', gestion_dossiers.ajout_arr, name = 'ajout_arr'),
    url(r'^modules/gestion-dossiers/modifier-arrete/([0-9]+)/$', gestion_dossiers.modif_arr, name = 'modif_arr'),
    url(r'^modules/gestion-dossiers/supprimer-arrete/([0-9]+)/$', gestion_dossiers.suppr_arr, name = 'suppr_arr'),
    url(r'^modules/gestion-dossiers/consulter-arrete/([0-9]+)/$', gestion_dossiers.cons_arr, name = 'cons_arr'),
    url(r'^modules/gestion-dossiers/ajouter-photo/$', gestion_dossiers.ajout_ph, name = 'ajout_ph'),
    url(r'^modules/gestion-dossiers/modifier-photo/([0-9]+)/$', gestion_dossiers.modif_ph, name = 'modif_ph'),
    url(r'^modules/gestion-dossiers/supprimer-photo/([0-9]+)/$', gestion_dossiers.suppr_ph, name = 'suppr_ph'),
    url(r'^modules/gestion-dossiers/ajouter-prestataire/$', gestion_dossiers.ajout_org_prest, name = 'ajout_org_prest')
]

handler403 = main.h_403
handler404 = main.h_404
handler500 = main.h_500

if settings.DEBUG is True :
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)