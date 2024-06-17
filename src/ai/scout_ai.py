# src/ai/scout_ai.py

class ScoutAI:
    def __init__(self, team):
        self.team = team

    def scout_players(self):
        """Buscar y evaluar nuevos talentos"""
        self.evaluate_players()
        self.recommend_signings()

    def evaluate_players(self):
        """Evaluar las habilidades y el potencial de los jugadores"""
        # Ejemplo de lógica de evaluación de jugadores
        for player in self.team.players:
            player.potential = player.skills['overall'] + 10
        print(f"{self.team.name}: Jugadores evaluados por su potencial.")

    def recommend_signings(self):
        """Recomendar jugadores para fichajes"""
        # Ejemplo de lógica de recomendaciones de fichajes
        potential_signings = sorted(self.team.players, key=lambda p: p.potential, reverse=True)[:5]
        self.team.potential_signings = potential_signings
        print(f"{self.team.name}: Jugadores recomendados para fichajes.")
