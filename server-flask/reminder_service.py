"""
Sistema de recordatorios automáticos para tareas
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from models import db, Assignment, Notification, Submission, Student
import atexit


class ReminderService:
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar el servicio con la app Flask"""
        self.app = app
        
        # Configurar tareas programadas
        # Verificar recordatorios cada hora
        self.scheduler.add_job(
            func=self.check_due_dates,
            trigger="interval",
            hours=1,
            id='check_due_dates'
        )
        
        # Iniciar scheduler
        self.scheduler.start()
        
        # Asegurar que el scheduler se cierre al salir
        atexit.register(lambda: self.scheduler.shutdown())
    
    def check_due_dates(self):
        """Verificar tareas próximas a vencer y enviar recordatorios"""
        if not self.app:
            return
        
        with self.app.app_context():
            try:
                now = datetime.utcnow()
                
                # Buscar tareas que vencen en las próximas 24 horas
                upcoming = Assignment.query.filter(
                    Assignment.due_date.between(now, now + timedelta(hours=24))
                ).all()
                
                for assignment in upcoming:
                    # Obtener estudiantes que no han entregado
                    submitted_student_ids = [s.student_id for s in Submission.query.filter_by(assignment_id=assignment.id).all()]
                    
                    # Obtener todos los estudiantes (TODO: filtrar por curso cuando se implemente matrícula)
                    students = Student.query.filter(~Student.id.in_(submitted_student_ids) if submitted_student_ids else True).all()
                    
                    for student in students:
                        # Verificar si ya se envió recordatorio
                        existing = Notification.query.filter_by(
                            user_id=student.user_id,
                            message=f'Recordatorio: La tarea "{assignment.title}" vence pronto'
                        ).first()
                        
                        if not existing:
                            # Crear notificación
                            hours_left = int((assignment.due_date - now).total_seconds() / 3600)
                            notification = Notification(
                                user_id=student.user_id,
                                message=f'Recordatorio: La tarea "{assignment.title}" vence en {hours_left} horas'
                            )
                            db.session.add(notification)
                
                db.session.commit()
                print(f"[ReminderService] Checked due dates at {now}")
                
            except Exception as e:
                print(f"[ReminderService] Error checking due dates: {e}")
                db.session.rollback()
    
    def send_assignment_notification(self, assignment_id, student_ids):
        """Enviar notificación de nueva tarea a estudiantes específicos"""
        if not self.app:
            return
        
        with self.app.app_context():
            try:
                assignment = Assignment.query.get(assignment_id)
                if not assignment:
                    return
                
                for student_id in student_ids:
                    student = Student.query.get(student_id)
                    if student:
                        notification = Notification(
                            user_id=student.user_id,
                            message=f'Nueva tarea asignada: "{assignment.title}"'
                        )
                        db.session.add(notification)
                
                db.session.commit()
                
            except Exception as e:
                print(f"[ReminderService] Error sending notification: {e}")
                db.session.rollback()


# Instancia global del servicio
reminder_service = ReminderService()
