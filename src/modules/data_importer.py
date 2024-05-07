import pandas as pd
import os
from . import database

# Lista de Temporadas - Variable Global por si se introduce una temporada nueva
season_list = [2015, 2016, 2017, 2018, 2020, 2021, 2022, 2023]

# Función para crear la tabla de equipos e introducir todos los datos procedentes de la hoja de cálculo
def teams_table(db, df_teams):
    # Sentencia de creación de tabla
    create_teams_table = '''
    CREATE TABLE IF NOT EXISTS nba_teams (
        id INTEGER PRIMARY KEY,
        team_name TEXT NOT NULL,
        conference TEXT NOT NULL,
        division TEXT NOT NULL,
        logo TEXT
    );
    '''
    # Ejecutar la consulta de creación
    db.execute(create_teams_table)

    # Insertar los datos en la tabla
    df_teams.to_sql('nba_teams', db, if_exists='replace', index=False)

# Función para crear la tabla de partidos e introducir todos los datos procedentes de la hoja de cálculo
def matches_table(db, df_matches):
    create_matches_table = '''
    CREATE TABLE IF NOT EXISTS nba_matches (
        id INTEGER PRIMARY KEY,
        season INTEGER NOT NULL,
        date TEXT NOT NULL,
        home_id INTEGER NOT NULL,
        home_team TEXT NOT NULL,
        home_points INTEGER NOT NULL,
        home_result INTEGER NOT NULL,
        visitor_id INTEGER NOT NULL,
        visitor_team TEXT NOT NULL,
        visitor_points INTEGER NOT NULL,
        visitor_result INTEGER NOT NULL,
        FOREIGN KEY(home_id) REFERENCES nba_teams(id),
        FOREIGN KEY(visitor_id) REFERENCES nba_teams(id)
    );
    '''
  
    db.execute(create_matches_table)

    df_matches.to_sql('nba_matches', db, if_exists='replace', index=False)

"""
Función para asegurar que los datos principales sobre partidos y equipos, 
procedentes de la hoja de cálculo, se importan al inicio de la aplicación.
"""
def import_excel_to_database():
    try:
        # Ruta al archivo Excel
        excel_file = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'nba_games.xlsx')
        # Lee el archivo Excel
        df_teams = pd.read_excel(excel_file, sheet_name='Teams')
    except FileNotFoundError:
        print(f"Archivo Excel no encontrado: {excel_file}")
        return
    except ValueError as e:
        print(f"Error al leer la hoja 'Teams' del archivo Excel: {e}")
        return
    
    try:
        # Conexión a la base de datos SQLite
        with database.get_database_connection() as db:
            # Crear la tabla de equipos
            teams_table(db, df_teams)

            # Inicialización del DataFrame vacío
            df_matches_all_seasons = pd.DataFrame()

            # Unir los partidos de todas las temporadas en un único DataFrame
            for season in season_list:
                try:
                    # Leer Excel y concatenar al DataFrame
                    df_matches = pd.read_excel(excel_file, sheet_name=str(season))
                    df_matches_all_seasons = pd.concat([df_matches_all_seasons, df_matches], ignore_index=True)
                except ValueError as e:
                    print(f"Error al leer la hoja '{season}' del archivo Excel: {e}")
                    return

            # Crear la tabla de partidos
            matches_table(db, df_matches_all_seasons)

    except Exception as e:
        print(f"Error inesperado: {e}")
        return

    # Mensaje de éxito
    print("Datos importados correctamente")
