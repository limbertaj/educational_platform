"""
Rutas adicionales para completar todos los casos de uso
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Teacher, Student, Course, Subject, CourseSubject, Assignment, Question, QuestionOption, Submission, Answer, Notification
from datetime import datetime
from sqlalchemy import and_, or_

# Crear blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


def get_current_user():
    """Helper para obtener el usuario actual"""
    identity = get_jwt_identity()
    return User.query.get(identity['user_id'])


def role_required(role_name):
    """Decorator para requerir rol específico"""
    def decorator(fn):
        from functools import wraps
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if not identity:
                return jsonify({'msg': 'missing identity'}), 401
            if identity.get('role') != role_name and identity.get('role') != 'admin':
                return jsonify({'msg': f'forbidden - role required: {role_name}'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ============= ENDPOINTS PARA LISTAR (GET) =============

@api_bp.route('/courses', methods=['GET'])
@jwt_required()
def list_courses():
    """CU-02: Listar todos los cursos"""
    courses = Course.query.all()
    result = []
    for c in courses:
        teacher_name = None
        if c.teacher and c.teacher.user:
            teacher_name = c.teacher.user.username
        result.append({
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'teacher_id': c.teacher_id,
            'teacher_name': teacher_name
        })
    return jsonify(result), 200


@api_bp.route('/subjects', methods=['GET'])
@jwt_required()
def list_subjects():
    """CU-02: Listar todas las asignaturas"""
    subjects = Subject.query.all()
    result = [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects]
    return jsonify(result), 200


@api_bp.route('/teacher/<int:teacher_id>/courses', methods=['GET'])
@jwt_required()
def get_teacher_courses(teacher_id):
    """CU-02: Obtener cursos de un profesor específico"""
    courses = Course.query.filter_by(teacher_id=teacher_id).all()
    result = [{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'subjects': [{'id': cs.subject.id, 'name': cs.subject.name} for cs in c.course_subjects]
    } for c in courses]
    return jsonify(result), 200


@api_bp.route('/assignments', methods=['GET'])
@jwt_required()
def list_assignments():
    """CU-03.1: Listar tareas con filtros"""
    course_id = request.args.get('course_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    course_subject_id = request.args.get('course_subject_id', type=int)
    assignment_type = request.args.get('type')
    
    query = Assignment.query
    
    if course_subject_id:
        query = query.filter_by(course_subject_id=course_subject_id)
    elif course_id or subject_id:
        query = query.join(CourseSubject)
        if course_id:
            query = query.filter(CourseSubject.course_id == course_id)
        if subject_id:
            query = query.filter(CourseSubject.subject_id == subject_id)
    
    if assignment_type:
        query = query.filter_by(type=assignment_type)
    
    assignments = query.order_by(Assignment.created_at.desc()).all()
    
    result = []
    for a in assignments:
        result.append({
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'due_date': a.due_date.isoformat() if a.due_date else None,
            'type': a.type,
            'course_subject_id': a.course_subject_id,
            'created_at': a.created_at.isoformat(),
            'questions_count': len(a.questions)
        })
    
    return jsonify(result), 200


@api_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment_detail(assignment_id):
    """Obtener detalle completo de una tarea"""
    assignment = Assignment.query.get_or_404(assignment_id)
    
    questions = []
    for q in assignment.questions:
        question_data = {
            'id': q.id,
            'text': q.text,
            'type': q.type,
            'required': q.required,
            'order_index': q.order_index
        }
        
        if q.options:
            question_data['options'] = [{
                'id': opt.id,
                'option_text': opt.option_text,
                'is_correct': opt.is_correct,
                'order_index': opt.order_index
            } for opt in q.options]
        
        if q.scale:
            question_data['scale'] = {
                'min': q.scale.scale_min,
                'max': q.scale.scale_max,
                'labels': q.scale.scale_labels
            }
        
        questions.append(question_data)
    
    return jsonify({
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
        'type': assignment.type,
        'file_url': assignment.file_url,
        'created_at': assignment.created_at.isoformat(),
        'questions': questions
    }), 200


# ============= ENDPOINTS PARA PROFESORES =============

@api_bp.route('/teacher/submissions', methods=['GET'])
@role_required('teacher')
def get_teacher_submissions():
    """CU-08: Revisar todas las entregas del profesor"""
    identity = get_jwt_identity()
    user = User.query.get(identity['user_id'])
    teacher = user.teacher
    
    if not teacher:
        return jsonify({'msg': 'teacher profile not found'}), 404
    
    # Obtener todas las entregas de cursos del profesor
    submissions = db.session.query(Submission).join(Assignment).join(CourseSubject).join(Course).filter(
        Course.teacher_id == teacher.id
    ).order_by(Submission.submission_date.desc()).all()
    
    result = []
    for sub in submissions:
        student_name = sub.student.user.username if sub.student and sub.student.user else 'Unknown'
        result.append({
            'id': sub.id,
            'assignment_title': sub.assignment.title,
            'assignment_type': sub.assignment.type,
            'student_name': student_name,
            'student_id': sub.student_id,
            'submission_date': sub.submission_date.isoformat(),
            'status': sub.status,
            'ai_score': float(sub.ai_score) if sub.ai_score else None,
            'final_score': float(sub.final_score) if sub.final_score else None
        })
    
    return jsonify(result), 200


@api_bp.route('/submissions/<int:submission_id>', methods=['GET'])
@jwt_required()
def get_submission_detail(submission_id):
    """CU-08: Ver detalle completo de una entrega"""
    submission = Submission.query.get_or_404(submission_id)
    
    # Obtener respuestas con sus preguntas
    answers_detail = []
    for answer in submission.answers:
        question = Question.query.get(answer.question_id)
        answer_data = {
            'id': answer.id,
            'question_id': answer.question_id,
            'question_text': question.text if question else None,
            'question_type': question.type if question else None,
            'selected_options': answer.selected_options,
            'text_answer': answer.text_answer,
            'numeric_answer': float(answer.numeric_answer) if answer.numeric_answer else None,
            'correct': answer.correct,
            'ai_comment': answer.ai_comment
        }
        answers_detail.append(answer_data)
    
    return jsonify({
        'id': submission.id,
        'assignment_id': submission.assignment_id,
        'assignment_title': submission.assignment.title,
        'student_id': submission.student_id,
        'student_name': submission.student.user.username if submission.student and submission.student.user else None,
        'submission_date': submission.submission_date.isoformat(),
        'file_url': submission.file_url,
        'ai_feedback': submission.ai_feedback,
        'ai_score': float(submission.ai_score) if submission.ai_score else None,
        'final_score': float(submission.final_score) if submission.final_score else None,
        'status': submission.status,
        'answers': answers_detail
    }), 200


# ============= ENDPOINTS PARA ESTUDIANTES =============

@api_bp.route('/student/courses', methods=['GET'])
@role_required('student')
def get_student_courses():
    """CU-12: Consultar materias asignadas del estudiante"""
    identity = get_jwt_identity()
    user = User.query.get(identity['user_id'])
    student = user.student
    
    if not student:
        return jsonify({'msg': 'student profile not found'}), 404
    
    # Por ahora, retornar todos los cursos (TODO: implementar matrícula)
    courses = Course.query.all()
    result = []
    for course in courses:
        teacher_name = course.teacher.user.username if course.teacher and course.teacher.user else None
        result.append({
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'teacher_name': teacher_name,
            'subjects': [{'id': cs.subject.id, 'name': cs.subject.name} for cs in course.course_subjects]
        })
    
    return jsonify(result), 200


@api_bp.route('/student/assignments/pending', methods=['GET'])
@role_required('student')
def get_student_pending_assignments():
    """CU-13: Ver actividades pendientes del estudiante"""
    identity = get_jwt_identity()
    user = User.query.get(identity['user_id'])
    student = user.student
    
    if not student:
        return jsonify({'msg': 'student profile not found'}), 404
    
    # Filtros opcionales
    assignment_type = request.args.get('type')
    
    # Obtener IDs de tareas ya entregadas por el estudiante
    submitted_ids = [s.assignment_id for s in Submission.query.filter_by(student_id=student.id).all()]
    
    # Obtener tareas no entregadas
    query = Assignment.query.filter(~Assignment.id.in_(submitted_ids) if submitted_ids else True)
    
    if assignment_type:
        query = query.filter_by(type=assignment_type)
    
    assignments = query.order_by(Assignment.due_date.asc()).all()
    
    result = []
    for a in assignments:
        days_until_due = None
        if a.due_date:
            days_until_due = (a.due_date - datetime.utcnow()).days
        
        result.append({
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'type': a.type,
            'due_date': a.due_date.isoformat() if a.due_date else None,
            'days_until_due': days_until_due,
            'is_overdue': days_until_due < 0 if days_until_due is not None else False,
            'questions_count': len(a.questions)
        })
    
    return jsonify(result), 200


@api_bp.route('/student/grades', methods=['GET'])
@role_required('student')
def get_student_grades():
    """CU-14: Consultar todas las calificaciones del estudiante"""
    identity = get_jwt_identity()
    user = User.query.get(identity['user_id'])
    student = user.student
    
    if not student:
        return jsonify({'msg': 'student profile not found'}), 404
    
    submissions = Submission.query.filter_by(student_id=student.id, status='graded').order_by(Submission.submission_date.desc()).all()
    
    result = []
    total_score = 0
    count = 0
    
    for sub in submissions:
        if sub.final_score:
            total_score += float(sub.final_score)
            count += 1
        
        result.append({
            'id': sub.id,
            'assignment_title': sub.assignment.title,
            'assignment_type': sub.assignment.type,
            'submission_date': sub.submission_date.isoformat(),
            'final_score': float(sub.final_score) if sub.final_score else None,
            'ai_score': float(sub.ai_score) if sub.ai_score else None,
            'feedback': sub.ai_feedback
        })
    
    average = total_score / count if count > 0 else 0
    
    return jsonify({
        'grades': result,
        'statistics': {
            'average': round(average, 2),
            'total_assignments': count,
            'pending_assignments': len(Submission.query.filter_by(student_id=student.id, status='pending').all())
        }
    }), 200


@api_bp.route('/student/submissions/<int:submission_id>/grade', methods=['GET'])
@role_required('student')
def get_student_submission_grade(submission_id):
    """CU-14: Ver calificación específica con feedback detallado"""
    identity = get_jwt_identity()
    user = User.query.get(identity['user_id'])
    student = user.student
    
    submission = Submission.query.filter_by(id=submission_id, student_id=student.id).first_or_404()
    
    return jsonify({
        'id': submission.id,
        'assignment_title': submission.assignment.title,
        'assignment_description': submission.assignment.description,
        'submission_date': submission.submission_date.isoformat(),
        'status': submission.status,
        'final_score': float(submission.final_score) if submission.final_score else None,
        'ai_score': float(submission.ai_score) if submission.ai_score else None,
        'ai_feedback': submission.ai_feedback,
        'graded': submission.status == 'graded'
    }), 200


# ============= NOTIFICACIONES =============

@api_bp.route('/notifications/create', methods=['POST'])
@jwt_required()
def create_notification():
    """CU-10: Crear notificación/recordatorio"""
    data = request.get_json() or {}
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not (user_id and message):
        return jsonify({'msg': 'user_id and message required'}), 400
    
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'id': notification.id, 'message': notification.message}), 201


@api_bp.route('/notifications/<int:notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_notification_read(notification_id):
    """CU-15: Marcar notificación como leída"""
    identity = get_jwt_identity()
    user_id = identity['user_id']
    
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first_or_404()
    notification.read = True
    db.session.commit()
    
    return jsonify({'msg': 'notification marked as read'}), 200
