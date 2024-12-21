# Student_Management/app/index.py

from flask import request, redirect, render_template, flash, url_for,session,jsonify
from flask import Flask
from Student_Management.app import app,login,dao
from flask_login import login_user, logout_user, login_required
from Student_Management.app.models import UserRole,User


from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
from flask_login import current_user
from Student_Management.app.dao import *

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
def edit_score():
    return render_template('/teacher/edit_score.html')

@app.route('/get_subjects', methods=['GET'])
def get_subjects():
    try:
        # Lấy Teacher dựa trên current_user
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if not teacher:
            return jsonify({'error': 'User is not a teacher'}), 403

        # Lấy danh sách môn học
        subjects = Subject.query.join(TeacherSubject).filter(TeacherSubject.teacher_id == teacher.id).all()
        subject_list = [{'id': s.id, 'name': s.name} for s in subjects]
        return jsonify(subject_list)
    except Exception as e:
        print(f"Error fetching subjects: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/get_classes', methods=['GET'])
def get_classes():
    subject_id = request.args.get('subject_id')
    classes = ClassSubject.query.filter_by(subject_id=subject_id).all()
    class_list = [{'id': c.class_.id, 'name': c.class_.name} for c in classes]
    return jsonify(class_list)

@app.route('/get_semesters', methods=['GET'])
def get_semesters():
    subject_id = request.args.get('subject_id')
    semesters = SemesterSubject.query.filter_by(subject_id=subject_id).all()
    semester_list = [{'id': s.semester.id, 'name': s.semester.name} for s in semesters]
    return jsonify(semester_list)

@app.route('/get_students', methods=['GET'])
def get_students():
    try:
        class_id = request.args.get('class_id', type=int)
        subject_id = request.args.get('subject_id', type=int)

        if not class_id or not subject_id:
            return jsonify({'error': 'Missing class_id or subject_id'}), 400

        # Truy vấn danh sách học sinh thuộc lớp và môn học
        students = Student.query.join(StudentSubject).filter(
            StudentSubject.subject_id == subject_id,
            Student.class_id == class_id
        ).all()

        # Trả về danh sách học sinh
        student_list = [{'id': s.id, 'name': s.user.name} for s in students]
        return jsonify(student_list)

    except Exception as e:
        print(f"Error fetching students: {e}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == "__main__":
    app.run(debug=True)