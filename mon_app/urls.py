from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import ActualitePublicListView, admin_publie_photo, detail_actualite

urlpatterns = [
    # Page d'accueil : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
    path('', views.index, name='index'),
    path('formation/<slug:slug>/', views.detail_formation, name='detail_formation'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('nos-formations/', views.nos_formations_liste, name='nos_formation'),
    path('notre_album/', views.notre_album, name='notre_album'),
    path('actualites/simple/', views.ActualitePublicListView, name='actualites_site'),
    path('annonce/<slug:slug>/', views.detail_annonce, name='detail_annonce'),
    
   

    
   # =============================== Admin==========================

   path('dashboard/formations/creer/', views.admin_creer_formation, name='admin_creer_formation'),
   path('dashboard/connexion/', views.connexion_dashboard, name='connexion_dashboard'),
   path('dashboard/', views.admin_creer_formation, name='admin_dashboard'),
   path('dashboard/deconnexion/', auth_views.LogoutView.as_view(next_page='index'), name='deconnexion'),
   path('dashboard_CPE/', views.dash_admin, name='dashboard_admin'),
   path('list_formations/', views.admin_liste_formations, name='admin_liste_formations'),
   path('list_anonces/', views.admin_list_anonces, name='admin_list_anonces'),
   path('dashboard/annonces/creer/', views.admin_creer_annonce, name='admin_creer_annonce'),
   path('dashboard/album/publier/', views.admin_publie_photo, name='admin_publier_photo'),
   path('dashboard/album/', views.admin_liste_photos, name='admin_liste_photos'),
   path('dashboard/album/supprimer/<int:pk>/', views.admin_supprimer_photo, name='admin_supprimer_photo'),
   path('actualites/', views.actualite_liste, name='actualite_liste'),
   path('actualites/creer/', views.admin_actualite_creer, name='actualite_creer'),
   path('notifications/admin/', views.notifications_page, name='notifications_page'),
   path('dashboard/partenaires/', views.admin_list_partenaires, name='admin_list_partenaires'),
   path('dashboard/partenaires/ajouter/', views.admin_creer_partenaire, name='admin_creer_partenaire'), # <--- Ajout de /ajouter/
   path('dashboard/partenaires/supprimer/<int:pk>/', views.admin_supprimer_partenaire, name='admin_supprimer_partenaire'),

   path('actualites/<slug:slug>/', detail_actualite, name='actualite_detail'),
   path('actualites/supprimer/<slug:slug>/', views.admin_supprimer_actualite, name='admin_supprimer_actualite'),
   path('formations/modifier/<slug:slug>/', views.admin_modifier_formation, name='admin_modifier_formation'),
   path('annonces/modifier/<slug:slug>/', views.admin_modifier_annonce, name='admin_modifier_annonce'),
   path('actualites/modifier/<slug:slug>/', views.admin_actualite_modifier, name='admin_actualite_modifier'),



   path('formations/supprimer/<slug:slug>/', views.admin_supprimer_formation, name='admin_supprimer_formation'),
   path('annonces/supprimer/<slug:slug>/', views.admin_supprimer_annonce, name='admin_supprimer_annonce'),
   path('actualites/modifier/<slug:slug>/', views.admin_actualite_modifier, name='admin_actualite_modifier'),



]


