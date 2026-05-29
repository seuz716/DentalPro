"""
Generador de reportes PDF profesionales para DentalPro.
"""

from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime


class PatientReportGenerator:
    """
    Genera reportes PDF profesionales de pacientes.
    """
    
    def __init__(self, patient):
        """
        Inicializa generador.
        
        Args:
            patient: Instancia de Patient model
        """
        self.patient = patient
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configura estilos personalizados."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0d9488'),
            alignment=TA_CENTER,
            spaceAfter=12,
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=10,
        ))
    
    def generate(self):
        """
        Genera PDF del paciente.
        
        Returns:
            BytesIO: Buffer con PDF generado
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        story = []
        
        # Header
        story.append(Paragraph("DentalPro", self.styles['CustomTitle']))
        story.append(Paragraph("Reporte Clínico del Paciente", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Información del paciente
        patient_data = [
            ['Campo', 'Valor'],
            ['Nombre', self.patient.full_name],
            ['Documento', f"{self.patient.get_document_type_display()} {self.patient.document_number}"],
            ['Fecha Nacimiento', self.patient.birth_date.strftime('%d/%m/%Y') if self.patient.birth_date else '—'],
            ['Edad', f"{self.patient.age} años" if self.patient.birth_date else '—'],
            ['Género', self.patient.get_gender_display() if self.patient.gender else '—'],
            ['Teléfono', self.patient.phone or '—'],
            ['Email', self.patient.email or '—'],
            ['Tipo Sangre', self.patient.blood_type or '—'],
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d9488')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        
        story.append(Paragraph("Información del Paciente", self.styles['CustomHeading']))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Información Clínica
        if self.patient.blood_type or self.patient.allergies or self.patient.chronic_conditions:
            story.append(Paragraph("Información Clínica", self.styles['CustomHeading']))
            
            if self.patient.allergies:
                story.append(Paragraph(
                    f"<b>Alergias:</b> {self.patient.allergies}",
                    self.styles['Normal']
                ))
            
            if self.patient.chronic_conditions:
                story.append(Paragraph(
                    f"<b>Enfermedades Crónicas:</b> {self.patient.chronic_conditions}",
                    self.styles['Normal']
                ))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Pie de página
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            ParagraphStyle(name='Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        # Construir PDF
        doc.build(story)
        self.buffer.seek(0)
        return self.buffer
    
    def get_filename(self):
        """Retorna nombre de archivo sugerido."""
        return f"Reporte_{self.patient.document_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
