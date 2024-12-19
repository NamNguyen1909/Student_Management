# Student_Management/app/models.py

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum, DateTime
from enum import Enum as RoleEnum
from flask_login import UserMixin
from datetime import datetime
from Student_Management.app import app,db


def generate_username(role_prefix, user_role):

    """
    Hàm tạo username dạng 'ST000001', 'TC000001' dựa trên role_prefix và user_role.
    """
    # Lấy id lớn nhất của user thuộc user_role cụ thể
    last_user = User.query.filter_by(user_role=user_role).order_by(User.id.desc()).first()

    # Nếu không có bản ghi nào, bắt đầu từ 1
    if not last_user:
        new_id = 1
    else:
        # Lấy id của bản ghi cuối cùng và cộng thêm 1
        new_id = int(last_user.username[len(role_prefix):]) + 1

    # Đảm bảo username có đủ 10 ký tự, bao gồm cả prefix
    number_length = 10 - len(role_prefix) - len(str(new_id))
    return f"{role_prefix}{str(new_id).zfill(number_length)}"

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
    avatar = Column(String(255), nullable=True, default='https://res.cloudinary.com/ds05mb5xf/image/upload/v1734438824/avatar-default-symbolic-icon-479x512-n8sg74wg_rvl14k.png')
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
    students = relationship('Student', backref='user-', lazy=True)
    teachers = relationship('Teacher', backref='user-', lazy=True)
    employees = relationship('Employee', backref='user-', lazy=True)
    admin= relationship('Admin', backref='user-', lazy=True)

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
    students = relationship('Student', backref='class_relationship', lazy=True)


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
    # user = relationship('User', backref='student', uselist=False)
    results = relationship('Result', backref='student', lazy=True)
    # class_ = relationship('Class', backref='student_relationship')  # Mối quan hệ với Class



# Teacher Table
class Teacher(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    # Relationships
    # user = relationship('User', backref='teacher', uselist=False)
    subjects = relationship('Subject', secondary='teacher_subject', backref='teachers')  # Nhiều môn học

# Employee Table
class Employee(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    position = Column(String(100), nullable=True)

    # Relationships
    # user = relationship('User', backref='employee', uselist=False)




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

def create_fake_data():
    # 1. Tạo Admins
    admins = [
        {
            "name": "Nguyễn Thanh Nam",
            "dob": datetime(1990, 5, 15),
            "address": "Hà Nội",
            "phone": "0912345678",
            "email": "nam.nguyen@example.com",
        },
        {
            "name": "Lê Hoàng Phúc",
            "dob": datetime(1992, 8, 20),
            "address": "TP Hồ Chí Minh",
            "phone": "0919876543",
            "email": "phuc.le@example.com",
        },
    ]
    for admin in admins:
        user = User(
            username=generate_username("AD", UserRole.ADMIN),
            password="123456",
            name=admin["name"],
            sex=True,
            dob=admin["dob"],
            address=admin["address"],
            phone=admin["phone"],
            email=admin["email"],
            user_role=UserRole.ADMIN,
        )
        db.session.add(user)
        db.session.commit()

        admin_record = Admin(user_id=user.id)
        db.session.add(admin_record)
        db.session.commit()

    # 2. Tạo Employees
    employees = [
        {
            "name": "Trần Văn Hòa",
            "dob": datetime(1985, 6, 25),
            "address": "Đà Nẵng",
            "phone": "0987654321",
            "email": "hoa.tran@example.com",
        },
        {
            "name": "Phạm Minh Tuấn",
            "dob": datetime(1990, 10, 15),
            "address": "Cần Thơ",
            "phone": "0976543210",
            "email": "tuan.pham@example.com",
        },
    ]
    for emp in employees:
        user = User(
            username=generate_username("EM", UserRole.EMPLOYEE),
            password="123456",
            name=emp["name"],
            sex=True,
            dob=emp["dob"],
            address=emp["address"],
            phone=emp["phone"],
            email=emp["email"],
            user_role=UserRole.EMPLOYEE,
        )
        db.session.add(user)
        db.session.commit()

        employee_record = Employee(user_id=user.id, position="Nhân viên văn phòng")
        db.session.add(employee_record)
        db.session.commit()

    # 3. Tạo Grade Levels
    grade_levels = ["Lớp 10", "Lớp 11", "Lớp 12"]
    grade_level_objects = []
    for name in grade_levels:
        grade = GradeLevel(name=name)
        db.session.add(grade)
        db.session.commit()
        grade_level_objects.append(grade)

    # 4. Tạo Classes
    classes = [
        {"name": "10A1", "grade_level": grade_level_objects[0]},
        {"name": "11B2", "grade_level": grade_level_objects[1]},
        {"name": "12C3", "grade_level": grade_level_objects[2]},
    ]
    class_objects = []
    for cls in classes:
        class_item = Class(name=cls["name"], grade_level_id=cls["grade_level"].id)
        db.session.add(class_item)
        db.session.commit()
        class_objects.append(class_item)

    # 5. Tạo Students
    students = [
        {
            "name": "Nguyễn Thị Lan",
            "dob": datetime(2005, 4, 20),
            "address": "Hà Nội",
            "phone": "0912345670",
            "email": "lan.nguyen@example.com",
            "class": class_objects[0],
        },
        {
            "name": "Trần Minh Quân",
            "dob": datetime(2004, 11, 10),
            "address": "TP Hồ Chí Minh",
            "phone": "0912345671",
            "email": "quan.tran@example.com",
            "class": class_objects[1],
        },
        {
            "name": "Lê Thị Mai",
            "dob": datetime(2006, 2, 14),
            "address": "Đà Nẵng",
            "phone": "0912345672",
            "email": "mai.le@example.com",
            "class": class_objects[2],
        },
    ]
    for stu in students:
        user = User(
            username=generate_username("ST", UserRole.STUDENT),
            password="123456",
            name=stu["name"],
            sex=True,
            dob=stu["dob"],
            address=stu["address"],
            phone=stu["phone"],
            email=stu["email"],
            user_role=UserRole.STUDENT,
        )
        db.session.add(user)
        db.session.commit()

        student_record = Student(user_id=user.id, class_id=stu["class"].id)
        db.session.add(student_record)
        db.session.commit()

    # 6. Tạo Teachers
    teachers = [
        {
            "name": "Vũ Minh Tuân",
            "dob": datetime(1980, 1, 15),
            "address": "Hà Nội",
            "phone": "0934567890",
            "email": "tuan.vu@example.com",
        },
        {
            "name": "Đoàn Thị Mai",
            "dob": datetime(1975, 8, 30),
            "address": "Đà Nẵng",
            "phone": "0934567891",
            "email": "mai.doan@example.com",
        },
    ]
    for teacher in teachers:
        user = User(
            username=generate_username("TC", UserRole.TEACHER),
            password="123456",
            name=teacher["name"],
            sex=True,
            dob=teacher["dob"],
            address=teacher["address"],
            phone=teacher["phone"],
            email=teacher["email"],
            user_role=UserRole.TEACHER,
        )
        db.session.add(user)
        db.session.commit()

        teacher_record = Teacher(user_id=user.id)
        db.session.add(teacher_record)
        db.session.commit()

    # 7. Tạo Subjects
    subjects = ["Toán", "Ngữ văn", "Vật lý"]
    subject_objects = []
    for name in subjects:
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.commit()
        subject_objects.append(subject)

    # 8. Tạo Semesters
    semesters = ["Học kỳ 1", "Học kỳ 2"]
    for name in semesters:
        semester = Semester(name=name)
        db.session.add(semester)
        db.session.commit()

    # 6. Tạo Regulations
    regulations = [
        {"name": "Độ tuổi tối thiểu", "value": 15, "note": "Học sinh phải từ 15 tuổi trở lên"},
        {"name": "Độ tuổi tối đa", "value": 20, "note": "Học sinh không được quá 20 tuổi"},
        {"name": "Sĩ số tối đa mỗi lớp", "value": 40, "note": "Tối đa 40 học sinh trong một lớp học"},
        {"name": "Thời gian học tối đa", "value": 4, "note": "Thời gian học không quá 4 năm"}
    ]

    for regulation in regulations:
        regulation_item = Regulation(
            name=regulation["name"],
            value=regulation["value"],
            note=regulation["note"]
        )
        db.session.add(regulation_item)

    db.session.commit()  # Commit sau khi thêm tất cả các quy định


if __name__ == '__main__':
    with app.app_context():  # Đảm bảo có app context
        # db.create_all()  # Chạy để tạo DB
        # db.session.commit()
        create_fake_data()
        print("Dữ liệu giả đã được tạo thành công!")



