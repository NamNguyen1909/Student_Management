from flask import redirect, url_for, session, flash
from flask_admin import BaseView, expose, AdminIndexView, Admin

from app import app, db, dao
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from app.models import UserRole, User, Student, Teacher, Class, Employee, Regulation
import json

class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class AuthenticatedAdminView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class UserView(AuthenticatedAdmin):
    column_searchable_list = ['username', 'user_role']
    form_excluded_columns = ['password']
    column_list = ('username', 'name')
    column_labels = dict(username='Tên đăng nhập', fullname='Họ tên', image="Ảnh đại diện", user_role="Vai trò")

class ClassView(AuthenticatedAdmin):
    column_searchable_list = ['name']
    column_list = ('name', 'si_so')

class RuleView(AuthenticatedAdmin):
    column_searchable_list = ['name']
    column_list = ('name', 'value', 'note')

class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        session.clear()
        return redirect('/login')

class HomeView(AuthenticatedView):
    @expose('/')
    def index(self):
        return redirect('/')

class StatsView(AuthenticatedAdminView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')

admin = Admin(app=app, name='Quản lý', template_mode='bootstrap4', index_view=MyAdminIndex())
admin.add_view(UserView(User, db.session, name="Người dùng"))
admin.add_view(ClassView(Class, db.session, name="Lớp học"))
admin.add_view(StatsView(name="Thống kê báo cáo"))
admin.add_view(RuleView(Regulation, db.session, name="Quy định"))
admin.add_view(HomeView(name='Trang chủ người dùng'))
admin.add_view(LogoutView(name='Đăng xuất'))