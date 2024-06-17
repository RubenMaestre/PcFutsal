# src/core/load_players.py

import csv
from proyecto_pcfutbol.manager.src.core.jugador import Player
from proyecto_pcfutbol.manager.src.core.equipo import Team
from proyecto_pcfutbol.manager.src.core.liga import League

def load_players(file_path):
    players = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            player = Player(
                player_id=row['player_id'],
                player_url=None,
                fifa_version=None,
                fifa_update=None,
                update_as_of=None,
                short_name=row['player_name'],
                long_name=row['player_name'],
                player_positions=row['position'],
                overall=int(row['overall']),
                potential=int(row['potential']),
                value_eur=int(row['value_eur']),
                wage_eur=int(row['wage_eur']),
                age=int(row['age']),
                dob=None,
                height_cm=None,
                weight_kg=None,
                club_team_id=None,
                club_name=row['team_name'],
                league_id=None,
                league_name=None,
                league_level=None,
                club_position=None,
                club_jersey_number=None,
                club_loaned_from=None,
                club_joined_date=None,
                club_contract_valid_until_year=None,
                nationality_id=None,
                nationality_name=None,
                nation_team_id=None,
                nation_position=None,
                nation_jersey_number=None,
                preferred_foot=row['preferred_foot'],
                weak_foot=None,
                skill_moves=int(row['skill_moves']),
                international_reputation=None,
                work_rate=None,
                body_type=None,
                real_face=None,
                release_clause_eur=None,
                player_tags=None,
                player_traits=None,
                pace=int(row['pace']),
                shooting=int(row['shooting']),
                passing=int(row['passing']),
                dribbling=int(row['dribbling']),
                defending=int(row['defending']),
                physic=int(row['physic']),
                attacking_crossing=None,
                attacking_finishing=None,
                attacking_heading_accuracy=None,
                attacking_short_passing=None,
                attacking_volleys=None,
                skill_dribbling=None,
                skill_curve=None,
                skill_fk_accuracy=None,
                skill_long_passing=None,
                skill_ball_control=None,
                movement_acceleration=None,
                movement_sprint_speed=None,
                movement_agility=None,
                movement_reactions=None,
                movement_balance=None,
                power_shot_power=None,
                power_jumping=None,
                power_stamina=None,
                power_strength=None,
                power_long_shots=None,
                mentality_aggression=None,
                mentality_interceptions=None,
                mentality_positioning=None,
                mentality_vision=None,
                mentality_penalties=None,
                mentality_composure=None,
                defending_marking_awareness=None,
                defending_standing_tackle=None,
                defending_sliding_tackle=None,
                goalkeeping_diving=None,
                goalkeeping_handling=None,
                goalkeeping_kicking=None,
                goalkeeping_positioning=None,
                goalkeeping_reflexes=None,
                goalkeeping_speed=None,
                ls=None,
                st=None,
                rs=None,
                lw=None,
                lf=None,
                cf=None,
                rf=None,
                rw=None,
                lam=None,
                cam=None,
                ram=None,
                lm=None,
                lcm=None,
                cm=None,
                rcm=None,
                rm=None,
                lwb=None,
                ldm=None,
                cdm=None,
                rdm=None,
                rwb=None,
                lb=None,
                lcb=None,
                cb=None,
                rcb=None,
                rb=None,
                gk=None,
                talent_stars=float(row['talent_stars'])
            )
            players.append(player)
    return players

def assign_players_to_teams(players, teams):
    team_dict = {team.name: team for team in teams}
    for player in players:
        if player.club_name in team_dict:
            team_dict[player.club_name].add_player(player)

# Ejemplo de uso
if __name__ == "__main__":
    from proyecto_pcfutbol.manager.src.core.cargar_equipos import load_teams, assign_teams_to_leagues

    teams = load_teams('data/teams.csv')
    leagues = assign_teams_to_leagues(teams)
    players = load_players('data/players.csv')

    all_teams = [team for league in leagues.values() for team in league.get_teams()]
    assign_players_to_teams(players, all_teams)

    for team in all_teams:
        print(f"Equipo: {team.name}")
        for player in team.players:
            print(f"  Jugador: {player.short_name}, Valor: {player.value_eur}, Sueldo: {player.wage_eur}")
