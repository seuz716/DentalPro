"""
Comando de gestión para administrar credenciales WebAuthn.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import WebAuthnCredential, WebAuthnChallenge
from datetime import timedelta


class Command(BaseCommand):
    help = 'Gestiona credenciales y desafíos WebAuthn'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            dest='subcommand',
            help='Subcomandos disponibles'
        )

        # Listar credenciales
        list_parser = subparsers.add_parser(
            'list',
            help='Listar credenciales WebAuthn'
        )
        list_parser.add_argument(
            '--user',
            help='Filtrar por nombre de usuario'
        )
        list_parser.add_argument(
            '--active',
            action='store_true',
            help='Mostrar solo credenciales activas'
        )

        # Desactivar credencial
        disable_parser = subparsers.add_parser(
            'disable',
            help='Desactivar una credencial'
        )
        disable_parser.add_argument(
            'credential_id',
            help='ID de la credencial a desactivar'
        )

        # Limpiar desafíos expirados
        clean_parser = subparsers.add_parser(
            'clean-challenges',
            help='Limpiar desafíos expirados'
        )

        # Información de usuario
        info_parser = subparsers.add_parser(
            'user-info',
            help='Mostrar información de credenciales de un usuario'
        )
        info_parser.add_argument(
            'username',
            help='Nombre de usuario'
        )

        # Estadísticas
        stats_parser = subparsers.add_parser(
            'stats',
            help='Mostrar estadísticas de WebAuthn'
        )

    def handle(self, *args, **options):
        subcommand = options.get('subcommand')

        if subcommand == 'list':
            self.handle_list(options)
        elif subcommand == 'disable':
            self.handle_disable(options)
        elif subcommand == 'clean-challenges':
            self.handle_clean_challenges(options)
        elif subcommand == 'user-info':
            self.handle_user_info(options)
        elif subcommand == 'stats':
            self.handle_stats(options)
        else:
            self.stdout.write(self.style.ERROR('Especifica un subcomando'))

    def print_table(self, headers, rows):
        """Imprime una tabla simple."""
        # Calcular ancho de columnas
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Imprimir encabezado
        header_line = ' │ '.join(
            h.ljust(col_widths[i]) for i, h in enumerate(headers)
        )
        self.stdout.write(header_line)
        self.stdout.write('─' * len(header_line))

        # Imprimir filas
        for row in rows:
            row_line = ' │ '.join(
                str(cell).ljust(col_widths[i])
                for i, cell in enumerate(row)
            )
            self.stdout.write(row_line)

    def handle_list(self, options):
        """Listar credenciales."""
        queryset = WebAuthnCredential.objects.all()

        if options.get('user'):
            queryset = queryset.filter(user__username=options['user'])

        if options.get('active'):
            queryset = queryset.filter(is_active=True)

        if not queryset.exists():
            self.stdout.write(self.style.WARNING('No hay credenciales'))
            return

        headers = ['Usuario', 'Dispositivo', 'Activa', 'Sign Count', 'Creada', 'Última vez']
        rows = []
        for cred in queryset:
            rows.append([
                cred.user.username,
                cred.name or 'Sin nombre',
                '✓' if cred.is_active else '✗',
                cred.sign_count,
                cred.created_at.strftime('%Y-%m-%d %H:%M'),
                cred.last_used_at.strftime('%Y-%m-%d %H:%M') if cred.last_used_at else '-',
            ])

        self.stdout.write('')
        self.print_table(headers, rows)
        self.stdout.write('')

    def handle_disable(self, options):
        """Desactivar una credencial."""
        credential_id = options['credential_id']

        try:
            cred = WebAuthnCredential.objects.get(credential_id=credential_id)
        except WebAuthnCredential.DoesNotExist:
            raise CommandError(f'Credencial no encontrada: {credential_id}')

        cred.is_active = False
        cred.save()

        self.stdout.write(self.style.SUCCESS(
            f'✓ Credencial desactivada: {cred.name} ({cred.user.username})'
        ))

    def handle_clean_challenges(self, options):
        """Limpiar desafíos expirados."""
        expired = WebAuthnChallenge.objects.filter(
            expires_at__lt=timezone.now()
        )
        count = expired.count()
        expired.delete()

        self.stdout.write(self.style.SUCCESS(
            f'✓ {count} desafío(s) expirado(s) eliminado(s)'
        ))

    def handle_user_info(self, options):
        """Mostrar información de credenciales de un usuario."""
        username = options['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Usuario no encontrado: {username}')

        self.stdout.write(self.style.SUCCESS(f'\n=== Usuario: {user.username} ==='))
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Nombre completo: {user.first_name} {user.last_name}')

        credentials = user.webauthn_credentials.all()
        if not credentials.exists():
            self.stdout.write(self.style.WARNING('\nNo hay credenciales registradas'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n=== Credenciales ({credentials.count()}) ==='))

        headers = ['Dispositivo', 'Activa', 'Sign Count', 'Creada', 'Última vez', 'AAGUID']
        rows = []
        for cred in credentials:
            rows.append([
                cred.name or 'Sin nombre',
                '✓' if cred.is_active else '✗',
                cred.sign_count,
                cred.created_at.strftime('%Y-%m-%d %H:%M'),
                cred.last_used_at.strftime('%Y-%m-%d %H:%M') if cred.last_used_at else 'Nunca',
                cred.aaguid or 'N/A',
            ])

        self.print_table(headers, rows)

        # Desafíos activos del usuario
        challenges = WebAuthnChallenge.objects.filter(
            user=user,
            is_used=False,
            expires_at__gt=timezone.now()
        )
        if challenges.exists():
            self.stdout.write(self.style.WARNING(f'\n⚠ {challenges.count()} desafío(s) pendiente(s)'))

    def handle_stats(self, options):
        """Mostrar estadísticas de WebAuthn."""
        total_users_with_creds = User.objects.filter(
            webauthn_credentials__isnull=False
        ).distinct().count()

        total_creds = WebAuthnCredential.objects.count()
        active_creds = WebAuthnCredential.objects.filter(is_active=True).count()

        pending_challenges = WebAuthnChallenge.objects.filter(
            is_used=False,
            expires_at__gt=timezone.now()
        ).count()

        expired_challenges = WebAuthnChallenge.objects.filter(
            expires_at__lt=timezone.now()
        ).count()

        self.stdout.write(self.style.SUCCESS('\n=== Estadísticas WebAuthn ==='))
        self.stdout.write(f'Usuarios con credenciales: {total_users_with_creds}')
        self.stdout.write(f'Total de credenciales: {total_creds}')
        self.stdout.write(f'  - Activas: {active_creds}')
        self.stdout.write(f'  - Inactivas: {total_creds - active_creds}')
        self.stdout.write(f'\nDesafíos pendientes: {pending_challenges}')
        self.stdout.write(f'Desafíos expirados: {expired_challenges}')

        # Dispositivos más usados
        from django.db.models import Count
        devices = WebAuthnCredential.objects.filter(
            name__isnull=False
        ).values('name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        if devices:
            self.stdout.write(self.style.SUCCESS('\n=== Dispositivos Top 5 ==='))
            for device in devices:
                self.stdout.write(f'{device["name"]}: {device["count"]}')
