from flask import Flask, render_template, request, flash, redirect, url_for, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_migrate import Migrate
from flask_babelex import Babel
from flask_user import UserManager, login_required, current_user
from datetime import datetime, timedelta
from config import ConfigClass
import re
import base64
import os

app = Flask(__name__)
app.config.from_object(ConfigClass)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Despacho, User

#Exporta la funcion b64encode a los templates para mostrar los blobs como imagenes
app.jinja_env.globals.update(base64encode = base64.b64encode)

babel = Babel(app)
user_manager = UserManager(app, db, User)

@app.route('/')
def home_page():
    return redirect(url_for('user.login'))

@app.route('/despachos')
@login_required
def index():
    '''Pagina principal de la aplicación, se muestran los despachos listos '''
    # Obtiene la fecha de el dia de hoy para filtrar las entradas
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    #despachos = Despacho.query.filter_by(status='correcto')
    #query para mostrar los despachos de la fecha de el dia de hoy
    despachos = Despacho.query.filter(Despacho.timestamp >= todays_datetime).filter(Despacho.status =='correcto')
    return render_template('index.html', despachos=despachos)

@app.route('/reporte', methods=['GET', 'POST'])
@login_required
def reporte():
    '''Pagina de los reportes '''
    if request.method == "POST":
        #Si la peticion es un POST obtiene las entradas de la fecha que se envia en el formulario
        user_date = request.form['fecha']
        fecha = datetime.strptime(user_date, '%Y-%m-%d')
        fecha_all_day = fecha + timedelta(days=1)
        despachos = Despacho.query.filter(Despacho.timestamp >= fecha).filter(Despacho.timestamp <= fecha_all_day).filter(Despacho.status =='despachado')
    else:
        # Si es un get muestra los despachos de el dia de hoy
        fecha = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
        tomorrow_datetime = fecha + timedelta(days=1)
        despachos = Despacho.query.filter(Despacho.timestamp >= fecha ).filter(Despacho.status =='despachado')
    return render_template('reporte.html', despachos=despachos)

@app.route('/errores')
@login_required
def errores():
    ''' Si el codigo QR no se pudo verificar los datos requeridos de el sito del SAT el codigo cae en esta categoria '''
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    despachos = Despacho.query.filter(Despacho.status =='error')
    return render_template('errores.html', despachos=despachos)

@app.route('/despachando', methods=['POST'])
@login_required
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
@login_required
def firma():
    ''' Esta vista recoge la firma y la guarda en la base de datos como BLOB, para este modulo se usa una libreria JS externa '''
    despacho_id = session['despacho']
    despacho = Despacho.query.filter_by(id=despacho_id).first() 
    if request.method == 'POST':
        # Obtenemos la imagen en base64, lista para agregarla a la base de datos
        # Los espacios son repmplazados por + para que la imagen pueda ser codificada de nuevo
        data_url = request.form.get('firma').replace(' ', '+')
        header, encoded = data_url.split(',', 1)
        image_data = base64.b64decode(encoded)

        # Se manda la informacion a la base de datos
        despacho.firma_chofer = image_data
        despacho.status = 'despachado'
        despacho.user = current_user
        db.session.add(despacho)
        db.session.commit()
        return redirect(url_for('despachado', despacho_id=despacho.id))
    return render_template("firma_pad.html")

@app.route('/despachado/<int:despacho_id>')
@login_required
def despachado(despacho_id):
    despacho = Despacho.query.filter_by(id=despacho_id).first()
    if (despacho == None) or ( despacho.status != 'despachado'):
       flash('El despacho no se encuentra o no ha sido despachado', 'danger')
       return redirect(url_for('index'))
    return render_template('despachado.html', despacho=despacho)

#TODO: hay que revisar esta vista por que parece te permite borrar entradas aleatorias
@app.route('/borrar/<int:despacho_id>')
@login_required
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
@login_required
def qr_reader():
    ''' usando JS abre la camara y escanea el codigo hace uso de la vista api '''
    return render_template("qr_reader.html")