# src/core/load_teams.py

import csv
from proyecto_pcfutbol.manager.src.core.equipo import Team
from proyecto_pcfutbol.manager.src.core.liga import League

def load_teams(file_path):
    teams = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            team = Team(row['team_name'], int(row['budget']))
            teams.append((team, row['country'], row['league']))
    return teams

def assign_teams_to_leagues(teams):
    leagues = {}
    for team, country, league_name in teams:
        if league_name not in leagues:
            leagues[league_name] = League(league_name, country, 1)
        leagues[league_name].add_team(team)
    return leagues
