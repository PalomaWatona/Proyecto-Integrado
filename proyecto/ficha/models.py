from django.db import models

# Tabla para guardar los datos del Formulario de Fichas.
class Fichas(models.Model):
    nombrepaciente = models.CharField(max_length=80, default='')
    apellidopaciente = models.CharField(max_length=80, default='')
    rutpaciente = models.CharField(max_length=12, default='')
    rutparamedico = models.CharField(max_length=12, default='')
    telefono = models.CharField(max_length=9, default='')
    prevision = models.CharField(max_length=50, default='')
    genero = models.CharField(max_length=10, default='')
    edad = models.IntegerField(default='')
    motivoconsulta = models.CharField(max_length=100, default='')
    comorbilidades = models.CharField(max_length=50, default='')
    alergias = models.CharField(max_length=50, default='')
    frecuenciacardiaca = models.CharField(max_length=50, default='')
    temperatura = models.CharField(max_length=50, default='')
    presionarterial = models.CharField(max_length=50, default='')
    tiposangre = models.CharField(max_length=5, default='')
    observaciones = models.CharField(max_length=2000, default='')
    fechacreacion = models.DateTimeField(auto_now_add=True)
    revisado = models.BooleanField(default=False)
    
    
# Tabla para guardan los datos de los Usuarios creados (Paramedicos, Cordinador, etc.)
class Usuario(models.Model):
    rut = models.CharField(max_length=12, unique=True )
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=9)
    bio = models.CharField(max_length=200)
    contraseña = models.CharField(max_length=100)
    correo = models.CharField(max_length=50)
    rol = models.CharField(max_length=20)
    estado = models.BooleanField(default=True)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    
'''
class HistorialFichas(models.Model):
    ficha = models.ForeignKey(Fichas, on_delete=models.CASCADE)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    cambios_realizados = models.TextField()
'''

# Tabla para el Historial de Acciones que guarda las acciones de los Usuarios
class HistorialAcciones(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    accion = models.CharField(max_length=1000)
    cambios = models.JSONField(null=True, blank=True)
    fechacreacion = models.DateTimeField(auto_now_add=True)