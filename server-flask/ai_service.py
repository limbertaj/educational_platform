"""
Servicio de IA usando Google Gemini para retroalimentación educativa
"""
import os
import google.generativeai as genai
from typing import Dict, List, Any


class GeminiAIService:
    def __init__(self):
        # Configurar API key
        api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyCd3FrWxnmg-gzhibRjmNkCUo-lIJ2UNek')
        genai.configure(api_key=api_key)
        
        # Configurar modelo
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Configuración de generación
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 1024,
        }
    
    def analyze_submission(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza una entrega de estudiante y genera retroalimentación
        
        Args:
            submission_data: Diccionario con información de la entrega:
                - assignment_title: Título de la tarea
                - assignment_description: Descripción de la tarea
                - questions: Lista de preguntas
                - answers: Lista de respuestas del estudiante
                
        Returns:
            Dict con feedback y score sugerido
        """
        try:
            # Construir prompt para Gemini
            prompt = self._build_analysis_prompt(submission_data)
            
            # Generar respuesta
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Procesar respuesta
            feedback_text = response.text
            
            # Intentar extraer calificación del feedback
            score = self._extract_score(feedback_text)
            
            return {
                'feedback': feedback_text,
                'suggested_score': score,
                'analysis_complete': True
            }
            
        except Exception as e:
            return {
                'feedback': f'Error al generar retroalimentación: {str(e)}',
                'suggested_score': None,
                'analysis_complete': False,
                'error': str(e)
            }
    
    def _build_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Construye el prompt para análisis de la entrega"""
        
        assignment_title = data.get('assignment_title', 'Tarea sin título')
        assignment_desc = data.get('assignment_description', '')
        questions = data.get('questions', [])
        answers = data.get('answers', [])
        
        prompt = f"""Eres un asistente educativo experto. Analiza la siguiente entrega de un estudiante y proporciona retroalimentación constructiva.

TAREA: {assignment_title}
DESCRIPCIÓN: {assignment_desc}

PREGUNTAS Y RESPUESTAS DEL ESTUDIANTE:
"""
        
        # Agregar cada pregunta y respuesta
        for i, (question, answer) in enumerate(zip(questions, answers), 1):
            q_text = question.get('text', '')
            q_type = question.get('type', '')
            
            prompt += f"\n{i}. PREGUNTA ({q_type}): {q_text}\n"
            
            if answer.get('text_answer'):
                prompt += f"   RESPUESTA: {answer['text_answer']}\n"
            elif answer.get('selected_options'):
                prompt += f"   OPCIONES SELECCIONADAS: {answer['selected_options']}\n"
            elif answer.get('numeric_answer'):
                prompt += f"   RESPUESTA NUMÉRICA: {answer['numeric_answer']}\n"
        
        prompt += """

Por favor proporciona:
1. Una evaluación general de la entrega
2. Retroalimentación específica para cada respuesta
3. Puntos fuertes y áreas de mejora
4. Una calificación sugerida del 0 al 100
5. Recomendaciones para el estudiante

FORMATO DE RESPUESTA:
Calificación Sugerida: [número del 0-100]

Evaluación General:
[tu evaluación]

Retroalimentación Detallada:
[análisis por pregunta]

Fortalezas:
[puntos fuertes]

Áreas de Mejora:
[aspectos a mejorar]

Recomendaciones:
[sugerencias específicas]
"""
        
        return prompt
    
    def _extract_score(self, feedback_text: str) -> float:
        """Intenta extraer la calificación del texto de feedback"""
        try:
            # Buscar patrón "Calificación Sugerida: XX"
            import re
            match = re.search(r'Calificación Sugerida:\s*(\d+(?:\.\d+)?)', feedback_text, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                # Asegurar que esté en rango 0-100
                return max(0, min(100, score))
            return None
        except:
            return None
    
    def analyze_text_answer(self, question: str, answer: str, criteria: str = "") -> Dict[str, Any]:
        """
        Analiza una respuesta de texto abierta específica
        """
        try:
            prompt = f"""Analiza esta respuesta de estudiante:

PREGUNTA: {question}
RESPUESTA DEL ESTUDIANTE: {answer}
{f'CRITERIOS DE EVALUACIÓN: {criteria}' if criteria else ''}

Proporciona:
1. Si la respuesta es correcta/adecuada
2. Calificación del 0-10
3. Feedback constructivo
4. Sugerencias de mejora
"""
            
            response = self.model.generate_content(prompt)
            
            return {
                'feedback': response.text,
                'analysis_complete': True
            }
        except Exception as e:
            return {
                'feedback': f'Error: {str(e)}',
                'analysis_complete': False
            }


# Instancia global del servicio
gemini_service = GeminiAIService()
