import sqlite3
import os
from . import data_importer

def initialize_database():
    ruta_db = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'nba_data.db')
    db = sqlite3.connect(ruta_db)
    cursor = db.cursor()
    # Comprobar si está vacía
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    if len(tablas) == 0:
        data_importer.import_excel_to_database()
    else:
        print("Database already exists")
    
