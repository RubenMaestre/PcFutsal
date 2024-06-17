import csv
from proyecto_pcfutbol.manager.src.core.presidente import President

def load_presidents(file_path):
    presidents = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            president = President(
                id=row['id'],
                name=row['name'],
                character=row['character'],
                patience=row['patience'],
                preferred_coach_types=row['preferred_coach_types'].split(' and '),
                preferred_director_types=row['preferred_director_types'].split(' and ')
            )
            presidents.append(president)
    return presidents
