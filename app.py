from flask import Flask, render_template, request
from src.modules import database
from src.modules import analytics

app = Flask(__name__, template_folder="src/templates",static_folder='src/static')

# Inicio de la aplicación
@app.route('/')
def home():
    database.initialize_database()
    return render_template('index.html')

@app.route('/classifications')
def classifications():
    # Obtiene el parámetro 'season' de la consulta, con un valor por defecto si no se proporciona
    season = request.args.get('season', default=2021, type=int)
    
    norm_classif, new_classif = analytics.get_analytics(season)
    if norm_classif is None or new_classif is None:
        return render_template('not_found.html'), 404
    return render_template('classifications.html', norm_classif=norm_classif, new_classif=new_classif)

# Manejador de error para el error 404 (Página no encontrada)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True)