from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import redirect

from ficha.models import HistorialAcciones, Usuario
from ficha.models import Fichas
import hashlib

responselist = [
    { 'type' : 'error', 'message' : 'Ha ocurrido un error inesperado.' },
    { 'type' : 'error', 'message' : 'Debe iniciar sesion.' },
    { 'type' : 'error', 'message' : 'Error en el usuario y/o contraseña.' },
    { 'type' : 'error', 'message' : 'Esta cuenta esta inhabilitada. Porfavor contactese con un administrador.' },
    { 'type' : 'success', 'message' : 'Sesion cerrada correctamente.' },
    { 'type' : 'error', 'message' : 'No autorizado para realizar esta accion.' },
    { 'type' : 'error', 'message' : 'No autorizado para ver este perfil.' },
    { 'type' : 'success', 'message' : 'Perfil actualizado correctamente.' },
    { 'type' : 'success', 'message' : 'Ficha creada correctamente.' },
    { 'type' : 'success', 'message' : 'Ficha actualizada correctamente.' },
    { 'type' : 'success', 'message' : 'Ficha eliminada correctamente.' }
]

def redir(request):
    r = request.GET.get('r')
    if request.session.get('userid'):
        return redirect(f'/menu/?r={r }') if r else redirect('/menu/')
    else:
        return redirect('/login/')

def menu(request):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para ingresar al formulario'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    if not usuario.estado:
        cerrarSesion(request, disabled=True)

    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None
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
            return redirect('/login/?r=2')
        
        if not usuario.estado:
            return redirect('/login/?r=3')
        
        request.session['userid'] = usuario.id
        return redirect('menu')
    else:
        return render(request, 'login.html' , {'r': r} )


def cerrarSesion(request, disabled=False):
    if not request.session.get('userid'):
        return redirect('/')
    
    HistorialAcciones.objects.create(
        usuario_id=request.session.get('userid'),
        accion='Sesión cerrada'
    )
    request.session.pop('userid', None)
    request.session.flush()

    if disabled == True: return redirect('/login/?r=3')
    else:return redirect('/login/?r=4')




def perfil(request, id):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    usuario_perfil = get_object_or_404(Usuario, pk=id)
    if usuario.id != usuario_perfil.id and (usuario.rol or '').lower() != 'admin':
        return redirect('/?r=6')

    lastlog = HistorialAcciones.objects.filter(usuario=usuario_perfil, accion='Sesión iniciada').order_by('-fechacreacion').first()
    lastactions = HistorialAcciones.objects.filter(usuario=usuario_perfil).order_by('-fechacreacion')[:10]

    perfilself = (usuario.id == usuario_perfil.id)

    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None
    datos = {'usuario': usuario, 'r': r, 'usuario_perfil': usuario_perfil, 'lastlog': lastlog, 'perfilself': perfilself, 'lastactions': lastactions}
    return render(request, 'perfil.html', datos)


def editarperfil(request, id):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    usuario_perfil = get_object_or_404(Usuario, pk=id)

    if usuario.id != usuario_perfil.id and (usuario.rol or '').lower() != 'admin':
        return redirect('/?r=5')

    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None
    datos = {'usuario': usuario, 'r': r, 'usuario_perfil': usuario_perfil}
    return render(request, 'editarperfil.html', datos)


def editarperfil_send(request, id):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    usuario_perfil = get_object_or_404(Usuario, pk=id)

    if usuario.id != usuario_perfil.id and (usuario.rol or '').lower() != 'admin':
        return redirect('/?r=5')

    usuario_perfil.nombre =     request.POST['txtnom']
    usuario_perfil.apellido =   request.POST['txtape']
    usuario_perfil.correo =      request.POST['txtcor']
    usuario_perfil.telefono =   request.POST['txttel']
    if (usuario.rol or '').lower() == 'admin':
        rol_post = request.POST.get('cborol')
        if rol_post:
            usuario_perfil.rol = rol_post
        estado_post = request.POST.get('cboest')
        if estado_post is not None and estado_post != '':
            usuario_perfil.estado = estado_post
    usuario_perfil.save()

    HistorialAcciones.objects.create(
                usuario=usuario, 
                accion='Perfil editado. id: {}'.format(usuario_perfil.id)
    )
    return redirect(f'/perfil/{usuario_perfil.id}/?r=7')






def formulario(request):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        return redirect('/?r=5')

    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None
    datos = {'usuario': usuario, 'r': r}
    return render(request, 'formulario.html', datos)


def formulario_send(request):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        return redirect('/?r=5')

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
                accion='Ficha insertada. id: <a href="/verficha/{}">{}</a>'.format(ficha.id, ficha.id)
    )

    return redirect(f'/verficha/{ficha.id}/?r=8')


def editarficha(request, id):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        return redirect('/?r=5')

    ficha = get_object_or_404(Fichas, pk=id)
    
    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None
    datos = {'usuario': usuario, 'r': r, 'ficha': ficha, 'edit': True}
    return render(request, 'formulario.html', datos)


def editarficha_send(request, id):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        return redirect('/?r=5')

    ficha = get_object_or_404(Fichas, pk=id)

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

    ficha.save()

    HistorialAcciones.objects.create(
                usuario=usuario, 
                accion='Ficha editada. id: {}'.format(ficha.id)
    )

    return redirect(f'/verficha/{ficha.id}/?r=9')


def eliminarficha(request, id):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        return redirect('/?r=5')
    
    HistorialAcciones.objects.create(
                usuario=usuario, 
                accion='Ficha eliminada. id: {}'.format(id)
    )

    ficha = get_object_or_404(Fichas, pk=id)
    ficha.delete()

    return redirect('listado/?r=10')


def verficha(request, id):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para ver una ficha'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)

    ficha = get_object_or_404(Fichas, pk=id)

    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None
    datos = {'usuario': usuario, 'r': r, 'ficha': ficha}
    return render(request, 'Ficha.html', datos)




def listado(request):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'coordinador' and rol != 'paramedico':
        return redirect('/?r=5')

    fichas = Fichas.objects.all().filter().filter().order_by('-fechacreacion')
    
    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None
    datos = {'usuario': usuario, 'r': r, 'fichas': fichas}
    return render(request, 'Listado.html', datos)


def log(request):
    userid = request.session.get('userid')
    if not userid:
        return redirect('/login/?r=1')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        return redirect('/?r=5')

    log = HistorialAcciones.objects.all().filter().order_by('-fechacreacion')

    r = responselist[ int(request.GET.get('r'))] if request.GET.get('r') else None
    datos = {'usuario': usuario, 'r': r, 'log': log}
    return render(request, 'log.html', datos)








