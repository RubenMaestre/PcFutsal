import csv
from proyecto_pcfutbol.manager.src.core.entrenador import Coach

def load_coaches(file_path):
    coaches = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            coach = Coach(
                id=row['id'],
                name=row['name'],
                preferred_system=row['preferred_system'],
                secondary_systems=row['secondary_systems'].split(','),
                preferred_player_types=row['preferred_player_types'].split(' and '),
                control_vestuario=row['control_vestuario'],
                cantera=row['cantera'],
                aguante=row['aguante'],
                dejar_aconsejar=row['dejar_aconsejar']
            )
            coaches.append(coach)
    return coaches
