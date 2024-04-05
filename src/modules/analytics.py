from . import database

def get_analytics(season: int):
    # Si la tabla de clasificaciones normal no existe, se calcula y se crea
    if database.verify_table("nba_normal_classification") == False:
        # Se calcula la clasificación normal de la temporada usando la tabla de partidos
        normal_classification = database.calculate_normal_classification(season)
        # Se crea la tabla de clasificación normal
        database.create_normal_classification_table(normal_classification, season)

    # Se obtiene la clasificación normal de la temporada para su posterior utilización
    data_normal_classification = database.get_normal_classification(season)
    # print(data_normal_classification)

    new_classification = 0
    