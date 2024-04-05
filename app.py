from flask import Flask, render_template
from src.modules import database
from src.modules import analytics

app = Flask(__name__, template_folder="src/templates",static_folder='src/static')

@app.route('/')
def home():
    database.initialize_database()
    analytics.get_analytics(2021)
    clasificaciones = "clasificaciones" # PlaceHolder
    return render_template('index.html', clasificaciones=clasificaciones)

# Manejador de error para el error 404 (Página no encontrada)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True)