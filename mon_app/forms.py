from django import forms
from .models import Formation, Annonce, AlbumPhoto, Actualite, Partenaire
from django.utils.text import slugify


class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        # On ajoute 'categorie' dans la liste des champs affichés
        fields = ['titre', 'categorie', 'description_courte', 'programme_detaille', 'duree', 'prix', 'image', 'est_active']
        widgets = {
            'description_courte': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Résumé de la formation...'}),
            'programme_detaille': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Détails des modules...'}),
        }

    # Petite astuce pour générer le slug automatiquement à partir du titre
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
        # Liste des champs modifiables par l'administrateur
        fields = ['titre', 'slug', 'contenu', 'image', 'est_epinglee', 'est_active']

        # Ajout de classes CSS pour rendre le formulaire beau (compatible avec du style personnalisé)
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': "Entrez le titre de l'annonce..."}),
            'slug': forms.TextInput(attrs={'placeholder': "Ex: depeche-rentree-2026 (ou laissez vide si généré automatiquement)"}),
            'contenu': forms.Textarea(attrs={'rows': 6, 'placeholder': "Rédigez le contenu détaillé de l'annonce ici..."}),
        }


class AlbumPhotoForm(forms.ModelForm):
    class Meta:
        model = AlbumPhoto
        fields = ['titre', 'contenu', 'image']


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