from django.contrib import admin
from django.utils.html import format_html
from .models import Formation, DemandeContact, Annonce, Partenaire, AlbumPhoto

@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'duree', 'prix', 'est_active')
    list_filter = ('est_active',)
    search_fields = ('titre', 'description_courte')
    prepopulated_fields = {'slug': ('titre',)}


@admin.register(DemandeContact)
class DemandeContactAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'email', 'telephone', 'formation_interet', 'date_envoi', 'lu')
    list_filter = ('lu', 'date_envoi')
    readonly_fields = ('nom_complet', 'email', 'telephone', 'formation_interet', 'message', 'date_envoi')


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'est_epinglee', 'est_active', 'date_publication')
    list_filter = ('est_epinglee', 'est_active', 'date_publication')
    search_fields = ('titre', 'contenu')
    prepopulated_fields = {'slug': ('titre',)}


@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ordre_affichage', 'site_web')
    search_fields = ('nom',)


@admin.register(AlbumPhoto)
class AlbumPhotoAdmin(admin.ModelAdmin):
    list_display = ('titre', 'contenu_court', 'image_apercu')
    search_fields = ('titre', 'contenu')
    list_filter = ('image',)

    # Méthode pour tronquer le texte de l'annonce dans la liste
    @admin.display(description="Extrait du contenu")
    def contenu_court(self, obj):
        if obj.contenu and len(obj.contenu) > 50:
            return obj.contenu[:50] + "..."
        return obj.contenu

    # Méthode sécurisée pour afficher la miniature sous Django 6
    @admin.display(description="Aperçu")
    def image_apercu(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "Pas d'image"