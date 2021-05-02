import os
import sys
import cx_Oracle
from flaskpost import db, login_manager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, Column, Table, String, Integer, DateTime, Text
from flask_login import UserMixin

Base = automap_base()

class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column('user_id', Integer, primary_key=True)
    username = Column('username', String)
    email = Column('email', String)
    image_file = Column('image_file', String)
    password = Column('password', String)    

class Comment(Base):
    __tablename__='comments'
    id = Column('comment_id', Integer, primary_key=True)
    content = Column('content', Text)
    series_id = Column('series_id', Integer)
    author = Column('author', String)

Base.prepare(db.engine, reflect=True)
Base.query = db.session.query_property()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)