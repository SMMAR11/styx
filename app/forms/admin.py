#!/usr/bin/env python
#-*- coding: utf-8

# Imports
from app.constants import *
from app.models import TAction
from app.models import TAxe
from app.models import TFinanceur
from app.models import TMoa
from app.models import TOrganisme
from app.models import TPrestataire
from app.models import TProgramme
from app.models import TSousAxe
from app.models import TUtilisateur
from django import forms

class MSousAxe(forms.ModelForm) :

    zl_axe = forms.ChoiceField(label = 'Axe')

    class Meta :
        fields = '__all__'
        model = TSousAxe

    def __init__(self, *args, **kwargs) :
        super(MSousAxe, self).__init__(*args, **kwargs)

        if self.instance.pk :

            # Je pointe vers l'objet TAxe.
            o_axe = self.instance.id_axe

            # Je sélectionne par défaut la valeur de l'axe de l'enregistrement en cours.
            arr_axes = [(o_axe.id_axe, o_axe)]
            self.fields['zl_axe'].initial = o_axe

        else :
            arr_axes = [DEFAULT_OPTION]

            for p in TProgramme.objects.all() :

                # Je récupère les axes de l'objet TProgramme courant.
                qs_axes_progr = TAxe.objects.filter(id_progr = p)

                if len(qs_axes_progr) > 0 :

                    # J'empile le tableau des axes de l'objet TProgramme courant.
                    arr_axes_progr = []
                    for ap in qs_axes_progr :
                        arr_axes_progr.append((ap.id_axe, ap))

                    # J'empile le tableau des axes.
                    arr_axes.append(
                        (p.int_progr, arr_axes_progr)
                    )

        # J'alimente la liste déroulante des axes.
        self.fields['zl_axe'].choices = arr_axes

    def clean(self) :

        # Je récupère certaines données.
        v_axe = self.cleaned_data.get('zl_axe')
        v_num_ss_axe = self.cleaned_data.get('num_ss_axe')

        if v_axe and len(TSousAxe.objects.filter(id_axe = v_axe, num_ss_axe = v_num_ss_axe)) > 0 :
            raise forms.ValidationError('Le sous-axe existe déjà.')

    def save(self, commit = True) :
        o = super(MSousAxe, self).save(commit = False)
        o.id_axe = TAxe.objects.get(id_axe = self.cleaned_data.get('zl_axe'))
        if commit :
            o.save()
        return o

class MAction(forms.ModelForm) :

    zl_ss_axe = forms.ChoiceField(label = 'Sous-axe')

    class Meta :
        fields = '__all__'
        model = TAction

    def __init__(self, *args, **kwargs) :
        super(MAction, self).__init__(*args, **kwargs)

        if self.instance.pk :

            # Je pointe vers l'objet TSousAxe.
            o_ss_axe = self.instance.id_ss_axe

            # Je sélectionne par défaut la valeur du sous-axe de l'enregistrement en cours.
            arr_ss_axes = [(o_ss_axe.id_ss_axe, o_ss_axe)]
            self.fields['zl_ss_axe'].initial = o_ss_axe

        else :
            arr_ss_axes = [DEFAULT_OPTION]

            for a in TAxe.objects.all() :

                # Je récupère les sous-axes de l'objet TAxe courant.
                qs_ss_axes_axe = TSousAxe.objects.filter(id_axe = a)

                if len(qs_ss_axes_axe) > 0 :

                    # J'empile le tableau des sous-axes de l'objet TAxe courant.
                    arr_ss_axes_axe = []
                    for ssaa in qs_ss_axes_axe :
                        arr_ss_axes_axe.append((ssaa.id_ss_axe, ssaa))

                    # J'empile le tableau des sous-axes.
                    arr_ss_axes.append(
                        ('[{0}] {1}'.format(a.id_progr, a), arr_ss_axes_axe)
                    )

        # J'alimente la liste déroulante des sous-axes.
        self.fields['zl_ss_axe'].choices = arr_ss_axes

    def clean(self) :

        # Je récupère certaines données.
        v_ss_axe = self.cleaned_data.get('zl_ss_axe')
        v_num_act = self.cleaned_data.get('num_act')

        if v_ss_axe and len(TAction.objects.filter(id_ss_axe = v_ss_axe, num_act = v_num_act)) > 0 :
            raise forms.ValidationError('L\'action existe déjà.')

    def save(self, commit = True) :
        o = super(MAction, self).save(commit = False)
        o.id_ss_axe = TSousAxe.objects.get(id_ss_axe = self.cleaned_data.get('zl_ss_axe'))
        if commit :
            o.save()
        return o

class MUtilisateurCreate(forms.ModelForm) :

    arr_org = [
        DEFAULT_OPTION,
        (
            'Financeurs', (
                [(f.id_org_fin.id_org, f.id_org_fin) for f in TFinanceur.objects.all()]
            )
        ),
        (
            'Maîtres d\'ouvrages', (
                [(m.id_org_moa.id_org, m.id_org_moa) for m in TMoa.objects.all()]
            )
        ),
        (
            'Prestataires', (
                [(p.id_org_prest.id_org, p.id_org_prest) for p in TPrestataire.objects.all()]
            )
        )
    ]

    zl_org = forms.ChoiceField(choices = arr_org, label = 'Organisme')
    zs_pwd1 = forms.CharField(label = 'Mot de passe', max_length = 255, widget = forms.PasswordInput())
    zs_pwd2 = forms.CharField(label = 'Confirmation du mot de passe', max_length = 255, widget = forms.PasswordInput())

    class Meta :
        fields = '__all__'
        model = TUtilisateur   

    def clean_zs_pwd2(self) :

        # Je récupère les mots de passe saisis0
        v_pwd1 = self.cleaned_data.get('zs_pwd1')
        v_pwd2 = self.cleaned_data.get('zs_pwd2')

        if v_pwd1 and v_pwd2 :
            if v_pwd1 != v_pwd2 :
                raise forms.ValidationError('Les deux mots de passe ne correspondent pas.')

    def save(self, commit = True) :
        o = super(MUtilisateurCreate, self).save(commit = False)
        o.set_password(self.cleaned_data.get('zs_pwd1'))
        o.id_org = TOrganisme.objects.get(id_org = self.cleaned_data.get('zl_org'))
        if commit :
            o.save()
        return o

class MUtilisateurUpdate(forms.ModelForm) :

    # Imports
    from django.contrib.auth.forms import ReadOnlyPasswordHashField

    arr_org = [
        DEFAULT_OPTION,
        (
            'Financeurs', (
                [(f.id_org_fin.id_org, f.id_org_fin) for f in TFinanceur.objects.all()]
            )
        ),
        (
            'Maîtres d\'ouvrages', (
                [(m.id_org_moa.id_org, m.id_org_moa) for m in TMoa.objects.all()]
            )
        ),
        (
            'Prestataires', (
                [(p.id_org_prest.id_org, p.id_org_prest) for p in TPrestataire.objects.all()]
            )
        )
    ]

    password = ReadOnlyPasswordHashField(
        help_text = '''
        Les mots de passe ne sont pas enregistrés en clair, ce qui ne permet pas d\'afficher le mot de passe de cet
        utilisateur, mais il est possible de le changer en utilisant <a href="../password/">ce formulaire</a>.
        ''',
        label = 'Mot de passe'
    )
    zl_org = forms.ChoiceField(choices = arr_org, label = 'Organisme')

    class Meta :
        fields = '__all__'
        model = TUtilisateur

    def __init__(self, *args, **kwargs) :
        super(MUtilisateurUpdate, self).__init__(*args, **kwargs)
        self.fields['zl_org'].initial = self.instance.id_org.pk

    def clean_password(self) :
        return self.initial['password']

    def save(self, commit = True) :
        o = super(MUtilisateurUpdate, self).save(commit = False)
        o.id_org = TOrganisme.objects.get(id_org = self.cleaned_data.get('zl_org'))
        if commit :
            o.save()
        return o