#!/bin/bash

echo "▶️ Iniciando Bonprix..."
python mongo_insert_bonprix.py

echo "▶️ Iniciando Día..."
python mongo_insert_dia.py

echo "✅ Todos los scrapers finalizados"
