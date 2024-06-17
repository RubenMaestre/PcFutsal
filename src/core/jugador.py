# src/core/jugador.py
# Aquí están las posiciones para el fútbol, habría que adaptarlo para el fútbol sala

class Jugador:
    def __init__(self, id_jugador, url_jugador, version_fifa, actualizacion_fifa, actualizacion_al_dia, nombre_corto, nombre_largo,
                 posiciones_jugador, general, potencial, valor_eur, salario_eur, edad, fecha_nacimiento, altura_cm, peso_kg, id_equipo_club,
                 nombre_club, id_liga, nombre_liga, nivel_liga, posicion_club, numero_camiseta_club, cedido_desde_club,
                 fecha_ingreso_club, contrato_valido_hasta, id_nacionalidad, nombre_nacionalidad, id_equipo_nacional,
                 posicion_nacion, numero_camiseta_nacion, pie_preferido, pie_debil, movimientos_habilidad, reputacion_internacional,
                 tasa_trabajo, tipo_cuerpo, cara_real, clausula_rescision_eur, etiquetas_jugador, rasgos_jugador, ritmo, tiro, pase,
                 regate, defensa, fisico, ataque_centros, ataque_definicion, ataque_precision_cabeza, ataque_pase_corto, ataque_voleas,
                 habilidad_regate, habilidad_efecto, habilidad_precision_tiro_libre, habilidad_pase_largo, habilidad_control_balon,
                 movimiento_aceleracion, movimiento_velocidad_sprint, movimiento_agilidad, movimiento_reacciones, movimiento_equilibrio,
                 potencia_fuerza_tiro, potencia_salto, potencia_resistencia, potencia_fuerza, potencia_tiros_lejanos, mentalidad_agresion,
                 mentalidad_intercepciones, mentalidad_posicionamiento, mentalidad_vision, mentalidad_penaltis, mentalidad_compostura,
                 defensa_marcaje, defensa_entrada, defensa_entrada_deslizante, portero_estirada, portero_manejo, portero_saque,
                 portero_colocacion, portero_reflejos, portero_velocidad, ls, st, rs, lw, lf, cf, rf, rw, lam, cam, ram, lm, lcm, cm, rcm,
                 rm, lwb, ldm, cdm, rdm, rwb, lb, lcb, cb, rcb, rb, gk, estrellas_talento):
        self.id_jugador = id_jugador
        self.url_jugador = url_jugador
        self.version_fifa = version_fifa
        self.actualizacion_fifa = actualizacion_fifa
        self.actualizacion_al_dia = actualizacion_al_dia
        self.nombre_corto = nombre_corto
        self.nombre_largo = nombre_largo
        self.posiciones_jugador = posiciones_jugador
        self.general = general
        self.potencial = potencial
        self.valor_eur = valor_eur
        self.salario_eur = salario_eur
        self.edad = edad
        self.fecha_nacimiento = fecha_nacimiento
        self.altura_cm = altura_cm
        self.peso_kg = peso_kg
        self.id_equipo_club = id_equipo_club
        self.nombre_club = nombre_club
        self.id_liga = id_liga
        self.nombre_liga = nombre_liga
        self.nivel_liga = nivel_liga
        self.posicion_club = posicion_club
        self.numero_camiseta_club = numero_camiseta_club
        self.cedido_desde_club = cedido_desde_club
        self.fecha_ingreso_club = fecha_ingreso_club
        self.contrato_valido_hasta = contrato_valido_hasta
        self.id_nacionalidad = id_nacionalidad
        self.nombre_nacionalidad = nombre_nacionalidad
        self.id_equipo_nacional = id_equipo_nacional
        self.posicion_nacion = posicion_nacion
        self.numero_camiseta_nacion = numero_camiseta_nacion
        self.pie_preferido = pie_preferido
        self.pie_debil = pie_debil
        self.movimientos_habilidad = movimientos_habilidad
        self.reputacion_internacional = reputacion_internacional
        self.tasa_trabajo = tasa_trabajo
        self.tipo_cuerpo = tipo_cuerpo
        self.cara_real = cara_real
        self.clausula_rescision_eur = clausula_rescision_eur
        self.etiquetas_jugador = etiquetas_jugador
        self.rasgos_jugador = rasgos_jugador
        self.ritmo = ritmo
        self.tiro = tiro
        self.pase = pase
        self.regate = regate
        self.defensa = defensa
        self.fisico = fisico
        self.ataque_centros = ataque_centros
        self.ataque_definicion = ataque_definicion
        self.ataque_precision_cabeza = ataque_precision_cabeza
        self.ataque_pase_corto = ataque_pase_corto
        self.ataque_voleas = ataque_voleas
        self.habilidad_regate = habilidad_regate
        self.habilidad_efecto = habilidad_efecto
        self.habilidad_precision_tiro_libre = habilidad_precision_tiro_libre
        self.habilidad_pase_largo = habilidad_pase_largo
        self.habilidad_control_balon = habilidad_control_balon
        self.movimiento_aceleracion = movimiento_aceleracion
        self.movimiento_velocidad_sprint = movimiento_velocidad_sprint
        self.movimiento_agilidad = movimiento_agilidad
        self.movimiento_reacciones = movimiento_reacciones
        self.movimiento_equilibrio = movimiento_equilibrio
        self.potencia_fuerza_tiro = potencia_fuerza_tiro
        self.potencia_salto = potencia_salto
        self.potencia_resistencia = potencia_resistencia
        self.potencia_fuerza = potencia_fuerza
        self.potencia_tiros_lejanos = potencia_tiros_lejanos
        self.mentalidad_agresion = mentalidad_agresion
        self.mentalidad_intercepciones = mentalidad_intercepciones
        self.mentalidad_posicionamiento = mentalidad_posicionamiento
        self.mentalidad_vision = mentalidad_vision
        self.mentalidad_penaltis = mentalidad_penaltis
        self.mentalidad_compostura = mentalidad_compostura
        self.defensa_marcaje = defensa_marcaje
        self.defensa_entrada = defensa_entrada
        self.defensa_entrada_deslizante = defensa_entrada_deslizante
        self.portero_estirada = portero_estirada
        self.portero_manejo = portero_manejo
        self.portero_saque = portero_saque
        self.portero_colocacion = portero_colocacion
        self.portero_reflejos = portero_reflejos
        self.portero_velocidad = portero_velocidad
        self.ls = ls
        self.st = st
        self.rs = rs
        self.lw = lw
        self.lf = lf
        self.cf = cf
        self.rf = rf
        self.rw = rw
        self.lam = lam
        self.cam = cam
        self.ram = ram
        self.lm = lm
        self.lcm = lcm
        self.cm = cm
        self.rcm = rcm
        self.rm = rm
        self.lwb = lwb
        self.ldm = ldm
        self.cdm = cdm
        self.rdm = rdm
        self.rwb = rwb
        self.lb = lb
        self.lcb = lcb
        self.cb = cb
        self.rcb = rcb
        self.rb = rb
        self.gk = gk
        self.estrellas_talento = estrellas_talento
        self.lesion = None
        self.partidos_jugados_temporada_pasada = 0
        self.confianza_entrenador = True
        self.retirado = False

    def ajustar_atributo(self, atributo, valor):
        """Ajustar un atributo específico del jugador"""
        if hasattr(self, atributo):
            setattr(self, atributo, valor)
        else:
            raise AttributeError(f"El objeto Jugador no tiene el atributo '{atributo}'")

    def obtener_estrellas_talento(self):
        """Visualizar el talento en forma de estrellas"""
        estrellas_completas = int(self.estrellas_talento)
        media_estrella = 0 if self.estrellas_talento == estrellas_completas else 1
        estrellas_vacias = 5 - estrellas_completas - media_estrella
        return "★" * estrellas_completas + "☆" * estrellas_vacias + ("½" if media_estrella else "")

    def actualizar_habilidad(self, habilidad, valor):
        """Actualizar una habilidad específica del jugador"""
        if hasattr(self, habilidad):
            setattr(self, habilidad, valor)
        else:
            raise AttributeError(f"El objeto Jugador no tiene la habilidad '{habilidad}'")

    def cambiar_moral(self, cantidad):
        """Cambiar la moral del jugador"""
        self.moral = max(0, min(100, self.moral + cantidad))

    def cambiar_condicion_fisica(self, cantidad):
        """Cambiar el estado físico del jugador"""
        self.condicion_fisica = max(0, min(100, self.condicion_fisica + cantidad))

    def sufrir_lesion(self, lesion):
        """Asignar una lesión al jugador"""
        self.lesion = lesion
        self.cambiar_moral(-20)  # Reducir la moral debido a la lesión

    def recuperar_de_lesion(self):
        """Recuperar al jugador de la lesión"""
        if self.lesion:
            self.lesion.duracion -= 1
            if self.lesion.duracion <= 0:
                self.lesion = None
                self.cambiar_moral(10)  # Aumentar la moral tras la recuperación

    def considerar_retiro(self):
        """Evaluar si el jugador debe retirarse"""
        from proyecto_pcfutbol.manager.src.core.retirada import should_retire
        self.retirado = should_retire(self)

class JugadorJuvenil(Jugador):
    def __init__(self, nombre, edad, posicion, habilidades, potencial, moral=100, condicion_fisica=100):
        super().__init__(nombre, edad, posicion, habilidades, moral, condicion_fisica)
        self.potencial = potencial  # Potencial de desarrollo del jugador joven

    def desarrollar(self):
        """Desarrollar las habilidades del jugador joven"""
        for habilidad in self.habilidades:
            if self.habilidades[habilidad] < self.potencial:
                self.habilidades[habilidad] += 1  # Mejorar la habilidad
