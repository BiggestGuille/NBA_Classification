from . import database
import numpy as np
import matplotlib.pyplot as plt
from . import data_importer
# import random
# import csv

# Función que calcula las clasificaciones normales y nuevas de una temporada dada
def get_analytics(season: int):

    # En primer lugar, se recogen o calculan las clasificaciones normales de la temporada

    # Si la tabla de clasificaciones normal no existe en esa temporada, se calcula y se crea
    if not database.verify_table("nba_normal_classification") or not database.check_season_data("nba_normal_classification", season):
        # Se calcula la clasificación normal de la temporada usando la tabla de partidos
        results = database.calculate_normal_classification(season)
        total_matches = 72 if season == 2020 else 82
        # Se calcula el porcentaje de victorias con los datos obtenidos
        victory_percentage_by_id = {team: round((victories / total_matches), 3) for team, victories in results}
        # Se crea la tabla de clasificación normal
        database.create_normal_classification_table(victory_percentage_by_id, season)

    # Se obtiene la clasificación normal de la temporada
    data_normal_classification = database.get_normal_classification(season)
    # Añadimos columna para desempate
    tie_breaker = 0
    norm_classif_modified = [row + (tie_breaker,) for row in data_normal_classification]
    norm_classif_modified = sorted(norm_classif_modified, key=lambda x: x[1], reverse=True)
    # Pasamos a lista de listas para que no sea inmutable
    norm_classif_list = [list(tupla) for tupla in norm_classif_modified]
    # Se realiza el desempate
    norm_classif_tie_breaker = check_draws(norm_classif_list, season)
    # Se vuelve a ordenar la clasificación con los desempates según la columna nuevamente añadida
    norm_classif_sorted = sorted(norm_classif_tie_breaker, key=lambda x: (x[1], x[4]), reverse=True)
    # Se vuelve a desempatar y ordenar por si hay triple empate.
    norm_classif_tie_breaker = check_draws(norm_classif_sorted, season)
    norm_classif_sorted = sorted(norm_classif_tie_breaker, key=lambda x: (x[1], x[4]), reverse=True)



    # Se recogen las clasificaciones nuevas de la temporada (según el método estudiado)

    # Si la tabla de clasificaciones nuevas no existe en esa temporada, se calcula y se crea
    if database.verify_table("nba_new_classification") == False or not database.check_season_data("nba_new_classification", season):
        # Se calcula la clasificación nueva de la temporada
        new_classification = calculate_new_classification(season)
        if new_classification is None:
            return None
        # Se crea la tabla de clasificación nueva
        database.create_new_classification_table(new_classification, season)

    # Se obtiene la clasificación nueva de la temporada
    data_new_classification = database.get_new_classification(season)
    data_new_classification = [list(tupla) for tupla in data_new_classification]

    # Se convierten las clasificaciones a formato JSON para su tratamiento en el frontend
    norm_classif_json = [
        {'name': team[0], 'percentage': team[1], 'conference': team[2], 'logo': team[3]}
        for team in norm_classif_sorted
    ]
    
    new_classif_json = [
        {'name': team[0], 'percentage': team[1], 'conference': team[2], 'logo': team[3]}
        for team in data_new_classification
    ]

    # Se actualizan las clasificaciones en la tabla de todas las clasificaciones
    if not database.verify_table("all_classifications"):
        database.create_all_classifications_table()

    if not database.check_season_data("all_classifications", season):
        database.update_all_classifications(norm_classif_json, season, "normal")
        database.update_all_classifications(new_classif_json, season, "new")

    return norm_classif_json, new_classif_json
    
# Función que calcula los desempates en caso de empate en la clasificación
def check_draws(classification, season):
    # Necesitaremos la matriz de victorias
    victories_matrix = get_victories_matrix(season)
    teams_names = [team[0] for team in database.get_teams()]

    for i in range(len(classification) - 1):
        # Comparamos si el porcentaje actual es igual al siguiente (hay empate). Si hay empate triple puede que sea mayor en una unidad.
        if classification[i][1] == classification[i + 1][1] and classification[i][4] - classification[i + 1][4] <= 1 and classification[i-1][4]<2:

            team1 = classification[i][0]
            team2 = classification[i + 1][0]
            team3 = None
            team4 = None

            # Caso empate cuádruple
            # Sólo se da una vez en 10 años en una misma conferencia. Se hará manualmente.
            if i < len(classification) - 3 and classification[i][1] == classification[i + 1][1] == classification[i + 2][1] == classification[i + 3][1]:
                team3 = classification[i + 2][0]
                team4 = classification[i + 3][0]
                if database.get_team_conference(team1) == database.get_team_conference(team2) == database.get_team_conference(team3) == database.get_team_conference(team4) and classification[i+1][0] != "Atlanta Hawks":
                    classification[i][4] = 3
                    classification[i+3][4] = 2
                    classification[i+2][4] = 1
                    classification[i+1][4] = 0
                    continue

            # Caso empate cuiádruple en el que sólo 3 equipos son de la misma conferencia. Se hará manualmente para la única temporada en que ocurre, pues no es prioridad.
            if i < len(classification) - 3 and classification[i][1] == classification[i + 1][1] == classification[i + 2][1] == classification[i + 3][1]:
                team3 = classification[i + 2][0]
                team4 = classification[i + 3][0]
                if database.get_team_conference(team1) == database.get_team_conference(team2) == database.get_team_conference(team4) and database.get_team_conference(team3) != database.get_team_conference(team1):
                    classification[i+1][4] = 3
                    classification[i+2][4] = 2
                    classification[i+3][4] = 1
                    classification[i][4] = 0
                    continue

            # Caso empate triple
            if i < len(classification) - 2 and classification[i][1] == classification[i + 1][1] == classification[i + 2][1]:
                
                # En primer lugar, se mira si hay empate triple y hay líderes de división, en cuyo caso se desempata
                team3 = classification[i + 2][0]
                if database.get_team_conference(team1) == database.get_team_conference(team2) == database.get_team_conference(team3):
                    division_from_team1 = [team[0] for team in database.get_team_whole_division(team1, season)]
                    division_from_team2 = [team[0] for team in database.get_team_whole_division(team2, season)]
                    division_from_team3 = [team[0] for team in database.get_team_whole_division(team3, season)]

                    if division_from_team1.index(team1) == 0 and division_from_team2.index(team2) != 0 and division_from_team3.index(team3) != 0:
                        classification[i][4] = 2
                        team1 = classification[i+1][0]
                        team2 = classification[i + 2][0]
                        
                    elif division_from_team2.index(team2) == 0 and division_from_team1.index(team1) != 0 and division_from_team3.index(team3) != 0:
                        classification[i+1][4] = 2
                        team2 = classification[i + 2][0]
                        
                    elif division_from_team3.index(team3) == 0 and division_from_team1.index(team1) != 0 and division_from_team2.index(team2) != 0:
                        classification[i+2][4] = 2

                    elif division_from_team1.index(team1) == 0 and division_from_team2.index(team2) == 0 and division_from_team3.index(team3) != 0:
                        classification[i][4] = 2
                        classification[i+1][4] = 2
                        continue
                    elif division_from_team1.index(team1) == 0 and division_from_team3.index(team3) == 0 and division_from_team2.index(team2) != 0:
                        classification[i][4] = 2
                        classification[i+2][4] = 2
                        continue
                    elif division_from_team2.index(team2) == 0 and division_from_team3.index(team3) == 0 and division_from_team1.index(team1) != 0:
                        classification[i+1][4] = 2
                        classification[i+2][4] = 2
                        continue

                    else:
                        # Empate triple entre equipos que no son líderes de división. Seguir desempatando...
                        # Ganará el equipo con mejor % de victorias en todos los partidos entre los equipos empatados
                        total_matches_team1 = 0
                        total_matches_team2 = 0
                        total_matches_team3 = 0
                        victories_team1 = 0
                        victories_team2 = 0
                        victories_team3 = 0

                        for team in [team1, team2, team3]:
                            total_matches_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team)] + victories_matrix[teams_names.index(team), teams_names.index(team1)]
                            total_matches_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team)] + victories_matrix[teams_names.index(team), teams_names.index(team2)]
                            total_matches_team3 += victories_matrix[teams_names.index(team3), teams_names.index(team)] + victories_matrix[teams_names.index(team), teams_names.index(team3)]
                            victories_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team)]
                            victories_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team)]
                            victories_team3 += victories_matrix[teams_names.index(team3), teams_names.index(team)]

                        if victories_team1/total_matches_team1 > victories_team2/total_matches_team2 and victories_team1/total_matches_team1 > victories_team3/total_matches_team3:
                            classification[i][4] = 2
                            team1 = classification[i+1][0]
                            team2 = classification[i + 2][0]
                        elif victories_team2/total_matches_team2 > victories_team1/total_matches_team1 and victories_team2/total_matches_team2 > victories_team3/total_matches_team3:
                            classification[i+1][4] = 2
                            team2 = classification[i + 2][0]
                        elif victories_team3/total_matches_team3 > victories_team1/total_matches_team1 and victories_team3/total_matches_team3 > victories_team2/total_matches_team2:
                            classification[i+2][4] = 2
                        # else:
                            # Más desempate triple es necesario
                # else:
                    # Empate entre tres equipos de distinta conferencia. No es relevante. 


            # Empate entre dos Equipos

            # GANARÁ el equipo que tenga más victorias entre ellos
            victories_team1 = victories_matrix[teams_names.index(team1), teams_names.index(team2)]
            victories_team2 = victories_matrix[teams_names.index(team2), teams_names.index(team1)]

            if victories_team1 > victories_team2:
                classification[i][4] += 1
                continue
            elif victories_team1 < victories_team2:
                classification[i+1][4] += 1
                continue
            # Si no hay desempate...
            else:

                # GANARÁ un equipo X que es líder de su división si el otro equipo Y no lo es
                division_from_team1 = [team[0] for team in database.get_team_whole_division(team1, season)]
                division_from_team2 = [team[0] for team in database.get_team_whole_division(team2, season)]

                if division_from_team1.index(team1) == 0 and division_from_team2.index(team2) != 0:
                    classification[i][4] += 1
                    continue
                elif division_from_team2.index(team2) == 0 and division_from_team1.index(team1) != 0:
                    classification[i+1][4] += 1
                    continue
                # Si no hay desempate...
                else:

                    # GANARÁ el equipo con mejor % de victorias contra rivales de la misma división (si el empate es entre equipos de la misma división)
                    victories_team1 = 0
                    victories_team2 = 0
                    total_matches_team1 = 0
                    total_matches_team2 = 0
                    if database.get_team_division(team1) == database.get_team_division(team2):
                        for team_in_division in division_from_team1:
                            victories_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team_in_division)]
                            victories_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team_in_division)]
                            total_matches_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team_in_division)] + victories_matrix[teams_names.index(team_in_division), teams_names.index(team1)]
                            total_matches_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team_in_division)] + victories_matrix[teams_names.index(team_in_division), teams_names.index(team2)]
                        
                        if victories_team1/total_matches_team1 > victories_team2/total_matches_team2:
                            classification[i][4] += 1
                            continue
                        elif victories_team1/total_matches_team1 < victories_team2/total_matches_team2:
                            classification[i+1][4] += 1
                            continue
    
                    # Si no hay desempate...o si no son de la misma división...
                    # Ganará el equipo con mejor % de victorias contra rivales de la misma conferencia (si el empate es entre equipos de la misma conferencia)
                    conference_from_team1 = database.get_team_whole_conference(team1, season)
                    conference_from_team2 = database.get_team_whole_conference(team2, season)
                    if database.get_team_conference(team1) == database.get_team_conference(team2):
                        for team_in_conference in conference_from_team1:
                            victories_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team_in_conference[0])]
                            victories_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team_in_conference[0])]
                            total_matches_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team_in_conference[0])] + victories_matrix[teams_names.index(team_in_conference[0]), teams_names.index(team1)]
                            total_matches_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team_in_conference[0])] + victories_matrix[teams_names.index(team_in_conference[0]), teams_names.index(team2)]
                        
                        if victories_team1/total_matches_team1 > victories_team2/total_matches_team2:
                            classification[i][4] += 1
                            continue
                        elif victories_team1/total_matches_team1 < victories_team2/total_matches_team2:
                            classification[i+1][4] += 1
                            continue

                    elif database.get_team_conference(team1) != database.get_team_conference(team2):
                        if classification[i+2][1] == classification[i+1][1] and database.get_team_conference(classification[i+2][0]) == database.get_team_conference(classification[i][0]):
                            classification[i+2][4] += 1
                            continue
                        # Empate entre dos equipos de distinta conferencia. No es relevante.
                        continue
                        
                    # Si no hay desempate...
                    # Ganará el equipo con mejor % de victorias contra rivales que están clasificados a play-off en tu misma conferencia
                    # (es decir, del 1 al 8 de tu misma conferencia incluyendo aquellos empatados por debajo del octavo puesto)
                    counter = 0
                    # Team1 y Team 2 ya son de la misma conferencia
                    teams_playoff_same_conference = []
                    victories_team1 = 0
                    victories_team2 = 0
                    total_matches_team1 = 0
                    total_matches_team2 = 0

                    for team in conference_from_team1:
                        if len(teams_playoff_same_conference)>=8 and conference_from_team1[counter][1] != conference_from_team1[counter-1][1]:
                            break
                        else:
                            teams_playoff_same_conference.append(team[0])
                            counter += 1

                    for team_in_playoff in teams_playoff_same_conference:
                        if team_in_playoff != team1:
                            victories_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team_in_playoff)]
                            total_matches_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team_in_playoff)] + victories_matrix[teams_names.index(team_in_playoff), teams_names.index(team1)]

                    for team_in_playoff in teams_playoff_same_conference:
                        if team_in_playoff != team2:
                            victories_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team_in_playoff)]
                            total_matches_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team_in_playoff)] + victories_matrix[teams_names.index(team_in_playoff), teams_names.index(team2)]

                    if victories_team1/total_matches_team1 > victories_team2/total_matches_team2:
                        classification[i][4] += 1
                        continue
                    elif victories_team1/total_matches_team1 < victories_team2/total_matches_team2:
                        classification[i+1][4] += 1
                        continue

                    else:
                        teams_playoff_diff_conference = []
                        counter = 0
                        victories_team1 = 0
                        victories_team2 = 0
                        total_matches_team1 = 0
                        total_matches_team2 = 0
                        opposite_conference = "East" if database.get_team_conference(team1) == "West" else "West"
                        opposite_conference_team = "Denver Nuggets" if opposite_conference == "West" else "Brooklyn Nets"
                        opposite_conference_from_team1 = database.get_team_whole_conference(opposite_conference, season)

                        for team in opposite_conference_from_team1:
                            if len(teams_playoff_diff_conference)>=8 and conference_from_team1[counter][1] != conference_from_team1[counter-1][1]:
                                break
                            else:
                                teams_playoff_diff_conference.append(team[0])
                                counter += 1

                        for team_in_playoff in teams_playoff_diff_conference:
                            victories_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team_in_playoff)]
                            total_matches_team1 += victories_matrix[teams_names.index(team1), teams_names.index(team_in_playoff)] + victories_matrix[teams_names.index(team_in_playoff), teams_names.index(team1)]

                        for team_in_playoff in teams_playoff_diff_conference:
                            victories_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team_in_playoff)]
                            total_matches_team2 += victories_matrix[teams_names.index(team2), teams_names.index(team_in_playoff)] + victories_matrix[teams_names.index(team_in_playoff), teams_names.index(team2)]

                        if victories_team1/total_matches_team1 > victories_team2/total_matches_team2:
                            classification[i][4] += 1
                            continue
                        elif victories_team1/total_matches_team1 < victories_team2/total_matches_team2:
                            classification[i+1][4] += 1
                            continue

                        else:
                            # Nunca se llega a la última condición de desempate
                            print("NECESITAS DESEMPATAR MÁS")

    return classification

# Función para calcular la nueva clasificación de la temporada según el método estudiado	
def calculate_new_classification(season: int):

    # Se obtiene la matriz de victorias entre cada pareja de franquicias
    victories_matrix = get_victories_matrix(season)
    
    # Se comprueba que se cumple el teorema de Perron-Frobenius
    # y los requisitos para que el método de las potencias converja al vector de Perron
    if verify_perron_frobenius(victories_matrix):

        # Aplicamos el método de las potencias para obtener el vector de Perron

        # Vector inicial
        initial_vector = np.ones(30) 
        # Método de las potencias
        perron_vector = power_method(victories_matrix, initial_vector)
        # Redondear el resultado a 5 decimales
        perron_vector = np.round(perron_vector, decimals=5)

        # Se enlaza el resultado para obtener el ranking de los equipos
        new_classification = {}
        teams_sql = database.get_teams()
        teams_ids = [team[1] for team in teams_sql]

        # Usamos un bucle for para iterar sobre cada elemento del vector
        for i, value in enumerate(perron_vector, start=1):
            key = teams_ids[i-1]
            # Insertamos el par clave-valor en el diccionario
            new_classification[key] = value

        # Se devuelve la nueva clasificación
        return new_classification
    else:
        # Indicar error en caso de no cumplir los requisitos del teorema (altamente improbable)
        print("No se cumple el teorema de Perron-Frobenius. No se puede aplicar el método de las potencias.")
        return None

# Consigue la matriz de victorias que indica las victorias de cada par de equipos i - j
def get_victories_matrix(season: int):
    # Conseguir las victorias por cada par de equipos
    victories_per_pair = database.get_victories_per_pair(season)
    teams_sql = database.get_teams()
    # Cada elemento de la lista es una tupla, por lo que hay que transformarlo a strings
    teams_names = [team[0] for team in teams_sql]
    # Creamos una matriz de ceros de 30x30 para almacenar las victorias de cada equipo sobre cada equipo
    victories_matrix = np.zeros((30, 30))

    # Conformamos la matriz con las victorias que hemos obtenido
    for home_team, visitor_team, local_victories, visitor_victories in victories_per_pair:
        i = teams_names.index(home_team)
        j = teams_names.index(visitor_team)
        # Excepción - Puede existir algún emparejamiento que no se dió en uno de los sentidos
        if local_victories is None or visitor_victories is None:
            victories_matrix[i, j] += 0
            victories_matrix[j, i] += 0
        #  Sumar las victorias del equipo local cuando juega como local y como visitante
        else:
            victories_matrix[i, j] += local_victories
            victories_matrix[j, i] += visitor_victories

    # show_matrix(victories_matrix, teams_names)
    return victories_matrix

# Comprueba que la matriz es cuadrada, no negativa y primitiva
def verify_perron_frobenius(matrix):
    # Verificar si la matriz es cuadrada
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("La matriz no es cuadrada.")
    
    # Verificar si la matriz es no negativa
    if np.any(matrix < 0):
        raise ValueError("La matriz contiene elementos negativos.")
    
    # Verificar si la matriz es primitiva (y por tanto irreducible)
    if not np.all(np.linalg.matrix_power(matrix, 10) > 0):
        raise ValueError("La matriz no es primitiva.")
    
    return True

# Muestra gráficamente la matriz de victorias de cada equipo contra cada equipo
def show_matrix(matrix, teams):
    
    # Gráfico de matriz (heatmap)
    fig, ax = plt.subplots(figsize=(10, 10))
    cax = ax.matshow(matrix, cmap='coolwarm')

    # Añadir anotaciones con los números
    for (i, j), val in np.ndenumerate(matrix):
        ax.text(j, i, f'{int(val)}', ha='center', va='center', color='black')

    # Añadir nombres de equipos en los ejes
    plt.xticks(range(len(teams)), teams, rotation=90)
    plt.yticks(range(len(teams)), teams)

    # Añadir barra de colores para indicar la escala
    fig.colorbar(cax)

    # Crear Figura
    plt.show()  

# Ejecuta el método de las potencias para calcular el vector de Perron
def power_method(matrix, initial_vector, tol=1e-7, max_iterations=1000):

    lambda_old = 0.0
    vector_iter = np.copy(initial_vector)

    for iterations in range(max_iterations):
        # Multiplica la matriz por el vector
        vector_iter = matrix.dot(vector_iter)
        # Normaliza el vector
        vector_iter /= np.sum(vector_iter)
        # print(vector_iter)
        
        # Verifica la convergencia
        lambda_new = np.dot(vector_iter, matrix.dot(vector_iter))
        if np.abs(lambda_new - lambda_old) < tol:
            print(f"Converge después de {iterations+1} iteraciones.")
            return vector_iter
        
        lambda_old = lambda_new
        
    print("No converge.")
    return vector_iter

# Inicializa las clasificaciones de todas las temporadas para mostrar los gráficos al inicio del programa
def initialize_seasons():
    for season in data_importer.season_list:
        get_analytics(season)



