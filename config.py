import os
from dotenv import load_dotenv

load_dotenv()

class ConfigClass(object):

    #flask configs
    SECRET_KEY = '5Y8W8W5Y3H32F346O9HTE8R3443H5I36'

    #sqlalchemy configs
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db' #la base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False #evita un warning de sqlalchemy

    #Flask user settings
    USER_APP_NAME = "DespachosDoda"
    USER_ENABLE_REGISTER = False
    USER_ENABLE_EMAIL = False
    USER_ENABLE_USERNAME = True
    USER_REQUIRE_RETYPE_PASSWORD = True 
    USER_AFTER_LOGIN_ENDPOINT = 'index'

    #Flask Mail settings
    MAIL_SERVER= os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT') or 25
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['felipe@nogson.com']

    #Babel settings
    BABEL_DEFAULT_LOCALE = 'es'