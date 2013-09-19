#! /usr/bin/env python3.3

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
import math

# ==========
# Paramètres
# ==========

if(len(sys.argv) == 1):
    exit('Vous devez fournir au moins un numéro de station en argument.')

stations = []
for station in sys.argv[1:]:
    stations.append(int(station))

base_url = ('http://www.velib.paris.fr/service/stationdetails/paris/')

PIN_SCE = 3
PIN_RESET = 4
PIN_DC = 5
PIN_SDIN = 6
PIN_SCLK = 7

LCD_C = "LOW"
LCD_D = "HIGH"
LCD_X = 84

LCD_Y = 48

# =============================
# Initialisation des librairies
# =============================
http = urllib3.PoolManager()

# ====
# Date
# ====
now = datetime.datetime.now()
date = now.strftime('%d/%m/%Y')
time = now.strftime('%H:%M')

# =======================
# Requête sur l'API Vélib
# =======================
available = {}
free = {}
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
url_weather = ('http://api.wunderground.com/api/bc48fae29b73e75a/' +
               'hourly/lang:FR/q/zmw:00000.98.07150.xml')
r = http.request('GET', url_weather)

weather_now = ''
temp_now = -1
weather_5h = ''
temp_5h = -1
weather_10h = ''
temp_10h = -1

if r.status == 200:
    weather_xml = ET.fromstring(r.data)

    for child in weather_xml.iter('forecast'):
        day = child.find('FCTTIME').find('mday')

        # Garder uniquement les événements pour aujourd'hui et éventuellement
        # demain
        if (int(day.text) != int(now.strftime("%d")) and
           int(day.text) != int(now.strftime("%d")) + 1):
            continue

        epoch = child.find('FCTTIME').find('epoch')
        epoch = datetime.datetime.fromtimestamp(int(epoch.text))

        # Météo maintenant
        if (math.floor((epoch - now).seconds/3600) == 0 and
           int(day.text) == int(now.strftime('%d'))):
            weather_now = child.find('condition').text
            temp_now = child.find('temp').find('metric').text
        # Météo à 5h
        elif math.floor((epoch - now).seconds/3600) == 5:
            weather_5h = child.find('condition').text
            temp_5h = child.find('temp').find('metric').text
        # Météo à 10h
        elif math.floor((epoch - now).seconds/3600) == 10:
            weather_10h = child.find('condition').text
            temp_10h = child.find('temp').find('metric').text

# ============================
# Afficher les infos à l'écran
# ============================
