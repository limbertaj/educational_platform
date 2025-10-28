from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    teacher = db.relationship('Teacher', back_populates='user', uselist=False, cascade='all,delete')
    student = db.relationship('Student', back_populates='user', uselist=False, cascade='all,delete')
    notifications = db.relationship('Notification', back_populates='user', cascade='all,delete')


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    user = db.relationship('User', back_populates='teacher')
    courses = db.relationship('Course', back_populates='teacher')


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    user = db.relationship('User', back_populates='student')
    submissions = db.relationship('Submission', back_populates='student')


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='SET NULL'))
    teacher = db.relationship('Teacher', back_populates='courses')
    course_subjects = db.relationship('CourseSubject', back_populates='course', cascade='all,delete')


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    course_subjects = db.relationship('CourseSubject', back_populates='subject', cascade='all,delete')


class CourseSubject(db.Model):
    __tablename__ = 'course_subjects'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'))
    __table_args__ = (db.UniqueConstraint('course_id', 'subject_id', name='uix_course_subject'),)
    course = db.relationship('Course', back_populates='course_subjects')
    subject = db.relationship('Subject', back_populates='course_subjects')
    assignments = db.relationship('Assignment', back_populates='course_subject', cascade='all,delete')


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    course_subject_id = db.Column(db.Integer, db.ForeignKey('course_subjects.id', ondelete='CASCADE'))
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    type = db.Column(db.String(20))
    file_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course_subject = db.relationship('CourseSubject', back_populates='assignments')
    questions = db.relationship('Question', back_populates='assignment', cascade='all,delete')
    submissions = db.relationship('Submission', back_populates='assignment')


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'))
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), nullable=False)
    required = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assignment = db.relationship('Assignment', back_populates='questions')
    options = db.relationship('QuestionOption', back_populates='question', cascade='all,delete')
    scale = db.relationship('QuestionScale', back_populates='question', uselist=False, cascade='all,delete')


class QuestionOption(db.Model):
    __tablename__ = 'question_options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'))
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    question = db.relationship('Question', back_populates='options')


class QuestionScale(db.Model):
    __tablename__ = 'question_scale'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'))
    scale_min = db.Column(db.Integer, default=1)
    scale_max = db.Column(db.Integer, default=5)
    scale_labels = db.Column(db.JSON)
    question = db.relationship('Question', back_populates='scale')


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'))
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_url = db.Column(db.Text)
    ai_feedback = db.Column(db.Text)
    ai_score = db.Column(db.Numeric)
    final_score = db.Column(db.Numeric)
    status = db.Column(db.String(20), default='pending')
    assignment = db.relationship('Assignment', back_populates='submissions')
    student = db.relationship('Student', back_populates='submissions')
    answers = db.relationship('Answer', back_populates='submission', cascade='all,delete')


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'))
    selected_options = db.Column(db.JSON)
    text_answer = db.Column(db.Text)
    numeric_answer = db.Column(db.Numeric)
    correct = db.Column(db.Boolean)
    ai_comment = db.Column(db.Text)
    submission = db.relationship('Submission', back_populates='answers')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='notifications')
