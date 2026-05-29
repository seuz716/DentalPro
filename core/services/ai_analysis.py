"""
Servicio de análisis de radiografías con Google Gemini Flash 2.5.
"""

import json
import base64
from core.services.gemini_config import get_gemini_client, GEMINI_PROMPTS, GEMINI_CONFIG


class RadiographAnalysisService:
    """Análisis de radiografías con Gemini."""
    
    @staticmethod
    def analyze_image(image_path_or_file):
        """Analiza radiografía dental."""
        try:
            genai = get_gemini_client()
            
            # Convertir imagen a base64
            if isinstance(image_path_or_file, str):
                with open(image_path_or_file, 'rb') as f:
                    image_data = base64.standard_b64encode(f.read()).decode()
                mime_type = 'image/jpeg'
            else:
                image_bytes = image_path_or_file.read()
                image_data = base64.standard_b64encode(image_bytes).decode()
                mime_type = getattr(image_path_or_file, 'content_type', 'image/jpeg')
            
            model = genai.GenerativeModel(GEMINI_CONFIG['model'])
            
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"inline_data": {"mime_type": mime_type, "data": image_data}},
                        {"text": GEMINI_PROMPTS['radiograph_analysis']}
                    ]
                }
            ]
            
            response = model.generate_content(contents)
            analysis_text = response.text
            
            try:
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                json_str = analysis_text[start_idx:end_idx]
                analysis = json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                analysis = {
                    'findings': analysis_text,
                    'affected_teeth': [],
                    'severity': 'Moderada',
                    'recommendations': ['Consultar especialista'],
                    'urgency': 'Rutinaria',
                }
            
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'findings': 'Error analizando radiografía',
                'affected_teeth': [],
                'severity': 'Desconocida',
                'recommendations': ['Revisión manual'],
                'urgency': 'Urgente',
            }
    
    @staticmethod
    def translate_clinical_notes(notes_text):
        """Traduce notas técnicas a lenguaje claro."""
        try:
            genai = get_gemini_client()
            model = genai.GenerativeModel(GEMINI_CONFIG['model'])
            
            prompt = f"{GEMINI_PROMPTS['clinical_notes_translator']}\n\nNotas: {notes_text}"
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error: {str(e)}"
