from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import redirect
from django.conf import settings
from ficha.models import HistorialAcciones, Usuario, Fichas # Importa los modelos necesarios para Historial de acciones, Usuario y Fichas.
import os, json, hashlib # Módulos para manejo de rutas de archivos, JSON y hash.

# Carga el archivo de respuestas JSON, que contiene mensajes de notificación.
with open(os.path.join(settings.BASE_DIR, 'ficha', 'static', 'json', 'responses.json'), 'r', encoding='utf-8') as f:
    responselist = json.load(f)


def getstatus(request):
    # Función para obtener y limpiar mensajes de estado de la sesión.
    if request.session.get('r'):
        # Obtiene el índice 'r' (response ID) de la sesión.
        r = responselist[ int(request.session.get('r')) ] if request.session.get('r') else None
        request.session.pop('r') # Elimina el mensaje 'r' de la sesión para que solo se muestre una vez.
    else:
        r = None
    return r


def redir(request, r=None):
    # Funcion que verificar la sesión.
    userid = request.session.get('userid')
    if userid:
        try:
            # Intenta obtener el objeto Usuario para verificar que el ID de sesión sea válido.
            get_object_or_404(Usuario, pk=userid)
        except:
            # Si el usuario no existe (ejemplo: fue eliminado), limpia la sesión y redirige al login.
            request.session.pop('userid', None)
            request.session.flush()
            request.session['r'] = 1 # Mensaje de sesión invalida.
            return redirect('/login/')
        if r is not None: request.session['r'] = r # Establece un mensaje de estado si se proporciona.
        return redirect('/menu/') # Redirige al menú si la sesión es válida.

    else:
        # Si no hay 'userid' en la sesión, redirige al login.
        request.session['r'] = 1
        return redirect('/login/')


def menu(request):
    # Para ver el menu principal. Requiere tener la sesión iniciada.
    userid = request.session.get('userid')
    if not userid:
        return redir(request) # Redirige al login si no está logueado.
    usuario = get_object_or_404(Usuario, pk=userid)
    if not usuario.estado:
        # Si el usuario está deshabilitado, cierra la sesión.
        cerrarSesion(request, disabled=True)
    
    r = getstatus(request) # Obtiene el mensaje de estado.
    request.session['lasturl'] = request.get_full_path() # Guarda la URL actual para posibles redirecciones posteriores.
    datos = {'usuario': usuario, 'r': r}
    return render(request, 'menu.html', datos) # Renderiza la plantilla del menu.
    

def iniciarSesion(request):
    # Vista para el inicio de sesión.
    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None # Obtiene mensaje de la URL (no usado con getstatus).
    if request.method == 'POST':
        rut = request.POST['rut']
        con = request.POST['password']
        has = hashlib.md5(con.encode('utf-8')).hexdigest() # Cifra la contraseña ingresada usando hash.
        try:
            # Busca al usuario por RUT y contraseña cifrada.
            usuario = Usuario.objects.get(rut=rut, contraseña=has)
            # Registra la acción de iniciar de sesión.
            HistorialAcciones.objects.create(
                usuario=usuario, 
                accion='Sesión iniciada'
            )
        except Usuario.DoesNotExist:
            request.session['r'] = 2 # Mensaje de credenciales inválidas.
            return redirect('/login/')
        
        if not usuario.estado:
            request.session['r'] = 3 # Mensaje de usuario deshabilitado.
            return redirect('/login/')
        
        request.session['userid'] = usuario.id # Establece la sesión con el ID del usuario.
        return redirect('menu')
    else:
        # Si es GET, muestra el formulario de login.
        r = getstatus(request)
        request.session['lasturl'] = request.get_full_path()
        return render(request, 'login.html' , {'r': r} )


def cerrarSesion(request, disabled=False):
    # Cierra la sesión del usuario.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    
    # Registra el cierre de sesión.
    HistorialAcciones.objects.create(
        usuario_id=request.session.get('userid'),
        accion='Sesión cerrada'
    )
    request.session.pop('userid', None) # Elimina el ID de usuario de la sesión.
    request.session.flush() # Limpia todos los datos de la sesión.

    if disabled == True: request.session['r'] = 3 # Mensaje por deshabilitación.
    else: request.session['r'] = 4 # Mensaje por cierre voluntario.
    return redirect('/login/')


def perfil(request):
    # Vista para mostrar el perfil de un usuario.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    
    # Obtiene el ID del perfil a ver (propio o de otro usuario si se pasa 'id' (Solo el admin puede ver el de otros Usuarios)).
    id = int(request.GET.get('id', 1)) if request.GET.get('id') else usuario.id
    usuario_perfil = get_object_or_404(Usuario, pk=id)
    
    # Restricción: Una persona que no sea admin no puede ver el perfil de un admin.
    if (usuario_perfil.rol or '').lower() == 'admin' and (usuario.rol or '').lower() != 'admin':
        return redir(request, r=6)
    
    # Obtiene el último inicio de sesión.
    lastlog = HistorialAcciones.objects.filter(usuario=usuario_perfil, accion='Sesión iniciada').order_by('-fechacreacion').first()
    perfilself = (usuario.id == usuario_perfil.id) # Indica si se ve el propio perfil.
    # Obtiene las últimas 10 acciones registradas para el usuario.
    lastactions = HistorialAcciones.objects.filter(usuario=usuario_perfil).order_by('-fechacreacion')[:10]

    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r, 'usuario_perfil': usuario_perfil, 'lastlog': lastlog, 'perfilself': perfilself, 'lastactions': lastactions}
    return render(request, 'perfil.html', datos)


def editarperfil(request):
    # Vista para el formulario de edición del perfil.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    id = int(request.GET.get('id', 1)) if request.GET.get('id') else usuario.id
    usuario_perfil = get_object_or_404(Usuario, pk=id)
    perfilself = (usuario.id == usuario_perfil.id)

    # Restricción: Solo el propio usuario puede editar su perfil. (Un admin puede editar el perfil de otros usuarios)
    if usuario.id != usuario_perfil.id and (usuario.rol or '').lower() != 'admin':
        return redir(request, r=5) # Mensaje de acceso denegado.

    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r, 'usuario_perfil': usuario_perfil, 'perfilself': perfilself}
    return render(request, 'editarperfil.html', datos)


def editarperfil_send(request, id):
    # Maneja el POST para la edición de perfil.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    usuario_perfil = get_object_or_404(Usuario, pk=id)

    if usuario.id != usuario_perfil.id and (usuario.rol or '').lower() != 'admin':
        return redir(request, r=5)

    # Copia el objeto antes de actualizar para comparar los cambios.
    old_usuario_perfil = get_object_or_404(Usuario, pk=id) 

    # Actualiza los campos de texto.
    usuario_perfil.nombre = request.POST['txtnom']
    usuario_perfil.apellido = request.POST['txtape']
    usuario_perfil.correo = request.POST['txtcor']
    usuario_perfil.bio = request.POST['txtbio']
    usuario_perfil.telefono = request.POST['txttel']

    # Logica para el cambio de contraseña.
    if (usuario.rol or '').lower() == 'admin' and usuario.id != usuario_perfil.id:
        # Admin editando a otro: cambia la contraseña si se proporciona una (en txtpassold).
        if request.POST['txtpassold'] != '': usuario_perfil.contraseña = hashlib.md5(request.POST['txtpassold'].encode('utf-8')).hexdigest()
    else:
        # Usuario editandose a si mismo: requiere contraseña antigua correcta.
        if usuario_perfil.contraseña == hashlib.md5(request.POST['txtpassold'].encode('utf-8')).hexdigest():
            # Validación de contraseñas nuevas (no vacias, coinciden).
            if request.POST['txtpass1'] == '' or request.POST['txtpass2'] == '':
                request.session['r'] = 13
                return redirect(f'/editarperfil/?id={usuario_perfil.id}')
            if request.POST['txtpass1'] != request.POST['txtpass2']:
                request.session['r'] = 14
                return redirect(f'/editarperfil/?id={usuario_perfil.id}')
            else:
                usuario_perfil.contraseña = hashlib.md5(request.POST['txtpass1'].encode('utf-8')).hexdigest()
        elif request.POST['txtpassold'] != '':
            # Contraseña antigua incorrecta.
            request.session['r'] = 12
            return redirect(request.session.get('lasturl'))

    # El administrador puede cambiar el rol y el estado.
    if (usuario.rol or '').lower() == 'admin':
        rol_post = request.POST.get('cborol')
        if rol_post:
            usuario_perfil.rol = rol_post
        estado_post = request.POST.get('cboest')
        if estado_post is not None and estado_post != '':
            usuario_perfil.estado = estado_post
    
    # Compara el objeto anterior y el actual para registrar los cambios.
    cambios = {}
    for field in usuario_perfil._meta.fields:
        fieldname = field.name
        old_value = getattr(old_usuario_perfil, fieldname)
        new_value = getattr(usuario_perfil, fieldname)
        if old_value != new_value:
            cambios[fieldname] = {'old': old_value, 'new': new_value}
    
    usuario_perfil.save() # Guarda el usuario actualizado.
    
    # Registra el historial de acciones y el detalle de los cambios.
    HistorialAcciones.objects.create(usuario=usuario, cambios=cambios,)
    h = HistorialAcciones.objects.filter().order_by('-id').first()
    h.accion=f'Perfil editado. <a href="/perfil/?id={usuario_perfil.id}">id: {usuario_perfil.id}</a> - <a href="/logcambios/?id={h.id}">[ Ver cambios ]</a>'
    h.save()
    
    request.session['r'] = 7 # Mensaje de éxito.
    return redirect(f'/perfil/?id={usuario_perfil.id}')


def adduser(request):
    # Vista para mostrar el formulario de creación de usuario. Solo para admin.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        return redir(request, r=5)
    
    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r}
    return render(request, 'addUser.html', datos)


def adduser_send(request): 
    # Maneja el POST para la creación de usuario. Solo para admin.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        return redir(request, r=5)
    
    has = hashlib.md5(request.POST['txtpass'].encode('utf-8')).hexdigest() # Cifra la contraseña.
    
    # Crea la nueva instancia de Usuario.
    nuevo_usuario = Usuario(
        rut=          request.POST['txtrut'],
        nombre=       request.POST['txtnombre'],
        apellido=     request.POST['txtapellido'],
        telefono=     request.POST['txttelefono'],
        contraseña=   has,
        correo=       request.POST['txtcorreo'],
        rol=          request.POST['cborol'],
    )
    nuevo_usuario.save()

    # Registra la creación del usuario.
    HistorialAcciones.objects.create(
        usuario=usuario, 
        accion=f'Usuario creado. <a href="/perfil/?id={nuevo_usuario.id}">id: {nuevo_usuario.id}</a>'
    )
    request.session['r'] = 11
    return redirect(f'/perfil/?id={nuevo_usuario.id}')


def formulario(request):
    # Vista del formulario de creación de Ficha. Solo para admin/paramedico.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        return redir(request, r=5)
    
    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r}
    return render(request, 'formulario.html', datos)


def formulario_send(request):
    # Maneja el POST para la creación de Ficha.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        return redir(request, r=5)
    
    # Crea la nueva instancia de Ficha con los datos del POST.
    ficha = Fichas(
        nombrepaciente=       request.POST['txtnompa'],
        apellidopaciente=     request.POST['txtapepa'],
        rutpaciente=          request.POST['txtrutpa'],
        rutparamedico=        usuario.rut, # Asigna el RUT del paramédico logueado.
        edad=                 request.POST['txteda'],
        telefono=             request.POST['txttel'],
        genero=               request.POST['cbogen'],
        prevision=            request.POST['cbopre'],
        motivoconsulta=       request.POST['txtmot'],
        comorbilidades=       request.POST['txtcom'],
        alergias=             request.POST['txtale'],
        frecuenciacardiaca=   request.POST['txtfre'],
        temperatura=          request.POST['txttem'],
        presionarterial=      request.POST['txtpre'],
        tiposangre=           request.POST['cbosan'],
        observaciones=        request.POST['txtobs']
    )
    ficha.save()

    # Registra la creación de la ficha.
    HistorialAcciones.objects.create(
        usuario=usuario, 
        accion=f'Ficha insertada. <a href="/ficha/?id={ficha.id}">id: {ficha.id}</a>'
    )
    request.session['r'] = 8
    return redirect(f'/ficha/?id={ficha.id}')


def editarficha(request, self = False):
    # Vista para el formulario de edición de la Ficha.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'coordinador':
        self = True # Si no es admin o coordinador, solo puede editar sus propias fichas.
    
    id = int(request.GET.get('id', 1)) if request.GET.get('id') else 1
    ficha = get_object_or_404(Fichas, pk=id)
    
    # Si está en modo 'self', verifica que el rut del paramédico coincida con el usuario actual.
    if self and ficha.rutparamedico != usuario.rut:
        return redir(request, r=5)
    
    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r, 'ficha': ficha, 'edit': True}
    return render(request, 'formulario.html', datos)


def editarficha_send(request, id):
    # Maneja el POST para la edición de Ficha.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    
    # Permisos de edición.
    if rol != 'admin' and rol != 'coordinador':
        self = True

    ficha = get_object_or_404(Fichas, pk=id)
    if 'self' in locals() and self and ficha.rutparamedico != usuario.rut: # Verifica si 'self' se definió.
        return redir(request, r=5)

    old_ficha = get_object_or_404(Fichas, pk=id) # Objeto anterior para el log de cambios.

    # Actualiza todos los campos de la ficha.
    ficha.nombrepaciente= request.POST['txtnompa']
    ficha.apellidopaciente= request.POST['txtapepa']
    ficha.rutpaciente= request.POST['txtrutpa']
    ficha.edad= request.POST['txteda']
    ficha.telefono= request.POST['txttel']
    ficha.genero= request.POST['cbogen']
    ficha.prevision= request.POST['cbopre']
    ficha.motivoconsulta= request.POST['txtmot']
    ficha.comorbilidades= request.POST['txtcom']
    ficha.alergias= request.POST['txtale']
    ficha.frecuenciacardiaca= request.POST['txtfre']
    ficha.temperatura= request.POST['txttem']
    ficha.presionarterial= request.POST['txtpre']
    ficha.tiposangre= request.POST['cbosan']
    ficha.observaciones= request.POST['txtobs']


    # Compara y registra los cambios.
    cambios = {}
    for field in ficha._meta.fields:
        fieldname = field.name
        old_value = getattr(old_ficha, fieldname)
        new_value = getattr(ficha, fieldname)
        if old_value != new_value:
            cambios[fieldname] = {'old': old_value, 'new': new_value}
    
    ficha.save()
    HistorialAcciones.objects.create(usuario=usuario, cambios=cambios,)
    h = HistorialAcciones.objects.filter().order_by('-id').first()
    h.accion=f'Ficha editada. <a href="/ficha/?id={ficha.id}">id: {ficha.id}</a> - <a href="/logcambios/?id={h.id}">[ Ver cambios ]</a>'
    h.save()
    
    request.session['r'] = 9
    return redirect(f'/ficha/?id={ficha.id}')


def eliminarficha(request, id):
    # Elimina una ficha. Solo para admin.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        return redir(request, r=5)
    
    HistorialAcciones.objects.create(
        usuario=usuario, 
        accion='Ficha eliminada. id: {}'.format(id)
    )

    ficha = get_object_or_404(Fichas, pk=id)
    ficha.delete() # Elimina la Ficha.

    request.session['r'] = 10
    return redirect(request.session.get('lasturl')) # Redirige a la última URL visitada.


def verficha(request):
    # Vista para ver los detalles de una ficha.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    id = int(request.GET.get('id', 1)) if request.GET.get('id') else 1

    ficha = get_object_or_404(Fichas, pk=id)

    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r, 'ficha': ficha}
    return render(request, 'Ficha.html', datos)


def cambioestado(request, id):
    # Cambia el estado 'revisado' de una ficha (True/False). Solo para admin y coordinador.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'coordinador':
        return redir(request, r=5)
    
    ficha = get_object_or_404(Fichas, pk=id)
    ficha.revisado = not ficha.revisado # Invierte el estado.
    ficha.save()

    # Registra la acción del cambio de estado.
    HistorialAcciones.objects.create(
        usuario=usuario, 
        accion=f'Ficha {"marcada como revisada" if ficha.revisado else "marcada como no revisada"}. <a href="/ficha/?id={ficha.id}">id: {ficha.id}</a>'
    )
    return redirect(request.session.get('lasturl'))


def listado(request, self = False):
    # Vista para el listado de fichas con filtros, búsqueda y paginación.
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'coordinador':
        self = True # Restringe a ver solo sus propias fichas.
    
    filter_kwargs = {} # Diccionario para construir los filtros del queryset.

    # Lógica de búsqueda avanzada: 'fs' es el campo, 's' es el valor. ':' indica búsqueda exacta.
    searchfilter = request.GET.get('fs', None) or None
    exact = False
    if searchfilter and searchfilter.startswith(':'):
        searchfilter = searchfilter[1:]
        exact=True
    search = request.GET.get('s', None) or None
    if searchfilter and search:
        filter_kwargs.update({f'{searchfilter}__{"iexact" if exact else "icontains"}': search})
        
    # Filtrar por no revisadas (rv='y' por defecto).
    hidereviewed = request.GET.get('rv', 'y') or 'y'
    if hidereviewed == 'y': 
        filter_kwargs.update({'revisado': False})
        
    # Filtrar solo las fichas del usuario actual si es necesario.
    if self:
        filter_kwargs.update({'rutparamedico': usuario.rut})

    # Lógica de ordenamiento: 'fo' es el campo, 'o' es el orden.
    orderfilter = request.GET.get('fo', 'fechacreacion') or 'fechacreacion'
    order = request.GET.get('o', 'desc') or 'desc'
    if order == 'desc': order = '-' # Prefijo '-' para orden descendente.
    elif order == 'asc': order = '' # Vacío para orden ascendente.
    else: order = '-'
        
    # Lógica de paginación.
    page = int(request.GET.get('page', 1)) or 1
    pagesize = 10
    # Aplica filtros y ordenamiento.
    fulllist = Fichas.objects.all().filter(**filter_kwargs).order_by(f'{order}{orderfilter}')
    # Calcula el número total de páginas.
    totalpages = (fulllist.count() // pagesize) + (1 if fulllist.count() % pagesize > 0 else 0)
    
    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r,
        'fichas': fulllist[ (page-1)*pagesize : page*pagesize ], # Slice el queryset para la página actual.
        'page': page,
        'totalpages': totalpages,
        'totalresults': fulllist.count(),
        'self': self
    }
    return render(request, 'Listado.html', datos)


def log(request):
    # Vista para el listado del historial de acciones (log). Solo para admin.
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        return redir(request, r=5)
    
    filter_kwargs = {}

    # Lógica de búsqueda y ordenamiento (similar a listado).
    searchfilter = request.GET.get('fs', None) or None
    exact = False
    if searchfilter and searchfilter.startswith(':'):
        searchfilter = searchfilter[1:]
        exact=True
    search = request.GET.get('s', None) or None
    if searchfilter and search:
        filter_kwargs.update({f'{searchfilter}__{"iexact" if exact else "icontains"}': search})

    orderfilter = request.GET.get('fo', 'fechacreacion') or 'fechacreacion'
    order = request.GET.get('o', 'desc') or 'desc'
    if order == 'desc': order = '-'
    elif order == 'asc': order = ''
    else: order = '-'

    # Lógica de paginación.
    page = int(request.GET.get('page', 1)) or 1
    pagesize = 15
    
    # Obtiene el historial con filtros y ordenamiento.
    fulllog = HistorialAcciones.objects.all().filter(**filter_kwargs).order_by(f'{order}{orderfilter}')
    totalpages = (fulllog.count() // pagesize) + (1 if fulllog.count() % pagesize > 0 else 0)

    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = { 'usuario': usuario, 'r': r,
        'log': fulllog[ (page-1)*pagesize : page*pagesize ],
        'page': page,
        'totalpages': totalpages,
        'totalresults': fulllog.count(),
    }
    return render(request, 'log.html', datos)


def logcambios(request):
    # Vista para ver el detalle de los cambios registrados en una entrada de HistorialAcciones. Solo para admin.
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    if usuario.rol != 'admin':
        return redir(request, r=5)
    
    id = int(request.GET.get('id', 1)) if request.GET.get('id') else 1
    entry = HistorialAcciones.objects.get(pk=id) # Obtiene la entrada específica del log.
    

    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r, 'entry': entry}
    return render(request, 'Logcambios.html', datos)