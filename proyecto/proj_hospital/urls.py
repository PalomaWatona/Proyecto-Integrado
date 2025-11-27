from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from ficha import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.redir, name='redirect'),
    path('menu/', views.menu, name='menu'),
    
    # --- Rutas de Perfil y Usuario ---
    
    path('perfil/', views.perfil, name='perfil'),
    path('editarperfil/', views.editarperfil, name='editarperfil'),
    path('editarperfil_send/<int:id>/', views.editarperfil_send, name='editarperfil_send'),
    path('adduser/', views.adduser, name='adduser'),
    path('adduser_send/', views.adduser_send, name='adduser_send'),
    
    # --- Rutas de Autenticación ---
    
    path('login/', views.iniciarSesion, name='login'),
    path('logout/', views.cerrarSesion, name='logout'),
    
    # --- Rutas de Fichas (Registrar, editar, listar y eliminar) ---
    
    path('formulario/', views.formulario, name='formulario'),
    path('formulario_send/', views.formulario_send, name='formulario_send'),
    path('editarficha/', views.editarficha, name='editarficha'),
    path('editarficha_send/<int:id>/', views.editarficha_send, name='editarficha_send'),
    path('listado/', views.listado, name='listado'),
    path('cambioestado/<int:id>/', views.cambioestado, name='cambioestado'),
    path('eliminarficha/<int:id>/', views.eliminarficha, name='eliminarficha'),
    path('ficha/', views.verficha, name='verficha'),
    
    # --- Rutas de Logs y Auditoría ---
    
    path('log/', views.log, name='log'),
    path('logcambios/', views.logcambios, name='logcambios'),
]

