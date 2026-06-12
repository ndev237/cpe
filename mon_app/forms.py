from django import forms
from .models import Formation, Annonce, AlbumPhoto, Actualite, Partenaire
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class AdminUserCreateForm(forms.Form):
    """Création d'un compte autorisé à se connecter au dashboard."""
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'ex: marie.dupont'}),
    )
    email = forms.EmailField(
        label="Adresse email",
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'nom@exemple.com'}),
    )
    first_name = forms.CharField(
        label="Prénom", max_length=150, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Marie'}),
    )
    last_name = forms.CharField(
        label="Nom", max_length=150, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Dupont'}),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': '8 caractères minimum'}),
    )
    password_confirm = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Retapez le mot de passe'}),
    )
    is_staff = forms.BooleanField(
        label="Accès administrateur (peut gérer le contenu)",
        required=False, initial=True,
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get('password')
        pwd2 = cleaned.get('password_confirm')
        if pwd and pwd2 and pwd != pwd2:
            self.add_error('password_confirm', "Les deux mots de passe ne correspondent pas.")
        if pwd:
            try:
                validate_password(pwd)
            except ValidationError as e:
                self.add_error('password', list(e.messages))
        return cleaned

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data.get('email') or '',
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data.get('first_name') or '',
            last_name=self.cleaned_data.get('last_name') or '',
        )
        user.is_staff = self.cleaned_data.get('is_staff', False)
        user.save()
        return user


class AdminPasswordResetForm(forms.Form):
    """Changement du mot de passe d'un utilisateur depuis le dashboard."""
    new_password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': '8 caractères minimum'}),
    )
    new_password_confirm = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Retapez le mot de passe'}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get('new_password')
        pwd2 = cleaned.get('new_password_confirm')
        if pwd and pwd2 and pwd != pwd2:
            self.add_error('new_password_confirm', "Les deux mots de passe ne correspondent pas.")
        if pwd:
            try:
                validate_password(pwd, user=self.user)
            except ValidationError as e:
                self.add_error('new_password', list(e.messages))
        return cleaned

    def save(self):
        if not self.user:
            raise RuntimeError("AdminPasswordResetForm requires `user` in __init__")
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()
        return self.user

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        # Assurez-vous que 'programme_detaille' a BIEN disparu d'ici :
        fields = [
            'titre', 'categorie', 'description_courte',
            'niveau_requis', 'debouches', 'duree', 'image', 'est_active'
        ]

        # Et qu'il a BIEN disparu d'ici également :
        widgets = {
            'description_courte': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Résumé de la formation (affiché sur les cartes)...'
            }),
            'niveau_requis': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Ex: Baccalauréat, Niveau d\'études minimum, diplômes ou compétences prérequises...'
            }),
            'debouches': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Ex: Métiers accessibles, secteurs d\'insertion professionnelle après la formation...'
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.titre)
        if commit:
            instance.save()
        return instance

class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = ['titre', 'slug', 'contenu', 'image', 'est_epinglee', 'est_active']

        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': "Entrez le titre de l'annonce..."}),
            'slug': forms.TextInput(attrs={'placeholder': "Laissez vide pour génération automatique"}),
            'contenu': forms.Textarea(attrs={'rows': 6, 'placeholder': "Rédigez le contenu détaillé de l'annonce ici..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # slug optionnel : auto-genere depuis le titre cote modele
        self.fields['slug'].required = False

    def clean_contenu(self):
        contenu = (self.cleaned_data.get('contenu') or '').strip()
        # Quill envoie souvent "<p><br></p>" quand vide
        if contenu in ('', '<p><br></p>', '<p></p>'):
            raise forms.ValidationError("Le contenu de l'annonce est obligatoire.")
        return contenu


class AlbumPhotoForm(forms.ModelForm):
    class Meta:
        model = AlbumPhoto
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


class ActualiteForm(forms.ModelForm):
    class Meta:
        model = Actualite
        fields = ['titre', 'image', 'contenu', 'statut']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Cérémonie de remise des diplômes...'}),
            'contenu': forms.Textarea(attrs={'class': 'form-input textarea', 'rows': 6, "placeholder": "Rédigez le contenu de l\'article ici..."}),
            'statut': forms.Select(attrs={'class': 'form-input'}),
            'image': forms.FileInput(attrs={'class': 'form-file'}),
        }



class PartenaireForm(forms.ModelForm):
    class Meta:
        model = Partenaire
        fields = ['nom', 'logo', 'site_web', 'ordre_affichage']  # <--- Correction ici
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Banque Nationale du Mali'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-file',
                'accept': 'image/*'
            }),
            'site_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: https://www.nom-partenaire.com'
            }),
            'ordre_affichage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Ex: 1'
            }),
        }