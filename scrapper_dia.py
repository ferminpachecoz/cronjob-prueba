from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pandas as pd
import time

URL = "https://diaonline.supermercadosdia.com.ar/bebidas/cervezas"

def limpiar_precio(texto):
    try:
        texto = texto.replace("$", "").replace(".", "").replace(",", ".").strip()
        return round(float(texto), 2)
    except:
        return None

def limpiar_precio_litro(texto):
    try:
        texto = texto.split("LT")[-1]  # "Precio por 1 LT $ 3.276,96"
        texto = texto.replace("$", "").replace(".", "").replace(",", ".").strip()
        return round(float(texto), 2)
    except:
        return None

def scroll_completo(driver):
    scroll_step = 600  # pixeles por scroll
    scroll_pause = 2.5  # segundos de espera
    max_scrolls = 50    # cantidad máxima de scrolls

    for i in range(max_scrolls):
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")
        time.sleep(scroll_pause)

        # Ver cuántos productos se cargaron hasta ahora
        productos_actuales = driver.find_elements(By.CSS_SELECTOR, "article.vtex-product-summary-2-x-element--shelf")
        print(f"⬇️ Scroll #{i+1}: Productos cargados: {len(productos_actuales)}")

        # Si se alcanza el total esperado, se corta
        if len(productos_actuales) >= 37:
            print("✅ Todos los productos detectados. Fin del scroll.")
            break


def get_productos():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1280,720")

    driver = uc.Chrome(options=options, headless=True)

    nombres = []
    precios = []
    precios_por_litro = []
    descuentos = []
    imagenes = []

    try:
        driver.get(URL)
        time.sleep(3)

        scroll_completo(driver)
        print("📜 Scroll finalizado. Extrayendo productos...")

        productos = driver.find_elements(By.CSS_SELECTOR, "article.vtex-product-summary-2-x-element--shelf")
        print(f"🛒 Productos encontrados: {len(productos)}")

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
                element = prod.find_element(By.CSS_SELECTOR, "span.vtex-product-price-1-x-savingsPercentage")
                if element:
                    descuento = element.text
                else:
                    descuento = ""
            except:
                descuento = None
            descuentos.append(descuento)
            
            #Imagen
            try:
                imagen = prod.find_element(By.TAG_NAME, "img")
                url_imagen = imagen.get_attribute("src")
            except:
                url_imagen = None
            imagenes.append(url_imagen)
                

    except Exception as e:
        print("❌ Error en el scraping:")
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

# Test manual
if __name__ == "__main__":
    df = get_productos()
    print(df.head())
    print(f"✅ Total productos recopilados: {len(df)}")
    df.to_excel("productos_dia.xlsx", index=False)
