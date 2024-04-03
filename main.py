from src.modules import database
from src.modules import data_importer
from src.modules import analytics

def main():
    database.initialize_database()
    analytics.get_analytics(2021)



if __name__ == "__main__":
    main()