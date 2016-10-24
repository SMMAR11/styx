from app.constants import *
from app.functions import *
from app.models import *
from app.validators import *
from django import forms

class Identifier(forms.Form) :

	# Je définis les champs du formulaire.
	zs_pseudo = forms.CharField(
		error_messages = MESSAGES,
		label = 'Nom d\'utilisateur',
		widget = forms.TextInput(attrs = { 'class' : 'form-control' })
	)

	zs_mdp = forms.CharField(
		error_messages = MESSAGES,
		label = 'Mot de passe',
		widget = forms.PasswordInput(attrs = { 'class' : 'form-control' })
	)

	def clean(self) :

		# Je récupère les données utiles du formulaire pré-valide.
		tab_donnees = super(Identifier, self).clean()
		v_pseudo = tab_donnees.get('zs_pseudo')
		v_mdp = crypt_val(tab_donnees.get('zs_mdp'))

		# Je déclare des booléens me permettant de jauger l'état de l'identification.
		pseudo_trouve = False
		mdp_trouve = False

		# Je stocke dans un tableau tous les utilisateurs référencés dans la base de données.
		les_utilisateurs = TUtilisateur.objects.all()

		# Je parcours chaque utilisateur afin de vérifier si l'identification est possible ou non.
		for un_utilisateur in les_utilisateurs :
			if v_pseudo == un_utilisateur.pseudo_util :
				pseudo_trouve = True
				if v_mdp == un_utilisateur.mdp_util :
					mdp_trouve = True

		# Je définis les messages d'erreurs.
		if pseudo_trouve == True :
			if mdp_trouve == False :
				self.add_error('zs_mdp', 'Veuillez saisir le bon mot de passe lié à ce compte.')
		else :
			self.add_error('zs_pseudo', 'Aucun compte n\'est lié à ce courriel.')

class OublierMotDePasse(forms.Form) :

	# Je définis le champ du formulaire.
	zs_courr = forms.CharField(
		error_messages = MESSAGES,
		label = 'Adresse électronique' + CHAMP_REQUIS,
		widget = forms.TextInput(attrs = { 'class' : 'form-control' }),
		validators = [valid_courr]
	)

	def clean_zs_courr(self) :

		# Je récupère le courriel saisi.
		v_courriel = self.cleaned_data['zs_courr']

		# Je déclare un booléen me permettant de voir si le courriel saisi est lié ou non à un compte.
		courriel_trouve = False

		# Je stocke dans un tableau tous les utilisateurs référencés dans la base de données.
		les_utilisateurs = TUtilisateur.objects.all()

		# Je parcours chaque utilisateur afin de vérifier si le courriel saisi est lié ou non à un compte.
		for un_utilisateur in les_utilisateurs :
			if v_courriel == un_utilisateur.courr_util :
				courriel_trouve = True

		# Je définis le message d'erreur.
		if courriel_trouve == False :
			raise forms.ValidationError('Veuillez saisir le courriel lié à votre compte.')

		return v_courriel