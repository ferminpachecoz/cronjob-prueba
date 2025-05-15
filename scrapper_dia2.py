from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import pandas as pd
import time

BASE_URL = "https://diaonline.supermercadosdia.com.ar/bebidas/cervezas"

def limpiar_precio(texto):
    try:
        texto = texto.replace("$", "").replace(".", "").replace(",", ".").strip()
        return round(float(texto), 2)
    except:
        return None

def limpiar_precio_litro(texto):
    try:
        texto = texto.split("LT")[-1]
        texto = texto.replace("$", "").replace(".", "").replace(",", ".").strip()
        return round(float(texto), 2)
    except:
        return None

def get_productos():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1280,720")

    driver = uc.Chrome(options=options, headless=True)

    total_paginas = 3
    nombres, precios, precios_por_litro, descuentos, imagenes = [], [], [], [], []

    try:
        for pagina in range(1, total_paginas + 1):
            url = BASE_URL if pagina == 1 else f"{BASE_URL}?page={pagina}"
            driver.get(url)
            time.sleep(2)
            # Scroll mínimo para cargar productos visibles
            for _ in range(2):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(0.4)
            
            # esperar a que se cargue bien todo
            time.sleep(2)
            productos = driver.find_elements(By.CSS_SELECTOR, "article.vtex-product-summary-2-x-element--shelf")
            print(f"🧾 Página {pagina}: {len(productos)} productos encontrados")

            for prod in productos:
                try:
                    nombre = prod.find_element(By.CSS_SELECTOR, "span.vtex-product-summary-2-x-brandName").text.strip()
                except:
                    nombre = "No encontrado"
                nombres.append(nombre)

                try:
                    precio_texto = prod.find_element(By.CSS_SELECTOR, "span.diaio-store-5-x-sellingPriceValue").text.strip()
                    precio = limpiar_precio(precio_texto)
                except:
                    precio = None
                precios.append(precio)

                try:
                    litro_texto = prod.find_element(By.CSS_SELECTOR, "div.diaio-store-5-x-custom_specification_wrapper").text.strip()
                    precio_litro = limpiar_precio_litro(litro_texto)
                except:
                    precio_litro = None
                precios_por_litro.append(precio_litro)

                try:
                    descuento = prod.find_element(By.CSS_SELECTOR, "span.vtex-product-price-1-x-savingsPercentage").text.strip()
                except:
                    descuento = None
                descuentos.append(descuento)

                try:
                    imagen = prod.find_element(By.TAG_NAME, "img")
                    url_imagen = imagen.get_attribute("src")
                except:
                    url_imagen = None
                imagenes.append(url_imagen)

    except Exception as e:
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
    df["supermercado"] = "Día"
    return df

if __name__ == "__main__":
    df = get_productos()
    print(f"✅ Total productos recopilados: {len(df)}")
    print(df.head())
    df.to_excel("productos_dia.xlsx", index=False)
