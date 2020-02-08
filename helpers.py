# coding: utf-8
from pdb import set_trace
from scraping import get_the_soup, get_the_data, zip_validadores

url = "https://pecem.mat.sat.gob.mx/app/qr/ce/faces/pages/mobile/validadorqr.jsf?D1=16&D2=1&D3=40106649"

def get_pedimentos_list(pedimentos):
    pedis_list = []
    for pedimento in pedimentos:
        # usando las funciones para crear el diccionario
        tabla = pedimento.find('table')
        datos = get_the_data(tabla)
        validadores = zip_validadores(datos)
        pedis_list.append(validadores)
    return pedis_list

def get_pedimentos(sopa):
    ul_pedimentos_id = "j_idt12:2:j_idt13:j_idt28"
    pedimentos = sopa.find('ul', id=ul_pedimentos_id)
    pedimentos = pedimentos.find_all('li')
    pedimentos = get_pedimentos_list(pedimentos)
    return pedimentos

def get_candado(sopa):
    candado_id = "j_idt12:3:j_idt13:j_idt28:0:j_idt29"
    tabla = sopa.find('table', id=candado_id)
    datos = get_the_data(tabla)
    if len(datos) == 3:
        datos.append('SIN CANDADO')
    candado = zip_validadores(datos)
    return candado

def get_sat_data(url):
    try:
        sopa = get_the_soup(url.strip())
        pedimentos = get_pedimentos(sopa)
        candado = get_candado(sopa)
    except:
        pedimentos = [{'Pedimentos:' : "ERROR" }]
        candado = {'Candados:' : 'ERROR'}
    return { "pedimentos" : pedimentos, "candado": candado}
