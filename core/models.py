"""
Modelos de la aplicación core.
"""

from django.db import models
from django.contrib.auth.models import User
import json


class WebAuthnCredential(models.Model):
    """
    Modelo para almacenar credenciales WebAuthn (FIDO2) de usuarios.
    Cada usuario puede tener múltiples credenciales registradas.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='webauthn_credentials',
        verbose_name='Usuario'
    )
    
    credential_id = models.CharField(
        max_length=1000,
        unique=True,
        verbose_name='ID de Credencial',
        db_index=True
    )
    
    public_key = models.TextField(
        verbose_name='Clave Pública (JSON)',
        help_text='Clave pública en formato JSON codificada'
    )
    
    sign_count = models.IntegerField(
        default=0,
        verbose_name='Contador de Firma',
        help_text='Contador para detectar clonación de autenticadores'
    )
    
    transports = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Transportes',
        help_text='Transportes disponibles: usb, nfc, ble, internal'
    )
    
    aaguid = models.CharField(
        max_length=36,
        blank=True,
        verbose_name='AAGUID',
        help_text='Identificador único del modelo de autenticador'
    )
    
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nombre del Dispositivo',
        help_text='Nombre descriptivo del dispositivo biométrico'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Utilización'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si la credencial está habilitada'
    )
    
    class Meta:
        verbose_name = 'Credencial WebAuthn'
        verbose_name_plural = 'Credenciales WebAuthn'
        ordering = ['-created_at']
        unique_together = [['user', 'credential_id']]
    
    def __str__(self):
        return f"{self.user.username} - {self.name or 'Sin nombre'}"


class WebAuthnChallenge(models.Model):
    """
    Modelo para almacenar desafíos (challenges) temporales de WebAuthn.
    Se utiliza durante el proceso de registro y autenticación.
    """
    
    CHALLENGE_TYPE_CHOICES = [
        ('register', 'Registro'),
        ('authenticate', 'Autenticación'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='webauthn_challenges',
        verbose_name='Usuario'
    )
    
    challenge = models.CharField(
        max_length=1000,
        unique=True,
        verbose_name='Desafío (Challenge)',
        db_index=True
    )
    
    challenge_type = models.CharField(
        max_length=20,
        choices=CHALLENGE_TYPE_CHOICES,
        verbose_name='Tipo de Desafío'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='Fecha de Expiración'
    )
    
    is_used = models.BooleanField(
        default=False,
        verbose_name='Utilizado',
        help_text='Indica si el desafío ya ha sido consumido'
    )
    
    class Meta:
        verbose_name = 'Desafío WebAuthn'
        verbose_name_plural = 'Desafíos WebAuthn'
        ordering = ['-created_at']
    
    def __str__(self):
        username = self.user.username if self.user else 'Anónimo'
        return f"{username} - {self.challenge_type} - {self.created_at}"
