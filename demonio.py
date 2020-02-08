# coding: utf-8
from webapp import Despacho, db
from helpers import get_sat_data
from time import sleep

print('Empezando el demonio')
while True:
    query = Despacho.query.filter_by(status='pendiente').all()
    sleep(1)
    if query != []:
        for pend in query:
            sat_info = get_sat_data(pend.url)
            try:
                sat_info['pedimentos'][0]['Pedimento:']
                pend.placas = sat_info['pedimentos'][0]['Datos de Identificación  del Vehículo:']
                pend.caja = sat_info['candado']['Contenedores:']
                pend.sello = sat_info['candado']['Candados:']
                pend.status = 'correcto'
                db.session.add(pend)
                db.session.commit()
                print(f"Catch one, con status {pend.status}")
            except:
                pend.status = 'error'
                db.session.add(pend)
                db.session.commit()
                print("Catch one error")
