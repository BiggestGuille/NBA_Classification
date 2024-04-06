from . import database
import numpy as np
import matplotlib.pyplot as plt

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
    victories_per_pair = database.get_victories_per_pair(season)
    teams_sql = database.get_teams()
    # Cada elemento de la lista es una tupla, por lo que hay que transformarlo a strings
    teams = [team[0] for team in teams_sql]

    # Creamos una matriz de ceros de 30x30 para almacenar las victorias de cada equipo sobre cada equipo
    victories_matrix = np.zeros((30, 30))

    # Llenamos la matriz con las victorias que hemos obtenido
    for home_team, visitor_team, local_victories, visitor_victories in victories_per_pair:
        i = teams.index(home_team)
        j = teams.index(visitor_team)
        # Asegúrate de sumar las victorias del equipo local cuando juega en casa y como visitante
        victories_matrix[i, j] += local_victories
        victories_matrix[j, i] += visitor_victories

    show_matrix(victories_matrix, teams)


def show_matrix(matrix, teams):
    fig, ax = plt.subplots(figsize=(10, 10)) # Ajusta el tamaño si es necesario
    cax = ax.matshow(matrix, cmap='coolwarm')

    # Añadir anotaciones con los números
    for (i, j), val in np.ndenumerate(matrix):
        ax.text(j, i, f'{int(val)}', ha='center', va='center', color='black')

    # Añadir nombres de equipos en los ejes
    plt.xticks(range(len(teams)), teams, rotation=90)
    plt.yticks(range(len(teams)), teams)

    # Opcional: Añadir barra de colores para indicar la escala
    fig.colorbar(cax)

    plt.show()  