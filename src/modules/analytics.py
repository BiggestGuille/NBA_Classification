from . import database
from flask import jsonify
import numpy as np
import matplotlib.pyplot as plt
import random
import csv

def get_analytics(season: int):

    # Se recogen las clasificaciones normales de la temporada

    # Si la tabla de clasificaciones normal no existe en esa temporada, se calcula y se crea
    if not database.verify_table("nba_normal_classification") or not database.check_season_data("nba_normal_classification", season):
        # Se calcula la clasificación normal de la temporada usando la tabla de partidos
        results = database.calculate_normal_classification(season)
        total_matches = 72 if season == 2020 else 82
        # Se calcula el porcentaje de victorias con los datos obtenidos
        victory_percentage_by_id = {team: round((victories / total_matches), 3) for team, victories in results}
        # Se crea la tabla de clasificación normal
        database.create_normal_classification_table(victory_percentage_by_id, season)

    # Se obtiene la clasificación normal de la temporada para su posterior utilización
    data_normal_classification = database.get_normal_classification(season)
    # Añadimos columna desempate
    tie_breaker = 0
    # Añadir el valor a cada tupla usando una comprensión de listas
    norm_classif_modified = [row + (tie_breaker,) for row in data_normal_classification]
    norm_classif_modified = sorted(norm_classif_modified, key=lambda x: x[1], reverse=True)
    # Pasamos a lista de listas para que no sea inmutable
    norm_classif_list = [list(tupla) for tupla in norm_classif_modified]
    # Si hay empates, necesitamos especificar la clasificación de desempate
    norm_classif_tie_breaker = check_draws(norm_classif_list, season)
    # Se ordena la clasificación de nuevo con los desempates
    norm_classif_sorted = sorted(norm_classif_tie_breaker, key=lambda x: (x[1], x[4]), reverse=True)
    
    norm_classif_json = [
        {'name': team[0], 'percentage': team[1], 'conference': team[2], 'logo': team[3]}
        for team in norm_classif_sorted
    ]

    # Se recogen las clasificaciones nuevas de la temporada (según método estudiado)

    # Si la tabla de clasificaciones nuevas no existe en esa temporada, se calcula y se crea
    if database.verify_table("nba_new_classification") == False or not database.check_season_data("nba_new_classification", season):
        # Se calcula la clasificación nueva de la temporada
        new_classification = calculate_new_classification(season)
        if new_classification is None:
            return None
        # Se crea la tabla de clasificación nueva
        database.create_new_classification_table(new_classification, season)
    
    # Se obtiene la clasificación nueva de la temporada para su posterior utilización
    data_new_classification = database.get_new_classification(season)
    data_new_classification = [list(tupla) for tupla in data_new_classification]
    new_classif_sorted = sorted(data_new_classification, key=lambda x: x[1], reverse=True)
    new_classif_json = [
        {'name': team[0], 'percentage': team[1], 'conference': team[2], 'logo': team[3]}
        for team in new_classif_sorted
    ]

    return norm_classif_json, new_classif_json

    """
    # Comprobar que el Quality Percentage es correcto (debe ser 1 con algún decimal de precisión)
    print(database.check_quality_percentage(season))

    # Primera prueba de que, en efecto, la clasificación cambia
    print(norm_classif_sorted)
    print(new_classif_sorted)
    """

    """
    with open('classifications.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Team Name', 'Percentage'])  # Encabezados del CSV
        writer.writerows(norm_classif_sorted)
        writer.writerow([])  # Añade una línea vacía entre los dos conjuntos de datos
        writer.writerows(new_classif_sorted)
    """
    
# Función que calcula los desempates en caso de empate en la clasificación
def check_draws(classification, season):
    for i in range(len(classification) - 1):
        victories_team1 = 0
        victories_team2 = 0
        # Comparamos si el porcentaje actual es diferente al siguiente
        if classification[i][1] == classification[i + 1][1]:
            team1 = classification[i][0]
            team2 = classification[i + 1][0]
            victories_per_pair = database.get_victories_per_pair(season)
            # Buscamos los partidos entre los dos equipos
            for home_team, visitor_team, local_victories, visitor_victories in victories_per_pair:
                if team1 == home_team and team2 == visitor_team:
                    victories_team1 += local_victories
                    victories_team2 += visitor_victories
                elif team2 == home_team and team1 == visitor_team:
                    victories_team2 += local_victories
                    victories_team1 += visitor_victories
            # Si el equipo 1 tiene más victorias, se le asigna un valor mayor
            if victories_team1 > victories_team2:
                classification[i][4] = 1
            elif victories_team1 < victories_team2:
                classification[i+1][4] = 1
            else:
                division_from_team1 = [team[0] for team in database.get_team_whole_division(team1)]
                division_from_team2 = [team[0] for team in database.get_team_whole_division(team2)]
                if division_from_team1.index(team1) == 0 and division_from_team2.index(team2) != 0:
                    classification[i][4] = 1
                elif division_from_team2.index(team2) == 0 and division_from_team1.index(team1) != 0:
                    classification[i+1][4] = 1
                else:
                    print("SE HA LLEGADO AL LÍMITE DE DESEMPATE. NO SE PUEDE RESOLVER.")
    return classification


# Función para calcular la clasificación de la temporada según el método estudiado	
def calculate_new_classification(season: int):
    # Buscamos construir una matriz de victorias de cada equipo contra cada equipo.
    victories_per_pair = database.get_victories_per_pair(season)
    teams_sql = database.get_teams()
    # Cada elemento de la lista es una tupla, por lo que hay que transformarlo a strings
    teams_names = [team[0] for team in teams_sql]
    teams_ids = [team[1] for team in teams_sql]

    # Creamos una matriz de ceros de 30x30 para almacenar las victorias de cada equipo sobre cada equipo
    victories_matrix = np.zeros((30, 30))

    # Llenamos la matriz con las victorias que hemos obtenido
    for home_team, visitor_team, local_victories, visitor_victories in victories_per_pair:
        i = teams_names.index(home_team)
        j = teams_names.index(visitor_team)
        # Asegúrate de sumar las victorias del equipo local cuando juega en casa y como visitante
        victories_matrix[i, j] += local_victories
        victories_matrix[j, i] += visitor_victories
    
    # show_matrix(victories_matrix, teams)

    # Se comprueba que se cumple el teorema de Perron-Frobenius
    # de manera que el método de las potencias converge al vector de Perron
    if verify_perron_frobenius(victories_matrix):

        # Aplicamos el método de las potencias para obtener el vector de Perron
        initial_vector = np.ones(30) # Vector inicial
        matrix_iter = victories_matrix 

        # Método de las potencias
        perron_vector = power_method(matrix_iter, initial_vector)
        # Redondear el resultado a 5 decimales
        perron_vector = np.round(perron_vector, decimals=5)

        """
        # Comprobación con un vector aleatorio, debería dar el mismo resultado
        vector_random = [random.randint(0, 100) for _ in range(30)]
        perron_vector2 = power_method(matrix_iter, vector_random)
        perron_vector2 = np.round(perron_vector2, decimals=5)
        comparacion = perron_vector == perron_vector2
        print(comparacion)
        """

        # Se enlaza el resultado para obtener el ranking de los equipos
        new_classification = {}

        # Usamos un bucle for para iterar sobre cada elemento del vector
        for i, value in enumerate(perron_vector, start=1):
            key = teams_ids[i-1]
            # Insertamos el par clave-valor en el diccionario
            new_classification[key] = value

        return new_classification
    else:
        print("No se cumple el teorema de Perron-Frobenius. No se puede aplicar el método de las potencias.")
        return None

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
            print(f"Convergió después de {iterations+1} iteraciones.")
            return vector_iter
        
        lambda_old = lambda_new
        
    print("No convergió.")
    return vector_iter








