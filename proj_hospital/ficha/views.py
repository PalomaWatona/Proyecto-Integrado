from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import redirect

from ficha.models import HistorialAcciones, Usuario
from ficha.models import Fichas
import hashlib



def redir(request):
    if request.session.get('userid'):
        return redirect('menu')
    else:
        return redirect('login')

def menu(request):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para ingresar al formulario'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()

    datos = {'usuario': usuario}
    return render(request, 'menu.html', datos)
    

def iniciarSesion(request):
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
            datos = {'r': 'Error en el usuario y/o contraseña'}
            return render(request, 'login.html', datos)
        request.session['userid'] = usuario.id

        return redirect('menu')
    else:
        return render(request, 'login.html')


def cerrarSesion(request):

    HistorialAcciones.objects.create(
        usuario_id=request.session.get('userid'),
        accion='Sesión cerrada'
    )
    request.session.pop('userid', None)
    request.session.pop('rol', None)
    request.session.flush()

    return redirect('login')




def perfil(request, id):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para ingresar al perfil'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    usuario_perfil = get_object_or_404(Usuario, pk=id)
    lastlog = HistorialAcciones.objects.filter(usuario=usuario_perfil, accion='Sesión iniciada').order_by('-fechacreacion').first()
    lastactions = HistorialAcciones.objects.filter(usuario=usuario_perfil).order_by('-fechacreacion')[:10]

    perfilself = (usuario.id == usuario_perfil.id)

    datos = {'usuario': usuario, 'usuario_perfil': usuario_perfil, 'lastlog': lastlog, 'perfilself': perfilself, 'lastactions': lastactions}
    return render(request, 'perfil.html', datos)

def editarperfil(request, id):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para editar el perfil'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    usuario_perfil = get_object_or_404(Usuario, pk=id)

    if usuario.id != usuario_perfil.id and (usuario.rol or '').lower() != 'admin':
        datos = {'r': 'No autorizado para editar este perfil'}
        return redirect('/')

    datos = {'usuario': usuario, 'usuario_perfil': usuario_perfil}

    return render(request, 'editarperfil.html', datos)

def editarperfil_send(request, id):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para editar el perfil'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    usuario_perfil = get_object_or_404(Usuario, pk=id)

    if usuario.id != usuario_perfil.id and (usuario.rol or '').lower() != 'admin':
        datos = {'r': 'No autorizado para editar este perfil'}
        return redirect('/')

    usuario_perfil.nombre =     request.POST['txtnom']
    usuario_perfil.apellido =   request.POST['txtape']
    usuario_perfil.email =      request.POST['txtcor']
    usuario_perfil.telefono =   request.POST['txttel']
    usuario_perfil.save()

    HistorialAcciones.objects.create(
                usuario=usuario, 
                accion='Perfil editado. id: {}'.format(usuario_perfil.id)
    )
    return redirect('perfil', id=usuario_perfil.id)






def formulario(request):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para ingresar al formulario'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        datos = {'r': 'Rol no autorizado para ingresar al formulario'}
        return redirect('/')

    datos = {'usuario': usuario}
    return render(request, 'formulario.html', datos)

def editarficha(request, id):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para editar una ficha'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        datos = {'r': 'Rol no autorizado para editar una ficha'}
        return redirect('/')

    ficha = get_object_or_404(Fichas, pk=id)
    datos = {'usuario': usuario, 'ficha': ficha, 'edit': True}

    return render(request, 'formulario.html', datos)

def editarficha_send(request, id):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para editar una ficha'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico' and rol != 'coordinador':
        datos = {'r': 'Rol no autorizado para editar una ficha'}
        return redirect('/')
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

    return redirect('verficha', id=ficha.id)

def formulario_send(request):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'login requerido'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        datos = {'r': 'Rol no autorizado para insertar una ficha'}
        return redirect('/')

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

    return redirect('/menu/')

def editarficha_send(request, id):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'login requerido'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'paramedico':
        datos = {'r': 'Rol no autorizado para editar una ficha'}
        return redirect('/')

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

    return redirect('verficha', id=ficha.id)

def eliminarficha(request, id):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para eliminar una ficha'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        datos = {'r': 'Rol no autorizado para eliminar una ficha'}
        return redirect('/')
    
    HistorialAcciones.objects.create(
                usuario=usuario, 
                accion='Ficha eliminada. id: {}'.format(id)
    )

    ficha = get_object_or_404(Fichas, pk=id)
    ficha.delete()

    return redirect('listado')

def verficha(request, id):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para ver una ficha'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)

    ficha = get_object_or_404(Fichas, pk=id)
    datos = {'usuario': usuario, 'ficha': ficha}

    return render(request, 'Ficha.html', datos)




def listado(request):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para ingresar al listado'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin' and rol != 'coordinador' and rol != 'paramedico':
        datos = {'r': 'Rol no autorizado para ingresar al listado'}
        return redirect('/')

    fichas = Fichas.objects.all().filter().filter().order_by('-fechacreacion')
    datos = {'usuario': usuario, 'fichas': fichas}

    return render(request, 'Listado.html', datos)

def log(request):
    userid = request.session.get('userid')
    if not userid:
        datos = {'r': 'Debe iniciar sesión para ingresar al log'}
        return redirect('login')
    usuario = get_object_or_404(Usuario, pk=userid)
    rol = (usuario.rol or '').lower()
    if rol != 'admin':
        datos = {'r': 'Rol no autorizado para ingresar al log'}
        return redirect('/')

    log = HistorialAcciones.objects.all().filter().order_by('-fechacreacion')
    datos = {'usuario': usuario, 'log': log}

    return render(request, 'log.html', datos)
    
    
    
    
    
    
    
    
    