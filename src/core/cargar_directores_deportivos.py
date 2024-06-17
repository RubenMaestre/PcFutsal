import csv
from src.core.director_deportivo import SportingDirector

def load_sporting_directors(file_path):
    sporting_directors = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sporting_director = SportingDirector(
                id=row['id'],
                name=row['name'],
                preferred_player_types=row['preferred_player_types'].split(' and '),
                preferred_coach_types=row['preferred_coach_types'].split(' and ')
            )
            sporting_directors.append(sporting_director)
    return sporting_directors
