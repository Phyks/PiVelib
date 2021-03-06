#! /usr/bin/env python3.3
#-*- coding: utf-8 -*-

# Auteur : Phyks (phyks@phyks.me)
# Site web : http://phyks.me
# Licence : BEERWARE

# Description :
# =============
# Récupérer et afficher la météo et le nombre de vélibs aux stations
# prédéfinies sur un écran LCD nokia 3310 (connecté via les pins GPIO)
# Plus d'informations sur le montage :
# http://blog.idleman.fr/raspberry-pi-11-relier-a-un-ecran-et-afficher-du-texte

import sys
import urllib3
import xml.etree.ElementTree as ET
import datetime
import wiringpi2 as wp2
import time as time_lib
import signal
import threading

wp2.wiringPiSetup()

# ===========
# Pins du LCD
# ===========

PIN_SCE = 3
PIN_RESET = 4
PIN_DC = 5
PIN_SDIN = 6
PIN_SCLK = 7

LCD_C = 0
LCD_D = 1
LCD_X = 84
LCD_Y = 48


ASCII = [
    [0x00, 0x00, 0x00, 0x00, 0x00],  # 20 " "
    [0x00, 0x00, 0x5f, 0x00, 0x00],  # 21 !
    [0x00, 0x07, 0x00, 0x07, 0x00],  # 22 "
    [0x14, 0x7f, 0x14, 0x7f, 0x14],  # 23 #
    [0x24, 0x2a, 0x7f, 0x2a, 0x12],  # 24 $
    [0x23, 0x13, 0x08, 0x64, 0x62],  # 25 %
    [0x36, 0x49, 0x55, 0x22, 0x50],  # 26 &
    [0x00, 0x05, 0x03, 0x00, 0x00],  # 27 '
    [0x00, 0x1c, 0x22, 0x41, 0x00],  # 28 (
    [0x00, 0x41, 0x22, 0x1c, 0x00],  # 29 )
    [0x14, 0x08, 0x3e, 0x08, 0x14],  # 2a *
    [0x08, 0x08, 0x3e, 0x08, 0x08],  # 2b +
    [0x00, 0x50, 0x30, 0x00, 0x00],  # 2c ,
    [0x08, 0x08, 0x08, 0x08, 0x08],  # 2d -
    [0x00, 0x60, 0x60, 0x00, 0x00],  # 2e .
    [0x20, 0x10, 0x08, 0x04, 0x02],  # 2f /
    [0x3e, 0x51, 0x49, 0x45, 0x3e],  # 30 0
    [0x00, 0x42, 0x7f, 0x40, 0x00],  # 31 1
    [0x42, 0x61, 0x51, 0x49, 0x46],  # 32 2
    [0x21, 0x41, 0x45, 0x4b, 0x31],  # 33 3
    [0x18, 0x14, 0x12, 0x7f, 0x10],  # 34 4
    [0x27, 0x45, 0x45, 0x45, 0x39],  # 35 5
    [0x3c, 0x4a, 0x49, 0x49, 0x30],  # 36 6
    [0x01, 0x71, 0x09, 0x05, 0x03],  # 37 7
    [0x36, 0x49, 0x49, 0x49, 0x36],  # 38 8
    [0x06, 0x49, 0x49, 0x29, 0x1e],  # 39 9
    [0x00, 0x36, 0x36, 0x00, 0x00],  # 3a :
    [0x00, 0x56, 0x36, 0x00, 0x00],  # 3b ;
    [0x08, 0x14, 0x22, 0x41, 0x00],  # 3c <
    [0x14, 0x14, 0x14, 0x14, 0x14],  # 3d =
    [0x00, 0x41, 0x22, 0x14, 0x08],  # 3e >
    [0x02, 0x01, 0x51, 0x09, 0x06],  # 3f ?
    [0x32, 0x49, 0x79, 0x41, 0x3e],  # 40 @
    [0x7e, 0x11, 0x11, 0x11, 0x7e],  # 41 A
    [0x7f, 0x49, 0x49, 0x49, 0x36],  # 42 B
    [0x3e, 0x41, 0x41, 0x41, 0x22],  # 43 C
    [0x7f, 0x41, 0x41, 0x22, 0x1c],  # 44 D
    [0x7f, 0x49, 0x49, 0x49, 0x41],  # 45 E
    [0x7f, 0x09, 0x09, 0x09, 0x01],  # 46 F
    [0x3e, 0x41, 0x49, 0x49, 0x7a],  # 47 G
    [0x7f, 0x08, 0x08, 0x08, 0x7f],  # 48 H
    [0x00, 0x41, 0x7f, 0x41, 0x00],  # 49 I
    [0x20, 0x40, 0x41, 0x3f, 0x01],  # 4a J
    [0x7f, 0x08, 0x14, 0x22, 0x41],  # 4b K
    [0x7f, 0x40, 0x40, 0x40, 0x40],  # 4c L
    [0x7f, 0x02, 0x0c, 0x02, 0x7f],  # 4d M
    [0x7f, 0x04, 0x08, 0x10, 0x7f],  # 4e N
    [0x3e, 0x41, 0x41, 0x41, 0x3e],  # 4f O
    [0x7f, 0x09, 0x09, 0x09, 0x06],  # 50 P
    [0x3e, 0x41, 0x51, 0x21, 0x5e],  # 51 Q
    [0x7f, 0x09, 0x19, 0x29, 0x46],  # 52 R
    [0x46, 0x49, 0x49, 0x49, 0x31],  # 53 S
    [0x01, 0x01, 0x7f, 0x01, 0x01],  # 54 T
    [0x3f, 0x40, 0x40, 0x40, 0x3f],  # 55 U
    [0x1f, 0x20, 0x40, 0x20, 0x1f],  # 56 V
    [0x3f, 0x40, 0x38, 0x40, 0x3f],  # 57 W
    [0x63, 0x14, 0x08, 0x14, 0x63],  # 58 X
    [0x07, 0x08, 0x70, 0x08, 0x07],  # 59 Y
    [0x61, 0x51, 0x49, 0x45, 0x43],  # 5a Z
    [0x00, 0x7f, 0x41, 0x41, 0x00],  # 5b [
    [0x02, 0x04, 0x08, 0x10, 0x20],  # 5c ¥
    [0x00, 0x41, 0x41, 0x7f, 0x00],  # 5d ]
    [0x04, 0x02, 0x01, 0x02, 0x04],  # 5e ^
    [0x40, 0x40, 0x40, 0x40, 0x40],  # 5f _
    [0x00, 0x01, 0x02, 0x04, 0x00],  # 60 `
    [0x20, 0x54, 0x54, 0x54, 0x78],  # 61 a
    [0x7f, 0x48, 0x44, 0x44, 0x38],  # 62 b
    [0x38, 0x44, 0x44, 0x44, 0x20],  # 63 c
    [0x38, 0x44, 0x44, 0x48, 0x7f],  # 64 d
    [0x38, 0x54, 0x54, 0x54, 0x18],  # 65 e
    [0x08, 0x7e, 0x09, 0x01, 0x02],  # 66 f
    [0x0c, 0x52, 0x52, 0x52, 0x3e],  # 67 g
    [0x7f, 0x08, 0x04, 0x04, 0x78],  # 68 h
    [0x00, 0x44, 0x7d, 0x40, 0x00],  # 69 i
    [0x20, 0x40, 0x44, 0x3d, 0x00],  # 6a j
    [0x7f, 0x10, 0x28, 0x44, 0x00],  # 6b k
    [0x00, 0x41, 0x7f, 0x40, 0x00],  # 6c l
    [0x7c, 0x04, 0x18, 0x04, 0x78],  # 6d m
    [0x7c, 0x08, 0x04, 0x04, 0x78],  # 6e n
    [0x38, 0x44, 0x44, 0x44, 0x38],  # 6f o
    [0x7c, 0x14, 0x14, 0x14, 0x08],  # 70 p
    [0x08, 0x14, 0x14, 0x18, 0x7c],  # 71 q
    [0x7c, 0x08, 0x04, 0x04, 0x08],  # 72 r
    [0x48, 0x54, 0x54, 0x54, 0x20],  # 73 s
    [0x04, 0x3f, 0x44, 0x40, 0x20],  # 74 t
    [0x3c, 0x40, 0x40, 0x20, 0x7c],  # 75 u
    [0x1c, 0x20, 0x40, 0x20, 0x1c],  # 76 v
    [0x3c, 0x40, 0x30, 0x40, 0x3c],  # 77 w
    [0x44, 0x28, 0x10, 0x28, 0x44],  # 78 x
    [0x0c, 0x50, 0x50, 0x50, 0x3c],  # 79 y
    [0x44, 0x64, 0x54, 0x4c, 0x44],  # 7a z
    [0x00, 0x08, 0x36, 0x41, 0x00],  # 7b {
    [0x00, 0x00, 0x7f, 0x00, 0x00],  # 7c |
    [0x00, 0x41, 0x36, 0x08, 0x00],  # 7d ]
    [0x10, 0x08, 0x08, 0x10, 0x08],  # 7e ?
    [0x78, 0x46, 0x41, 0x46, 0x78],  # 7f ?
]


def writeLCD(dc, data):
    wp2.digitalWrite(PIN_DC, dc)
    wp2.digitalWrite(PIN_SCE, 0)
    wp2.shiftOut(PIN_SDIN, PIN_SCLK, 1, data)
    wp2.digitalWrite(PIN_SCE, 1)


def characterLCD(character):
    writeLCD(LCD_D, 0x00)
    for i in range(0, 5):
        writeLCD(LCD_D, ASCII[ord(character) - 0x20][i])
    writeLCD(LCD_D, 0x00)


def stringLCD(string):
    for character in string:
        characterLCD(character)


# X ranges from 0 to 84
# Y ranges from 0 to 5
def gotoXYLCD(x, y):
    writeLCD(0, 0x80 | x)
    writeLCD(0, 0x40 | y)


def initLCD():
    wp2.pinMode(PIN_SCE, 1)
    wp2.pinMode(PIN_RESET, 1)
    wp2.pinMode(PIN_DC, 1)
    wp2.pinMode(PIN_SDIN, 1)
    wp2.pinMode(PIN_SCLK, 1)
    wp2.digitalWrite(PIN_RESET, 0)
    wp2.digitalWrite(PIN_RESET, 1)

    writeLCD(LCD_C, 0x21)  # LCD Extended commands
    writeLCD(LCD_C, 0x98)  # Set LCD Vop (contrast)
    writeLCD(LCD_C, 0x04)  # Set Temp coefficient
    writeLCD(LCD_C, 0x13)  # LCD bias mode (1:48)
    writeLCD(LCD_C, 0x0C)  # LCD in normal mode
    writeLCD(LCD_C, 0x20)
    writeLCD(LCD_C, 0x0C)


def clearLCD():
    for i in range(0, int(LCD_X*LCD_Y/8)):
        writeLCD(LCD_D, 0x00)
    characterLCD(' ')


def kill_handler(signum, frame):
    global running
    global update_thread
    print("Exiting...")
    running = False
    update_thread.cancel()


def update():
    print("Updating...")
    global available
    global free
    global weather_now
    global temp_now
    global weather_3h
    global temp_3h
    global weather_6h
    global temp_6h
    global weather_9h
    global temp_9h
    global running

    # =======================
    # Requête sur l'API Vélib
    # =======================
    for station in stations:
        r = http.request('GET', base_url+str(station))

        if r.status == 200:
            station_xml = ET.fromstring(r.data)

            for child in station_xml.iter('available'):
                available[station] = child.text
            for child in station_xml.iter('free'):
                free[station] = child.text

        else:
            available[station] = -1
            free[station] = -1

    # ==================================
    # Requête pour les prédictions météo
    # ==================================
    url_weather = ('http://api.openweathermap.org/data/2.5/forecast' +
                   '?q=Paris,fr&mode=xml&lang=fr&units=metric')
    r = http.request('GET', url_weather)

    if r.status == 200:
        weather_xml = ET.fromstring(r.data)

        for child in weather_xml.iter('forecast'):
            for time in child.iter('time'):
                time_from = datetime.datetime.strptime(time.attrib['from'],
                                                       "%Y-%m-%dT%H:%M:%S")
                time_to = datetime.datetime.strptime(time.attrib['to'],
                                                     "%Y-%m-%dT%H:%M:%S")

                if time_to > now and time_from < now:
                    weather_now = time.find('clouds').attrib['value']
                    temp_now = time.find('temperature').attrib['value']

                if (time_to > now + datetime.timedelta(hours=3) and
                   time_from < now+datetime.timedelta(hours=3)):
                    weather_3h = time.find('clouds').attrib['value']
                    temp_3h = time.find('temperature').attrib['value']

                if (time_to > now+datetime.timedelta(hours=6) and
                   time_from < now+datetime.timedelta(hours=6)):
                    weather_6h = time.find('clouds').attrib['value']
                    temp_6h = time.find('temperature').attrib['value']

                if (time_to > now+datetime.timedelta(hours=9) and
                   time_from < now+datetime.timedelta(hours=9)):
                    weather_9h = time.find('clouds').attrib['value']
                    temp_9h = time.find('temperature').attrib['value']
# ==========
# Paramètres
# ==========

if(len(sys.argv) == 1):
    sys.exit('You must provide at least one station number as ' +
             'argument on the command line.')

stations = []
for station in sys.argv[1:]:
    stations.append(int(station))

base_url = ('http://www.velib.paris.fr/service/stationdetails/paris/')

# =============================
# Initialisation des librairies
# =============================
http = urllib3.PoolManager()
initLCD()
clearLCD()
gotoXYLCD(0, 0)
stringLCD("Loading...")

running = True
update_thread = threading.Timer(900, update)
update_thread.start()
signal.signal(signal.SIGINT, kill_handler)

# ====
# Date
# ====
now = datetime.datetime.now()
date = now.strftime('%d/%m/%Y')
time = now.strftime('%H:%M')

# ====
# Vars
# ====
available = {}
free = {}

weather_now = ''
temp_now = -1
weather_3h = ''
temp_3h = -1
weather_6h = ''
temp_6h = -1
weather_9h = ''
temp_9h = -1

update()


# ============================
# Afficher les infos à l'écran
# ============================
while running:
    for station in stations:
        clearLCD()
        gotoXYLCD(0, 0)
        stringLCD("Station:")
        gotoXYLCD(0, 1)
        stringLCD(str(station))
        gotoXYLCD(0, 3)
        stringLCD("Avail.: "+str(available[station]))
        gotoXYLCD(0, 5)
        stringLCD("Free: "+str(free[station]))
        time_lib.sleep(2)

    if running is False:
        continue
    clearLCD()
    gotoXYLCD(0, 0)
    stringLCD("[Weather]")
    gotoXYLCD(0, 1)
    stringLCD("Now:")
    gotoXYLCD(0, 2)
    stringLCD(weather_now.capitalize())
    gotoXYLCD(0, 4)
    stringLCD("Temp:"+str(temp_now)+"C")
    time_lib.sleep(2)

    if running is False:
        continue
    clearLCD()
    gotoXYLCD(0, 0)
    stringLCD("[Weather]")
    gotoXYLCD(0, 1)
    stringLCD("In 3h:")
    gotoXYLCD(0, 2)
    stringLCD(weather_3h.capitalize())
    gotoXYLCD(0, 4)
    stringLCD("Temp:"+str(temp_3h)+"C")
    time_lib.sleep(2)

    if running is False:
        continue
    clearLCD()
    gotoXYLCD(0, 0)
    stringLCD("[Weather]")
    gotoXYLCD(0, 1)
    stringLCD("In 6h:")
    gotoXYLCD(0, 2)
    stringLCD(weather_6h.capitalize())
    gotoXYLCD(0, 4)
    stringLCD("Temp:"+str(temp_6h)+"C")
    time_lib.sleep(2)

    if running is False:
        continue
    clearLCD()
    gotoXYLCD(0, 0)
    stringLCD("[Weather]")
    gotoXYLCD(0, 1)
    stringLCD("In 9h:")
    gotoXYLCD(0, 2)
    stringLCD(weather_9h.capitalize())
    gotoXYLCD(0, 4)
    stringLCD("Temp:"+str(temp_9h)+"C")
    time_lib.sleep(2)

clearLCD()
