from flask import request, redirect, render_template, flash, url_for, jsonify
from app import login, dao
from flask_login import login_user, logout_user, login_required
from app.dao import *
from sqlalchemy.exc import SQLAlchemyError

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
                return redirect('/admin')
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
    return render_template('employee/employee.html', UserRole=UserRole)

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

        if current_user.user_role == UserRole.TEACHER:
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

@app.route('/api/check-or-create-result', methods=['POST'])
@login_required
def check_or_create_result():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        subject_id = data.get('subject_id')
        semester_id = data.get('semester_id')

        if not student_id or not subject_id or not semester_id:
            return jsonify({'error': 'Missing student_id, subject_id, or semester_id'}), 400

        # Kiểm tra xem Result đã tồn tại chưa
        result = Result.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            semester_id=semester_id
        ).first()

        if not result:
            # Nếu chưa tồn tại, tạo mới Result
            result = Result(
                student_id=student_id,
                subject_id=subject_id,
                semester_id=semester_id
            )
            db.session.add(result)
            db.session.commit()

            # Tạo 3 ScoreDetail mặc định
            score_types = [1, 2, 3]  # 1: 15 phút, 2: 45 phút, 3: điểm thi
            for score_type_id in score_types:
                score_detail = ScoreDetail(
                    result_id=result.id,
                    score_type_id=score_type_id,
                    value=0  # Điểm mặc định
                )
                db.session.add(score_detail)

            db.session.commit()

        # Lấy thông tin ScoreDetail
        score_details = ScoreDetail.query.filter_by(result_id=result.id).all()
        score_details_list = [
            {
                'id': sd.id,
                'score_type_id': sd.score_type_id,
                'value': sd.value
            } for sd in score_details
        ]

        return jsonify({
            'id': result.id,
            'score_details': score_details_list
        })

    except SQLAlchemyError as e:
        print(f"Error checking/creating result: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/save-scores', methods=['POST'])
@login_required
def save_scores():
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'error': 'Invalid input format'}), 400

        for item in data:
            student_id = item.get('student_id')
            subject_id = item.get('subject_id')
            semester_id = item.get('semester_id')
            scores = item.get('scores')

            if not student_id or not subject_id or not semester_id or not scores:
                print(data)
                return jsonify({'error': 'Missing required fields'}), 400

            # Kiểm tra hoặc tạo Result
            result = Result.query.filter_by(
                student_id=student_id,
                subject_id=subject_id,
                semester_id=semester_id
            ).first()

            if not result:
                return jsonify({'error': 'Result not found'}), 404

            # Xử lý từng điểm
            for score in scores:
                score_type_id = score.get('score_type_id')
                value = score.get('value')

                if score_type_id is None or value is None:
                    continue

                score_detail = ScoreDetail.query.filter_by(
                    result_id=result.id,
                    score_type_id=score_type_id
                ).first()

                if not score_detail:
                    score_detail = ScoreDetail(
                        result_id=result.id,
                        score_type_id=score_type_id,
                        value=value
                    )
                    db.session.add(score_detail)
                else:
                    score_detail.value = value

        db.session.commit()

        #Cập nhật điểm trung bình
        calculate_average(result.id)
        db.session.commit()

        return jsonify({'message': 'Scores saved successfully'}), 200

    except SQLAlchemyError as e:
        print(f"Error saving scores: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/view_score', methods=['GET', 'POST'])
def view_score():
    if request.method == 'POST':
        # Lấy thông tin từ form
        class_id = request.form.get('class_id')
        year = request.form.get('year')

        # Lấy tất cả các semester.id tương ứng với year đã chọn
        semesters = Semester.query.filter_by(year=year).all()
        semester_ids = [s.id for s in semesters]

        # Lấy danh sách học sinh của lớp được chọn
        students = Student.query.filter_by(class_id=class_id).all()

        # Tính điểm trung bình cho từng học sinh theo học kỳ
        results_data = []
        for student in students:
            user = User.query.get(student.user_id)  # Lấy thông tin User
            averages = {}
            for semester_id in semester_ids:
                results = Result.query.filter_by(student_id=student.id, semester_id=semester_id).all()
                if results:
                    averages[semester_id] = sum([r.average for r in results if r.average]) / len(results)
                else:
                    averages[semester_id] = None

            results_data.append({
                'name': user.name,
                'class_name': Class.query.get(class_id).name,
                'averages': averages
            })

        return render_template('/teacher/view_score.html', results=results_data, year=year, semester_ids=semester_ids, classes=Class.query.all(), years=Semester.query.with_entities(Semester.year).distinct().all())

    # GET request: Hiển thị form chọn lớp và năm học
    return render_template('/teacher/view_score.html', classes=Class.query.all(), years=Semester.query.with_entities(Semester.year).distinct().all())

# =============================================================================


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
    from app.admin import *
    app.run(debug=True)