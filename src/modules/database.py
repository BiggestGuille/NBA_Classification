import sqlite3
import os
from . import data_importer


# Función para obtener la conexión a la base de datos
def get_database_connection():
    ruta_db = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'nba_data.db')
    return sqlite3.connect(ruta_db)

# Función para inicializar la base de datos si es necesario (tablas que se importan desde las hojas de cálculo)
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
            # print(f"La tabla '{table_name}' ya existe.")
            return True
        else:
            # La tabla no existe
            # print(f"La tabla '{table_name}' no existe.")
            return False

# Función para verificar si hay datos de una temporada específica en cualquier tabla
def check_season_data(table_name, season):
    with get_database_connection() as db:
        cursor = db.cursor()
        query = f"SELECT COUNT(*) FROM {table_name} WHERE season = '{season}' OR season = '{season}_normal' OR season = '{season}_new';"
        cursor.execute(query)
        result = cursor.fetchone()
    if result[0] == 0:
        print("No hay datos de la temporada ", season," en la tabla.")
    # Devuelve True si hay algún dato, False en caso contrario
    return result[0] > 0  

# Función para comprobar que el Quality Percentage es correcto (Pruebas)
def check_quality_percentage(season: int):
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT SUM("Quality Percentage") FROM nba_new_classification WHERE Season = ?
        """
        cursor.execute(query, (season,))
        result = cursor.fetchone()
    return result[0]



"""
Función para Calcular la Clasificación Normal de la temporada dados los partidos de la misma.
Devuelve un Diccionario con el Id del Equipo y el Número de Victorias.
"""
def calculate_normal_classification(season: int):
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT team, SUM(victories) AS total_victories
        FROM (
            -- Suma las victorias como local
            SELECT "Home Id" AS team, COUNT(*) AS victories
            FROM nba_matches
            WHERE "Home Result" = 1 and Season = ?
            GROUP BY "Home Id"
    
            UNION ALL
    
            -- Suma las victorias como visitante
            SELECT "Visitor Id" AS team, COUNT(*) AS victories
            FROM nba_matches
            WHERE "Visitor Result" = 1 AND Season = ?
            GROUP BY "Visitor Id"
        ) AS victories_per_team
        GROUP BY team
        ORDER BY total_victories DESC;
        """
        cursor.execute(query, (season, season))
        results = cursor.fetchall()
        return results

"""
Función para crear la tabla de clasificación normal en la base de datos e insertar los datos correspondientes.
normal_classification es un diccionario con el Id del equipo y el Porcentaje de Victorias.
"""
def create_normal_classification_table(normal_classification, season):
    with get_database_connection() as db:
        # Crear la tabla
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS nba_normal_classification (
            "Key" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Team Id" INTEGER,
            Season INTEGER NOT NULL,
            "Victory Percentage" REAL NOT NULL,
            FOREIGN KEY("Team Id") REFERENCES nba_teams(id)
        );
        ''')
        db.commit()
        print(f"La tabla  ha sido creada con éxito.")

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
        # Realizar un JOIN entre nba_normal_classification y nba_teams para obtener Team Name y Victory Percentage
        cursor.execute("""
            SELECT t."Team Name", nc."Victory Percentage", t.Conference, t.Logo
            FROM nba_normal_classification AS nc
            JOIN nba_teams AS t ON nc."Team Id" = t.Id
            WHERE nc.Season = ?
            ORDER BY nc."Victory Percentage" DESC
        """, (season,))
        data_normal_classification = cursor.fetchall()
    return data_normal_classification



"""
Función para crear la tabla de clasificación nueva en la base de datos e insertar los datos correspondientes.
new_classification es un Diccionario con el Id del Equipo y el Porcentaje de Importancia o Calidad de las Victorias.
"""
def create_new_classification_table(new_classification, season):
    with get_database_connection() as db:
        # Crear la tabla
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS nba_new_classification (
            "Key" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Team Id" INTEGER,
            Season INTEGER NOT NULL,
            "Quality Percentage" REAL NOT NULL,
            FOREIGN KEY("Team Id") REFERENCES nba_teams(id)
        );
        ''')
        db.commit()
        print(f"La tabla  ha sido creada con éxito.")

        # Insertar o actualizar los datos en la tabla
        for team_id, quality_percentage in new_classification.items():
            # Sentencia SQL para insertar cada fila
            query = "INSERT INTO nba_new_classification ([Team Id], season, [Quality Percentage]) VALUES (?, ?, ?)"
            data = (team_id, season, quality_percentage)
            # Ejecutar la consulta
            cursor.execute(query, data)
            db.commit()
        print(f"Los datos han sido insertados con éxito.")

# Función para obtener la nueva clasificación basada en la calidad de victorias de la temporada especificada
def get_new_classification(season: int):
    with get_database_connection() as db:
        cursor = db.cursor()
        # Realizar un JOIN entre nba_new_classification y nba_teams para obtener Team Name y Quality Percentage
        cursor.execute("""
            SELECT t."Team Name", nc."Quality Percentage", t.Conference, t.Logo
            FROM nba_new_classification AS nc
            JOIN nba_teams AS t ON nc."Team Id" = t.Id
            WHERE nc.Season = ?
            ORDER BY nc."Quality Percentage" DESC
        """, (season,))
        data_new_classification = cursor.fetchall()
    return data_new_classification



# Función para crear la tabla que contendrá todas las clasificaciones de todos los equipos entre todas las temporadas disponibles
def create_all_classifications_table():
    with get_database_connection() as db:
        # Crear la tabla
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS all_classifications (
            "Key" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Team Name" INTEGER,
            season INTEGER NOT NULL,
            Position INTEGER NOT NULL
        );
        ''')
        db.commit()
        print(f"La tabla  ha sido creada con éxito.")

# Función para actualizar la tabla de todas las clasificaciones de todos los equipos entre todas las temporadas disponibles
def update_all_classifications(classification, season, type):
    # Cuando la tabla ya existe se insertan los datos de la clasificación de la temporada actual
    with get_database_connection() as db:
        for team in classification:

            team_name = team['name']
            season_type = str(season) + "_"+ type
            position = classification.index(team) + 1

            cursor = db.cursor()
            query = "INSERT INTO all_classifications ([Team Name], season, Position) VALUES (?, ?, ?)"
            data = (team_name, season_type, position)
            cursor.execute(query, data)
            db.commit()
            # print(f"La tabla  ha sido actualizada.")

#Función para obtener la tabla de todas las clasificaciones de todos los equipos entre todas las temporadas disponibles
def get_all_classifications():
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT "Team Name", season, Position 
        FROM all_classifications
        ORDER BY season
        """
        cursor.execute(query)
        result = cursor.fetchall()
    return result




# Función para obtener las victorias por cada pareja de equipos
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

# Función para obtener la información de los equipos de la NBA
def get_teams():
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT "Team Name", Id, Conference, Division, Logo FROM nba_teams
        """
        cursor.execute(query)
        teams = cursor.fetchall()
    return teams

# Función para obtener la división de un equipo
def get_team_division(team_name):
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT Division FROM nba_teams WHERE "Team Name" = ? 
        """
        cursor.execute(query, (team_name,))
        result = cursor.fetchone()
    return result[0]

# Función para obtener la conferencia de un equipo
def get_team_conference(team_name):
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT Conference FROM nba_teams WHERE "Team Name" = ?
        """
        cursor.execute(query, (team_name,))
        result = cursor.fetchone()
    return result[0]

# Función para devolver todos los equipos que son de la misma división que otro equipo dado
def get_team_whole_division(team_name, season):
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
            SELECT 
                nt."Team Name"
            FROM 
                nba_teams nt
            JOIN 
                nba_normal_classification nc ON nt."Id" = nc."Team Id"
            WHERE 
                nt.Division = (SELECT Division FROM nba_teams WHERE "Team Name" = ?)
                AND nc.Season = ?       
            ORDER BY nc."Victory Percentage" DESC
            """
        cursor.execute(query, (team_name, season))
        result = cursor.fetchall()
    return result

# Función para devolver todos los equipos que son de la misma conferencia que otro equipo dado
def get_team_whole_conference(team_name, season):
    with get_database_connection() as db:
        cursor = db.cursor()
        query = """
        SELECT 
                nt."Team Name", nc."Victory Percentage"
            FROM 
                nba_teams nt
            JOIN 
                nba_normal_classification nc ON nt."Id" = nc."Team Id"
            WHERE 
                nt.Conference = (SELECT Conference FROM nba_teams WHERE "Team Name" = ?)
                AND nc.Season = ?       
            ORDER BY nc."Victory Percentage" DESC
        """
        cursor.execute(query, (team_name, season))
        result = cursor.fetchall()
    return result






