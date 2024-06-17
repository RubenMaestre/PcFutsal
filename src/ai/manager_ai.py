# src/ai/manager_ai.py

class ManagerAI:
    def __init__(self, team):
        self.team = team

    def make_decisions(self):
        """Tomar decisiones estratégicas para el equipo"""
        self.manage_finances()
        self.hire_coach()
        self.handle_crisis()

    def manage_finances(self):
        """Gestionar las finanzas del equipo"""
        # Ejemplo de lógica de finanzas
        if self.team.finance.budget < 50000:
            print(f"{self.team.name}: Necesitamos aumentar los ingresos.")
            # Implementar estrategias para aumentar ingresos

    def hire_coach(self):
        """Contratar un entrenador si es necesario"""
        # Ejemplo de lógica de contratación de entrenadores
        if not self.team.coach:
            print(f"{self.team.name}: Necesitamos contratar un entrenador.")
            # Implementar lógica para contratar un entrenador

    def handle_crisis(self):
        """Manejar situaciones de crisis"""
        # Ejemplo de manejo de crisis
        if self.team.performance < 50:
            print(f"{self.team.name}: Estamos en crisis, necesitamos cambios.")
            # Implementar estrategias para manejar la crisis
