from django.contrib import admin
from django.utils.html import format_html
from .models import Formation, DemandeContact, Annonce, Partenaire, AlbumPhoto


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'duree', 'est_active')
    list_filter = ('est_active', 'categorie')
    search_fields = ('titre', 'description_courte', 'niveau_requis', 'debouches')  # Modifié ici
    prepopulated_fields = {'slug': ('titre',)}

    fieldsets = (
        ('Informations Générales', {
            'fields': ('titre', 'slug', 'categorie', 'duree', 'image', 'est_active')
        }),
        ('Contenus et Critères', {
            'fields': ('description_courte', 'niveau_requis', 'debouches'),  # Modifié ici
        }),
    )

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
    list_display = ['id', 'image_apercu', 'get_nom_fichier']
    search_fields = ['image']

    @admin.display(description="Aperçu de l'image")
    def image_apercu(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />')
        return "Aucun aperçu"

    @admin.display(description="Nom du fichier")
    def get_nom_fichier(self, obj):
        if obj.image:
            return obj.image.name.split('/')[-1]
        return "-"
    @admin.display(description="Aperçu")
    def image_apercu(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "Pas d'image"