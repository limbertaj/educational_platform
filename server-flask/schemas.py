from datetime import datetime
from typing import Optional, List, Union, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

class UserRole(str, Enum):
    TEACHER = 'teacher'
    STUDENT = 'student'
    ADMIN = 'admin'

class AssignmentType(str, Enum):
    TASK = 'task'
    QUIZ = 'quiz'
    EXAM = 'exam'

class QuestionType(str, Enum):
    TRUE_FALSE = 'true_false'
    SINGLE_CHOICE = 'single_choice'
    MULTIPLE_CHOICE = 'multiple_choice'
    SHORT_ANSWER = 'short_answer'
    LONG_ANSWER = 'long_answer'
    RATING_SCALE = 'rating_scale'
    RANKING = 'ranking'
    MIXED = 'mixed'

# Auth Schemas
class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole

    @validator('password')
    def password_strength(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLoginSchema(BaseModel):
    username: str
    password: str

# Course Schemas
class CourseCreateSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    teacher_id: int

class SubjectCreateSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None

class CourseSubjectCreateSchema(BaseModel):
    course_id: int
    subject_id: int

# Assignment Schemas
class QuestionOptionSchema(BaseModel):
    option_text: str
    is_correct: bool = False
    order_index: Optional[int] = 0

class QuestionScaleSchema(BaseModel):
    scale_min: int = 1
    scale_max: int = 5
    scale_labels: Optional[Dict[str, str]] = None

class QuestionCreateSchema(BaseModel):
    text: str
    type: QuestionType
    required: bool = True
    order_index: Optional[int] = 0
    options: Optional[List[QuestionOptionSchema]] = None
    scale: Optional[QuestionScaleSchema] = None

class AssignmentCreateSchema(BaseModel):
    course_subject_id: int
    title: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    type: AssignmentType
    questions: List[QuestionCreateSchema]

# Submission Schemas
class AnswerSubmitSchema(BaseModel):
    question_id: int
    selected_options: Optional[List[Union[str, Dict[str, Any]]]] = None
    text_answer: Optional[str] = None
    numeric_answer: Optional[float] = None

class SubmissionCreateSchema(BaseModel):
    assignment_id: int
    answers: List[AnswerSubmitSchema]
    file_url: Optional[str] = None

class GradingSchema(BaseModel):
    final_score: float = Field(..., ge=0, le=100)
    ai_feedback: Optional[str] = None

# Notification Schemas
class NotificationSchema(BaseModel):
    user_id: int
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False

# Response Schemas
class TokenResponse(BaseModel):
    access_token: str
    user: dict

class MessageResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None
