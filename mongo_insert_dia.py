# -*- coding: utf-8 -*-
"""
Created on Tue May 13 21:16:53 2025

@author: fermi
"""

# -*- coding: utf-8 -*-
from datetime import datetime
from scrapper_dia import get_productos
from pymongo import MongoClient

# Cargar productos del scrapper
df = get_productos()

if df.empty:
    print("⚠️ No se extrajeron productos. Posible error en el scraping. Abortando inserción.")
    exit()

# Conexión a MongoDB Atlas
uri = "mongodb+srv://ferminpz:pacheco2002@cluster0.q9s2nsn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client["fresquitas_db"]      # Podés usar otro nombre si querés
collection = db["productos"]     # Podés cambiar el nombre si scrapeás de otros supermercados

# Eliminar productos anteriores del mismo supermercado
supermercado_nombre = df["supermercado"].iloc[0]
collection.delete_many({"supermercado": supermercado_nombre})

# Agregar timestamp de actualización
df["actualizacion"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Insertar los nuevos productos
data = df.to_dict(orient="records")
collection.insert_many(data)

print("✅ Productos insertados correctamente en MongoDB Atlas (modo reemplazo total por supermercado).")
