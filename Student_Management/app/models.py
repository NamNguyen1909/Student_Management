# Student_Management/app/models.py

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum, DateTime
from enum import Enum as RoleEnum
from flask_login import UserMixin
from datetime import datetime
from Student_Management.app import app,db


# Define User Roles
class UserRole(RoleEnum):
    ADMIN = 1
    EMPLOYEE = 2
    TEACHER = 3
    STUDENT = 4


# User Table
class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    sex = Column(Boolean, default=True)
    dob = Column(DateTime)
    address = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime, nullable=True)
    user_role = Column(Enum(UserRole), default=UserRole.STUDENT)

    # Relationships
    students = relationship('Student', backref='user', lazy=True)
    teachers = relationship('Teacher', backref='user', lazy=True)
    employees = relationship('Employee', backref='user', lazy=True)
    admin= relationship('Admin', backref='user', lazy=True)

# Grade Level Table
class GradeLevel(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    # Relationships
    students = relationship('Student', backref='grade_level', lazy=True)
    classes = relationship('Class', backref='grade_level', lazy=True)

# Class Table
class Class(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    si_so = Column(Integer, default=0)
    grade_level_id = Column(Integer, ForeignKey(GradeLevel.id), nullable=False)

    # Relationships
    students = relationship('Student', backref='class_', lazy=True)  # Thêm mối quan hệ với student

# Admin Table
class Admin(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

# Student Table
class Student(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    grade_level_id = Column(Integer, ForeignKey(GradeLevel.id), nullable=True)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)  # Khóa ngoại trỏ đến Class

    # Relationships
    user = relationship('User', backref='student', uselist=False)
    results = relationship('Result', backref='student', lazy=True)
    class_ = relationship('Class', backref='students')  # Mối quan hệ với Class


# Teacher Table
class Teacher(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    # Relationships
    user = relationship('User', backref='teacher', uselist=False)
    subjects = relationship('Subject', secondary='teacher_subject', backref='teachers')  # Nhiều môn học

# Employee Table
class Employee(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    position = Column(String(100), nullable=True)

    # Relationships
    user = relationship('User', backref='employee', uselist=False)




# Regulation Table
class Regulation(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    value = Column(Integer, nullable=True)
    note = Column(String(255), nullable=True)\


# Subject Table
class Subject(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    # Relationships
    results = relationship('Result', backref='subject', lazy=True)

# Semester Table
class Semester(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    # Relationships
    results = relationship('Result', backref='semester', lazy=True)
    subjects = relationship('Subject', secondary='semester_subject', backref='semesters')  # Nhiều môn học

# Result Table
class Result(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    semester_id = Column(Integer, ForeignKey(Semester.id), nullable=False)
    average = Column(Float, nullable=True)

    # Relationships
    score_details = relationship('ScoreDetail', backref='result', lazy=True)


# Score Type Table
class ScoreType(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    weight = Column(Integer, nullable=False)

    # Relationships
    scores = relationship('ScoreDetail', backref='score_type', lazy=True)

# Score Detail Table
class ScoreDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, ForeignKey(Result.id), nullable=False)
    value = Column(Float, nullable=False)
    score_type_id = Column(Integer, ForeignKey(ScoreType.id), nullable=False)

# Association Table for Teacher-Subject (Many-to-Many)
teacher_subject = db.Table('teacher_subject',
    Column('teacher_id', Integer, ForeignKey('teacher.id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subject.id'), primary_key=True)
)

# Association Table for Student-Subject (Many-to-Many)
student_subject = db.Table('student_subject',
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subject.id'), primary_key=True)
)

# Association Table for Semester-Subject (Many-to-Many)
semester_subject = db.Table('semester_subject',
    Column('semester_id', Integer, ForeignKey('semester.id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subject.id'), primary_key=True)
)

if __name__ == '__main__':
    with app.app_context():  # Đảm bảo có app context
        db.create_all()  # Chạy để tạo DB
        db.session.commit()


