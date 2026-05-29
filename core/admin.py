"""
Configuración de administración para la aplicación core.
"""

from django.contrib import admin
from .models import WebAuthnCredential, WebAuthnChallenge


@admin.register(WebAuthnCredential)
class WebAuthnCredentialAdmin(admin.ModelAdmin):
    """Administrador para credenciales WebAuthn."""
    
    list_display = (
        'user',
        'name',
        'is_active',
        'created_at',
        'last_used_at',
        'sign_count',
    )
    list_filter = (
        'is_active',
        'created_at',
        'last_used_at',
        'aaguid',
    )
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'name',
        'credential_id',
    )
    readonly_fields = (
        'credential_id',
        'public_key',
        'sign_count',
        'created_at',
        'last_used_at',
        'aaguid',
    )
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información de Dispositivo', {
            'fields': ('name', 'transports', 'aaguid')
        }),
        ('Seguridad', {
            'fields': (
                'is_active',
                'sign_count',
                'credential_id',
            ),
            'description': 'El sign_count se incrementa con cada autenticación exitosa para detectar clonación.'
        }),
        ('Datos Técnicos', {
            'fields': ('public_key',),
            'classes': ('collapse',),
            'description': 'Clave pública en formato CBOR/Base64. No modificar.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_used_at'),
            'classes': ('collapse',),
        }),
    )
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """No permitir agregar credenciales desde admin."""
        return False


@admin.register(WebAuthnChallenge)
class WebAuthnChallengeAdmin(admin.ModelAdmin):
    """Administrador para desafíos WebAuthn."""
    
    list_display = (
        'user',
        'challenge_type',
        'is_used',
        'created_at',
        'expires_at',
        'is_expired',
    )
    list_filter = (
        'challenge_type',
        'is_used',
        'created_at',
        'expires_at',
    )
    search_fields = (
        'user__username',
        'challenge',
    )
    readonly_fields = (
        'challenge',
        'created_at',
        'expires_at',
    )
    fieldsets = (
        ('Información', {
            'fields': ('user', 'challenge_type', 'is_used')
        }),
        ('Desafío', {
            'fields': ('challenge',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at'),
        }),
    )
    date_hierarchy = 'created_at'
    actions = ['mark_as_used', 'delete_expired']
    
    def is_expired(self, obj):
        """Muestra si el desafío está expirado."""
        from django.utils import timezone
        from django.utils.html import format_html
        
        if obj.expires_at < timezone.now():
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Expirado</span>'
            )
        return format_html(
            '<span style="color: green; font-weight: bold;">✓ Vigente</span>'
        )
    is_expired.short_description = 'Estado'
    
    def mark_as_used(self, request, queryset):
        """Action para marcar desafíos como usados."""
        updated = queryset.update(is_used=True)
        self.message_user(
            request,
            f'{updated} desafío(s) marcado(s) como usado(s).'
        )
    mark_as_used.short_description = 'Marcar como usado'
    
    def delete_expired(self, request, queryset):
        """Action para eliminar desafíos expirados."""
        from django.utils import timezone
        expired = queryset.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        self.message_user(
            request,
            f'{count} desafío(s) expirado(s) eliminado(s).'
        )
    delete_expired.short_description = 'Eliminar desafíos expirados'
    
    def has_add_permission(self, request):
        """No permitir agregar desafíos desde admin."""
        return False
