#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from django import forms
from app.models import TAction, TAxe, TFinanceur, TMoa, TOrganisme, TPrestataire, TProgramme, TSousAxe, TUtilisateur

class MUtilisateurCreate(forms.ModelForm) :

    # Je définis les champs du formulaire.
    password1 = forms.CharField(max_length = 255, widget = forms.PasswordInput(), label = 'Mot de passe')
    password2 = forms.CharField(
        max_length = 255, widget = forms.PasswordInput(), label = 'Confirmation du mot de passe'
    )
    les_org = forms.ChoiceField(
        label = 'Organisme'
    )

    class Meta :
        model = TUtilisateur
        fields = '__all__'

    def __init__(self, *args, **kwargs) :
        super(MUtilisateurCreate, self).__init__(*args, **kwargs)

        # J'alimente la liste déroulante des organismes.
        self.fields['les_org'].choices = [
            ('', '---------'),
            (
                'Financeurs', (
                    [(i.id_org_fin.id_org, i.id_org_fin) for i in TFinanceur.objects.all()]
                )
            ),
            (
                'Maîtres d\'ouvrages', (
                    [(i.id_org_moa.id_org, i.id_org_moa) for i in TMoa.objects.all()]
                )
            ),
            (
                'Prestataires', (
                    [(i.id_org_prest.id_org, i.id_org_prest) for i in TPrestataire.objects.all()]
                )
            )
        ]

    def clean_password2(self) :

        # Je récupère les mots de passe saisis.
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # Je renvoie une erreur si les mots de passe saisis sont différents
        if password1 and password2 :
            if password1 != password2 :
                raise forms.ValidationError('Les deux mots de passe ne correspondent pas.')

    def save(self, commit = True) :
        obj = super(MUtilisateurCreate, self).save(commit = False)
        obj.set_password(self.cleaned_data['password1'])
        obj.id_org = TOrganisme.objects.get(id_org = self.cleaned_data['les_org'])
        if commit :
            obj.save()
        return obj

class MUtilisateurUpdate(forms.ModelForm) :

    ''' Imports '''
    from django.contrib.auth.forms import ReadOnlyPasswordHashField

    # Je définis les champs du formulaire.
    password = ReadOnlyPasswordHashField(
        help_text = 'Les mots de passe ne sont pas enregistrés en clair, ce qui ne permet pas d\'afficher le mot de passe de cet utilisateur, mais il est possible de le changer en utilisant <a href="../password/">ce formulaire</a>.',
        label = 'Mot de passe'
    )
    les_org = forms.ChoiceField(
        label = 'Organisme'
    )

    class Meta :
        model = TUtilisateur
        fields = '__all__'

    def __init__(self, *args, **kwargs) :
        super(MUtilisateurUpdate, self).__init__(*args, **kwargs)

        # J'alimente la liste déroulante des organismes.
        self.fields['les_org'].choices = [
            ('', '---------'),
            (
                'Financeurs', (
                    [(i.id_org_fin.id_org, i.id_org_fin) for i in TFinanceur.objects.all()]
                )
            ),
            (
                'Maîtres d\'ouvrages', (
                    [(i.id_org_moa.id_org, i.id_org_moa) for i in TMoa.objects.all()]
                )
            ),
            (
                'Prestataires', (
                    [(i.id_org_prest.id_org, i.id_org_prest) for i in TPrestataire.objects.all()]
                )
            )
        ]

        self.fields['les_org'].initial = self.instance.id_org.id_org

    def clean_password(self) :
        return self.initial['password']

    def save(self, commit = True) :
        obj = super(MUtilisateurUpdate, self).save(commit = False)
        obj.id_org = TOrganisme.objects.get(id_org = self.cleaned_data['les_org'])
        if commit :
            obj.save()
        return obj

class MSousAxe(forms.ModelForm) :

    # Je définis le champ du formulaire.
    les_axes = forms.ChoiceField(
        label = 'Axe'
    )

    class Meta :
        model = TSousAxe
        fields = '__all__'

    def __init__(self, *args, **kwargs) :
        super(MSousAxe, self).__init__(*args, **kwargs)

        if self.instance.pk :

            # J'affiche l'intitulé de l'objet TAxe lié à l'instance de TSousAxe.
            tab_axes = [(self.instance.id_axe.id_progr, [(self.instance.id_axe.id_axe, self.instance.id_axe)])]
            self.fields['les_axes'].initial = self.instance.id_axe.id_axe

        else :

            # Je récupère les programmes.
            les_progr = TProgramme.objects.all()

            tab_axes = [('', '---------')]
            for un_progr in les_progr :

                # Je récupère les axes de l'objet TProgramme courant.
                les_axes_progr = TAxe.objects.filter(id_progr = un_progr.id_progr)

                if len(les_axes_progr) > 0 :

                    # J'empile le tableau des axes de l'objet TProgramme courant.
                    tab_axes_progr = []
                    for un_axe_progr in les_axes_progr :
                        tab_axes_progr.append((un_axe_progr.id_axe, un_axe_progr))

                    # J'empile le tableau des axes.
                    tab_axes.append(
                        (un_progr.int_progr, tab_axes_progr)
                    )

        # J'alimente la liste déroulante des axes.
        self.fields['les_axes'].choices = tab_axes

    def clean(self) :

        # Je récupère certaines valeurs saisies.
        v_axe = self.cleaned_data.get('les_axes')
        v_num_ss_axe = self.cleaned_data.get('num_ss_axe')

        if v_axe :
            if len(TSousAxe.objects.filter(id_axe = v_axe, num_ss_axe = v_num_ss_axe)) > 0 :
                raise forms.ValidationError('Le sous-axe existe déjà.')

    def save(self, commit = True) :
        obj = super(MSousAxe, self).save(commit = False)
        obj.id_axe = TAxe.objects.get(id_axe = self.cleaned_data['les_axes'])
        if commit :
            obj.save()
        return obj

class MAction(forms.ModelForm) :

    # Je définis le champ du formulaire.
    les_ss_axes = forms.ChoiceField(
        label = 'Sous-axe'
    )

    class Meta :
        model = TAction
        fields = '__all__'

    def __init__(self, *args, **kwargs) :
        super(MAction, self).__init__(*args, **kwargs)

        if self.instance.pk :

            # J'affiche l'intitulé de l'objet TSousAxe lié à l'instance de TAction.
            tab_ss_axes = [(
                '[{0}] {1}'.format(self.instance.id_ss_axe.id_axe.id_progr, self.instance.id_ss_axe.id_axe),
                [(self.instance.id_ss_axe.id_ss_axe, '{0} - {1}'.format(
                    self.instance.id_ss_axe.num_ss_axe, self.instance.id_ss_axe.int_ss_axe
                ))]
            )]
            self.fields['les_ss_axes'].initial = self.instance.id_ss_axe.id_ss_axe

        else :

            # Je récupère les axes.
            les_axes = TAxe.objects.all()

            tab_ss_axes = [('', '---------')]
            for un_axe in les_axes :

                # Je récupère les sous-axes de l'objet TAxe courant.
                les_ss_axes_axe = TSousAxe.objects.filter(id_axe = un_axe.id_axe)

                if len(les_ss_axes_axe) > 0 :

                    # J'empile le tableau des sous-axes de l'objet TAxe courant.
                    tab_ss_axes_axe = []
                    for un_ss_axe_axe in les_ss_axes_axe :
                        tab_ss_axes_axe.append((un_ss_axe_axe.id_ss_axe, '{0} - {1}'.format(
                            un_ss_axe_axe.num_ss_axe, un_ss_axe_axe.int_ss_axe)
                        ))

                    # J'empile le tableau des sous-axes.
                    tab_ss_axes.append(
                        ('[{0}] {1}'.format(un_axe.id_progr, un_axe), tab_ss_axes_axe)
                    )

        # J'alimente la liste déroulante des sous-axes.
        self.fields['les_ss_axes'].choices = tab_ss_axes

    def clean(self) :

        # Je récupère certaines valeurs saisies.
        v_ss_axe = self.cleaned_data.get('les_ss_axes')
        v_num_act = self.cleaned_data.get('num_act')

        if v_ss_axe :
            if len(TAction.objects.filter(id_ss_axe = v_ss_axe, num_act = v_num_act)) > 0 :
                raise forms.ValidationError('L\'action existe déjà.')

    def save(self, commit = True) :
        obj = super(MAction, self).save(commit = False)
        obj.id_ss_axe = TSousAxe.objects.get(id_ss_axe = self.cleaned_data['les_ss_axes'])
        if commit :
            obj.save()
        return obj