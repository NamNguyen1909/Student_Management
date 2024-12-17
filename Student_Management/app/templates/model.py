
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean,Enum,DateTime
from enum import Enum as RoleEnum
from flask_login import UserMixin
from datetime import datetime

class UserRole(RoleEnum):
    ADMIN=1
    EMPLOYEE=2
    TEACHER=3

class User(db.Model,UserMixin):
    id=Column(Integer,primary_key=True,autoincrement=True)
    name=Column(String(100),nullable=False)
    username=Column(String(100),nullable=False,unique=True)
    password=Column(String(100),nullable=False)
    avatar=Column(String(100),nullable=True,default='https://res.cloudinary.com/ds05mb5xf/image/upload/v1734438824/avatar-default-symbolic-icon-479x512-n8sg74wg_rvl14k.png')
    active=Column(Boolean,default=True)
    user_role=Column(Enum(UserRole),default=UserRole.EMPLOYEE)