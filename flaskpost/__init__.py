import os
import sys
import cx_Oracle
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '581c338d975285183d94d07008c4f334'
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://OTB:omar2001@localhost:1521/xe'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

connection = cx_Oracle.connect("OTB", "omar2001", "localhost:1521/xe", encoding="UTF-8")


from flaskpost import routes