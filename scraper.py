#Librerias y dependencias
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
import pandas as pd
import sqlite3
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains

'''
Google Flights Scraper
Author: Josemaria Saldias
Date: 2022-07-04
'''

class Scraper():
    #Rutas
    path_driver = r"C:\driver_chrome_selenium\chromedriver.exe"
    path_browser = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    #Variables de clase
    options = webdriver.ChromeOptions()
    options.binary_location = path_browser   #-> Indicamos el path del binario de Brave
    options.add_argument("--ignore-gpu-blocklist")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1024,768")
    options.add_argument("--no-sandbox")

    service = Service(executable_path=path_driver)

    def __init__(self, TIMEOUT=3, url="https://www.google.com/travel/flights?tfs=CBwQARoaagwIAhIIL20vMGRscXYSCjIwMjItMTEtMTEaGhIKMjAyMi0xMi0wOXIMCAISCC9tLzBkbHF2cAGCAQsI____________AUABQAFIAZgBAQ"):
        self.TIMEOUT =TIMEOUT
        self.url = url
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.wait = WebDriverWait(self.driver, 30)

    def getURL(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(20) #Linea de codigo muy importante, espera a que el elemento especifico sea encontrado


    def introducirFechasViaje(self):
        destino = input("Ingrese el codigo de aeropuerto de destino: ")
        f_salida = input("Ingrese la fecha de salida en el siguiente formato (YYYY-MM-DD): ")
        f_vuelta = input("Ingrese la fecha de vuelta en el siguiente formato (YYYY-MM-DD): ")

        return destino, f_salida, f_vuelta

    def collectData(self, destino, f_salida, f_vuelta):
        time.sleep(self.TIMEOUT)
        boton_destino = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="¿A dónde quieres ir?"]')))
        ActionChains(self.driver).send_keys_to_element(boton_destino, destino).perform()

        opcion = self.wait.until(EC.visibility_of_element_located((By.XPATH, f'//li[@data-code="{destino}"]')))
        self.driver.execute_script("arguments[0].click()", opcion)
        time.sleep(3)

        #Busca el boton de fecha y luego debe introducirla y apretar el boton search (cambiar la URL de arriba)
        salida = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Salida"]')))#-> Boton fecha salida
        self.driver.execute_script("arguments[0].click()", salida)
        fecha_ida = self.wait.until(EC.visibility_of_element_located((By.XPATH, f'//div[@data-iso="{f_salida}"]')))#Campo fecha ida
        self.driver.execute_script("arguments[0].click()", fecha_ida)

        time.sleep(3)
        fecha_vuelta = self.wait.until(EC.visibility_of_element_located((By.XPATH, f'//div[@data-iso="{f_vuelta}"]')))#Campo fecha vuelta
        self.driver.execute_script("arguments[0].click()", fecha_vuelta)
        boton_hecho = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ow62"]/div[2]/div/div[3]/div[3]/div/button/span')))
        self.driver.execute_script("arguments[0].click()", boton_hecho)
        # boton_buscar = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div/c-wiz/div[2]/div[1]/div[1]/div[2]/div/button/span[2]')))
        # self.driver.execute_script("arguments[0].click()", boton_buscar)
        
        time.sleep(10) #Se ejecuta la busqueda, debo esperar acá
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-Bz112c-M1Soyc VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe LQeN7 nJawce OTelKf iIo4pd"]'))).click()
        time.sleep(5)
        data = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//ul[@class="Rk10dc"]/li[@class="pIav2d"]')))

        return data

    def parseData(self, data):
        regex = r"(?P<Hora_salida>\d{2}:\d{2})\s\s\W\s\s(?P<hora_llegada>\d{2}:\d{2})\W?(?P<dias_viaje>\d)?\s(?P<aerolinea1>\w+(?:\s)?(?:\w+)?)(?:,)? (?P<aerolinea2>[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:\W)?(?:\s)?(?:[a-zA-Z]+)?(?:,)?(?:\s)?(?:[a-zA-Z]+)?(?:\/)?([a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:,)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:,)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?:[a-zA-Z]+)?(?:\s)?(?P<duracion_vuelo>\d* \w (?:\d* min\s)?)(?P<codigos_destinos>\w+\W\w+) (?P<numero_escalas>\d) \w+(?P<duracion_escala> \d+ [a-z]? \d+ min)? (?P<escala1>\w+(\s)?(\w+)?(\s)?(\w+)?)(?:, (?P<escala2>\w+)?)?(?P<total_emisiones_co2> \d*,\d+ \w+ \w+ \w+ (?:\W?\s?\d+?\s?\W?\s?(?:de)?)?\w+\s?\w+\.?)? (?P<codigo_moneda>\w+) (?P<precio>[0-9]*,[0-9]*(?:,[0-9]*)?)"
        
        data_list = []

        c=0
        for text_data in data:
            text_data = text_data.text.replace('\n', ' ') #Retorna un string con los datos, ese lo parseo con una expresion regular  
            print(text_data)
            match = re.search(regex, text_data)
            if match == None:
                print(f"Esta frase {text_data} no se pudo clasificar")
                c+=1
                continue
            else:
                diccionario = match.groupdict()
                diccionario['destino'] = destino
                diccionario["fecha_salida"] = f_salida
                diccionario["fecha_vuelta"] = f_vuelta
                data_list.append(diccionario)

        print('\n'+"Se encontraron: "+str(len(data))+" elementos")
        print(f"\nTotal de datos que no se pudieron clasificar: {c}\n")  
        
        data_json = json.dumps(data_list)
        self.driver.quit()
        return data_json


    def createDB(self, df):
        #Insertamos la data en la base de datos
        sqlite3.register_adapter(np.int64, int)    #-> especificamos que np.int64 corresponde a un integer. Esto se hace porque sqlite3 no soporta ese formato y debemos especificarlo o si no guarda el dato como un blob en forma binaria
        connection = sqlite3.connect("Flights-data.db")

        cursor = connection.cursor()

        #Solo necesito crear la base de datos una vez. Descomentar las lineas de abajo si se quiere crear la bbdd por primera vez

        cursor.execute('''CREATE TABLE flights_data 
                            (
                            hora_salida TIME, 
                            hora_llegada TIME, 
                            dias_viaje INTEGER, 
                            aerolinea1 TEXT, 
                            aerolinea2 TEXT, 
                            duracion_vuelo TEXT, 
                            codigos_destinos TEXT, 
                            numero_escalas INTEGER, 
                            duracion_escala TEXT, 
                            escala1 TEXT,
                            escala2 TEXT, 
                            total_emisiones_co2 TEXT,
                            codigo_moneda TEXT, 
                            precio DOUBLE,
                            destino TEXT,
                            fecha_salida TEXT,
                            fecha_vuelta TEXT,
                            fecha_scrapeo TEXT
                            )''')

        for i in range(len(df)):
            cursor.execute(f"INSERT INTO flights_data values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))", df.iloc[i])
        
        connection.commit()
        connection.close()

    def updateDB(self, df):
        sqlite3.register_adapter(np.int64, int)
        connection = sqlite3.connect("Flights-data.db")
        cursor = connection.cursor()

        for i in range(len(df)):
            cursor.execute(f"INSERT INTO flights_data values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))", df.iloc[i])

        connection.commit()
        connection.close()



scraper = Scraper()
scraper.getURL()
destino, f_salida, f_vuelta = scraper.introducirFechasViaje()
scraped_data = scraper.collectData(destino, f_salida, f_vuelta)
data_json = scraper.parseData(scraped_data)
df = pd.read_json(data_json)

#scraper.createDB(df)
scraper.updateDB(df)