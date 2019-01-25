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
        fields = '__all__'; model = TAction

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