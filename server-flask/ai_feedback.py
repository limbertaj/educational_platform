import os
import google.generativeai as genai
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger()

# Configurar la API key
genai.configure(api_key='AIzaSyCd3FrWxnmg-gzhibRjmNkCUo-lIJ2UNek')

class AIFeedback:
    def __init__(self):
        # Configurar el modelo
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Prompt base para análisis de respuestas
        self.base_prompt = """
        Actúa como un profesor experto evaluando una respuesta de estudiante.
        Analiza la respuesta considerando:
        1. Precisión del contenido
        2. Claridad de expresión
        3. Uso de conceptos clave
        4. Argumentación y ejemplos
        
        Proporciona:
        1. Calificación numérica (0-100)
        2. Retroalimentación constructiva
        3. Áreas de mejora
        4. Conceptos destacados
        
        Respuesta a evaluar:
        {student_answer}
        
        Pregunta original:
        {question_text}
        
        Tipo de evaluación:
        {assignment_type}
        """

    async def generate_feedback(
        self,
        student_answer: str,
        question_text: str,
        assignment_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera retroalimentación para una respuesta de estudiante usando Gemini AI.
        
        Args:
            student_answer: Respuesta del estudiante
            question_text: Pregunta original
            assignment_type: Tipo de tarea (quiz, exam, etc.)
            context: Contexto adicional opcional
            
        Returns:
            Dict con score y feedback
        """
        try:
            # Construir el prompt
            prompt = self.base_prompt.format(
                student_answer=student_answer,
                question_text=question_text,
                assignment_type=assignment_type
            )
            
            # Agregar contexto si existe
            if context:
                prompt += f"\nContexto adicional:\n{context}"
            
            # Generar respuesta
            response = self.model.generate_content(prompt)
            
            # Procesar la respuesta para extraer score y feedback
            response_text = response.text
            
            # Análisis básico para extraer score (asumiendo que está en el formato "Calificación: XX/100")
            try:
                score_line = [line for line in response_text.split('\n') if 'calificación' in line.lower()][0]
                score = float(score_line.split(':')[1].strip().split('/')[0])
            except (IndexError, ValueError):
                score = 70  # Score por defecto si no se puede extraer
            
            return {
                'score': score,
                'feedback': response_text,
                'confidence': 0.85,  # Valor de confianza por defecto
                'areas_improvement': self._extract_areas_improvement(response_text),
                'highlights': self._extract_highlights(response_text)
            }
            
        except Exception as e:
            logger.error("error_generating_ai_feedback", error=str(e))
            return {
                'score': 50,
                'feedback': 'Error generando retroalimentación. Por favor, revisar manualmente.',
                'error': str(e)
            }
    
    def _extract_areas_improvement(self, feedback_text: str) -> list:
        """Extrae áreas de mejora del texto de retroalimentación."""
        try:
            areas_section = feedback_text.split('Áreas de mejora:')[1].split('\n\n')[0]
            areas = [area.strip() for area in areas_section.split('\n') if area.strip()]
            return areas
        except:
            return []
    
    def _extract_highlights(self, feedback_text: str) -> list:
        """Extrae conceptos destacados del texto de retroalimentación."""
        try:
            highlights_section = feedback_text.split('Conceptos destacados:')[1].split('\n\n')[0]
            highlights = [highlight.strip() for highlight in highlights_section.split('\n') if highlight.strip()]
            return highlights
        except:
            return []

# Singleton instance
ai_feedback = AIFeedback()