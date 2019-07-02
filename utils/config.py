import os
import json
from dotenv import load_dotenv
load_dotenv()

STUDENT_PAGE_LINKS = json.loads(os.environ["STUDENT_PAGE_LINKS"])

STUDENT_PAGE_NAMES = json.loads(os.environ["STUDENT_PAGE_NAMES"])

STUDENT_PAGE_DICT = dict(zip(STUDENT_PAGE_LINKS, STUDENT_PAGE_NAMES)) 

SUPERADMINS = json.loads(os.environ["SUPERADMINS"])

STUDENT_TYPES = json.loads(os.environ["STUDENT_TYPES"])

PUBLIC = os.environ["PUBLIC"]

SECRET_PASSWORD = os.environ["SECRETPASSWORD"]

EXPIRATION = int(os.environ["EXPIRATION"])

ALL_LOCATIONS = os.environ["ALL_LOCATIONS"]

LOCATIONS = json.loads(os.environ["LOCATIONS"])