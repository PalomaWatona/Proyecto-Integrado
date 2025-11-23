from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from ficha import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.redir, name='redirect'),
    path('menu/', views.menu, name='menu'),
    path('perfil/', views.perfil, name='perfil'),
    path('editarperfil/', views.editarperfil, name='editarperfil'),
    path('editarperfil_send/<int:id>/', views.editarperfil_send, name='editarperfil_send'),
    path('login/', views.iniciarSesion, name='login'),
    path('logout/', views.cerrarSesion, name='logout'),
    path('formulario/', views.formulario, name='formulario'),
    path('formulario_send/', views.formulario_send, name='formulario_send'),
    path('editarficha/', views.editarficha, name='editarficha'),
    path('editarficha_send/<int:id>/', views.editarficha_send, name='editarficha_send'),
    path('listado/', views.listado, name='listado'),
    path('eliminarficha/<int:id>/', views.eliminarficha, name='eliminarficha'),
    path('ficha/', views.verficha, name='verficha'),
    path('log/', views.log, name='log'),
]

