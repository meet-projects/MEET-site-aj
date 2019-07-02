from sqlalchemy import Column, Integer, ForeignKey, String, Enum, Boolean
from sqlalchemy.types import DateTime
from sqlalchemy.ext.declarative import declarative_base
import time
import enum
from werkzeug.security import generate_password_hash, \
     check_password_hash


class Access(enum.Enum):
    YearOne = 1
    YearTwo = 2
    YearThree = 3
    Alum = 4
    Admin = 5
    SuperAdmin = 6

models_access = {
    Access.YearOne: "y1",
    Access.YearTwo: "y2",
    Access.YearThree: "y3",
    Access.Alum: "alum",
    Access.Admin: "admin",
    Access.SuperAdmin: "superadmin",
}


# above but reversed
access_models = {j:i for i, j in models_access.items()}


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    # id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, primary_key=True, nullable=False)
    password = Column(String)
    access = Column(Enum(Access))
    authenticated = Column(Boolean, default=False)
    location = Column(String)



class Lecture(Base):
    __tablename__ = "lectures"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    link = Column(String)
    group = Column(String)
    assign_type = Column(String)
    lec_type = Column(String, default="slides")
    location = Column(String)


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    group = Column(String)
    document = Column(String)
    due = Column(DateTime)


class CompAssignment(Base):
    __tablename__ = "completed_assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student = Column(String, ForeignKey("users.email"))
    link = Column(String)
    completed = Column(DateTime)


class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    announced = Column(DateTime)
    name = Column(String)
    text = Column(String)
    poster = Column(String)
    group = Column(String, nullable=True)

