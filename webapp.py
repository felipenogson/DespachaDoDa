from flask import Flask, render_template, request, flash, redirect, url_for, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_moment import Moment
from flask_migrate import Migrate
from datetime import datetime, timedelta
import re
import base64
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = 'f8eqo8j09453ws09453w5qe3g3e3w3459eqf8q7hqooqf3jqwoq4tqqf34w8r7hd89hq173jqoq9hyeq173h93w5354qgquqe9'
#app.config['SQLALCHEMY_DATABASE_URI'] = (f'mysql://{db_user}:{db_password}@127.0.0.1:3306/nogslbqf_despacho')
app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Agrega la funcion de decodificar blobs en los templates 
app.jinja_env.globals.update(base64encode = base64.b64encode)

@app.shell_context_processor
def make_shell_context():
    ''' funcion para que flask shell carge automatico despachos y db '''
    return { 'db' : db, 'Despacho': Despacho}

class Despacho(db.Model):
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
    def __repr__(self):
        return '<despacho {}'.format(self.url)

@app.route('/')
def index():
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    #despachos = Despacho.query.filter_by(status='correcto')
    despachos = Despacho.query.filter(Despacho.timestamp >= todays_datetime).filter(Despacho.status =='correcto')
    return render_template('index.html', despachos=despachos)

@app.route('/reporte', methods=['GET', 'POST'])
def reporte():
    if request.method == "POST":
        user_date = request.form['fecha']
        fecha = datetime.strptime(user_date, '%Y-%m-%d')
        fecha_all_day = fecha + timedelta(days=1)
        despachos = Despacho.query.filter(Despacho.timestamp >= fecha).filter(Despacho.timestamp <= fecha_all_day).filter(Despacho.status =='despachado')
    else:
        fecha = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
        tomorrow_datetime = fecha + timedelta(days=1)
        #despachos = Despacho.query.filter_by(status='correcto')
        despachos = Despacho.query.filter(Despacho.timestamp >= fecha ).filter(Despacho.status =='despachado')
    return render_template('reporte.html', despachos=despachos)

@app.route('/reporte_caja', methods=['GET', 'POST'])
def reporte_caja():
    if request.method == "POST":
        user_caja = request.form['caja']
        despachos = Despacho.query.filter_by(caja=user_caja.upper()).order_by(desc(Despacho.despacho_timestamp)).limit(5).all()
    else:
        fecha = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
        tomorrow_datetime = fecha + timedelta(days=1)
        #despachos = Despacho.query.filter_by(status='correcto')
    if len(despachos) == 0: 
        despachos = None
    return render_template('reporte_caja.html', despachos=despachos)

@app.route('/errores')
def errores():
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    #despachos = Despacho.query.filter_by(status='correcto')
    despachos = Despacho.query.filter(Despacho.status =='error')
    return render_template('errores.html', despachos=despachos)

@app.route('/despachando', methods=['POST'])
def despachando():
    if request.form.get('get_id'):
        despacho_id = request.form.get('get_id')
        despacho = Despacho.query.filter_by(id=despacho_id).first()
        return render_template('despachando.html', despacho=despacho)
    if request.form.get('despacho_id'):
       despacho_id = request.form.get('despacho_id')
       despacho = Despacho.query.filter_by(id=despacho_id).first()
       # Obteniendo los valores del usuario
       data_form = request.form
       user_cliente = data_form['cliente']
       user_placas = data_form['placas']
       user_bultos = data_form['bultos']
       user_facturas = data_form['facturas']

       if "sello" not in data_form:
           user_sello = 'SIN CANDADO'
       else: user_sello = data_form['sello']
       #Limpiar las placas de caracteres que no sean letras o numeros
       regex = re.compile('[^a-zA-Z0-9]')
       placas = regex.sub('', despacho.placas)

       #Verificando que las placas correspondan con las del usuario
       if regex.sub('', user_placas).upper() != regex.sub('', despacho.placas).upper():
           flash('Las placas no corresponden, favor de verificar', 'danger')
           return render_template('despachando.html', despacho=despacho)

       elif user_sello != despacho.sello:
           flash('El candado no corresponde, favor de verificar', 'danger')
           return render_template('despachando.html', despacho=despacho)

       else:
           despacho.cliente = user_cliente
           despacho.despacho_timestamp = datetime.now()
           despacho.bultos = user_bultos
           despacho.facturas = user_facturas
           session['despacho'] = despacho.id
           db.session.add(despacho)
           db.session.commit()
           return redirect(url_for('firma'))

@app.route('/firma', methods=['GET', 'POST'])
def firma():
    ''' Esta vista recoge la firma y la guarda en un archivo o en la base de datos para poder hacer reporte'''
    despacho_id = session['despacho']
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
        db.session.add(despacho)
        db.session.commit()
        return redirect(url_for('despachado', despacho_id=despacho.id))
    return render_template("firma_pad.html")

@app.route('/despachado/<int:despacho_id>')
def despachado(despacho_id):
    despacho = Despacho.query.filter_by(id=despacho_id).first()
    if (despacho == None) or ( despacho.status != 'despachado'):
       flash('El despacho no se encuentra o no ha sido despachado', 'danger')
       return redirect(url_for('index'))
    return render_template('despachado.html', despacho=despacho)

@app.route('/borrar/<int:despacho_id>')
def borrar(despacho_id):
    despacho = Despacho.query.filter_by(id=despacho_id).first()
    despacho.status = 'borrado'

    flash(f'La entrada con el codigo {despacho.url} a sido borrardo', 'danger')
    db.session.delete(despacho)
    db.session.commit()
    return redirect(url_for('errores'))

@app.route('/api', methods=['POST'])
def doda_in():
    if not request.json or not 'url' in request.json:
        abort(400)
    # Hace un objeto json para regresar y para enviar a la base de datos
    doda = {
            'url': request.json['url'],
            'status': 'pendiente',
            'timestamp': datetime.now(),
            }

    # Si se encuentra en la base de datos envia el api envia los datoS
    despacho = Despacho.query.filter_by(url=doda['url']).first()
    if despacho:
        doda ={
                "url" : despacho.url,
                "status" : despacho.status,
                "candado" : despacho.sello,
                "caja" : despacho.caja,
                "cliente" : despacho.cliente,
                "timestamp" : despacho.timestamp
                }
        return jsonify({"doda":doda}), 201

    #Si no esta en la base de datos crea el objeto y lo inserta en la tabla, regresa los datos como confirmacion
    d = Despacho(url=doda['url'], status=doda['status'], timestamp=doda['timestamp'])
    db.session.add(d)
    db.session.commit()
    return jsonify({'doda': doda}), 201

@app.route('/qr_reader')
def qr_reader():
    return render_template("qr_reader.html")

