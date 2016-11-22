#!/usr/bin/env python
#-*- coding: utf-8

''' Imports '''
from django import forms
from app.models import TUtilisateur

class MUtilisateurCreate(forms.ModelForm) :

    # Je définis les champs du formulaire.
    password1 = forms.CharField(max_length = 255, widget = forms.PasswordInput(), label = 'Mot de passe')
    password2 = forms.CharField(
        max_length = 255, widget = forms.PasswordInput(), label = 'Confirmation du mot de passe'
    )
    est_techn = forms.BooleanField(
        help_text = 'Création automatique d\'un technicien si coché.', label = 'Est technicien', required = False
    )

    class Meta :
        model = TUtilisateur
        fields = '__all__'

    def clean_password2(self) :

        # Je récupère les mots de passe saisis.
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # Je renvoie une erreur si les mots de passe saisis sont différents
        if password1 and password2 :
            if password1 != password2 :
                raise forms.ValidationError('Les deux mots de passe ne correspondent pas.')

    def save(self, commit = True) :
        util = super(MUtilisateurCreate, self).save(commit = False)
        util.set_password(self.cleaned_data['password1'])
        if commit :
            util.save()
        return util

class MUtilisateurUpdate(forms.ModelForm) :

    ''' Imports '''
    from django.contrib.auth.forms import ReadOnlyPasswordHashField

    # Je définis les champs du formulaire.
    password = ReadOnlyPasswordHashField(
        help_text = 'Les mots de passe ne sont pas enregistrés en clair, ce qui ne permet pas d\'afficher le mot de passe de cet utilisateur, mais il est possible de le changer en utilisant <a href="../password/">ce formulaire</a>.',
        label = 'Mot de passe'
    )

    class Meta :
        model = TUtilisateur
        fields = '__all__'

    def clean_password(self) :
        return self.initial['password']