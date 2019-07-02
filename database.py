import os
import utils.config as config

from models import *
from werkzeug.security import generate_password_hash, \
     check_password_hash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///storage.db?check_same_thread=False')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

def create_user(email, password, name, access, location):
    user_object = User(
        #CHANGE THIS LATER, DONT WANT ALL SUPER ADMIN ACCESS
        access = access_models[access] if email not in config.SUPERADMINS else Access.SuperAdmin,
        email = email,
        password = generate_password_hash(password),
        name = name,
        location = location
        )
    session.add(user_object)
    session.commit()
    return 


def correct_user(email, password):
    user_object = session.query(User).filter_by(email=email).first()
    if user_object:
        return check_password_hash(user_object.password, password)
    else:
        return False


def authenticate_user(email):
    user_object = session.query(User).filter_by(email=email).first()
    if user_object:
        user_object.authenticated = True
        session.commit()
        return
    else:
        raise AssertionError("User does not exist.")


def user_exists(email):
    user_object = session.query(User).filter_by(email=email).first()
    return True if user_object else False


def user_authed(email):
    user_object = session.query(User).filter_by(email=email).first()
    if user_object:
        return user_object.authenticated
    else:
        raise AssertionError("User does not exist.")


def get_access(email):
    user_object = session.query(User).filter_by(email=email).first()
    if user_object:
        return models_access[user_object.access]
    else:
        raise AssertionError("User does not exist.")


def get_location(email):
    user_object = session.query(User).filter_by(email=email).first()
    if user_object:
        return user_object.location
    else:
        raise AssertionError("User does not exist.")


def get_name(email):
    user_object = session.query(User).filter_by(email=email).first()
    if user_object:
        return user_object.name
    else:
        raise AssertionError("User does not exist.")


def reset_password(email, password):
    user_object = session.query(User).filter_by(email=email).first()
    if user_object:
        user_object.password = generate_password_hash(password)
        session.commit()
        return
    else:
        raise AssertionError("User does not exist.")


def valid_access(key):
    return key in models_access.values()


def is_admin(access):
    return "admin" in access


def is_student(access):
    return access in config.STUDENT_TYPES


def get_git_link(email):
    return "https://github.com/" + email.split("@")[0] + "-meet"


def add_lecture(link, group, name, assign_type, lec_type, location):
    lec_object = Lecture(
        link = link,
        group = group, 
        name = name,
        assign_type = assign_type,
        lec_type=lec_type,
        location = location
        )
    session.add(lec_object)
    session.commit()
    return 


def remove_lecture(link, group, name):
    session.query(Lecture).filter_by(name=name, group=group, link=link).delete()
    session.commit()
    return


def valid_edit(editing, assignment):
    return (editing in config.STUDENT_TYPES or editing == config.PUBLIC) and assignment in config.STUDENT_PAGE_LINKS


def get_existing_lectures(group, assignment, location):
    if location:
        return session.query(Lecture).filter(Lecture.group==group, Lecture.assign_type==assignment, Lecture.location==location or Lecture.location==config.ALL_LOCATIONS).order_by(Lecture.id.desc())
    else:
        return session.query(Lecture).filter(Lecture.group==group, Lecture.assign_type==assignment).order_by(Lecture.id.desc())


def remove_user(email):
    session.query(User).filter_by(email=email).delete()
    session.commit()
    return 


def graduate_students(group):
    if group == "all":
        config.STUDENT_TYPES.sort(reverse=True)
        for year in config.STUDENT_TYPES:
            students = session.query(User).filter_by(access=access_models[year])
            value = access_models[year].value
            for student in students:
                student.access = Access(value + 1)
    else:
        students = session.query(User).filter_by(access=access_models[group])
        value = access_models[group].value
        for student in students:
            student.access = Access(value + 1)
    session.commit()
    return 


def get_users(group=None):
    if group is None:
        return session.query(User).filter(User.access!=Access.SuperAdmin)
    else:
        return session.query(User).filter(User.access == access_models[group])


def make_announcement(date, name, text, poster, group):
    announcement_object = Announcement(
        announced = date,
        name = name,
        text = text,
        poster = poster, 
        group=group
        )
    session.add(announcement_object)
    session.commit()
    return


def get_announcements(group):
    if group is None:
        return session.query(Announcement).filter_by(group=config.PUBLIC)
    else:
        return session.query(Announcement).filter_by(group=group)


def remove_announcement(removal):
    session.query(Announcement).filter_by(id=removal).delete()
    session.commit()
    return 


def embedable_link(link):
    return "embed" in link


def valid_location(location):
    return location in config.LOCATIONS
