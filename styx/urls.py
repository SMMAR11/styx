# Imports
from app.views import gestion_dossiers
from app.views import main
from app.views import pgre
from app.views import realisation_etats
from app.views.avancement_programme import AvancementProgrammeView
from app.views.real_etats.EtatAvancementProgramme import EtatAvancementProgramme
from app.views.real_etats.EtatPpi import EtatPpi
from app.views.real_etats.EtatCDGemapi import EtatCDGemapi
from app.views.real_etats.EtatDossiers import EtatDossiers
from app.views.real_etats.EtatPrestations import EtatPrestations
from app.views.real_etats.EtatSubventions import EtatSubventions
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
    url(r'^consulter-compte.html$', main.cons_util, name = 'cons_util'),
    url(r'^assistance.html$', main.assist, name = 'assist'),
    url(r'^autocompleter.html$', main.autocompl, name = 'autocompl'),
    url(r'^alertes.html$', main.alert, name = 'alert'),
    # Module Gestion des dossiers
    url(r'^modules/gestion-dossiers/$', gestion_dossiers.index, name = 'gest_doss'),
    url(r'^modules/gestion-dossiers/creer-dossier/$', gestion_dossiers.cr_doss, name = 'cr_doss'),
    url(r'^modules/gestion-dossiers/modifier-dossier/([0-9]+)/$', gestion_dossiers.modif_doss, name = 'modif_doss'),
    url(r'^modules/gestion-dossiers/supprimer-dossier/([0-9]+)/$', gestion_dossiers.suppr_doss, name = 'suppr_doss'),
    url(r'^modules/gestion-dossiers/choisir-dossier/$', gestion_dossiers.ch_doss, name = 'ch_doss'),
    url(r'^modules/gestion-dossiers/consulter-dossier/([0-9]+)/$', gestion_dossiers.cons_doss, name = 'cons_doss'),
    url(r'^modules/gestion-dossiers/imprimer-dossier/([0-9]+)/$', gestion_dossiers.impr_doss, name = 'impr_doss'),
    url(
        r'^modules/gestion-dossiers/presenter-dossier-cd-gemapi/([0-9]+)/$',
        gestion_dossiers.ajout_ddscdg,
        name = 'ajout_ddscdg'
    ),
    url(
        r'^modules/gestion-dossiers/de-presenter-dossier-cd-gemapi/([0-9]+)/$',
        gestion_dossiers.suppr_ddscdg,
        name = 'suppr_ddscdg'
    ),
    url(r'^modules/gestion-dossiers/modifier-fiche-de-vie/([0-9]+)/$', gestion_dossiers.modif_fdv, name = 'modif_fdv'),
    url(r'^modules/gestion-dossiers/supprimer-fiche-de-vie/([0-9]+)/$', gestion_dossiers.suppr_fdv, name = 'suppr_fdv'),
    url(r'^modules/gestion-dossiers/ajouter-financement/$', gestion_dossiers.ajout_fin, name = 'ajout_fin'),
    url(r'^modules/gestion-dossiers/modifier-financement/([0-9]+)/$', gestion_dossiers.modif_fin, name = 'modif_fin'),
    url(r'^modules/gestion-dossiers/supprimer-financement/([0-9]+)/$', gestion_dossiers.suppr_fin, name = 'suppr_fin'),
    url(r'^modules/gestion-dossiers/consulter-financement/([0-9]+)/$', gestion_dossiers.cons_fin, name = 'cons_fin'),
    url(r'^modules/gestion-dossiers/ajouter-prestation/$', gestion_dossiers.ajout_prest, name = 'ajout_prest'),
    url(
        r'^modules/gestion-dossiers/modifier-prestation/([0-9]+)/$', gestion_dossiers.modif_prest, name = 'modif_prest'
    ),
    url(r'^modules/gestion-dossiers/supprimer-prestation/([0-9]+)/$', gestion_dossiers.suppr_prest, name = 'suppr_prest'),
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
    url(r'^modules/gestion-dossiers/supprimer-avenant/([0-9]+)/$', gestion_dossiers.suppr_aven, name = 'suppr_aven'),
    url(r'^modules/gestion-dossiers/consulter-avenant/([0-9]+)/$', gestion_dossiers.cons_aven, name = 'cons_aven'),
    url(
        r'^modules/gestion-dossiers/ajouter-ordre-service/([0-9]+)/$',
        gestion_dossiers.ajout_os,
        { 'p_redirect' : 'cons_prest' },
        name = 'ajout_os'
    ),
    url(
        r'^modules/gestion-dossiers/ajouter-ordre-service-raccourci/([0-9]+)/$',
        gestion_dossiers.ajout_os,
        { 'p_redirect' : 'cons_doss' },
        name = 'ajout_os_racc'
    ),
    url(r'^modules/gestion-dossiers/modifier-ordre-service/([0-9]+)/$', gestion_dossiers.modif_os, name = 'modif_os'),
    url(r'^modules/gestion-dossiers/supprimer-ordre-service/([0-9]+)/$', gestion_dossiers.suppr_os, name = 'suppr_os'),
    url(r'^modules/gestion-dossiers/ajouter-facture/$', gestion_dossiers.ajout_fact, name = 'ajout_fact'),
    url(r'^modules/gestion-dossiers/modifier-facture/([0-9]+)/$', gestion_dossiers.modif_fact, name = 'modif_fact'),
    url(r'^modules/gestion-dossiers/supprimer-facture/([0-9]+)/$', gestion_dossiers.suppr_fact, name = 'suppr_fact'),
    url(r'^modules/gestion-dossiers/consulter-facture/([0-9]+)/$', gestion_dossiers.cons_fact, name = 'cons_fact'),
    url(r'^modules/gestion-dossiers/ajouter-demande-de-versement/$', gestion_dossiers.ajout_ddv, name = 'ajout_ddv'),
    url(
        r'^modules/gestion-dossiers/modifier-demande-de-versement/([0-9]+)/$',
        gestion_dossiers.modif_ddv,
        name = 'modif_ddv'
    ),
    url(r'^modules/gestion-dossiers/supprimer-demande-de-versement/([0-9]+)/$', gestion_dossiers.suppr_ddv, name = 'suppr_ddv'),
    url(
        r'^modules/gestion-dossiers/consulter-demande-de-versement/([0-9]+)/$',
        gestion_dossiers.cons_ddv,
        name = 'cons_ddv'
    ),
    url(
        r'^modules/gestion-dossiers/editer-lettre-type-demande-de-versement/([0-9]+)/$',
        gestion_dossiers.edit_lt_ddv,
        name = 'edit_lt_ddv'
    ),
    url(r'^modules/gestion-dossiers/ajouter-arrete/$', gestion_dossiers.ajout_arr, name = 'ajout_arr'),
    url(r'^modules/gestion-dossiers/modifier-arrete/([0-9]+)/$', gestion_dossiers.modif_arr, name = 'modif_arr'),
    url(r'^modules/gestion-dossiers/supprimer-arrete/([0-9]+)/$', gestion_dossiers.suppr_arr, name = 'suppr_arr'),
    url(r'^modules/gestion-dossiers/consulter-arrete/([0-9]+)/$', gestion_dossiers.cons_arr, name = 'cons_arr'),
    url(r'^modules/gestion-dossiers/ajouter-photo/$', gestion_dossiers.ajout_ph, name = 'ajout_ph'),
    url(r'^modules/gestion-dossiers/modifier-photo/([0-9]+)/$', gestion_dossiers.modif_ph, name = 'modif_ph'),
    url(r'^modules/gestion-dossiers/supprimer-photo/([0-9]+)/$', gestion_dossiers.suppr_ph, name = 'suppr_ph'),
    url(r'^modules/gestion-dossiers/ajouter-prestataire/$', gestion_dossiers.ajout_org_prest, name = 'ajout_org_prest'),
    url(
        r'^modules/gestion-dossiers/ajouter-ppi/$',
        gestion_dossiers.manppi,
        name='insppi'
    ),
    url(
        r'^modules/gestion-dossiers/mettre-a-jour-ppi/([0-9]+)/$',
        gestion_dossiers.manppi,
        name='updppi'
    ),
    url(
        r'^modules/gestion-dossiers/consulter-ppi/([0-9]+)/$',
        gestion_dossiers.getppi,
        name='getppi'
    ),

    # Module Réalisation d'états
    url(r'^modules/realisation-etats/$', realisation_etats.index, name = 'real_etats'),
    url(
        r'^modules/realisation-etats/vue-generale-dossiers/$',
        EtatDossiers.as_view(),
        name='EtatDossiers'
    ),
    url(
        r'^modules/realisation-etats/bilan-programme-actions/$',
        EtatAvancementProgramme.as_view(),
        name='EtatAvancementProgramme'
    ),
    url(
        r'^modules/realisation-etats/etat-subventions/$',
        EtatSubventions.as_view(),
        name='EtatSubventions'
    ),
    url(
        r'^modules/realisation-etats/etat-prestations/$',
        EtatPrestations.as_view(),
        name='EtatPrestations'
    ),
    url(
        r'^modules/realisation-etats/decisions-cd-gemapi/$',
        EtatCDGemapi.as_view(),
        name='EtatCDGemapi'
    ),
    url(
        r'^modules/realisation-etats/bilan-ppi/$',
        EtatPpi.as_view(),
        name='EtatPpi'
    ),

    # Module PGRE
    url(r'^modules/pgre/$', pgre.index, name = 'pgre'),
    url(r'^modules/pgre/creer-action-pgre/$', pgre.cr_act_pgre, name = 'cr_act_pgre'),
    url(r'^modules/pgre/modifier-action-pgre/([0-9]+)/$', pgre.modif_act_pgre, name = 'modif_act_pgre'),
    url(r'^modules/pgre/supprimer-action-pgre/([0-9]+)/$', pgre.suppr_act_pgre, name = 'suppr_act_pgre'),

    url(r'^modules/pgre/ajout-sous-action-pgre/$', pgre.ajout_ss_act_pgre, name = 'ajout_ss_act_pgre'),
    url(r'^modules/pgre/modifier-sous-action-pgre/([0-9]+)/$', pgre.modif_ss_act_pgre, name = 'modif_ss_act_pgre'),
    url(r'^modules/pgre/supprimer-ss-action-pgre/([0-9]+)/$', pgre.suppr_ss_act_pgre, name = 'suppr_ss_act_pgre'),

    url(r'^modules/pgre/choisir-action-pgre/$', pgre.ch_act_pgre, name = 'ch_act_pgre'),
    url(r'^modules/pgre/consulter-action-pgre/([0-9]+)/$', pgre.cons_act_pgre, name = 'cons_act_pgre'),
    url(r'^modules/pgre/ajouter-photo/$', pgre.ajout_ph_pgre, name = 'ajout_ph_pgre'),
    url(r'^modules/pgre/modifier-photo/([0-9]+)/$', pgre.modif_ph_pgre, name = 'modif_ph_pgre'),
    url(r'^modules/pgre/supprimer-photo/([0-9]+)/$', pgre.suppr_ph_pgre, name = 'suppr_ph_pgre'),
    url(r'^modules/pgre/modifier-point-de-controle/([0-9]+)/$', pgre.modif_pdc, name = 'modif_pdc'),
    url(r'^modules/pgre/supprimer-point-de-controle/([0-9]+)/$', pgre.suppr_pdc, name = 'suppr_pdc'),
    url(r'^modules/pgre/selectionner-actions-pgre/$', pgre.filtr_act_pgre, name = 'select_act_pgre')
]

handler403 = main.h_403
handler404 = main.h_404
handler500 = main.h_500

if settings.DEBUG is True :
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

# Détermination de certains paramètres du site d'administration
admin.site.index_title = 'Accueil'
admin.site.site_header = 'Administration de STYX 2.0'
admin.site.site_title = 'Site d\'administration de STYX 2.0'
