from django.db import models

  # class Categorie(models.Model):
      # nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
     #  slug = models.SlugField(max_length=100, unique=True, help_text="Sert pour l'URL (ex: informatique-web)")
      # icone = models.CharField(max_length=50, blank=True, help_text="Nom de l'icône (ex: fas fa-laptop)")

      # class Meta:
          # verbose_name = "Catégorie"
          # verbose_name_plural = "Catégories"

      # def __str__(self):
          # return self.nom


class Formation(models.Model):
      #categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='formations', verbose_name="Catégorie")
    titre = models.CharField(max_length=200, verbose_name="Titre de la formation")
    slug = models.SlugField(max_length=200, unique=True)
    description_courte = models.TextField(max_length=300, verbose_name="Description courte (pour les cartes)")
    programme_detaille = models.TextField(verbose_name="Programme détaillé")
    duree = models.CharField(max_length=50, verbose_name="Durée (ex: 3 mois / 120 heures)")
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (FCFA / €)", blank=True, null=True)
    image = models.ImageField(upload_to='formations/', verbose_name="Image d'illustration", blank=True, null=True)
    est_active = models.BooleanField(default=True, verbose_name="Afficher sur le site")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre


class DemandeContact(models.Model):
    nom_complet = models.CharField(max_length=150, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Adresse Email")
    telephone = models.CharField(max_length=20, verbose_name="Numéro de Téléphone")
    # On ne garde qu'une seule fois ce champ, configuré proprement
    formation_interet = models.ForeignKey(Formation, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Formation concernée", related_name='demandes')
    message = models.TextField(verbose_name="Message / Questions")
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False, verbose_name="Traité / Lu")

    class Meta:
        verbose_name = "Demande de contact"
        verbose_name_plural = "Demandes de contact"
        ordering = ['-date_envoi']

    def __str__(self):
        return f"Demande de {self.nom_complet} - {self.date_envoi.strftime('%d/%m/%Y')}"
    



class Annonce(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre de l'annonce")
    slug = models.SlugField(max_length=200, unique=True)
    contenu = models.TextField(verbose_name="Contenu de l'annonce ou de l'article")
    image = models.ImageField(upload_to='annonces/', verbose_name="Image d'illustration", blank=True, null=True)
    est_epinglee = models.BooleanField(default=False, verbose_name="Épingler en haut de page (Important)")
    est_active = models.BooleanField(default=True, verbose_name="Publier l'annonce")
    date_publication = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Annonce / Actualité"
        verbose_name_plural = "Annonces / Actualités"
        ordering = ['-est_epinglee', '-date_publication']

    def __str__(self):
        return self.titre


class Partenaire(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de l'entreprise / partenaire")
    logo = models.ImageField(upload_to='partenaires/', verbose_name="Logo du partenaire")
    site_web = models.URLField(max_length=200, blank=True, null=True, verbose_name="Lien vers leur site web (Optionnel)")
    ordre_affichage = models.IntegerField(default=0, verbose_name="Ordre d'affichage (ex: 1, 2, 3...)")

    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"
        ordering = ['ordre_affichage', 'nom']

    def __str__(self):
        return self.nom
    
class AlbumPhoto(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre de l'evenement")
    contenu = models.TextField(verbose_name="Contenu de l'annonce ou de l'article")
    image = models.ImageField(upload_to='annonces/', verbose_name="Image d'illustration", blank=True, null=True)

    class Meta:
        verbose_name = "Album"
        verbose_name_plural = "Albums"
        ordering = ['titre']

    def __str__(self):
        return self.titre