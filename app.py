from flask import Flask, jsonify, redirect, render_template, request, url_for
from src.modules import database
from src.modules import analytics

app = Flask(__name__, template_folder="src/templates",static_folder='src/static')

# Variable Global para saber si la base de datos ha sido inicializada
database_initialized = False

# Inicio de la aplicación
@app.route('/')
def home():
    # Se inicializa la base de datos si es necesario
    global database_initialized
    if not database_initialized:
        database.initialize_database()
        database_initialized = True
    # Se carga la plantilla inicial
    return render_template('index.html')


# Renderiza la plantilla de clasificaciones
@app.route('/classifications')
def classifications():
    # Si es la primera vez que se renderiza la web, se debe ir a la página inicial.
    if not database_initialized:
        return redirect(url_for('home'))
    # Obtiene el parámetro 'season' de la consulta, con un valor por defecto si no se proporciona
    season = request.args.get('season', default=2021, type=int)
    
    # Se calculan las clasificaciones de dicha temporada
    norm_classif, new_classif = analytics.get_analytics(season)
    
    # Se recogen las posiciones de los equipos en todas las temporadas
    all_classif = database.get_all_classifications()
    all_classif_json = [{'name': row[0], 'season': row[1], 'position': row[2]} for row in all_classif]

    # Verifica si se encontraron las clasificaciones
    if norm_classif is None or new_classif is None:
        return render_template('not_found.html'), 404
    
    # Verifica si es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'norm_classif': norm_classif, 'new_classif': new_classif})
    
    # Se renderiza la página de clasificaciones
    return render_template('classifications.html', norm_classif=norm_classif, new_classif=new_classif, all_classif=all_classif_json)


# Calcula todas las temporadas para asegurar la carga correcta de los gráficos de rendimiento entre temporadas
@app.route('/initialize_seasons', methods=['POST'])
def initialize_seasons():
    # Inicializar todas las temporadas para poder mostrar los gráficos y recogerlas
    analytics.initialize_seasons()
    all_classif = database.get_all_classifications()
    all_classif_json = [{'name': row[0], 'season': row[1], 'position': row[2]} for row in all_classif]
    return jsonify({'all_classif': all_classif_json})


# Renderiza la plantilla de explicación
@app.route('/explanation')
def explanation():
    # Si es la primera vez que se renderiza la web, se debe ir a la página inicial
    if not database_initialized:
        return redirect(url_for('home'))
    # Se recoge información de las franquicias
    teams_sql = database.get_teams()
    teams = [
        {'name': team[0], 'id': team[1], 'conference': team[2], 'division': team[3], 'logo': team[4]}
        for team in teams_sql
    ]
    # Se renderiza la página de clasificaciones
    return render_template('explanation.html', teams = teams)


# Manejador de errores para las páginas no encontradas (Error 404 Not Found)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html'), 404


# Aplicación Principal
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
