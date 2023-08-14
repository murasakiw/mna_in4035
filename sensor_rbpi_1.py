#! /usr/bin/python2

import json
from time import sleep
import http.client
import RPi.GPIO as GPIO
import sys
from hx711 import HX711

# Definir la URL
url = "/pls/apex/a01794338/update/sensor?status=" #Se le agrega el status
status = 'off'

pin_boton = 10
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pin_boton, GPIO.IN)

EMULATE_HX711=False
#Definir constante para calibración
referenceUnit = 361

def cleanAndExit():

    if not EMULATE_HX711:
        GPIO.cleanup()
    sys.exit()

def obtener_peso(hx):

    #hx = HX711(5, 6)

    #hx.set_reading_format("MSB", "MSB")

    #hx.set_reference_unit(139)

    #hx.reset()

    #hx.tare()

    #print("Tare done! Add weight now...")

    #for _ in range(20):
    try:
        val = max(0, int(hx.get_weight(5)))
        #val = hx.get_weight(5)
        #print(f'{val} [g]')

        hx.power_down()
        hx.power_up()
        sleep(0.1)
        peso = val
            

    except (KeyboardInterrupt, SystemExit):
        print(f'Peso final: {peso} [g]')
        cleanAndExit()

    print(f'Peso final: {peso} [g]')
    
    return peso

def publicar_datos(hx):
    peso = obtener_peso(hx)
    control = GPIO.input(pin_boton)
    if control == GPIO.HIGH:
        status = 'on'
        url_status = url + status + f'&peso={peso}'
    else:
        status = 'off'
        url_status = url + status + f'&peso={peso}'
    # Establecer la conexión
    conn = http.client.HTTPSConnection("apex.oracle.com")

    # Realizar la solicitud GET
    conn.request("GET", url_status)

    # Obtener la respuesta
    response = conn.getresponse()

    # Leer y mostrar el contenido de la respuesta
    data = response.read()
    #print(data.decode("utf-8"))

    # Cerrar la conexión
    conn.close()
    sleep(0.1)


def main():
    hx = HX711(5, 6)

    hx.set_reading_format("MSB", "MSB")

    hx.set_reference_unit(361)

    hx.reset()

    hx.tare()

    print("Tare done! Add weight now...")
    try:
        while True:
            publicar_datos(hx)
    except KeyboardInterrupt:
        print('Se interrumpio la ejecucion')
        cleanAndExit()


if __name__ == '__main__':
    main()





