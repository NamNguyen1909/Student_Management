# Student_Management/app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
import cloudinary
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key='SADKJH873414B31#@#!@#213K1HG1I5UH13294Y194HLKWQYE987Y1I34UH2I3YT187EWIOJKHQE87Q'


# app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://root:%s@localhost/saledb?charset=utf8mb4" %quote("Admin@123")
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://root:%s@localhost/school?charset=utf8mb4" %quote("ThanhNam*1909")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)



login=LoginManager(app)
cloudinary.config(cloud_name='ds05mb5xf',
                  api_key='129254722258642',
                  api_secret='OQScAUMjqFmA3g6gog1GfBRCM14')