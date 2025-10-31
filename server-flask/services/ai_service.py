from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AIResponse:
    """Representa la respuesta del servicio de AI."""
    score: float  # Puntuación numérica 0-100
    feedback: str  # Retroalimentación detallada
    confidence: float  # Nivel de confianza del modelo 0-1
    areas_improvement: List[str]  # Áreas específicas para mejorar
    highlights: List[str]  # Aspectos destacados positivos
    error: Optional[str] = None  # Mensaje de error si algo falla

class AIServiceInterface:
    """Interfaz abstracta para el servicio de AI."""
    
    async def evaluate_answer(
        self,
        student_answer: str,
        question_text: str,
        assignment_type: str,
        context: Optional[Dict] = None
    ) -> AIResponse:
        """
        Evalúa la respuesta de un estudiante.

        Args:
            student_answer: La respuesta del estudiante
            question_text: La pregunta original
            assignment_type: Tipo de tarea (quiz, exam, etc.)
            context: Contexto adicional opcional

        Returns:
            AIResponse: Objeto con la evaluación
        """
        raise NotImplementedError

    async def generate_feedback(
        self, 
        content: str,
        feedback_type: str,
        parameters: Optional[Dict] = None
    ) -> str:
        """
        Genera retroalimentación personalizada.

        Args:
            content: El contenido a evaluar
            feedback_type: Tipo de retroalimentación deseada
            parameters: Parámetros adicionales opcionales

        Returns:
            str: Retroalimentación generada
        """
        raise NotImplementedError

    async def generate_question(
        self,
        topic: str,
        difficulty: str,
        question_type: str,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """
        Genera una nueva pregunta.

        Args:
            topic: El tema de la pregunta
            difficulty: Nivel de dificultad
            question_type: Tipo de pregunta
            parameters: Parámetros adicionales opcionales

        Returns:
            Dict: Pregunta generada con metadatos
        """
        raise NotImplementedError