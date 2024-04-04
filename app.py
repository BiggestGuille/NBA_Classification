from flask import Flask, render_template
from src.modules import database
from src.modules import analytics

app = Flask(__name__, template_folder="src/templates")

@app.route('/')
def home():
    database.initialize_database()
    analytics.get_analytics(2021)
    clasificaciones = "clasificaciones" # PlaceHolder
    return render_template('index.html', clasificaciones=clasificaciones)



if __name__ == '__main__':
    app.run(debug=True)