from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from . import models
from .forms import FormationForm,AlbumPhotoForm, PartenaireForm
from .models import AlbumPhoto, Annonce, Partenaire
from .models import Actualite
from .forms import ActualiteForm
from django.views.generic import ListView
from .models import Actualite



def index(request):
    """Vue pour afficher la page d'accueil avec les annonces et formations phares"""
    # Ajout du préfixe models. pour corriger le NameError
    annonces = models.Annonce.objects.filter(est_active=True).order_by('-est_epinglee', '-date_publication')[:3]
    formations_phares = models.Formation.objects.filter(est_active=True).order_by('-date_creation')[:4]
    partenaires = models.Partenaire.objects.all()

    context = {
        'annonces': annonces,
        'formations_phares': formations_phares,
        'partenaires': partenaires,
    }
    return render(request, 'mon_app/index.html', context)


def detail_formation(request, slug):
    """Vue pour afficher les détails d'une formation et gérer les demandes d'inscription"""
    # Ajout du préfixe models.
    formation = get_object_or_404(models.Formation, slug=slug, est_active=True)

    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        message = request.POST.get('message')

        # Enregistrement en base
        demande = models.DemandeContact.objects.create(
            nom_complet=nom,
            email=email,
            telephone=telephone,
            formation_interet=formation,
            message=message
        )

        # Copie en session pour alimenter la page admin notifications (si elle utilise seulement session)
        notifications = request.session.get('liste_notifications', [])
        notifications.append({
            'formation_titre': formation.titre,
            'nom': demande.nom_complet,
            'email': demande.email,
            'telephone': demande.telephone,
            'message': demande.message,
        })
        request.session['liste_notifications'] = notifications

        messages.success(request, "Votre demande d'inscription a bien été envoyée !")
        return redirect('detail_formation', slug=slug)

    return render(request, 'mon_app/detail_formation.html', {'formation': formation})


def a_propos(request):
    """Vue pour la page À Propos"""
    return render(request, 'mon_app/apropos.html')


def nos_formations_liste(request):
    """Vue pour lister toutes les formations sur une page dédiée"""
    # Ajout du préfixe models.
    formations = models.Formation.objects.filter(est_active=True)
    return render(request, 'mon_app/formation.html', {'formations': formations})


def notre_album(request):

    # Ajout du préfixe models.
    albums = models.AlbumPhoto.objects.all()
    return render(request, "mon_app/album.html", {'albums': albums})

def ActualitePublicListView(request):
    actualites = Actualite.objects.filter(statut='Publie')

    # Récupère les annonces actives pour les afficher aussi dans actualiter.html
    annonces = models.Annonce.objects.filter(est_active=True).order_by('-est_epinglee', '-date_publication')

    # On les passe au template via le dictionnaire de contexte
    return render(request, 'mon_app/actualiter.html', {
        'actualites': actualites,
        'annonces': annonces,
    })



def detail_annonce(request, slug):
    """Vue pour afficher les détails d'une annonce / article spécifique"""
    # On récupère l'annonce par son slug, seulement si elle est active
    annonce = get_object_or_404(Annonce, slug=slug, est_active=True)
    
    # Récupérer les 3 autres annonces récentes pour les suggestions en bas de page
    annonces_recentes = Annonce.objects.filter(est_active=True).exclude(id=annonce.id).order_by('-date_publication')[:3]

    context = {
        'annonce': annonce,
        'annonces_recentes': annonces_recentes,
    }
    return render(request, 'mon_app/detail_annonce.html', context)




### --- ESPACE ADMIN / DASHBOARD --- ###

@csrf_exempt
def connexion_dashboard(request):
    """Vue en liaison directe SQL corrigée (sans boucle de redirection)"""

    # MODIFICATION : On vérifie notre propre session brute pour éviter les conflits
    if request.session.get('admin_brut_id'):
        return redirect('admin_creer_formation')

    if request.method == 'POST':
        nom_saisi = request.POST.get('nom')
        password_saisi = request.POST.get('password')

        with connection.cursor() as cursor:
            requete_sql = "SELECT id, password FROM auth_user WHERE username = %s"
            cursor.execute(requete_sql, [nom_saisi])
            resultat = cursor.fetchone()

        if resultat:
            user_id, password_stocke = resultat

            if check_password(password_saisi, password_stocke):
                request.session['admin_brut_id'] = user_id
                messages.success(request, "Connexion réussie en liaison directe !")
                return redirect('dashboard_admin')

        messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'mon_app/admin/connexion.html')


def admin_creer_formation(request):
    if not request.session.get('admin_brut_id'):
        messages.error(request, "Veuillez vous connecter pour accéder au tableau de bord.")
        return redirect('connexion_dashboard')

    if request.method == 'POST':
        form = FormationForm(request.POST, request.FILES)
        if request.POST.get('niveau_requis') in ['<p><br></p>', '']:
            form.data = form.data.copy()
            form.data['niveau_requis'] = ''
        if request.POST.get('debouches') in ['<p><br></p>', '']:
            form.data = form.data.copy()
            form.data['debouches'] = ''

        if form.is_valid():
            formation = form.save()
            messages.success(request, f"La formation '{formation.titre}' a été créée avec succès !")
            return redirect('admin_liste_formations')
        else:
            messages.error(request, "Impossible de publier la formation. Vérifiez les erreurs dans les étapes.")
    else:
        form = FormationForm()
    return render(request, 'mon_app/admin/formations/creer_formation.html', {'form': form})

def dash_admin(request):
    if not request.session.get('admin_brut_id'):
        messages.error(request, "Veuillez vous connecter pour accéder au tableau de bord.")
        return redirect('connexion_dashboard')


    total_formations = models.Formation.objects.count()
    total_annonces = models.Annonce.objects.count()
    total_actualites = models.Actualite.objects.count()


    total_demandes_en_attente = models.DemandeContact.objects.filter(lu=False).count()

    demandes_recentes = models.DemandeContact.objects.select_related('formation_interet').all()[:5]


    context = {
        'total_formations': total_formations,
        'total_annonces': total_annonces,
        'total_actualites': total_actualites,
        'total_demandes_en_attente': total_demandes_en_attente,
        'demandes_recentes': demandes_recentes,
    }

    # 5. Rendu du template
    return render(request, 'mon_app/admin/dash.html', context)



def admin_liste_formations(request):
    if not request.session.get('admin_brut_id'):
        messages.error(request, "Veuillez vous connecter pour accéder au tableau de bord.")
        return redirect('connexion_dashboard')

    formations = models.Formation.objects.all().order_by('-date_creation')
    return render(request, 'mon_app/admin/formations/liste_formations.html', {'formations': formations})


def admin_list_anonces(request):
    if not request.session.get('admin_brut_id'):
        messages.error(request, "Veuillez vous connecter pour accéder au tableau de bord.")
        return redirect('connexion_dashboard')
    anonces = models.Annonce.objects.all().order_by('-date_publication')
    return render(request, 'mon_app/admin/Anonces/list_anonces.html', {'annonces': anonces})


def admin_creer_annonce(request):

    if not request.session.get('admin_brut_id'):
        messages.error(request, "Veuillez vous connecter pour accéder au tableau de bord.")
        return redirect('connexion_dashboard')
    from .forms import AnnonceForm

    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES)
        if form.is_valid():
            annonce = form.save()
            messages.success(request, f"L'annonce '{annonce.titre}' a été publiée avec succès !")
            return redirect('admin_list_anonces')
    else:
        form = AnnonceForm()

    return render(request, 'mon_app/admin/Anonces/creer_anonces.html', {'form': form})



def admin_publie_photo(request):
    if request.method == 'POST':
        form = AlbumPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "La photo a été ajoutée avec succès à l'album !")
            return redirect('dashboard_admin')
        else:
            messages.error(request, "Le formulaire contient des erreurs. Veuillez réessayer.")
    else:
        form = AlbumPhotoForm()

    return render(request, 'mon_app/admin/album_photo/publier_photo.html', {'form': form})




def admin_liste_photos(request):
    # Récupère tous les albums triés selon la configuration Meta (par titre)
    photos = AlbumPhoto.objects.all()
    return render(request, 'mon_app/admin/album_photo/list_photo.html', {'photos': photos})

def admin_supprimer_photo(request, pk):
    # Action optionnelle mais indispensable pour la gestion : supprimer une photo
    if request.method == 'POST':
        photo = get_object_or_404(AlbumPhoto, pk=pk)
        photo.delete()
        messages.success(request, "La photo a été supprimée avec succès de l'album.")
    return redirect('admin_liste_photos')




def actualite_liste(request):
    """Affiche toutes les actualités publiées"""
    actualites = Actualite.objects.filter(statut='Publie')
    return render(request, 'mon_app/admin/Actualiter/list_actualiter.html', {'actualites': actualites})

def admin_actualite_creer(request):
    """Gère la création d'une nouvelle actualité"""
    if request.method == 'POST':
        form = ActualiteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "L'actualité a été publiée avec succès !")
            return redirect('actualite_liste') # Adapte le nom de ton URL
    else:
        form = ActualiteForm()

    return render(request, 'mon_app/admin/Actualiter/creer_actualiter.html', {'form': form})

def notifications_page(request):
    # On récupère les notifications stockées en session (ou une liste vide si rien n'existe)
    notifications = request.session.get('liste_notifications', [])

    return render(request, 'mon_app/admin/notifications/list_notifications.html', {'notifications': notifications})



def admin_list_partenaires(request):
    partenaires = Partenaire.objects.all()
    query = request.GET.get('search')
    if query:
        partenaires = partenaires.filter(nom__icontains=query)

    context = {
        'partenaires': partenaires,
        'search_query': query,
    }
    return render(request, 'mon_app/admin/partenaires/list_partenaire.html', context)



def admin_creer_partenaire(request):
    if request.method == 'POST':
        form = PartenaireForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Le partenaire a été ajouté avec succès !")
            return redirect('admin_list_partenaires')
        else:
            messages.error(request, "Une erreur est survenue lors de la validation du formulaire.")
    else:
        form = PartenaireForm()

    context = {
        'form': form,
        'titre_page': "Ajouter un nouveau partenaire",
    }
    return render(request, 'mon_app/admin/partenaires/Ajouter_partenaire.html', context)