from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, nom, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, **extra_fields)
        user.set_password(password) # Hache automatiquement le mot de passe
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, nom, password, **extra_fields)

class utilisateur(AbstractBaseUser):
    nom = models.CharField(max_length=200, verbose_name="Nom de l'utilisateur")
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    telephone = models.CharField(max_length=20, blank=True, null=True)
    
    # Propriétés requises pour que Django accepte ce modèle comme User principal
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'  # On se connectera avec l'email
    REQUIRED_FIELDS = ['nom']  # Champs obligatoires lors du createsuperuser

    def __str__(self):
        return self.email

    # Méthodes de permissions minimales requises par Django
    def has_perm(self, perm, obj=None): return True
    def has_module_perms(self, app_label): return True

    @property
    def is_staff(self):
        return self.is_admin


from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Formation(models.Model):
    class Categorie(models.TextChoices):
        paramedical = 'Paramedical', _('Paramedical')
        industrielle = 'Industrielle', _('Industrielle')
    titre = models.CharField(max_length=200, verbose_name="Titre de la formation")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description_courte = models.TextField(max_length=300, verbose_name="Description courte (pour les cartes)")
    niveau_requis = models.TextField(verbose_name="Niveau requis", blank=True, null=True)
    debouches = models.TextField(verbose_name="Débouchés professionnels", blank=True, null=True)

    categorie = models.CharField(max_length=50, choices=Categorie.choices, default=Categorie.paramedical)
    duree = models.CharField(max_length=50, verbose_name="Durée (ex: 3 mois / 120 heures)")
    image = models.ImageField(upload_to='formations/', verbose_name="Image d'illustration", blank=True, null=True)
    est_active = models.BooleanField(default=True, verbose_name="Afficher sur le site")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titre)
            slug = base_slug
            compteur = 1
            while Formation.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{compteur}"
                compteur += 1
            self.slug = slug
        super().save(*args, **kwargs)

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
    image = models.ImageField(upload_to='albums/', verbose_name="Image de l'album",  blank=True, null=True )
   
    class Meta:
        verbose_name = "Photo d'album"
        verbose_name_plural = "Album Photos"

    def __str__(self):
        if self.image:
            return f"Photo #{self.id} - {self.image.name.split('/')[-1]}"
        return f"Photo #{self.id} (Sans image)"
        


class Actualite(models.Model):
    class Statut(models.TextChoices):
        BROUILLON = 'Brouillon', _('Brouillon')
        PUBLIE = 'Publie', _('Publié')

    titre = models.CharField(max_length=250, verbose_name="Titre de l'actualité")
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    image = models.ImageField(upload_to='actualites/', verbose_name="Image d'illustration", blank=True, null=True)
    contenu = models.TextField(verbose_name="Contenu de l'article")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.PUBLIE)
    date_publication = models.DateTimeField(auto_now_add=True, verbose_name="Date de publication")
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
        ordering = ['-date_publication']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre