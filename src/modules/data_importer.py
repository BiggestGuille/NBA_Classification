import pandas as pd
import os
import sqlite3


def teams_table(db, df_teams):
    # Crear una tabla
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

    # Verificar los datos
    test_query = "SELECT * FROM nba_teams LIMIT 5;"
    print(pd.read_sql_query(test_query, db))


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

    # Verificar los datos
    test_query1 = f"SELECT * FROM nba_matches WHERE season = 2015 LIMIT 5;"
    test_query2 = f"SELECT * FROM nba_matches WHERE season = 2021 LIMIT 5;"
    print(pd.read_sql_query(test_query1, db))
    print(pd.read_sql_query(test_query2, db))


def import_excel_to_database():
    # Ruta al archivo Excel
    excel_file = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'nba_games.xlsx')
    # Lee el archivo Excel
    df_teams = pd.read_excel(excel_file, sheet_name='Teams')

    # Creación de la base de datos SQLite
    ruta_db = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'nba_data.db')
    db = sqlite3.connect(ruta_db)

    # Crear la tabla de equipos
    teams_table(db, df_teams)

    # Inicialización del DataFrame vacío
    df_matches_all_seasons = pd.DataFrame()
    # Lista de temporadas
    season_list = [2015, 2016, 2017, 2018, 2020, 2021, 2022]

    for season in season_list:

        # Leer partidos por temporada
        df_matches = pd.read_excel(excel_file, sheet_name = str(season))
        # Concatenar los datos de esta temporada al DataFrame general
        df_matches_all_seasons = pd.concat([df_matches_all_seasons, df_matches], ignore_index=True)

    # Crear la tabla de partidos
    matches_table(db, df_matches_all_seasons)

    # Mensaje de éxito
    print("Datos importados correctamente")

    # Cerrar la conexión
    db.close()
