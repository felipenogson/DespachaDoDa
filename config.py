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

    #Babel settings
    BABEL_DEFAULT_LOCALE = 'es'