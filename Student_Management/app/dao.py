# Student_Management/app/dao.py

import hashlib
from . import app, db
from Student_Management.app.models import User
import cloudinary.uploader
from flask_login import current_user


def auth_user(username,password,role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u= User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password))
    if role:
        u=u.filter(User.user_role.__eq__(role))

    return u.first()