# Student_Management/app/models.py
import hashlib

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum, DateTime
from enum import Enum as RoleEnum
from flask_login import UserMixin
from datetime import datetime

from app import app, db

def generate_md5_hash(password):
    """
    Tạo hash MD5 từ mật khẩu đầu vào.

    Args:
        password (str): Mật khẩu cần tạo hash.

    Returns:
        str: Chuỗi hash MD5 của mật khẩu.
    """
    if not isinstance(password, str):
        raise ValueError("Password must be a string.")
    return hashlib.md5(password.strip().encode('utf-8')).hexdigest()


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
    avatar = Column(String(255), nullable=True,
                    default='https://res.cloudinary.com/ds05mb5xf/image/upload/v1734438824/avatar-default-symbolic-icon-479x512-n8sg74wg_rvl14k.png')
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
    students = relationship('Student', backref='student_user', uselist=False,cascade='all, delete-orphan')
    teachers = relationship('Teacher', backref='teacher_user', lazy=True,cascade='all, delete-orphan')
    employees = relationship('Employee', backref='employee_user', lazy=True,cascade='all, delete-orphan')
    admin = relationship('Admin', backref='user', lazy=True,cascade='all, delete-orphan')

    def __str__(self):
        return self.name

    def set_password(self, password):
        self.password = generate_md5_hash(password)

    def check_password(self, password):
        return self.password == generate_md5_hash(password)

    def create_related_entity(self):
        """
        Tạo thực thể liên quan (Student, Teacher, Employee) dựa trên vai trò của user.
        """
        if self.user_role == UserRole.STUDENT:
            return Student(user=self)
        elif self.user_role == UserRole.TEACHER:
            return Teacher(user=self)
        elif self.user_role == UserRole.EMPLOYEE:
            return Employee(user=self)
        elif self.user_role == UserRole.ADMIN:
            return Admin(user=self)
        else:
            raise ValueError("Không thể tạo thực thể liên quan cho vai trò này.")

# Grade Level Table
class GradeLevel(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    # Relationships
    students = relationship('Student', backref='grade_level', lazy=True)
    classes = relationship('Class', backref='grade_level', lazy=True)

    def __str__(self):
        return self.name

# Class Table
class Class(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    si_so = Column(Integer, default=0)
    grade_level_id = Column(Integer, ForeignKey(GradeLevel.id), nullable=False)

    # Relationships
    students = relationship('Student', backref='class_relationship', lazy=True)

    def __str__(self):
        return self.name


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
    user = relationship('User', backref='student', uselist=False, cascade='all, delete')
    results = relationship('Result', backref='student', lazy=True, cascade='all, delete')
    # class_ = relationship('Class', backref='student_relationship')  # Mối quan hệ với Class

    def __str__(self):
        return f"{self.user.username} - {self.user.name} - {self.user.sex} - {self.user.dob} - {self.user.phone}"

    def calculate_gpa(self):
        """
        Tính điểm trung bình (GPA) của học sinh dựa trên bảng điểm (results).
        """
        if not self.results:
            return 0
        total_score = sum(r.average for r in self.results if r.average is not None)
        return total_score / len(self.results)

# Teacher Table
class Teacher(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    # Relationships
    user = relationship('User', backref='teacher', uselist=False, cascade='all, delete')
    subjects = relationship('Subject', secondary='teacher_subject', backref='teachers', cascade='all, delete') # Nhiều môn học

    def __str__(self):
        return f"{self.user.username} - {self.user.name} - {self.user.sex} - {self.user.dob} - {self.user.phone}"

    def get_subjects(self):
        """
        Trả về danh sách các môn học mà giáo viên đang dạy.
        """
        return [subject.name for subject in self.subjects]

# Employee Table
class Employee(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    position = Column(String(100), nullable=True)

    # Relationships
    user = relationship('User', backref='employee', uselist=False, cascade='all, delete')

    def __str__(self):
        return f"{self.user.username} - {self.user.name} - {self.user.sex} - {self.user.dob} - {self.user.phone}"


# Regulation Table
class Regulation(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    value = Column(Integer, nullable=True)
    note = Column(String(255), nullable=True)


# Subject Table
class Subject(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    # Relationships
    results = relationship('Result', backref='subject', lazy=True)

    def __str__(self):
        return self.name

# Semester Table
class Semester(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    year = Column(String(20), nullable=False)

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
    value = Column(Float, nullable=True, default=0)
    score_type_id = Column(Integer, ForeignKey(ScoreType.id), nullable=False)


class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subject'

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), primary_key=True)

    teacher = db.relationship('Teacher', backref='teacher_subjects')
    subject = db.relationship('Subject', backref='teacher_subjects')

    def __str__(self):
        return f"Teacher: {self.teacher.user.name}, Subject: {self.subject.name}"



class StudentSubject(db.Model):
    __tablename__ = 'student_subject'

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), primary_key=True)

    student = db.relationship('Student', backref='student_subjects')
    subject = db.relationship('Subject', backref='student_subjects')

    def __str__(self):
        return f"Student: {self.student.user.name}, Subject: {self.subject.name}"

class SemesterSubject(db.Model):
    __tablename__ = 'semester_subject'

    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), primary_key=True)

    semester = db.relationship('Semester', backref='semester_subjects')
    subject = db.relationship('Subject', backref='semester_subjects')


    def __str__(self):
        return f"Semester: {self.semester.name}, Subject: {self.subject.name}"

class ClassSubject(db.Model):
    __tablename__ = 'class_subject'

    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), primary_key=True)

    class_ = db.relationship('Class', backref='class_subjects')
    subject = db.relationship('Subject', backref='class_subjects')

    def __str__(self):
        return f"Class: {self.class_.name}, Subject: {self.subject.name}"


if __name__ == '__main__':
    with app.app_context():  # Đảm bảo có app context
        db.create_all()  # Chạy để tạo DB
        db.session.commit()





