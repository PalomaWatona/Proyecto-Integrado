from django.core.management.base import BaseCommand
from ficha.models import Fichas, Usuario, HistorialAcciones
from django.core.management import call_command
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Resets the database by deleting all records from Fichas, Usuario, and HistorialAcciones models.'

    def handle(self, *args, **kwargs):

        confirmation = input("Are you sure you want to reset the database?\nThis will delete all data.\n\nType 'yes' to confirm: ")
        if confirmation.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Database reset cancelled.'))
            return

        call_command('flush', '--noinput')
        call_command('makemigrations')
        call_command('migrate')

        User.objects.filter(is_superuser=True).delete()
        User.objects.create_superuser('admin', 'admin@hospitalrancagua.cl', '123')

        #creates a new admin
        Usuario.objects.create(
            rut='00.000.000-0',
            nombre='Victor',
            apellido='Ulloa',
            telefono='958224812',
            correo='admin@hospitalrancagua.cl',
            bio='Superuser account',
            contraseña='202cb962ac59075b964b07152d234b70',
            rol='admin',
            estado=True
        )

        Usuario.objects.create(
            rut='11.111.111-1',
            nombre='Juan',
            apellido='Luis',
            telefono='977727773',
            correo='v.u@hospitalrancagua.cl',
            bio='Hola que tal chavalez',
            contraseña='202cb962ac59075b964b07152d234b70',
            rol='paramedico',
            estado=True
        )

        Usuario.objects.create(
            rut='22.222.222-2',
            nombre='Jorge',
            apellido='Guzman',
            telefono='912857206',
            correo='j.g@hospitalrancagua.cl',
            bio='Yyyy muy bien!',
            contraseña='202cb962ac59075b964b07152d234b70',
            rol='coordinador',
            estado=True
        )

        self.stdout.write(self.style.SUCCESS('Database has been reset successfully.'))