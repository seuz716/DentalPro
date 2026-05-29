"""
Configuración de Google Gemini API para DentalPro.
Utiliza Gemini Flash 2.5 por su costo-efectividad en producción.
"""

import os
from django.conf import settings

# Configuración de Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

GEMINI_CONFIG = {
    'api_key': GEMINI_API_KEY,
    'model': 'gemini-2.0-flash',  # Modelo más económico
    'max_tokens': 1024,
    'temperature': 0.3,  # Más determinístico para análisis médico
}

# Prompts especializados para radiografías dentales
GEMINI_PROMPTS = {
    'radiograph_analysis': """Analiza esta radiografía dental profesionalmente.
    
Proporciona:
1. **Hallazgos principales**: Caries, restauraciones, anomalías óseas
2. **Piezas afectadas**: Número FDI (11-48)
3. **Severidad**: Leve, Moderada, Severa
4. **Recomendaciones**: Tratamientos sugeridos
5. **Urgencia**: Electiva, Rutinaria, Urgente

Formato: JSON estructura limpia.""",
    
    'clinical_notes_translator': """Convierte esta nota clínica técnica en lenguaje claro para el paciente.
    
Mantén la precisión médica pero hazla comprensible.
Usa ejemplos: "pequeña caries" en lugar de "caries oclusal".""",
}

def get_gemini_client():
    """
    Obtiene cliente configurado de Gemini.
    Requiere GEMINI_API_KEY en variables de entorno.
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY no configurada. "
            "Añade a .env: GEMINI_API_KEY=tu_clave"
        )
    
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    return genai

# Configuración de Anthropic
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')

def get_anthropic_client():
    """
    Obtiene cliente configurado de Anthropic.
    Requiere ANTHROPIC_API_KEY en variables de entorno.
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY no configurada. "
            "Añade a .env: ANTHROPIC_API_KEY=tu_clave"
        )
    
    import anthropic
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

