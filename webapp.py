from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from datetime import datetime, timedelta
import re
import base64
from dotenv import load_dotenv
import os

load_dotenv()

database_engine = os.env('database')
db_user = os.getenv('db_user')
db_password = os.getenv('db_password')

app = Flask(__name__)
app.secret_key = 'f8eqo8j09453ws09453w5qe3g3e3w3459eqf8q7hqooqf3jqwoq4tqqf34w8r7hd89hq173jqoq9hyeq173h93w5354qgquqe9'
app.config['SQLALCHEMY_DATABASE_URI'] = (f'mysql://{db_user}:{db_password}@127.0.0.1:3306/nogslbqf_despacho')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
moment = Moment(app)
db = SQLAlchemy(app)
app.jinja_env.globals.update(base64encode = base64.b64encode)

class Despacho(db.Model):
    '''Creando el esquema para la base de datos''' 
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), unique=True, nullable=False)
    cliente = db.Column(db.String(80))
    placas = db.Column(db.String(80))
    caja = db.Column(db.String(80))
    sello = db.Column(db.Integer)
    status = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime, index=True, default= datetime.now)
    despacho_timestamp = db.Column(db.DateTime)
    firma_chofer = db.Column(db.Text)
    def __repr__(self):
        return '<despacho {}'.format(self.url)

@app.route('/')
def index():
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    #despachos = Despacho.query.filter_by(status='correcto')
    despachos = Despacho.query.filter(Despacho.timestamp >= todays_datetime).filter(Despacho.status =='correcto')
    return render_template('index.html', despachos=despachos)

@app.route('/reporte')
def reporte():
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    tomorrow_datetime = todays_datetime + timedelta(days=1)
    #despachos = Despacho.query.filter_by(status='correcto')
    despachos = Despacho.query.filter(Despacho.timestamp >= todays_datetime).filter(Despacho.status =='despachado')
    return render_template('reporte.html', despachos=despachos)

@app.route('/errores')
def errores():
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    #despachos = Despacho.query.filter_by(status='correcto')
    despachos = Despacho.query.filter(Despacho.status =='error')
    return render_template('errores.html', despachos=despachos)

@app.route('/despachando/<despacho_id>', methods=['GET','POST'])
def despachando(despacho_id):
    despacho_id = int(despacho_id)
    despacho = Despacho.query.filter_by(id=despacho_id).first() 
    if request.method == "POST":
       # Obteniendo los valores del usuario
       data_form = request.form
       user_cliente = data_form['cliente']
       user_placas = data_form['placas']
       if "sello" not in data_form:
           user_sello = 'SIN CANDADO'
       else: user_sello = data_form['sello'] 
          
       #Limpiar las placas de caracteres que no sean letras o numeros
       regex = re.compile('[^a-zA-Z0-9]')
       placas = regex.sub('', despacho.placas)

       if regex.sub('', user_placas).upper() != regex.sub('', despacho.placas).upper():
           flash('Las placas no corresponden, favor de verificar', 'danger')
           return redirect(url_for('despachando', despacho_id=despacho.id))

       elif user_sello != despacho.sello[3:]:
           flash('El candado no corresponde, favor de verificar', 'danger') 
           return redirect(url_for('despachando', despacho_id=despacho.id))

       else:
           despacho.cliente = user_cliente
           despacho.despacho_timestamp = datetime.now()
           session['despacho'] = despacho.id
           db.session.add(despacho)
           db.session.commit()
           return redirect(url_for('firma'))
    return render_template('despachando.html', despacho=despacho)


@app.route('/firma', methods=['GET', 'POST'])
def firma():
    ''' Esta vista recoge la firma y la guarda en un archivo o en la base de datos para poder hacer reporte'''
    despacho_id = int(session['despacho'])
    despacho = Despacho.query.filter_by(id=despacho_id).first() 
    # Estas son pruebas para poder agarrar la firma de signature-pad y poder guardarla en un archivo
    # todavia viendo como enviar desde javascript
    if request.method == 'POST':
        # Obtenemos la imagen en base64, lista para agregarla a la base de datos
        # Los espacios son repmplazados por + para que la imagen pueda ser codificada de nuevo
        data_url = request.form.get('firma').replace(' ', '+')
        header, encoded = data_url.split(',', 1)
        image_data = base64.b64decode(encoded)

        # Se manda la informacion a la base de datos
        despacho.firma_chofer = image_data
        despacho.status = 'despachado'
        flash(f'El Contendedor {despacho.caja}, a sido despachado', 'success') 
        db.session.add(despacho)
        db.session.commit()
        return redirect( url_for('despachado', despacho_id=despacho_id))
    return render_template("firma_pad.html")

@app.route('/despachado/<int:despacho_id>')
def despachado(despacho_id):
    despacho = Despacho.query.filter_by(id=despacho_id).first()
    return render_template('despachado.html', despacho=despacho)

@app.route('/borrar/<int:despacho_id>')
def borrar(despacho_id):
    despacho = Despacho.query.filter_by(id=despacho_id).first()
    despacho.status = 'borrado'
    flash(f'La entrada con el codigo {despacho.url} a sido borrardo', 'danger')
    db.session.add(despacho)
    db.session.commit()
    return redirect(url_for('errores'))
