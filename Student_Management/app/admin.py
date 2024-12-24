# Student_Management/app/admin.py

from flask import redirect, session
from flask_admin import BaseView, expose, AdminIndexView, Admin
from flask_sqlalchemy.model import Model
from sqlalchemy import values

from app import app, db
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from app.models import UserRole, User, Class, Regulation, Employee, Teacher, Student,Semester


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class AuthenticatedAdminView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html',current_user=current_user)

class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class HomeView(AuthenticatedView):
    @expose('/')
    def index(self):
        return redirect('/')

class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        session.clear()
        return redirect('/login')


def format_sex(view, context, model, name):
    return "Nam" if model.sex else "Nữ"

def format_role_sex(view, context, model, name):
    return "Nam" if model.user.sex else "Nữ"

class UserView(AuthenticatedAdmin):
    can_create = True
    can_edit = True
    can_delete = False
    column_searchable_list = ['username', 'name']
    column_list = ('username', 'name', 'sex', 'dob', 'address', 'phone', 'email', 'user_role')
    column_labels = {
        'username': 'Tên đăng nhập',
        'name': 'Họ tên',
        'sex': 'Giới tính',
        'dob': 'Ngày sinh',
        'address': 'Địa chỉ',
        'phone': 'SĐT',
        'user_role': 'Vai trò'
    }
    column_formatters = {
        'sex': format_sex
    }

    def on_model_change(self, form, model, is_created):
        if is_created:
            # Hash the password
            model.set_password(form.password.data)
            db.session.add(model)
            db.session.commit()
            # Create the related role object based on the user_role
            if model.user_role == UserRole.STUDENT:
                print("Creating Student object...")
                student = Student(user=model)  # Automatically sets user_id
                db.session.add(student)
            elif model.user_role == UserRole.TEACHER:
                print("Creating Teacher object...")
                teacher = Teacher(user=model)  # Automatically sets user_id
                db.session.add(teacher)
            elif model.user_role == UserRole.EMPLOYEE:
                print("Creating Employee object...")
                employee = Employee(user=model)  # Automatically sets user_id
                db.session.add(employee)

            # Commit changes
            try:
                db.session.commit()
                print("Commit successful!")
            except Exception as e:
                print(f"Error during commit: {e}")
                db.session.rollback()

        return super(UserView, self).on_model_change(form, model, is_created)



class EmployeeView(AuthenticatedAdmin):
    can_create = False
    can_edit = True
    can_delete = False
    column_searchable_list = ['user.username', 'user.name', 'position']
    column_list = ('user.username', 'user.name', 'user.sex', 'user.dob', 'user.phone', 'position')
    column_labels = {
        'user.username': 'Tên đăng nhập',
        'user.name': 'Họ tên',
        'user.sex': 'Giới tính',
        'user.dob': 'Ngày sinh',
        'user.phone': 'SĐT',
        'position': 'Chức vụ'
    }
    column_formatters = {
        'user.sex': format_role_sex
    }

class TeacherView(AuthenticatedAdmin):
    can_create = False
    can_edit = True
    can_delete = False
    column_searchable_list = ['user.username', 'user.name']
    column_list = ('user.username', 'user.name', 'user.sex', 'user.dob', 'user.phone')
    column_labels = {
        'user.username': 'Tên đăng nhập',
        'user.name': 'Họ tên',
        'user.sex': 'Giới tính',
        'user.dob': 'Ngày sinh',
        'user.phone': 'SĐT'
    }
    column_formatters = {
        'user.sex': format_role_sex
    }

class StudentView(AuthenticatedAdmin):
    can_create = False
    can_edit = True
    can_delete = False
    column_searchable_list = ['user.username', 'user.name', 'class_relationship.name']
    column_list = (
        'user.username',
        'user.name',
        'user.sex',
        'user.dob',
        'user.phone',
        'class_relationship.name',
        'grade_level.name'
    )
    column_labels = {
        'user.username' : 'Tên đăng nhập',
        'user.name' : 'Họ tên',
        'user.sex' : 'Giới tính',
        'user.dob' : 'Ngày sinh',
        'user.phone' : 'SĐT',
        'class_relationship.name' : 'Lớp',
        'grade_level.name' : 'Khối'
    }


    column_formatters = {
        'user.sex': format_role_sex
    }


class ClassView(AuthenticatedAdmin):
    can_create = True
    can_edit = True
    can_delete = True
    column_searchable_list = ['name']
    column_list = ('name', 'si_so')
    form_excluded_columns = ['students']

class SemesterView(AuthenticatedAdmin):
    can_create = True
    can_edit = True
    can_delete = True
    column_searchable_list = ['name', 'year']
    column_list = ('id', 'name', 'year')
    column_labels = dict(name='Học kỳ',year='Năm học')
    form_columns = ('name', 'year')  # Các cột được hiển thị trong form thêm/sửa

class RuleView(AuthenticatedAdmin):
    can_create = True
    can_edit =True
    can_delete = True
    column_searchable_list = ['name']
    column_list = ('name', 'value', 'note')
    column_labels = dict(name='Tên quy định',value='Số lượng',note='Ghi chú')





class StatsView(AuthenticatedAdminView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')




# =========================================================================================================================
class AboutUsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/about-us.html')





# =========================================================================================================================




admin = Admin(app=app, name='Quản lý học sinh', template_mode='bootstrap4', index_view=MyAdminIndex())

admin.add_view(HomeView(name='Trang chủ'))
admin.add_view(UserView(User, db.session, name="Người dùng"))
admin.add_view(EmployeeView(Employee, db.session, name="Nhân viên"))
admin.add_view(TeacherView(Teacher, db.session, name="Giáo viên"))
admin.add_view(StudentView(Student, db.session, name="Học sinh"))
admin.add_view(ClassView(Class, db.session, name="Lớp học"))
admin.add_view(SemesterView(Semester, db.session, name="Học kỳ"))
admin.add_view(StatsView(name="Thống kê báo cáo"))
admin.add_view(RuleView(Regulation, db.session, name="Quy định"))
admin.add_view(AboutUsView(name="Giới thiệu"))
admin.add_view(LogoutView(name='Đăng xuất'))


# =========================================================================================================================






# =========================================================================================================================
