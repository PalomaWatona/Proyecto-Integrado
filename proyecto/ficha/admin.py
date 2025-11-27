from django.contrib import admin
from ficha.models import Fichas, HistorialAcciones, Usuario

# Las siguientes tablas se ven en el panel de /admin

# Tabla para Usuarios
class usuarioAdmin(admin.ModelAdmin):
    list_display = ['id','rut','nombre', 'contraseña','correo','rol']
admin.site.register(Usuario, usuarioAdmin)

# Tabla para Las Fichas de los Pacientes
class fichaAdmin(admin.ModelAdmin):
    list_display = ['id','nombrepaciente','apellidopaciente','rutpaciente','rutparamedico','telefono','prevision','genero','edad','motivoconsulta','comorbilidades','alergias','frecuenciacardiaca','temperatura','presionarterial','tiposangre','observaciones','fechacreacion']
admin.site.register(Fichas, fichaAdmin)

# Tabla para el Historial de Acciones
class historialAdmin(admin.ModelAdmin):
    list_display = ['id','usuario','accion','fechacreacion']
admin.site.register(HistorialAcciones, historialAdmin)