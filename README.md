# NBA_Classification 🏀

## Introduction 📍 
This repository contains a web application that provides an alternative classification for NBA teams in the USA. The classification system is based on the Perron-Frobenius theorem and takes into account the quality of each victory, rather than just the win-loss record. This unique approach aims to offer a fairer perspective on the performance of NBA teams.

## Compare Classifications 💥 
This web application enables you to contrast two different NBA team classifications. The **Standard Classification** is derived from conventional data analysis, encompassing every match and season from 2015 up to the present, excluding the 2019 season due to interruptions caused by COVID-19. On the other hand, the **Alternative Classification** offers a fresh perspective by considering the quality of each victory, based on principles from the Perron-Frobenius theorem. In this way, the variability in the number of games played between teams, typically influenced by distance considerations, ceases to be an unfair factor.

This innovative approach not only introduces new insights into team performance in each conference but also allows for a comprehensive classification of all NBA teams, independent of their conference affiliations. As a result, the web application presents a unified global table that ranks teams across the entire league, providing a better view of their standings.

## Setup 🔧

### Requirements 💻
- Python 3.12+ (lower version could be used but 3.12 was used for development)
- Docker

### Installation 💻 

Clone the repository:
   ```bash
   git clone https://github.com/BiggestGuille/NBA_Classification.git
   cd NBA_Classification
   ```

### Running the application ▶️

If you have Docker installed, you can now run the web application
```bash
   docker run -p 5000:5000 nba-classif-webapp
```
The application will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000) or [http://localhost:5000](http://localhost:5000).

### Configuration for development 💻

1. Create a virtual environment for managing dependencies and ensuring that your development environment is isolated from other Python projects:
```bash
   python -m venv venv   # Crea el entorno virtual
   source venv/bin/activate     # Activa el entorno virtual en macOS/Linux
   .\venv\Scripts\activate   # Activa el entorno virtual en Windows
```
2. Install all dependencies
```bash
   pip install -r requirements.txt
```
3. Run the application
```bash
   python app.py
```

If you use Docker, you could build the image from the Dockerfile and run the container:
```bash
docker build -t nba-classif-webapp .
docker run -p 5000:5000 nba-classif-webapp
```

