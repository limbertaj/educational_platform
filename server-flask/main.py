import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import bcrypt
from models import db, User, Teacher, Student, Course, Subject, CourseSubject, Assignment, Question, QuestionOption, QuestionScale, Submission, Answer, Notification
from dotenv import load_dotenv


load_dotenv()


def create_app():
    app = Flask(__name__)

    # Config
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql+psycopg2://postgres:postgres@localhost:5432/Taller_software'
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret')

    CORS(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)


    @app.route('/')
    def home():
        return "Servidor Flask funcionando correctamente 🚀"


    # --- Auth ---
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if not (username and email and password and role):
            return jsonify({'msg': 'username, email, password and role required'}), 400

        if role not in ('teacher', 'student', 'admin'):
            return jsonify({'msg': 'invalid role'}), 400

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({'msg': 'user exists'}), 400

        password_hash = bcrypt.hash(password)
        user = User(username=username, email=email, password_hash=password_hash, role=role)
        db.session.add(user)
        db.session.commit()

        # create teacher/student row
        if role == 'teacher':
            teacher = Teacher(user_id=user.id)
            db.session.add(teacher)
        if role == 'student':
            student = Student(user_id=user.id)
            db.session.add(student)
        db.session.commit()

        return jsonify({'msg': 'registered', 'user_id': user.id}), 201


    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        if not (username and password):
            return jsonify({'msg': 'username and password required'}), 400

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if not user or not bcrypt.verify(password, user.password_hash):
            return jsonify({'msg': 'invalid credentials'}), 401

        access_token = create_access_token(identity={'user_id': user.id, 'role': user.role})
        return jsonify({'access_token': access_token, 'user': {'id': user.id, 'username': user.username, 'role': user.role}})


    # Helper: role check
    def role_required(role_name):
        def decorator(fn):
            from functools import wraps

            @wraps(fn)
            @jwt_required()
            def wrapper(*args, **kwargs):
                identity = get_jwt_identity()
                if not identity:
                    return jsonify({'msg': 'missing identity'}), 401
                if identity.get('role') != role_name and identity.get('role') != 'admin':
                    return jsonify({'msg': 'forbidden - role required: %s' % role_name}), 403
                return fn(*args, **kwargs)

            return wrapper

        return decorator


    # --- Courses & Subjects ---
    @app.route('/api/subjects', methods=['POST'])
    @role_required('teacher')
    def create_subject():
        data = request.get_json() or {}
        name = data.get('name')
        description = data.get('description')
        if not name:
            return jsonify({'msg': 'name required'}), 400
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        return jsonify({'id': subject.id, 'name': subject.name}), 201


    @app.route('/api/courses', methods=['POST'])
    @role_required('teacher')
    def create_course():
        data = request.get_json() or {}
        name = data.get('name')
        description = data.get('description')
        teacher_id = data.get('teacher_id')
        if not name:
            return jsonify({'msg': 'name required'}), 400
        course = Course(name=name, description=description, teacher_id=teacher_id)
        db.session.add(course)
        db.session.commit()
        return jsonify({'id': course.id, 'name': course.name}), 201


    @app.route('/api/course_subjects', methods=['POST'])
    @role_required('teacher')
    def link_course_subject():
        data = request.get_json() or {}
        course_id = data.get('course_id')
        subject_id = data.get('subject_id')
        if not (course_id and subject_id):
            return jsonify({'msg': 'course_id and subject_id required'}), 400
        cs = CourseSubject(course_id=course_id, subject_id=subject_id)
        db.session.add(cs)
        db.session.commit()
        return jsonify({'id': cs.id}), 201


    # --- Assignments & Questions ---
    @app.route('/api/assignments', methods=['POST'])
    @role_required('teacher')
    def create_assignment():
        data = request.get_json() or {}
        course_subject_id = data.get('course_subject_id')
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        type_ = data.get('type')
        if not (course_subject_id and title):
            return jsonify({'msg': 'course_subject_id and title required'}), 400
        assignment = Assignment(course_subject_id=course_subject_id, title=title, description=description, type=type_)
        db.session.add(assignment)
        db.session.commit()
        return jsonify({'id': assignment.id, 'title': assignment.title}), 201


    @app.route('/api/assignments/<int:assignment_id>/questions', methods=['POST'])
    @role_required('teacher')
    def add_question(assignment_id):
        data = request.get_json() or {}
        text = data.get('text')
        qtype = data.get('type')
        required = data.get('required', True)
        options = data.get('options')  # list of {option_text, is_correct}
        scale = data.get('scale')  # dict with min/max/labels
        if not (text and qtype):
            return jsonify({'msg': 'text and type required'}), 400
        q = Question(assignment_id=assignment_id, text=text, type=qtype, required=required)
        db.session.add(q)
        db.session.commit()
        if options and isinstance(options, list):
            for opt in options:
                o = QuestionOption(question_id=q.id, option_text=opt.get('option_text'), is_correct=opt.get('is_correct', False))
                db.session.add(o)
        if scale and isinstance(scale, dict):
            s = QuestionScale(question_id=q.id, scale_min=scale.get('min', 1), scale_max=scale.get('max', 5), scale_labels=scale.get('labels'))
            db.session.add(s)
        db.session.commit()
        return jsonify({'id': q.id, 'text': q.text}), 201


    # --- Submissions ---
    @app.route('/api/assignments/<int:assignment_id>/submit', methods=['POST'])
    @role_required('student')
    def submit_assignment(assignment_id):
        identity = get_jwt_identity()
        student_user_id = identity.get('user_id')
        # find student record
        student = Student.query.filter_by(user_id=student_user_id).first()
        if not student:
            return jsonify({'msg': 'student profile not found'}), 404

        data = request.get_json() or {}
        file_url = data.get('file_url')
        answers = data.get('answers')  # list of answers
        sub = Submission(assignment_id=assignment_id, student_id=student.id, file_url=file_url)
        db.session.add(sub)
        db.session.commit()
        if answers and isinstance(answers, list):
            for a in answers:
                ans = Answer(submission_id=sub.id, question_id=a.get('question_id'), selected_options=a.get('selected_options'), text_answer=a.get('text_answer'), numeric_answer=a.get('numeric_answer'))
                db.session.add(ans)
        db.session.commit()
        return jsonify({'submission_id': sub.id}), 201


    @app.route('/api/submissions/<int:submission_id>/grade', methods=['POST'])
    @role_required('teacher')
    def grade_submission(submission_id):
        data = request.get_json() or {}
        final_score = data.get('final_score')
        ai_feedback = data.get('ai_feedback')
        sub = Submission.query.get(submission_id)
        if not sub:
            return jsonify({'msg': 'submission not found'}), 404
        sub.final_score = final_score
        sub.ai_feedback = ai_feedback
        sub.status = 'graded'
        db.session.commit()
        return jsonify({'msg': 'graded'}), 200


    @app.route('/api/submissions/<int:submission_id>/ai_feedback', methods=['POST'])
    @role_required('teacher')
    def generate_ai_feedback(submission_id):
        # Placeholder: basic heuristic-based feedback. Replace with real model integration.
        sub = Submission.query.get(submission_id)
        if not sub:
            return jsonify({'msg': 'submission not found'}), 404
        # Simple heuristic: score based on length of text answers
        answers = sub.answers
        total_len = 0
        count = 0
        for a in answers:
            if a.text_answer:
                total_len += len(a.text_answer)
                count += 1
        ai_score = None
        if count > 0:
            avg_len = total_len / count
            # map avg_len to 0-100 roughly
            ai_score = min(100, int(min(1.0, avg_len / 500.0) * 100))
        sub.ai_score = ai_score
        sub.ai_feedback = f'AI feedback placeholder. avg_text_len={avg_len if count>0 else 0}'
        db.session.commit()
        return jsonify({'ai_score': ai_score, 'ai_feedback': sub.ai_feedback}), 200


    # --- Notifications ---
    @app.route('/api/notifications', methods=['GET'])
    @jwt_required()
    def list_notifications():
        identity = get_jwt_identity()
        user_id = identity.get('user_id')
        nots = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        out = [{'id': n.id, 'message': n.message, 'created_at': n.created_at.isoformat(), 'read': n.read} for n in nots]
        return jsonify(out)


    return app


if __name__ == '__main__':
    app = create_app()
    # Helpful dev server settings
    debug = os.environ.get('FLASK_DEBUG', '1')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=(debug == '1'))
