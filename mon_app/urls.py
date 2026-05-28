from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import admin_publie_photo

urlpatterns = [
    # Page d'accueil : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
    path('', views.index, name='index'),
    path('formation/<slug:slug>/', views.detail_formation, name='detail_formation'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('nos-formations/', views.nos_formations_liste, name='nos_formation'),
    path('notre_album/', views.notre_album, name='notre_album'),
   


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

]
