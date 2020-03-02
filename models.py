from datetime import datetime
from webapp import db
from flask_user import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True) 
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    #Informacion para autenticar. collation='NOCASE' se requiere para la busqueda de usuarios
    # sea insensitivo a mayusculas y minusculas
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at =db.Column(db.DateTime())

    #Informacion del usuario
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, default='')
    
    # La relacion de el usuario con los despachos
    despachos = db.relationship('Despacho', backref='user', lazy='dynamic')

class Despacho(db.Model, UserMixin):
    '''Creando el esquema para la base de datos''' 
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), unique=True, nullable=False)
    cliente = db.Column(db.String(80))
    placas = db.Column(db.String(80))
    caja = db.Column(db.String(80))
    sello = db.Column(db.String(80))
    facturas = db.Column(db.Integer)
    bultos = db.Column(db.Integer)
    status = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime, index=True, default= datetime.now)
    despacho_timestamp = db.Column(db.DateTime)
    firma_chofer = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<despacho {}>'.format(self.url)