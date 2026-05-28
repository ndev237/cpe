from django import forms
from .models import Formation,  Annonce, AlbumPhoto
from django.utils.text import slugify


class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        # On liste tous les champs SAUF le slug et la date de création
        fields = ['titre', 'description_courte', 'programme_detaille', 'duree', 'prix', 'image', 'est_active']
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