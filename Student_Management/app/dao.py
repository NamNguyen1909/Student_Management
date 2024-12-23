# Student_Management/app/dao.py

import hashlib
from sqlalchemy import false
from app import app, db
from app.models import *
from sqlalchemy.orm import joinedload


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

def calculate_average(result_id):
    # Lấy Result từ database
    result = Result.query.options(
        joinedload(Result.score_details).joinedload(ScoreDetail.score_type)
    ).filter_by(id=result_id).first()

    if not result:
        return {"error": "Result not found."}, 404

    # Tính toán điểm trung bình
    total_weighted_score = 0
    total_weight = 0

    for score_detail in result.score_details:
        if score_detail.value is not None:
            weight = score_detail.score_type.weight
            total_weighted_score += score_detail.value * weight
            total_weight += weight

    if total_weight == 0:
        result.average = None  # Không có trọng số hợp lệ
    else:
        result.average = total_weighted_score / total_weight

    # Lưu kết quả vào database
    db.session.commit()

    return {"message": "Average calculated successfully.", "average": result.average}



# ==========================================================================================================================

def assign_subject_to_class(class_id, subject_id):
    """
    Tạo mối quan hệ giữa một lớp học và một môn học.

    Args:
        class_id (int): ID của lớp học.
        subject_id (int): ID của môn học.

    Returns:
        str: Thông báo về trạng thái của mối quan hệ.
    """
    # Kiểm tra xem mối quan hệ đã tồn tại chưa
    existing_relation = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
    if existing_relation:
        return f"Lớp {class_id} đã có môn {subject_id}."
    else:
        # Tạo mối quan hệ mới giữa lớp học và môn học
        new_relation = ClassSubject(class_id=class_id, subject_id=subject_id)
        db.session.add(new_relation)
        db.session.commit()
        print(f"Đã thêm môn {subject_id} vào lớp {class_id}.")


def enroll_student_to_subject(student_id, subject_id):
    # Kiểm tra xem mối quan hệ đã tồn tại chưa (sinh viên đã đăng ký môn học này chưa)
    existing_relation = StudentSubject.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if existing_relation:
        print(f"Sinh viên {student_id} đã đăng ký môn {subject_id} rồi.")
    else:
        # Tạo mối quan hệ mới giữa sinh viên và môn học
        new_relation = StudentSubject(student_id=student_id, subject_id=subject_id)
        db.session.add(new_relation)
        db.session.commit()
        print(f"Đã thêm sinh viên {student_id} vào môn {subject_id}.")


def assign_subject_to_semester(semester_id, subject_id):
    # Kiểm tra xem mối quan hệ đã tồn tại chưa (môn học đã thuộc về học kỳ này chưa)
    existing_relation = SemesterSubject.query.filter_by(semester_id=semester_id, subject_id=subject_id).first()
    if existing_relation:
        print(f"Môn học {subject_id} đã được thêm vào học kỳ {semester_id} rồi.")
    else:
        # Tạo mối quan hệ mới giữa học kỳ và môn học
        new_relation = SemesterSubject(semester_id=semester_id, subject_id=subject_id)
        db.session.add(new_relation)
        db.session.commit()
        print(f"Đã thêm môn {subject_id} vào học kỳ {semester_id}.")


def create_student_record(user_id, class_id):
    """
    Hàm tạo Student record từ User và Class ID.
    Tự động lấy GradeLevelId từ Class ID và tăng si_so của lớp.
    """
    # Lấy Class object từ class_id
    class_object = Class.query.get(class_id)

    if not class_object:
        raise ValueError("Class ID không tồn tại")

    # Lấy GradeLevelId từ Class
    grade_level_id = class_object.grade_level_id

    # Tạo Student record
    student_record = Student(user_id=user_id, class_id=class_id, grade_level_id=grade_level_id)
    db.session.add(student_record)

    # Tăng si_so của Class
    class_object.si_so += 1
    db.session.add(class_object)

    # Commit cả hai thay đổi
    db.session.commit()

# ==========================================================================================================================

def assign_subject_to_class(class_id, subject_id):
    """
    Tạo mối quan hệ giữa một lớp học và một môn học.

    Args:
        class_id (int): ID của lớp học.
        subject_id (int): ID của môn học.

    Returns:
        str: Thông báo về trạng thái của mối quan hệ.
    """
    # Kiểm tra xem mối quan hệ đã tồn tại chưa
    existing_relation = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
    if existing_relation:
        return f"Lớp {class_id} đã có môn {subject_id}."
    else:
        # Tạo mối quan hệ mới giữa lớp học và môn học
        new_relation = ClassSubject(class_id=class_id, subject_id=subject_id)
        db.session.add(new_relation)
        db.session.commit()
        print(f"Đã thêm môn {subject_id} vào lớp {class_id}.")

def enroll_student_to_subject(student_id, subject_id):
    # Kiểm tra xem mối quan hệ đã tồn tại chưa (sinh viên đã đăng ký môn học này chưa)
    existing_relation = StudentSubject.query.filter_by(student_id=student_id, subject_id=subject_id).first()
    if existing_relation:
        print(f"Sinh viên {student_id} đã đăng ký môn {subject_id} rồi.")
    else:
        # Tạo mối quan hệ mới giữa sinh viên và môn học
        new_relation = StudentSubject(student_id=student_id, subject_id=subject_id)
        db.session.add(new_relation)
        db.session.commit()
        print(f"Đã thêm sinh viên {student_id} vào môn {subject_id}.")

def assign_subject_to_semester(semester_id, subject_id):
    # Kiểm tra xem mối quan hệ đã tồn tại chưa (môn học đã thuộc về học kỳ này chưa)
    existing_relation = SemesterSubject.query.filter_by(semester_id=semester_id, subject_id=subject_id).first()
    if existing_relation:
        print(f"Môn học {subject_id} đã được thêm vào học kỳ {semester_id} rồi.")
    else:
        # Tạo mối quan hệ mới giữa học kỳ và môn học
        new_relation = SemesterSubject(semester_id=semester_id, subject_id=subject_id)
        db.session.add(new_relation)
        db.session.commit()
        print(f"Đã thêm môn {subject_id} vào học kỳ {semester_id}.")

def create_student_record(user_id, class_id):
    """
    Hàm tạo Student record từ User và Class ID.
    Tự động lấy GradeLevelId từ Class ID và tăng si_so của lớp.
    """
    # Lấy Class object từ class_id
    class_object = Class.query.get(class_id)

    if not class_object:
        raise ValueError("Class ID không tồn tại")

    # Lấy GradeLevelId từ Class
    grade_level_id = class_object.grade_level_id

    # Tạo Student record
    student_record = Student(user_id=user_id, class_id=class_id, grade_level_id=grade_level_id)
    db.session.add(student_record)

    # Tăng si_so của Class
    class_object.si_so += 1
    db.session.add(class_object)

    # Commit cả hai thay đổi
    db.session.commit()


# =================================================================================================================



# =================================================================================================================

def generate_username(role_prefix, user_role):
    """
    Tạo username dạng 'ST000001', 'TC000001' dựa trên role_prefix và user_role.
    """
    while True:
        # Lấy user cuối cùng thuộc role cụ thể
        last_user = User.query.filter_by(user_role=user_role).order_by(User.id.desc()).first()

        if not last_user or not last_user.username:
            new_id = 1
        else:
            try:
                new_id = int(last_user.username[len(role_prefix):]) + 1
            except ValueError:
                new_id = 1  # Phòng trường hợp username trước đó không hợp lệ

        # Đảm bảo username có đủ 10 ký tự
        number_length = 10 - len(role_prefix)
        new_username = f"{role_prefix}{str(new_id).zfill(number_length)}"

        # Kiểm tra xem username có tồn tại không
        if not User.query.filter_by(username=new_username).first():
            return new_username


def deactivate_user(model):
    """Hàm này sẽ set is_active của người dùng thành False và cập nhật end_date"""
    if model.is_active:  # Nếu người dùng hiện tại đang hoạt động
        model.is_active = False
        model.end_date = datetime.now()  # Gán end_date bằng thời gian hiện tại
        db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
        print(f"User {model.username} has been deactivated and end_date has been set.")
    else:
        print(f"User {model.username} is already deactivated.")

# =================================================================================================================

def employee_classes():
    # Lấy danh sách lớp học từ database
    classes = Class.query.all()
    return classes

# Check quy định
def check_regulation_for_student(dob: datetime) -> bool:
    # Lấy quy định độ tuổi từ bảng Regulation
    age_min_regulation = db.session.query(Regulation).filter(Regulation.name == "Độ tuổi tối thiểu").first()
    age_max_regulation = db.session.query(Regulation).filter(Regulation.name == "Độ tuổi tối đa").first()

    if age_min_regulation and age_max_regulation:
        min_age = age_min_regulation.value
        max_age = age_max_regulation.value
        age = (datetime.now() - dob).days // 365

        if min_age <= age <= max_age:
            return True
        else:
            return False
    else:
        return False

def check_class_capacity(class_id):
    class_ = db.session.query(Class).filter_by(id=class_id).first()
    if class_ and class_.si_so >= 40:
        return False
    return True
# =================================================================================================================


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
            "class_id": class_objects[0].id,
        },
        {
            "name": "Trần Minh Quân",
            "dob": datetime(2004, 11, 10),
            "address": "TP Hồ Chí Minh",
            "phone": "0912345671",
            "email": "quan.tran@example.com",
            "class_id": class_objects[1].id,
        },
        {
            "name": "Lê Thị Mai",
            "dob": datetime(2006, 2, 14),
            "address": "Đà Nẵng",
            "phone": "0912345672",
            "email": "mai.le@example.com",
            "class_id": class_objects[2].id,
        },
    ]

    # Duyệt qua từng student và tạo record
    for stu in students:
        # Tạo User
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

        # Tạo Student record
        create_student_record(user.id, stu["class_id"])

    # 6. Tạo Subjects
    subjects = ["Toán", "Ngữ văn", "Vật lý","Sinh học","Nhạc","Mĩ thuật","Tiếng anh","Tiếng pháp","GDCD"]
    subject_objects = []
    for name in subjects:
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.commit()
        subject_objects.append(subject)
    # Gán môn học vào các lớp
    for class_item in class_objects:
        for subject in subject_objects:
            assign_subject_to_class(class_item.id, subject.id)
    db.session.commit()

    # Gán sinh viên vào môn học
    student_objects = Student.query.all()  # Lấy tất cả sinh viên đã tạo
    for student in student_objects:
        for subject in subject_objects[:5]:  # Gán mỗi sinh viên học 5 môn đầu tiên (ví dụ)
            enroll_student_to_subject(student.id, subject.id)
    db.session.commit()


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

    # Gán môn học vào học kỳ
    semester_objects = Semester.query.all()  # Lấy tất cả học kỳ đã tạo
    for semester in semester_objects:
        for subject in subject_objects:
            assign_subject_to_semester(semester.id, subject.id)
    db.session.commit()

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

    # 7. Tạo ScoreType
    score_types = [
        {"name": "Điểm 15 phút", "weight": 1},
        {"name": "Điểm 45 phút", "weight": 2},
        {"name": "Điểm thi", "weight": 3},
    ]

    for st in score_types:
        # Kiểm tra nếu ScoreType chưa tồn tại để tránh trùng lặp
        existing_score_type = ScoreType.query.filter_by(name=st["name"]).first()
        if not existing_score_type:
            score_type = ScoreType(name=st["name"], weight=st["weight"])
            db.session.add(score_type)

    # Lưu thay đổi vào cơ sở dữ liệu
    db.session.commit()

def get_class_data_by_grade():
    classes = db.session.query(Class).all()

    class_data_by_grade = {
        '10': [],
        '11': [],
        '12': []
    }

    for class_ in classes:
        grade = class_.name[:2]  # Lấy 2 ký tự đầu tiên làm khối lớp
        students = db.session.query(Student).join(User).filter(
            Student.class_id == class_.id,
            User.is_active == True
        ).all()

        student_details = [
            {
                'id': student.id,
                'name': student.user.name,
                'sex': 'Nam' if student.user.sex else 'Nữ',
                'dob': student.user.dob.strftime('%Y') if student.user.dob else 'N/A',
                'address': student.user.address or 'N/A'
            }
            for student in students
        ]

        # Thêm lớp vào khối tương ứng
        if grade in class_data_by_grade:
            class_data_by_grade[grade].append({
                'class_name': class_.name,
                'si_so': class_.si_so,
                'students': student_details
            })

    return class_data_by_grade, classes


def remove_student_data(student_id):
    student = db.session.query(Student).filter_by(id=student_id).first()

    if student:
        student.user.end_date = datetime.now()
        student.user.is_active = False

        if student.class_id:
            class_ = db.session.query(Class).filter_by(id=student.class_id).first()
            if class_ and class_.si_so > 0:
                class_.si_so -= 1
        db.session.commit()
        return True, 'Học sinh đã bị xóa thành công!'
    else:
        return False, 'Không tìm thấy học sinh!'

# def remove_student_from_class(student_id):
#     student = db.session.query(Student).filter_by(id=student_id).first()
#
#     if student:
#         # Cập nhật sĩ số của lớp trước khi xóa học sinh
#         class_ = db.session.query(Class).filter_by(id=student.class_id).first()
#         if class_:
#             class_.si_so -= 1
#
#         # Xóa học sinh khỏi lớp (cập nhật class_id thành None)
#         student.is_active = 0
#         db.session.commit()

def transfer_student(student_id, new_class_id):
    student = db.session.query(Student).filter_by(id=student_id).first()

    if not student:
        return False, "Không tìm thấy học sinh!"

    if not new_class_id or new_class_id == student.class_id:
        return False, "Học sinh đã ở trong lớp này!"

    # Lớp cũ
    old_class = db.session.query(Class).filter_by(id=student.class_id).first()
    if old_class and old_class.si_so > 0:
        old_class.si_so -= 1

    # Lớp mới
    new_class = db.session.query(Class).filter_by(id=new_class_id).first()
    if not new_class:
        return False, "Không tìm thấy lớp học mới!"

    if new_class.si_so >= 40:
        return False, "Lớp học đã đầy, không thể chuyển học sinh vào!"

    # Cập nhật thông tin lớp của học sinh
    student.class_id = new_class_id
    new_class.si_so += 1

    db.session.commit()
    return True, "Chuyển lớp thành công!"

# Các hàm tạo lớp học
def get_all_grade_levels():
    return db.session.query(GradeLevel).all()

def get_class_by_name(class_name):
    return db.session.query(Class).filter_by(name=class_name).first()

def create_new_class(class_name, grade_level_id):
    new_class = Class(name=class_name, grade_level_id=int(grade_level_id))
    db.session.add(new_class)
    db.session.commit()
    return new_class

if __name__ == '__main__':
    with app.app_context():
        create_fake_data()