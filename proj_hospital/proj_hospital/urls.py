from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from ficha import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.redir, name='redirect'),
    path('menu/', views.menu, name='menu'),
    path('perfil/<int:id>/', views.perfil, name='perfil'),
    path('login/', views.iniciarSesion, name='login'),
    path('logout/', views.cerrarSesion, name='logout'),
    path('insertar/', views.insertar, name='insertar'),
    path('formulario/', views.formulario, name='formulario'),
    path('listado/', views.listado, name='listado'),
    path('eliminarficha/<int:id>/', views.eliminarficha, name='eliminarficha'),
    path('verficha/<int:id>/', views.verficha, name='verficha'),
]

