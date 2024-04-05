from . import database

def get_analytics(season: int):

    # Se recogen las clasificaciones normales de la temporada

    # Si la tabla de clasificaciones normal no existe, se calcula y se crea
    if database.verify_table("nba_normal_classification") == False:
        # Se calcula la clasificación normal de la temporada usando la tabla de partidos
        results = database.calculate_normal_classification(season)
        # Calculate the victory percentage for each team
        victory_percentage_by_id = {team: (victories / total_matches) for team, victories, total_matches in results}
        # Se crea la tabla de clasificación normal
        database.create_normal_classification_table(victory_percentage_by_id, season)

    # Se obtiene la clasificación normal de la temporada para su posterior utilización
    data_normal_classification = database.get_normal_classification(season)
    # print(data_normal_classification)

    # Se recogen las clasificaciones nuevas de la temporada (según método estudiado)

    if database.verify_table("nba_new_classification") == False:
        # Se calcula la clasificación nueva de la temporada
        new_classification = calculate_new_classification(season)
        # Se crea la tabla de clasificación nueva
        #database.create_new_classification_table(new_classification, season)
    
    #data_new_classification = database.get_new_classification(season)
    #print(data_new_classification)
    

def calculate_new_classification(season: int):
    # Buscamos construir una matriz de victorias de cada equipo contra cada equipo.
    database.get_victories_per_pair(season)