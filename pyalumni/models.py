import csv, os, time, logging
#from flask_login import LoginManager, UserMixin, login_required
#from flask import current_app
from datetime import datetime
from argon2 import PasswordHasher, exceptions
from itsdangerous import Signer
from flask import Flask, Response
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import load_only
import operator
#from flask_login import UserMixin
from flask import *
from flask_login import *

import yaml
from pyconf import *

db_string = "%s://%s:%s@%s:%s/%s" % (db_engine,  db_user, db_pass, db_host, db_port, db_database)

engine = create_engine(db_string, echo=False)

Base = declarative_base()

class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    class_year = Column(Integer())
    password = Column(String(100))
    email_confirmed = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    session_token = Column(String(100))

    def is_active(self):
        """True, as all users are active."""
        try:
            q = db_session.query(User).filter_by(email=email).first()
            return q.email_confirmed()
        except:
            return False

    def is_active(self):
        """True, as all users are active."""
        try:
            q = db_session.query(User).filter_by(email=email).first()
            return q.email_confirmed()
        except:
            return False

    def get_id(self):
        return unicode(self.session_token)

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_admin(self):
        return self.admin

    def __repr__(self):
        return "<User(email='%s', password='%s')>" % (self.email, self.password)

    @classmethod
    def get_user(cls, email):
        if isinstance(email, str):
            print 's is a string object'
            q = db_session.query(User).filter_by(email=email).first()
        elif isinstance(email, unicode):
            print 's is a unicode object'
            q = db_session.query(User).filter_by(email=email.encode('utf8')).first()
        print("email is:" + email)
        return q

    @classmethod
    def get_session(cls, session_token):
        q = db_session.query(User).filter(User.session_token.like(session_token)).first()
        return unicode(q)

class Sessions(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    password = Column(String(100))
    year = Column(Integer)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
        self.name, self.fullname, self.password)

class Student(Base):
    def __init__(self):
        self.images='blank.png'

    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    bio = Column(Text)
    birthday = Column(String(20))
    employer = Column(String(100))
    images = Column(Text)
    kids = Column(Text)
    email = Column(String(100))
    location = Column(String(2000))
    firstname = Column(String(20))
    lastname = Column(String(20))
    name = Column(String(30))
    obit = Column(Text)
    site = Column(Text)
    spouse = Column(String(100))
    updated = Column(DateTime)
    class_year = Column(Integer)
    userid = Column(Integer)

    #def __repr__(self):
    #    return "<Student(name='%s', last='%s')>" % (
    #    self.name, self.id)

    @classmethod
    def get_user(cls, name, year):
        try:
            query = db_session.query.filter(Student.name == name)

        except:
            query = None
        return query

    @classmethod
    def get_years(cls):
        years = []
        records = db_session.query(Student).options(load_only("year"))
        print("got records.")
        for record in records:
            years.append(record.year)
            print(record)
        return years

    @classmethod
    def paginate_students(self, start=1, per_page=25, orderby='name'):
        self.start=start
        self.per_page=per_page
        self.orderby=orderby
        records = []
        record_num = Student.select().count()
        for record in db_session.query(Student).order_by(Student.name):
            first=(record.name.split(".")[0])
            last=(record.name.split(".")[1])
            updated = record.updated.strftime('%Y-%m-%d') if record.updated else '1990-01'
            records.append({'name': record.name, 'year': record.year, 'email': record.email, 'updated': updated, 'first': first, 'last': last})
            yield record_num, records
            start = start + per_page

    @classmethod
    def list_all_students(self):
        student_list=[]
        student_list=db_session.query(Student).options(load_only("name"))
        return student_list

    @classmethod
    def show_students(self, **kwargs):
        students = db_session.query(Student).filter_by(**kwargs).all()
        for x in students:
            x.images = ['blank.png'] if x.images is None else x.images
            print x.images
        return students

    @classmethod
    def show_students_by_year(self, **kwargs):
        students = db_session.query(Student.lastname, (Student.firstname + '.' + Student.lastname), Student.images, Student.id).filter_by(**kwargs).all()
        return students

    @classmethod
    def process_updates(self, record):
        students = db_session.query(Student).all()
        for row in record:
            rowline=row[0]
            newrecord=None
            for student in students:
                #name=student.firstname + '.' + student.lastname
                if student.name == rowline['name']:
                    newrecord = student
            if newrecord is None:
                newrecord = Student()
                db_session.add(newrecord)
            for key,val in rowline.items():
                if val:
                    setattr(newrecord, key, val)
        db_session.commit()
#        #print (row[0], name, row[16], student.class_year)
#        #if row[0] == name and row[16] == student.class_year:
#        if row[0] == name and int(row[16]) == student.class_year:
#            print (row[0], name, row[16], student.class_year)
#            print student
#            print(type(student))
#            print line
#            #else:
#            #    print (name, row[0])
#
#        self.record_list=record_list[:]
#        update_list=[]
#        student_names=db_session.query(Student).options(load_only("name"))
#        for record in self.record_list[:]:
#            if record['name'] in record:
#                update_list.append(record)
#                self.record_list.pop()
#
#                db_session.add_all(record_list)
#
#        for row in update_list:
#            q = db_session.query(Student).filter_by(name=row['name']).first()
#            for name, value in row.items():
#                setattr(q, name, value)
#            q.save()

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()
db_session.close()
