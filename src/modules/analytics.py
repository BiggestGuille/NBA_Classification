from . import database

def get_analytics(season: int):
    normal_clasification = database.get_normal_classification(season)
    print(normal_clasification)
    new_clasification = 0
    