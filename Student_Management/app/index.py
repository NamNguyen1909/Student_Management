# Student_Management/app/index.py

from flask import request, redirect, render_template, flash, url_for
from flask import Flask
from Student_Management.app import app,login,dao
from flask_login import login_user, logout_user, login_required
from Student_Management.app.models import UserRole,User



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
    return render_template('admin.html')

@app.route("/student")
@login_required
def student_dashboard():
    return render_template('student.html')

@app.route("/teacher")
@login_required
def teacher_dashboard():
    return render_template('teacher.html')

@app.route("/employee")
@login_required
def employee_dashboard():
    return render_template('employee.html')

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)