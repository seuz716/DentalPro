"""
Modelos de la aplicación pacientes.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property


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
        verbose_name='Fecha de nacimiento',
        help_text='Rango válido: 1900-2099'
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
        help_text='Registro de notas clínicas. Acepta lista de objetos JSON o texto plano (se convierte automáticamente)'
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
    
    def __str__(self) -> str:
        """Representación en string del paciente."""
        return f"{self.first_name} {self.last_name} ({self.document_number})"
    
    @cached_property
    def age(self) -> Optional[int]:
        """
        Calcula la edad del paciente basada en su fecha de nacimiento.
        El resultado se cachea para evitar cálculos repetidos.
        
        Returns:
            int | None: Edad en años, o None si no hay fecha de nacimiento.
        """
        if not self.birth_date:
            return None
        today = date.today()
        born = self.birth_date
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del paciente."""
        return f"{self.first_name} {self.last_name}"
    
    def clean(self) -> None:
        """
        Valida los datos del paciente.
        Incluye validación de cédula colombiana para CC y límites de fecha de nacimiento.
        """
        errors: Dict[str, str] = {}
        
        # Validar fecha de nacimiento (rango razonable: 1900-2099)
        if self.birth_date:
            if self.birth_date > date.today():
                errors['birth_date'] = 'La fecha de nacimiento no puede ser en el futuro.'
            elif self.birth_date.year < 1900 or self.birth_date.year > 2099:
                errors['birth_date'] = 'La fecha de nacimiento debe estar entre 1900 y 2099.'
            
        # Validar y normalizar notas clínicas (JSON)
        # Acepta: lista de diccionarios, texto plano (lo convierte), o lista vacía
        if self.clinical_notes is None:
            self.clinical_notes = []
        elif isinstance(self.clinical_notes, str):
            # Convertir texto plano a formato JSON estructurado
            if self.clinical_notes.strip():
                self.clinical_notes = [{
                    'nota': self.clinical_notes.strip(),
                    'tipo': 'texto_plano'
                }]
            else:
                self.clinical_notes = []
        elif isinstance(self.clinical_notes, list):
            # Validar que cada elemento sea un diccionario
            for idx, note in enumerate(self.clinical_notes):
                if not isinstance(note, dict):
                    # Si es un string dentro de la lista, lo convertimos
                    if isinstance(note, str):
                        self.clinical_notes[idx] = {
                            'nota': note.strip(),
                            'tipo': 'texto_plano'
                        }
                    else:
                        errors['clinical_notes'] = f'Cada nota clínica debe ser un objeto JSON (diccionario). Elemento {idx} inválido.'
                        break
        else:
            errors['clinical_notes'] = 'Las notas clínicas deben tener formato de lista JSON o texto plano.'
        
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
    def _validate_cedula_colombiana(cedula_str: str) -> bool:
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
        cedula_list: List[int] = [int(d) for d in cedula_str[:-1]]
        dv_esperado: int = int(cedula_str[-1])
        
        # Multiplicadores oficiales corregidos
        multiplicadores: List[int] = [2, 7, 12, 17, 22, 27, 32, 37, 42, 47]
        
        suma: int = sum(d * m for d, m in zip(cedula_list, multiplicadores[:len(cedula_list)]))
        residuo: int = suma % 11
        
        if residuo <= 1:
            dv_calculado: int = residuo
        else:
            dv_calculado = 11 - residuo
            if dv_calculado == 10:
                dv_calculado = 0
        
        return dv_esperado == dv_calculado
