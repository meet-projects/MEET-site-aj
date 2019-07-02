from itsdangerous import URLSafeTimedSerializer

import sys
sys.path.append("..")

from app import app
import utils.config as config

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email)
    	#Maybe add this later
    	#app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            # salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=config.EXPIRATION
        )
    except:
        return False
    return email


def check_email(email):
	if "@" in email:
		if "meet.mit.edu" in email:
			return True

	return False