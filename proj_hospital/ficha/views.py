from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.utils.timezone import localdate
from ficha.models import HistorialAcciones, Usuario
from ficha.models import Fichas
import os, json, hashlib

with open(os.path.join(settings.BASE_DIR, 'ficha', 'static', 'json', 'responses.json'), 'r', encoding='utf-8') as f:
    responselist = json.load(f)





def getstatus(request):
    if request.session.get('r'):
        r = responselist[ int(request.session.get('r')) ] if request.session.get('r') else None
        request.session.pop('r')
    else:
        r = None
    return r




def redir(request, r=None):
    userid = request.session.get('userid')
    if userid:
        try:
            get_object_or_404(Usuario, pk=userid)
        except:
            request.session.pop('userid', None)
            request.session.flush()
            request.session['r'] = 1
            return redirect('/login/')
        if r is not None: request.session['r'] = r
        return redirect('/menu/')

    else:
        request.session['r'] = 1
        return redirect('/login/')


def menu(request):
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    if not usuario.estado:
        cerrarSesion(request, disabled=True)
    
    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r}
    return render(request, 'menu.html', datos)
    

def iniciarSesion(request):
    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None
    if request.method == 'POST':
        rut = request.POST['rut']
        con = request.POST['password']
        has = hashlib.md5(con.encode('utf-8')).hexdigest()
        try:
            usuario = Usuario.objects.get(rut=rut, contraseña=has)
            HistorialAcciones.objects.create(
                usuario=usuario, 
                accion='Sesión iniciada'
            )
        except Usuario.DoesNotExist:
            request.session['r'] = 2
            return redirect('/login/')
        
        if not usuario.estado:
            request.session['r'] = 3
            return redirect('/login/')
        
        request.session['userid'] = usuario.id
        return redirect('menu')
    else:
        r = getstatus(request)
        request.session['lasturl'] = request.get_full_path()
        return render(request, 'login.html' , {'r': r} )


def cerrarSesion(request, disabled=False):
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    
    HistorialAcciones.objects.create(
        usuario_id=request.session.get('userid'),
        accion='Sesión cerrada'
    )
    request.session.pop('userid', None)
    request.session.flush()

    if disabled == True: request.session['r'] = 3
    else: request.session['r'] = 4
    return redirect('/login/')




def perfil(request):
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    id = int(request.GET.get('id', 1)) if request.GET.get('id') else usuario.id
    usuario_perfil = get_object_or_404(Usuario, pk=id)
    if (usuario_perfil.rol or '').lower() == 'admin' and (usuario.rol or '').lower() != 'admin':
        return redir(request, r=6)
    
    lastlog = HistorialAcciones.objects.filter(usuario=usuario_perfil, accion='Sesión iniciada').order_by('-fechacreacion').first()
    perfilself = (usuario.id == usuario_perfil.id)
    lastactions = HistorialAcciones.objects.filter(usuario=usuario_perfil).order_by('-fechacreacion')[:10]

    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r, 'usuario_perfil': usuario_perfil, 'lastlog': lastlog, 'perfilself': perfilself, 'lastactions': lastactions}
    return render(request, 'perfil.html', datos)


def editarperfil(request):
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    id = int(request.GET.get('id', 1)) if request.GET.get('id') else usuario.id
    usuario_perfil = get_object_or_404(Usuario, pk=id)
    perfilself = (usuario.id == usuario_perfil.id)

    if usuario.id != usuario_perfil.id and (usuario.rol or '').lower() != 'admin':
        return redir(request, r=5)

    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r, 'usuario_perfil': usuario_perfil, 'perfilself': perfilself}
    return render(request, 'editarperfil.html', datos)


def editarperfil_send(request, id):
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    usuario_perfil = get_object_or_404(Usuario, pk=id)

    if usuario.id != usuario_perfil.id and (usuario.rol or '').lower() != 'admin':
        return redir(request, r=5)

    usuario_perfil.nombre =     request.POST['txtnom']
    usuario_perfil.apellido =   request.POST['txtape']
    usuario_perfil.correo =      request.POST['txtcor']
    usuario_perfil.bio =         request.POST['txtbio']
    usuario_perfil.telefono =   request.POST['txttel']

    if usuario.rol == 'admin' and usuario.id != usuario_perfil.id:
        if request.POST['txtpassold'] != '': usuario_perfil.contraseña = hashlib.md5(request.POST['txtpassold'].encode('utf-8')).hexdigest()
    else:
        if usuario_perfil.contraseña == hashlib.md5(request.POST['txtpassold'].encode('utf-8')).hexdigest():
            if request.POST['txtpass1'] == '' or request.POST['txtpass2'] == '':
                request.session['r'] = 13
                return redirect(f'/editarperfil/?id={usuario_perfil.id}')
            if request.POST['txtpass1'] != request.POST['txtpass2']:
                request.session['r'] = 14
                return redirect(f'/editarperfil/?id={usuario_perfil.id}')
            else:
                usuario_perfil.contraseña = hashlib.md5(request.POST['txtpass1'].encode('utf-8')).hexdigest()
        elif request.POST['txtpassold'] != '':
            request.session['r'] = 12
            return redirect(request.session.get('lasturl'))

    if (usuario.rol or '').lower() == 'admin':
        rol_post = request.POST.get('cborol')
        if rol_post:
            usuario_perfil.rol = rol_post
        estado_post = request.POST.get('cboest')
        if estado_post is not None and estado_post != '':
            usuario_perfil.estado = estado_post
    
    cambios = {}
    old_usuario_perfil = get_object_or_404(Usuario, pk=id)
    for field in usuario_perfil._meta.fields:
        fieldname = field.name
        old_value = getattr(old_usuario_perfil, fieldname)
        new_value = getattr(usuario_perfil, fieldname)
        if old_value != new_value:
            cambios[fieldname] = {'old': old_value, 'new': new_value}
    print(cambios)
    usuario_perfil.save()
    HistorialAcciones.objects.create(usuario=usuario, cambios=cambios,)
    h = HistorialAcciones.objects.filter().order_by('-id').first()
    h.accion=f'Perfil editado. <a href="/perfil/?id={usuario_perfil.id}">id: {usuario_perfil.id}</a> - <a href="/logcambios/?id={h.id}">[ Ver cambios ]</a>'
    h.save()
    

    
    
    request.session['r'] = 7
    return redirect(f'/perfil/?id={usuario_perfil.id}')


def adduser(request):
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
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        return redir(request, r=5)
    
    has = hashlib.md5(request.POST['txtpass'].encode('utf-8')).hexdigest()
    nuevo_usuario = Usuario(
        rut=        request.POST['txtrut'],
        nombre=     request.POST['txtnombre'],
        apellido=   request.POST['txtapellido'],
        telefono=   request.POST['txttelefono'],
        contraseña= has,
        correo=     request.POST['txtcorreo'],
        rol=        request.POST['cborol'],
    )
    nuevo_usuario.save()

    HistorialAcciones.objects.create(
                usuario=usuario, 
                accion=f'Usuario creado. <a href="/perfil/?id={nuevo_usuario.id}">id: {nuevo_usuario.id}</a>'
    )
    request.session['r'] = 11
    return redirect(f'/perfil/?id={nuevo_usuario.id}')




def formulario(request):
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
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        return redir(request, r=5)
    
    ficha = Fichas(
        nombrepaciente=     request.POST['txtnompa'],
        apellidopaciente=   request.POST['txtapepa'],
        rutpaciente=        request.POST['txtrutpa'],
        rutparamedico=      usuario.rut,
        edad=               request.POST['txteda'],
        telefono=           request.POST['txttel'],
        genero=             request.POST['cbogen'],
        prevision=          request.POST['cbopre'],
        motivoconsulta=     request.POST['txtmot'],
        comorbilidades=     request.POST['txtcom'],
        alergias=           request.POST['txtale'],
        frecuenciacardiaca= request.POST['txtfre'],
        temperatura=        request.POST['txttem'],
        presionarterial=    request.POST['txtpre'],
        tiposangre=         request.POST['cbosan'],
        observaciones=      request.POST['txtobs']
    )
    ficha.save()

    HistorialAcciones.objects.create(
                usuario=usuario, 
                accion=f'Ficha insertada. <a href="/ficha/?id={ficha.id}">id: {ficha.id}</a>'
    )
    request.session['r'] = 8
    return redirect(f'/ficha/?id={ficha.id}')


def editarficha(request, self = False):
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'coordinador':
        self = True
    
    id = int(request.GET.get('id', 1)) if request.GET.get('id') else 1
    ficha = get_object_or_404(Fichas, pk=id)
    if self and ficha.rutparamedico != usuario.rut:
        return redir(request, r=5)
    
    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r, 'ficha': ficha, 'edit': True}
    return render(request, 'formulario.html', datos)


def editarficha_send(request, id):
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'coordinador':
        self = True

    ficha = get_object_or_404(Fichas, pk=id)
    if self and ficha.rutparamedico != usuario.rut:
        return redir(request, r=5)

    ficha.nombrepaciente=     request.POST['txtnompa']
    ficha.apellidopaciente=   request.POST['txtapepa']
    ficha.rutpaciente=        request.POST['txtrutpa']
    ficha.edad=               request.POST['txteda']
    ficha.telefono=           request.POST['txttel']
    ficha.genero=             request.POST['cbogen']
    ficha.prevision=          request.POST['cbopre']
    ficha.motivoconsulta=     request.POST['txtmot']
    ficha.comorbilidades=     request.POST['txtcom']
    ficha.alergias=           request.POST['txtale']
    ficha.frecuenciacardiaca= request.POST['txtfre']
    ficha.temperatura=        request.POST['txttem']
    ficha.presionarterial=    request.POST['txtpre']
    ficha.tiposangre=         request.POST['cbosan']
    ficha.observaciones=      request.POST['txtobs']


    cambios = {}
    old_ficha = get_object_or_404(Fichas, pk=id)
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
    ficha.delete()

    request.session['r'] = 10
    return redirect(request.session.get('lasturl'))





def verficha(request):
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
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'coordinador':
        return redir(request, r=5)
    
    ficha = get_object_or_404(Fichas, pk=id)
    ficha.revisado = not ficha.revisado
    ficha.save()

    HistorialAcciones.objects.create(
                usuario=usuario, 
                accion=f'Ficha {"marcada como revisada" if ficha.revisado else "marcada como no revisada"}. <a href="/ficha/?id={ficha.id}">id: {ficha.id}</a>'
    )
    return redirect(request.session.get('lasturl'))


def listado(request, self = False):
    userid = request.session.get('userid')
    if not userid:
        return redir(request)
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'coordinador':
        self = True
    
    filter_kwargs = {}

    searchfilter = request.GET.get('fs', None) or None
    exact = False
    if searchfilter and searchfilter.startswith(':'):
        searchfilter = searchfilter[1:]
        exact=True
    search = request.GET.get('s', None) or None
    filter_kwargs.update({f'{searchfilter}__{"iexact" if exact else "icontains"}': search}) if searchfilter and search else None
    hidereviewed = request.GET.get('rv', 'y') or 'y'
    if hidereviewed == 'y': filter_kwargs.update({'revisado': False})
    if self:
        filter_kwargs.update({'rutparamedico': usuario.rut})

    orderfilter = request.GET.get('fo', 'fechacreacion') or 'fechacreacion'
    order = request.GET.get('o', 'desc') or 'desc'
    if order == 'desc': order = '-'
    elif order == 'asc': order = ''
    else: order = '-'
        
    page = int(request.GET.get('page', 1)) or 1
    pagesize = 10
    fulllist = Fichas.objects.all().filter(**filter_kwargs).order_by(f'{order}{orderfilter}')
    totalpages = (fulllist.count() // pagesize) + (1 if Fichas.objects.count() % pagesize > 0 else 0)
    
    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r,
        'fichas': fulllist[ (page-1)*pagesize : page*pagesize ],
        'page': page,
        'totalpages': totalpages,
        'totalresults': fulllist.count(),
        'self': self
    }
    return render(request, 'Listado.html', datos)


def log(request):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        return redir(request, r=5)
    
    filter_kwargs = {}

    searchfilter = request.GET.get('fs', None) or None
    exact = False
    if searchfilter and searchfilter.startswith(':'):
        searchfilter = searchfilter[1:]
        exact=True
    search = request.GET.get('s', None) or None
    filter_kwargs.update({f'{searchfilter}__{"iexact" if exact else "icontains"}': search}) if searchfilter and search else None

    orderfilter = request.GET.get('fo', 'fechacreacion') or 'fechacreacion'
    order = request.GET.get('o', 'desc') or 'desc'
    if order == 'desc': order = '-'
    elif order == 'asc': order = ''
    else: order = '-'

    page = int(request.GET.get('page', 1)) or 1
    pagesize = 15
    fulllog = HistorialAcciones.objects.all().filter(**filter_kwargs).order_by(f'{order}{orderfilter}')
    totalpages = (fulllog.count() // pagesize) + (1 if HistorialAcciones.objects.count() % pagesize > 0 else 0)

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
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    if usuario.rol != 'admin':
        return redir(request, r=5)
    
    id = int(request.GET.get('id', 1)) if request.GET.get('id') else 1
    entry = HistorialAcciones.objects.get(pk=id)
    

    r = getstatus(request)
    request.session['lasturl'] = request.get_full_path()
    datos = {'usuario': usuario, 'r': r, 'entry': entry}
    return render(request, 'Logcambios.html', datos)
