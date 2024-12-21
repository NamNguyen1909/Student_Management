from flask import Flask, request, redirect, render_template, flash, url_for, session, jsonify
from app import app, login, dao
from flask_login import login_user, logout_user, login_required
from app.models import UserRole, User, Teacher, Subject, TeacherSubject, ClassSubject, SemesterSubject, Student, StudentSubject, db
from app.dao import *
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)

            # Chuyển hướng dựa trên vai trò
            if user.user_role == UserRole.ADMIN:
                return redirect(url_for('admin_dashboard'))
            elif user.user_role == UserRole.STUDENT:
                return redirect(url_for('student_dashboard'))
            elif user.user_role == UserRole.TEACHER:
                return redirect(url_for('teacher_dashboard'))
            elif user.user_role == UserRole.EMPLOYEE:
                return redirect(url_for('employee_dashboard'))

            flash('Role not recognized!', 'danger')
            return redirect(url_for('login_process'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')

@app.route("/admin")
@login_required
def admin_dashboard():
    return render_template('admin/admin.html', UserRole=UserRole)

@app.route("/student")
@login_required
def student_dashboard():
    return render_template('/student/student.html', UserRole=UserRole)

@app.route("/teacher")
@login_required
def teacher_dashboard():
    return render_template('teacher/teacher.html', UserRole=UserRole)

@app.route("/employee")
@login_required
def employee_dashboard():
    classes = dao.employee_classes()
    return render_template('employee/employee.html', UserRole=UserRole, classes=classes)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    if request.method == "POST":
        # Lấy mật khẩu mới từ biểu mẫu
        new_password = request.form["new_password"]
        # Mã hóa mật khẩu mới
        hashed_password = generate_md5_hash(new_password)

        # Cập nhật mật khẩu trong cơ sở dữ liệu
        current_user.password = hashed_password
        db.session.commit()

        flash("Mật khẩu đã được thay đổi thành công!", "success")

        # Kiểm tra vai trò của người dùng và chuyển hướng tới trang tương ứng
        if current_user.user_role == UserRole.ADMIN:
            return redirect("/admin")
        elif current_user.user_role == UserRole.TEACHER:
            return redirect("/teacher")
        elif current_user.user_role == UserRole.EMPLOYEE:
            return redirect("/employee")
        elif current_user.user_role == UserRole.STUDENT:
            return redirect("/student")
        else:
            return redirect("/")  # Default redirect

    return render_template("changepassword.html")

@app.route('/teacher/editscore')
@login_required
def edit_score():
    return render_template('teacher/edit_score.html')

# API: Lấy danh sách môn học theo giáo viên
@app.route('/api/get-subjects', methods=['GET'])
@login_required
def get_subjects():
    try:
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if not teacher:
            return jsonify({'error': 'User is not a teacher'}), 403

        subjects = Subject.query.join(TeacherSubject).filter(TeacherSubject.teacher_id == teacher.id).all()
        subject_list = [{'id': s.id, 'name': s.name} for s in subjects]
        return jsonify(subject_list)
    except SQLAlchemyError as e:
        print(f"Error fetching subjects: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/get-classes/<int:subject_id>', methods=['GET'])
@login_required
def get_classes(subject_id):
    if not subject_id:
        return jsonify({'error': 'Missing subject_id'}), 400

    try:
        classes = ClassSubject.query.filter_by(subject_id=subject_id).all()
        class_list = [{'id': c.class_.id, 'name': c.class_.name} for c in classes]
        return jsonify(class_list)
    except SQLAlchemyError as e:
        print(f"Error fetching classes: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/get-semesters', methods=['GET'])
@app.route('/api/get-semesters/<int:subject_id>', methods=['GET'])
def get_semesters(subject_id=None):
    try:
        if not subject_id:
            subject_id = request.args.get('subject_id', type=int)

        if not subject_id:
            return jsonify({'error': 'Missing subject_id'}), 400

        # Debug dữ liệu đầu vào
        print(f"Fetching semesters for subject_id: {subject_id}")

        # Lấy danh sách các học kỳ liên quan đến môn học
        semester_subjects = SemesterSubject.query.filter_by(subject_id=subject_id).all()
        if not semester_subjects:
            return jsonify({'message': 'No semesters found for this subject'}), 404

        # Tạo danh sách học kỳ để trả về
        semesters = [{'id': ss.semester.id, 'name': ss.semester.name, 'year': ss.semester.year}
                     for ss in semester_subjects]

        # Debug dữ liệu trả về
        print(f"Semesters found: {semesters}")

        return jsonify(semesters)
    except SQLAlchemyError as e:
        print(f"Database Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/get-semester-year', methods=['GET'])
def get_semester_year():
    semester_id = request.args.get('semester_id')
    subject_id = request.args.get('subject_id')

    # Truy vấn thông tin học kỳ và môn học
    semester_subject = db.session.query(SemesterSubject).filter_by(
        semester_id=semester_id,
        subject_id=subject_id
    ).first()

    if semester_subject:
        return jsonify({
            'semester_name': semester_subject.semester.name,
            'year': semester_subject.semester.year
        })
    else:
        return jsonify({'error': 'Không tìm thấy thông tin'}), 404




@app.route('/api/get-students', methods=['GET'])
@login_required
def get_students():
    try:
        class_id = request.args.get('class_id', type=int)
        subject_id = request.args.get('subject_id', type=int)

        if not class_id or not subject_id:
            return jsonify({'error': 'Missing class_id or subject_id'}), 400

        # Lấy danh sách học sinh trong lớp và môn học
        students = Student.query.join(StudentSubject).filter(
            StudentSubject.subject_id == subject_id,
            Student.class_id == class_id
        ).all()

        student_list = [{'id': s.id, 'name': s.user.name} for s in students]
        return jsonify(student_list)
    except SQLAlchemyError as e:
        print(f"Error fetching students: {e}")
        return jsonify({'error': 'Internal server error'}), 500




@app.route('/api/get-scores', methods=['GET'])
@login_required
def get_scores():
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    semester_id = request.args.get('semester_id', type=int)

    if not all([class_id, subject_id, semester_id]):
        return jsonify({'error': 'Missing parameters'}), 400

    students = Student.query.filter_by(class_id=class_id).all()
    score_types = ScoreType.query.all() # Lấy tất cả các loại điểm

    student_data = []
    for student in students:
        result = Result.query.filter_by(
            student_id=student.id, subject_id=subject_id, semester_id=semester_id
        ).first()

        scores = {}
        if result:
            for score_detail in result.score_details:
                scores[score_detail.score_type.name] = score_detail.value

        student_data.append({
            'id': student.id,
            'name': student.user.name,
            'scores': scores
        })
    return jsonify({'students': student_data, 'score_types': [{'id': st.id, 'name': st.name} for st in score_types]})



@app.route('/api/save-scores', methods=['POST'])
@login_required
def save_scores():
    data = request.get_json()
    class_id = data.get('class_id')
    subject_id = data.get('subject_id')
    semester_id = data.get("semester_id")
    student_scores = data.get('student_scores')

    for student_score in student_scores:
        student_id = student_score['id']
        scores = student_score['scores']

        result = Result.query.filter_by(student_id=student_id, subject_id=subject_id, semester_id=semester_id).first()
        if not result:
            result = Result(student_id=student_id, subject_id=subject_id, semester_id=semester_id)
            db.session.add(result)
            db.session.flush() # để lấy id của result vừa tạo

        for score_type_name, value in scores.items():
            score_type = ScoreType.query.filter_by(name=score_type_name).first()
            if score_type:
                score_detail = ScoreDetail.query.filter_by(result_id=result.id, score_type_id=score_type.id).first()
                if not score_detail:
                    score_detail = ScoreDetail(result_id=result.id, score_type_id=score_type.id, value=value)
                    db.session.add(score_detail)
                else:
                    score_detail.value = value

    db.session.commit()
    return jsonify({'message': 'Scores saved successfully'})



# @app.route('/employee/register_student')
# @login_required
# def register_student():
#     return render_template('/employee/register_student.html')

@app.route('/employee/create_class')
@login_required
def create_class():
    return render_template('/employee/create_class.html')


# @app.route('/register_student', methods=['GET', 'POST'])
# def register_student():
#     err_msg = ''
#     if request.method == 'POST':
#         username = request.form.get('username')
#         full_name = request.form.get('full_name')
#         dob = request.form.get('dob')
#         gender = request.form.get('gender')
#         address = request.form.get('address')
#         phone = request.form.get('phone')
#         email = request.form.get('email')
#         class_id = request.form.get('class_id')
#         password = request.form.get('password')
#
#         dob = datetime.strptime(dob, '%Y-%m-%d')
#
#         if not check_regulation_for_student(dob):
#             err_msg = 'Độ tuổi không hợp lệ. Học sinh phải từ 15 đến 20 tuổi.'
#         else:
#             # Thêm người dùng vào bảng User
#             user = User(
#                 username=username,
#                 password=password,
#                 name=full_name,
#                 dob=dob,
#                 sex=True if gender == 'male' else False,
#                 address=address,
#                 phone=phone,
#                 email=email
#             )
#             db.session.add(user)
#             db.session.commit()
#
#             # Thêm học sinh vào bảng Student
#             try:
#                 create_student_record(user.id, class_id)
#                 flash("Học sinh đã được thêm thành công!", "success")
#                 return redirect(url_for('register_student'))  # Redirect to the same page or any other page
#             except ValueError as e:
#                 err_msg = str(e)
#
#     return render_template('employee/register_student.html', err_msg=err_msg)


@app.route('/employee/register_student', methods=['GET', 'POST'])
@login_required
def register_student():
    err_msg = ''
    if request.method == 'POST':
        # Lấy thông tin từ form
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        address = request.form.get('address')
        phone = request.form.get('phone')
        email = request.form.get('email')
        class_id = request.form.get('class_id')
        password = request.form.get('password')

        # Chuyển đổi dob thành datetime
        dob = datetime.strptime(dob, '%Y-%m-%d')

        # Kiểm tra độ tuổi hợp lệ
        if not check_regulation_for_student(dob):
            err_msg = 'Độ tuổi không hợp lệ. Học sinh phải từ 15 đến 20 tuổi.'
        else:
            # Thêm người dùng vào bảng User
            user = User(
                username=generate_username("ST", UserRole.STUDENT),
                password=generate_md5_hash(password),
                name=full_name,
                dob=dob,
                sex=True if gender == 'male' else False,
                address=address,
                phone=phone,
                email=email
            )
            db.session.add(user)
            db.session.commit()

            # Thêm học sinh vào bảng Student
            try:
                create_student_record(user.id, class_id)
                flash("Học sinh đã được thêm thành công!", "success")
                return redirect(url_for('register_student'))  # Redirect to the same page or any other page
            except ValueError as e:
                err_msg = str(e)

    return render_template('employee/register_student.html', err_msg=err_msg)



if __name__ == "__main__":
    app.run(debug=True, port=5001)
