"""
Modelos de la aplicación pacientes.
"""

from datetime import date
from django.db import models
from django.core.exceptions import ValidationError


class Patient(models.Model):
    """
    Modelo de Paciente.
    Contiene información personal y clínica del paciente dental.
    """
    
    # Tipos de documento permitidos
    DOCUMENT_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
    ]
    
    # Género del paciente
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    # Tipo de sangre
    BLOOD_TYPE_CHOICES = [
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    
    # Campos de identificación
    document_type = models.CharField(
        max_length=2,
        choices=DOCUMENT_CHOICES,
        default='CC',
        verbose_name='Tipo de documento'
    )
    document_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name='Número de documento',
        help_text='Debe ser único en el sistema'
    )
    
    # Datos personales
    first_name = models.CharField(
        max_length=50,
        verbose_name='Nombres'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Apellidos'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de nacimiento'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name='Género'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
        verbose_name='Teléfono'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Correo electrónico'
    )
    address = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    
    # Datos clínicos
    blood_type = models.CharField(
        max_length=3,
        choices=BLOOD_TYPE_CHOICES,
        blank=True,
        verbose_name='Tipo de sangre'
    )
    allergies = models.TextField(
        blank=True,
        verbose_name='Alergias',
        help_text='Descripción de alergias conocidas'
    )
    chronic_conditions = models.TextField(
        blank=True,
        verbose_name='Enfermedades crónicas',
        help_text='Enfermedades crónicas o condiciones médicas'
    )
    clinical_notes = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Notas clínicas',
        help_text='Registro de notas clínicas en formato JSON'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        indexes = [
            models.Index(fields=['document_number']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        """Representación en string del paciente."""
        return f"{self.first_name} {self.last_name} ({self.document_number})"
    
    @property
    def age(self):
        """
        Calcula la edad del paciente basada en su fecha de nacimiento.
        
        Returns:
            int: Edad en años.
        """
        today = date.today()
        born = self.birth_date
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    @property
    def full_name(self):
        """Retorna el nombre completo del paciente."""
        return f"{self.first_name} {self.last_name}"
    
    def clean(self):
        """
        Valida los datos del paciente.
        Incluye validación de cédula colombiana para CC.
        """
        errors = {}
        
        # Validar fecha de nacimiento
        if self.birth_date > date.today():
            errors['birth_date'] = 'La fecha de nacimiento no puede ser en el futuro.'
        
        # Validar cédula colombiana si es CC
        if self.document_type == 'CC':
            if not self._validate_cedula_colombiana(self.document_number):
                errors['document_number'] = (
                    'Número de cédula colombiana inválido. '
                    'Verifique el formato y dígito de control.'
                )
        
        if errors:
            raise ValidationError(errors)
    
    @staticmethod
    def _validate_cedula_colombiana(cedula_str):
        """
        Valida formato y dígito de control de cédula colombiana.
        
        Args:
            cedula_str: Cadena con el número de cédula.
        
        Returns:
            bool: True si es válida, False de lo contrario.
        """
        # Remover espacios
        cedula_str = cedula_str.replace(' ', '').strip()
        
        # Validar que solo contenga dígitos
        if not cedula_str.isdigit():
            return False
        
        # Validar longitud (7-10 dígitos)
        if len(cedula_str) < 7 or len(cedula_str) > 10:
            return False
        
        # Validar dígito de control (algoritmo de Luhn modificado)
        cedula_list = [int(d) for d in cedula_str[:-1]]
        dv_esperado = int(cedula_str[-1])
        
        # Multiplicadores
        multiplicadores = [3, 7, 13, 17, 19, 23, 29, 31, 37, 41]
        
        suma = sum(d * m for d, m in zip(cedula_list, multiplicadores[:len(cedula_list)]))
        dv_calculado = suma % 11
        dv_calculado = 11 - dv_calculado if dv_calculado < 11 else 0
        
        return dv_esperado == dv_calculado
