import sqlite3
import os
from . import data_importer


def get_database_connection():
    ruta_db = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'nba_data.db')
    return sqlite3.connect(ruta_db)



def initialize_database():
    with get_database_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if len(tables) == 0:
            data_importer.import_excel_to_database()
            print("Database initialized")
        else:
            print("Database already exists")



def get_normal_classification(season: int):
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT "Home ID",
               SUM("Home Result") AS victories,
               COUNT(*) AS total_matches
        FROM nba_matches
        WHERE season = ?
        GROUP BY "Home Id"
        """
        cursor.execute(query, (season,))
        results = cursor.fetchall()
        
        # Calculate the victory percentage for each team
        victory_percentage = {team: (victories / total_matches) * 100 for team, victories, total_matches in results}
        
        return victory_percentage


#for equipo, porcentaje in porcentaje_victorias.items():
 #   print(f"{equipo}: {porcentaje:.2f}% de victorias")
