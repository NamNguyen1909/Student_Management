# Student_Management/app/dao.py

import hashlib
from Student_Management.app import app, db
from Student_Management.app.models import *
import cloudinary.uploader
from flask_login import current_user


def auth_user(username,password,role=None):
    password = generate_md5_hash(password)

    u= User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password))
    if role:
        u=u.filter(User.user_role.__eq__(role))

    return u.first()

def teach(teacher_id, subject_id):
    # Kiểm tra xem mối quan hệ đã tồn tại chưa (giảng viên đã dạy môn học này chưa)
    existing_relation = TeacherSubject.query.filter_by(teacher_id=teacher_id, subject_id=subject_id).first()
    if existing_relation:
        print(f"Giảng viên {teacher_id} đã dạy môn {subject_id} rồi.")
    else:
        # Tạo mối quan hệ mới giữa giảng viên và môn học
        new_relation = TeacherSubject(teacher_id=teacher_id, subject_id=subject_id)
        db.session.add(new_relation)
        db.session.commit()
        print(f"Đã thêm giảng viên {teacher_id} dạy môn {subject_id}.")



# =================================================================================================================

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


# =================================================================================================================

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
            password=generate_md5_hash("123456"),
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
            password=generate_md5_hash("123456"),
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
            password=generate_md5_hash("123456"),
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

    # 6. Tạo Subjects
    subjects = ["Toán", "Ngữ văn", "Vật lý","Sinh học","Nhạc","Mĩ thuật","Tiếng anh","Tiếng pháp","GDCD"]
    subject_objects = []
    for name in subjects:
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.commit()
        subject_objects.append(subject)

    # 7. Tạo Teachers
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
            password=generate_md5_hash("123456"),
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

        # Giảng viên này sẽ dạy các môn học
        teach(teacher_record.id, subject_objects[0].id)  # Giảng viên dạy môn Toán
        teach(teacher_record.id, subject_objects[1].id)  # Giảng viên dạy môn Ngữ văn
        teach(teacher_record.id, subject_objects[2].id)  # Giảng viên dạy môn Vật lý

    # 8. Tạo Semesters
    semesters = [
        {"name": "Học kỳ 1", "year": "2024-2025"},
        {"name": "Học kỳ 2", "year": "2024-2025"}
    ]

    # Thêm từng học kỳ vào database
    for semester_data in semesters:
        name = semester_data["name"]  # Lấy giá trị name
        year = semester_data["year"]  # Lấy giá trị year
        semester = Semester(name=name, year=year)  # Tạo đối tượng Semester
        db.session.add(semester)  # Thêm vào phiên giao dịch
        db.session.commit()  # Lưu tất cả thay đổi

    # 6. Tạo Regulations
    regulations = [
        {"name": "Độ tuổi tối thiểu", "value": 15, "note": "Học sinh phải từ 15 tuổi trở lên"},
        {"name": "Độ tuổi tối đa", "value": 20, "note": "Học sinh không được quá 20 tuổi"},
        {"name": "Sĩ số tối đa mỗi lớp", "value": 40, "note": "Tối đa 40 học sinh trong một lớp học"}
    ]

    for regulation in regulations:
        regulation_item = Regulation(
            name=regulation["name"],
            value=regulation["value"],
            note=regulation["note"]
        )
        db.session.add(regulation_item)
        db.session.commit()  # Commit sau khi thêm tất cả các quy định
    print("Dữ liệu giả đã được tạo thành công!")

if __name__ == '__main__':
    with app.app_context():
        create_fake_data()