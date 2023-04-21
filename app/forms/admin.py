#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.constants import *
from app.models import TAction
from app.models import TAxe
from app.models import TDdsCdg
from app.models import TFinancement
from app.models import TFinanceur
from app.models import TMoa
from app.models import TOrganisme
from app.models import TPrestataire
from app.models import TProgramme
from app.models import TSousAxe
from app.models import TUtilisateur
from django import forms
from django.db.models import Q

class MSousAxe(forms.ModelForm) :

    class Meta :
        fields = '__all__'; model = TSousAxe

    def __init__(self, *args, **kwargs) :

        # Imports
        from app.classes.FFModelChoiceField import Class as FFModelChoiceField

        super().__init__(*args, **kwargs)

        # Redéfinition du champ "Axe"
        if not self.instance.pk :
            field = self.fields['id_axe']
            initial = field.initial; label = field.label; queryset = field.queryset; required = field.required
            self.fields['id_axe'] = FFModelChoiceField(
                initial = initial,
                label = label,
                obj_label = 'get_str_with_prg',
                queryset = queryset,
                required = required
            )

class MAction(forms.ModelForm) :

    class Meta :
        fields = '__all__'; model = TFinancement

    def __init__(self, *args, **kwargs) :

        # Imports
        from app.classes.FFModelChoiceField import Class as FFModelChoiceField

        super().__init__(*args, **kwargs)

        # Redéfinition du champ "Sous-axe"
        if not self.instance.pk :
            field = self.fields['id_ss_axe']
            initial = field.initial; label = field.label; queryset = field.queryset; required = field.required
            self.fields['id_ss_axe'] = FFModelChoiceField(
                initial = initial,
                label = label,
                obj_label = 'get_str_with_prg',
                queryset = queryset,
                required = required
            )

class MUtilisateurCreate(forms.ModelForm) :

    zs_pwd1 = forms.CharField(label = 'Mot de passe', max_length = 255, widget = forms.PasswordInput())
    zs_pwd2 = forms.CharField(label = 'Confirmation du mot de passe', max_length = 255, widget = forms.PasswordInput())
    cb_est_techn = forms.BooleanField(label = 'Est technicien', required = False)

    class Meta :
        fields = '__all__'
        model = TUtilisateur

    def __init__(self, *args, **kwargs) :

        # Imports
        from app.classes.FFModelChoiceField import Class as FFModelChoiceField

        super().__init__(*args, **kwargs)

        # Redéfinition du champ "Organisme"
        field = self.fields['id_org']
        initial = field.initial; label = field.label; queryset = field.queryset; required = field.required
        self.fields['id_org'] = FFModelChoiceField(
            initial = initial,
            label = label,
            obj_label = 'get_str_with_types',
            queryset = queryset,
            required = required
        )

        # Définition du paramètre "required" pour certains champs
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_zs_pwd2(self) :

        # Je récupère les mots de passe saisis.
        v_pwd1 = self.cleaned_data.get('zs_pwd1')
        v_pwd2 = self.cleaned_data.get('zs_pwd2')

        if v_pwd1 and v_pwd2 :
            if v_pwd1 != v_pwd2 :
                raise forms.ValidationError('Les deux mots de passe ne correspondent pas.')

    def save(self, commit = True) :

        # Imports
        from app.models import TTechnicien

        # Je créé l'instance TUtilisateur.
        o = super(MUtilisateurCreate, self).save(commit = False)
        o.set_password(self.cleaned_data.get('zs_pwd1'))
        o.save()

        # Je créé l'instance TTechnicien si l'utilisateur est un technicien.
        v_est_techn = self.cleaned_data.get('cb_est_techn')
        if v_est_techn == True :
            TTechnicien.objects.create(n_techn = o.last_name, pren_techn = o.first_name)
            
        return o

class MUtilisateurUpdate(forms.ModelForm) :

    # Imports
    from django.contrib.auth.forms import ReadOnlyPasswordHashField

    password = ReadOnlyPasswordHashField(
        help_text = '''
        Les mots de passe ne sont pas enregistrés en clair, ce qui ne permet pas d\'afficher le mot de passe de cet
        utilisateur, mais il est possible de le changer en utilisant <a href="../password/">ce formulaire</a>.
        ''',
        label = 'Mot de passe'
    )

    class Meta :
        fields = '__all__'
        model = TUtilisateur

    def __init__(self, *args, **kwargs) :

        # Imports
        from app.classes.FFModelChoiceField import Class as FFModelChoiceField

        super().__init__(*args, **kwargs)

        # Redéfinition du champ "Organisme"
        field = self.fields['id_org']
        initial = field.initial; label = field.label; queryset = field.queryset; required = field.required
        self.fields['id_org'] = FFModelChoiceField(
            initial = initial,
            label = label,
            obj_label = 'get_str_with_types',
            queryset = queryset,
            required = required
        )

    def clean_password(self) :
        return self.initial['password']

# ---------------------------------------------------------------------
# PROGRAMMATION
# ---------------------------------------------------------------------

class UpdateDdsCdgAdmin(forms.ModelForm):

    # Imports
    from app.constants import DEFAULT_OPTION

    # Champs

    int_doss = forms.CharField(
        label='Intitulé du dossier',
        required=False,
        widget = forms.Textarea(attrs={'readonly': True})
    )

    cdg_id_ajourne = forms.ChoiceField(
        choices=[DEFAULT_OPTION],
        label='Date de représentation du dossier ajourné à un CD GEMAPI',
        required=False
    )

    class Meta:
        fields = '__all__'
        model = TDdsCdg

    # Méthodes Django

    def __init__(self, *args, **kwargs) :

        # Imports
        from app.models import TCDGemapiCdg
        from app.models import VSuiviDossier

        super().__init__(*args, **kwargs)

        qsCdgs = TCDGemapiCdg.objects.filter(
            cdg_date__gt=self.instance.cdg_id.cdg_date
        ).reverse()
        self.fields['cdg_id_ajourne'].choices += [(cdg.pk, cdg) for cdg in qsCdgs]
        nextCdg = qsCdgs.first()
        self.fields['cdg_id_ajourne'].initial = nextCdg.pk if nextCdg else None

        self.fields['int_doss'].initial = VSuiviDossier.objects.get(pk=self.instance.dds_id.pk).int_doss

    def save(self, commit=True) :

        # Imports
        from app.models import TCDGemapiCdg
        from app.models import TDdsCdg

        oDdsCdg = super().save(commit=False)

        cleanedData = self.cleaned_data
        acpId = oDdsCdg.acp_id
        cdgIdAjourne = cleanedData.get('cdg_id_ajourne')

        # Représentation automatique à un CD GEMAPI ultérieur si
        # déterminé par l'utilisateur
        if (acpId.int_av_cp == 'Ajourné') and (cdgIdAjourne):
            oDdsCdgNext = TDdsCdg.objects.filter(
                cdg_id=TCDGemapiCdg.objects.get(pk=cdgIdAjourne),
                dds_id=oDdsCdg.dds_id
            )
            if not oDdsCdgNext.exists():
                TDdsCdg.objects.create(
                    cdg_id=TCDGemapiCdg.objects.get(pk=cdgIdAjourne),
                    dds_id=oDdsCdg.dds_id
                )

        if commit:
            oDdsCdg.save()
            
        return oDdsCdg

class UpdateFinAdmin(forms.ModelForm):

    class Meta:
        fields = '__all__'
        model = TFinancement

    def clean(self):

        # Imports
        from app.functions import obt_mont
        from app.models import TDossier
        from app.models import VFinancement
        from app.models import VSuiviDossier

        # Récupération des données du formulaire
        cleaned_data = super().clean()
        fin_mont_elig = cleaned_data.get('mont_elig_fin')
        fin_mont_part = cleaned_data.get('mont_part_fin')
        fin_pourc_elig = cleaned_data.get('pourc_elig_fin')
        dds_id = cleaned_data.get('id_doss')
        ofn_id = cleaned_data.get('id_org_fin')

        # Récupération d'instances TDossier et VSuiviDossier
        toDds = TDossier.objects.get(pk=dds_id.pk)
        voDds = VSuiviDossier.objects.get(pk=toDds.pk)

        # Si un financeur est sélectionné, alors...
        if ofn_id:

            # ---------------------------------------------------------
            # Gestion du cas où le financeur serait présent plusieurs
            # fois dans le plan de financement du dossier
            # ---------------------------------------------------------

            # Récupération du plan de financement du dossier
            qsFin = VFinancement.objects.filter(
                id_doss=voDds.pk, id_org_fin=ofn_id.pk
            )

            # Si instance TFinancement, alors non-prise en compte de celle-ci
            # dans le plan de financement du dossier
            if self.instance.pk:
                qsFin = qsFin.exclude(id_fin=self.instance.pk)

            # Erreur si le financeur participe déjà au plan de financement
            if qsFin.exists():
                self.add_error(
                    'id_org_fin',
                    'Le financeur participe déjà au montage financier.'
                )

            # ---------------------------------------------------------
            # Gestion du renseignement des champs mont_elig_fin et
            # pourc_elig_fin
            # ---------------------------------------------------------

            # Erreur si les deux champs ne sont pas renseignés
            # simultanément
            if (fin_mont_elig) and (fin_pourc_elig is None):
                self.add_error('pourc_elig_fin', ERROR_MESSAGES['required'])
            if (fin_mont_elig is None) and (fin_pourc_elig):
                self.add_error('mont_elig_fin', ERROR_MESSAGES['required'])

            # Erreur si le montant de l'assiette éligible de la
            # subvention est supérieur au montant du dossier
            if (fin_mont_elig) \
            and (float(fin_mont_elig) > float(toDds.mont_doss)):
                self.add_error(
                    'mont_elig_fin',
                    '''
                    Veuillez saisir un montant inférieur ou égal à {} €.
                    '''.format(obt_mont(toDds.mont_doss))
                )

            # ---------------------------------------------------------
            # Gestion du montant de la participation
            # ---------------------------------------------------------

            # Récupération du reste à financer du dossier
            fin_mont_part_max = voDds.mont_raf
            if self.instance.pk:
                fin_mont_part_max += self.instance.mont_part_fin

            # Erreur si le montant de la participation est supérieur au
            # reste à financer du dossier
            if (fin_mont_part) \
            and (float(fin_mont_part) > float(fin_mont_part_max)):
                self.add_error(
                    'mont_part_fin',
                    '''
                    Veuillez saisir un montant inférieur ou égal à {} €.
                    '''.format(obt_mont(fin_mont_part_max))
                )

            # Si instance TFinancement, alors...
            if self.instance.pk:
                # Récupération d'une instance VFinancement
                oFin = VFinancement.objects.get(id_fin=self.instance.pk)
                # Erreur si le montant de la participation est
                # inférieur à la somme des demandes de versements
                # effectuées sur ce financement
                if (fin_mont_part) \
                and (float(fin_mont_part) < oFin.mont_ddv_sum):
                    self.add_error(
                        'mont_part_fin',
                        '''
                        Veuillez saisir un montant supérieur ou égal à {} €.
                        '''.format(obt_mont(oFin.mont_ddv_sum))
                    )