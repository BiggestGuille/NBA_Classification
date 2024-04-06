import sqlite3
import os
from . import data_importer


# Función para obtener la conexión a la base de datos
def get_database_connection():
    ruta_db = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'nba_data.db')
    return sqlite3.connect(ruta_db)

# Función para inicializar la base de datos (primeras tablas importadas del excel si es necesario)
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

# Función para verificar si una tabla existe en la base de datos
def verify_table(table_name):
    with get_database_connection() as db:
        cursor = db.cursor()
        # Verificar si la tabla existe
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if cursor.fetchone():
            # La tabla existe
            print(f"La tabla '{table_name}' ya existe.")
            return True
        else:
            # La tabla no existe
            return False

# Función para CALCULAR la clasificación normal de la temporada dados los partidos de la misma
# Devuelve un diccionario con el Id del equipo y el porcentaje de victorias
def calculate_normal_classification(season: int):
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

        return results

# Función para crear la tabla de clasificación normal en la base de datos
# normal_classification es un diccionario con el Id del equipo y el porcentaje de victorias
def create_normal_classification_table(normal_classification, season):
    with get_database_connection() as db:
        # Crear la tabla
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS nba_normal_classification (
            "Team Id" INTEGER PRIMARY KEY,
            Season INTEGER NOT NULL,
            "Victory Percentage" REAL NOT NULL,
            FOREIGN KEY("Team Id") REFERENCES nba_teams(id)
        );
        ''')
        db.commit()
        print(f"La tabla  ha sido creada con éxito.")

        # Introducir los datos
        # Insertar o actualizar los datos en la tabla
        for team_id, percentage in normal_classification.items():
            # Sentencia SQL para insertar cada fila
            query = "INSERT INTO nba_normal_classification ([Team Id], season, [Victory Percentage]) VALUES (?, ?, ?)"
            data = (team_id, season, percentage)
            # Ejecutar la consulta
            cursor.execute(query, data)
            db.commit()

        print(f"Los datos han sido insertados con éxito.")

# Función para obtener la clasificación normal de la temporada
def get_normal_classification(season: int):
    with get_database_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM nba_normal_classification WHERE season = ?", (season,))
        data_normal_classification = cursor.fetchall()
    return data_normal_classification

# Función para obtener los equipos de la NBA
def get_teams():
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT "Team Name" FROM nba_teams
        """
        cursor.execute(query)
        teams = cursor.fetchall()
    return teams

# Función para obtener las victorias por pareja de equipos
def get_victories_per_pair(season: int):
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT 
            home."Team Name" AS home_team_name,
	        visitor."Team Name" AS visitor_team_name,
	        SUM(matches."Home Result") AS home_wins, 
            SUM(matches."Visitor Result") AS visitor_wins
        FROM 
            nba_teams home
        CROSS JOIN
	        nba_teams visitor
        LEFT JOIN
            nba_matches matches ON (home.id = matches."Home Id" AND visitor.id = matches."Visitor Id" AND matches.season = ?)
        WHERE 
            home.id != visitor.id
        GROUP BY 
            home."Team Name", 
            visitor."Team Name"
        """
        cursor.execute(query, (season,))
        results = cursor.fetchall()
    return results