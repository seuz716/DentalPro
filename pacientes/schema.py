"""
Esquema GraphQL para la aplicación pacientes usando Strawberry.
Optimiza la consulta de pacientes evitando problemas de sobre-fetching.
"""

import strawberry
from typing import List, Optional
from django.db.models import Q
from pacientes.models import Patient


@strawberry.type
class PatientType:
    """
    Tipo GraphQL que representa a un Paciente.
    El cliente puede solicitar solo los campos que necesita (ej. ID y nombre completo).
    """
    id: strawberry.ID
    document_type: str
    document_number: str
    first_name: str
    last_name: str
    full_name: str
    birth_date: Optional[str]
    age: Optional[int]
    gender: str
    phone: str
    email: str
    address: str
    blood_type: str
    allergies: str
    chronic_conditions: str
    created_at: str
    updated_at: str

    @classmethod
    def from_db(cls, patient: Patient):
        """Helper para mapear un modelo Django a un tipo Strawberry."""
        return cls(
            id=strawberry.ID(str(patient.id)),
            document_type=patient.document_type,
            document_number=patient.document_number,
            first_name=patient.first_name,
            last_name=patient.last_name,
            full_name=patient.full_name,
            birth_date=str(patient.birth_date) if patient.birth_date else None,
            age=patient.age,
            gender=patient.gender,
            phone=patient.phone,
            email=patient.email,
            address=patient.address,
            blood_type=patient.blood_type,
            allergies=patient.allergies,
            chronic_conditions=patient.chronic_conditions,
            created_at=str(patient.created_at),
            updated_at=str(patient.updated_at),
        )


@strawberry.type
class Query:
    """
    Consultas raíz de GraphQL para pacientes.
    """
    
    @strawberry.field
    def patients(self, search: Optional[str] = None) -> List[PatientType]:
        """
        Retorna la lista de todos los pacientes, permitiendo filtrar por búsqueda textual.
        """
        queryset = Patient.objects.all()
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(document_number__icontains=search) |
                Q(phone__icontains=search)
            )
        return [PatientType.from_db(p) for p in queryset]

    @strawberry.field
    def patient(self, id: strawberry.ID) -> Optional[PatientType]:
        """
        Retorna los detalles de un único paciente por su ID.
        """
        try:
            patient = Patient.objects.get(id=int(id))
            return PatientType.from_db(patient)
        except (Patient.DoesNotExist, ValueError):
            return None


schema = strawberry.Schema(query=Query)
