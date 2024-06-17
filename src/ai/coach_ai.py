# src/ai/coach_ai.py

class CoachAI:
    def __init__(self, team):
        self.team = team

    def make_tactical_decisions(self):
        """Tomar decisiones tácticas para el equipo"""
        self.select_players()
        self.set_tactics()
        self.plan_training()

    def select_players(self):
        """Seleccionar jugadores para el partido"""
        # Ejemplo de lógica de selección de jugadores
        starting_eleven = sorted(self.team.players, key=lambda p: p.skills['overall'], reverse=True)[:11]
        self.team.starting_eleven = starting_eleven
        print(f"{self.team.name}: Jugadores seleccionados para el próximo partido.")

    def set_tactics(self):
        """Establecer tácticas para el equipo"""
        # Ejemplo de lógica de tácticas
        self.team.tactics = "Defensiva"
        print(f"{self.team.name}: Tácticas establecidas a defensiva.")

    def plan_training(self):
        """Planificar sesiones de entrenamiento"""
        # Ejemplo de lógica de planificación de entrenamientos
        for player in self.team.players:
            player.fitness += 10
        print(f"{self.team.name}: Entrenamiento planificado para todos los jugadores.")
