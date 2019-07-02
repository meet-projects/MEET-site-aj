import sys 
sys.path.append("..")
from app import app
import os
import utils.config

from flask_mail import Message, Mail


mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}

app.config.update(mail_settings)
mail = Mail(app)

def send_email(to, subject, template):
    with app.app_context():
        msg = Message(
            subject,
            recipients=[to],
            html=template,
            sender=mail_settings["MAIL_USERNAME"]
            # sender="auth@meet.mit.edu"
        )
        mail.send(msg)