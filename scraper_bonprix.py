# -*- coding: utf-8 -*-
"""
Created on Wed May 14 09:42:54 2025

@author: fermi
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import re

CHROME_PATH = r"C:\ChromeForTesting\chrome.exe"
CHROMEDRIVER_PATH = r"C:\ChromeForTesting\chromedriver.exe"
URL = "https://grupobonprix.com.ar/productos/cerveza"

def get_productos():
    options = Options()
    options.binary_location = CHROME_PATH
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    
    nombres, precios, precios_por_litro, descuentos, imagenes = [],[],[],[],[]
    print("Bandera 2")
    try:
        driver.get(URL)
        
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "app-item-gift")))
        
        productos = driver.find_elements(By.CSS_SELECTOR, "app-item-gift")
        print("Bandera 1")
        for prod in productos:
            try:
                texto = prod.find_element(By.CSS_SELECTOR, ".item-gift__content-title").text.strip()
            except:
                texto = None
            
            #Nombres
            try:
                txt = texto.split("|")
                if len(txt)==2:
                    nombre = txt[0].strip() +" "+ txt[1].strip()
                elif len(txt) == 3:
                    nombre = txt[0].strip() +" "+ txt[1].strip()+" "+ txt[2].strip()
                elif len(txt)==4:
                    nombre = txt[0].strip() +" "+ txt[1].strip()+" "+ txt[2].strip() +" "+txt[3].strip()
                else:
                    nombre = None
            except:
                nombre = None
            
            nombres.append(nombre)
            
            #Precio
            try:
                precio_raw = prod.find_element(By.CSS_SELECTOR, ".price .value span").text.strip()
                precio = round(float(precio_raw.replace("$","").replace(".","")), 2)
            except:
                precio = None
            precios.append(precio)
            
            #Precio por Litro
            try:
                txt = texto.split("|")
                if len(txt) == 2:
                    volumen_raw = txt[1]
                else:
                    volumen_raw = txt[2]
                volumen = int(re.sub(r'\D', '', volumen_raw))
                if len(txt) == 4:
                    unidades = int(re.sub(r'\D', '', txt[3]))
                    precio_unidad = precio/unidades
                    precioxlitro = round((1000*precio_unidad)/volumen, 2)
                else:
                    precioxlitro = round((1000*precio)/volumen, 2)
            except:
                precioxlitro = None
            precios_por_litro.append(precioxlitro)
            
            #Descuentos
            try:
                descuento = prod.find_element(By.CSS_SELECTOR, "app-tag").text.strip()
            except:
                descuento = None
            descuentos.append(descuento)
            
            #Imagenes
            try:
                imagen = prod.find_element(By.TAG_NAME, "img")
                url_imagen = imagen.get_attribute("src")
            except:
                url_imagen = None
            imagenes.append(url_imagen)
            
    except:
        print("❌ Error durante el scraping:")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
    
    df = pd.DataFrame({
        "nombre": nombres,
        "precio": precios,
        "precioLitro": precios_por_litro,
        "descuentos": descuentos,
        "imagenUrl": imagenes
    })

    df["categoria"] = "Cerveza"
    df["supermercado"] = "Bonprix"
    
    return df
if __name__ == "__main__":
    df = get_productos()
    df.to_excel("productos_bonprix.xlsx", index=False)
    print(f"Total de items: {len(df)}")
        