from flask import Flask, jsonify, redirect, render_template, request, url_for
from src.modules import database
from src.modules import analytics

app = Flask(__name__, template_folder="src/templates",static_folder='src/static')
database_initialized = False

# Inicio de la aplicación
@app.route('/')
def home():
    global database_initialized
    if not database_initialized:
        database.initialize_database()
        database_initialized = True
    return render_template('index.html')

@app.route('/classifications')
def classifications():
    if not database_initialized:
        return redirect(url_for('home'))
    # Obtiene el parámetro 'season' de la consulta, con un valor por defecto si no se proporciona
    season = request.args.get('season', default=2020, type=int)
    
    norm_classif, new_classif = analytics.get_analytics(season)

    # Verifica si se encontraron las clasificaciones
    if norm_classif is None or new_classif is None:
        return render_template('not_found.html'), 404
    
    # Verifica si es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'norm_classif': norm_classif, 'new_classif': new_classif})
    
    return render_template('classifications.html', norm_classif=norm_classif, new_classif=new_classif)

@app.route('/explanation')
def explanation():
    if not database_initialized:
        return redirect(url_for('home'))
    return render_template('explanation.html')

# Manejador de error para el error 404 (Página no encontrada)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
