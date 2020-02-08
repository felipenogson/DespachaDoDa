# coding: utf-8
import requests
from bs4 import BeautifulSoup

# Hack para ignorar el debil cifrado de la coneccion https 
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

def get_the_soup(url):
        re = requests.get(url)
        soup = BeautifulSoup(re.text, 'html.parser')
        return soup

def get_the_data(tabla):
        lista = []
        for a in tabla.text.split("\n"):
                a = a.strip()
                if a != "":
                        lista.append(a)
        return lista

def zip_validadores(lista):
        """ Crea un diccionario de la lista, basicamente lo divide por la mitad, y la primer mitad son los keys
        y la segunda mitad son los values, regresa el diccionario"""
        divider = int(len(lista)/2)
        lista1,lista2 = lista[:divider],lista[divider:]
        validadores = dict(zip(lista1,lista2))
        return validadores
