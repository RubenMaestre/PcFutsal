# scraping/core/config_temporadas.py
#
# Configuración de temporadas y competiciones de FFCV para el scraping.
# Los IDs (id_temp, id_competicion, id_torneo) son específicos de la plataforma
# de FFCV y cambian cada temporada. Se obtienen inspeccionando las URLs de FFCV.
#
# Estructura:
# - id_temp: ID de temporada en FFCV (cambia cada año)
# - id_competicion: ID de la competición (ej: Tercera División)
# - id_torneo: ID del grupo/torneo específico (ej: Grupo XV, Grupo XIV)
# - jornadas: Número total de jornadas de la temporada

TEMPORADAS = {
    "2022-2023": {
        # IDs base de temporada
        "id_temp": 18,
        "id_modalidad": 33332,
        "jornadas": 30,

        # (compat) valores por defecto si NO se usa 'grupos'
        "id_competicion": 900104391,   # Tercera División (FFCV)
        "id_torneo": 44051,            # ← XV según tu config original

        # Tercera División: grupos XIV y XV
        "grupos": {
            "XV": {
                "grupo_nombre": "Grupo XV",
                "provincia": "Alicante",
                "id_competicion": 900104391,
                "id_torneo": 44051,
                "jornadas": 30,
            },
            "XIV": {
                "grupo_nombre": "Grupo XIV",
                "provincia": "Valencia",
                "id_competicion": 900104391,
                "id_torneo": 44049,   # enlace que has pasado para XIV
                "jornadas": 30,
            },
        },
    },

    "2023-2024": {
        "id_temp": 19,
        "id_modalidad": 33332,
        "jornadas": 30,

        "id_competicion": 900438374,   # Tercera
        "id_torneo": 900438376,        # XV (tu config original)

        "grupos": {
            "XV": {
                "grupo_nombre": "Grupo XV",
                "provincia": "Alicante",
                "id_competicion": 900438374,
                "id_torneo": 900438376,   # XV
                "jornadas": 30,
            },
            "XIV": {
                "grupo_nombre": "Grupo XIV",
                "provincia": "Valencia",
                "id_competicion": 900438374,
                "id_torneo": 900438375,   # XIV (tu enlace)
                "jornadas": 30,
            },
        },
    },

    "2024-2025": {
        "id_temp": 20,
        "id_modalidad": 33332,
        "jornadas": 30,

        "id_competicion": 903498670,   # Tercera
        "id_torneo": 903498672,        # XV (tu config original)

        "grupos": {
            "XV": {
                "grupo_nombre": "Grupo XV",
                "provincia": "Alicante",
                "id_competicion": 903498670,
                "id_torneo": 903498672,   # XV
                "jornadas": 30,
            },
            "XIV": {
                "grupo_nombre": "Grupo XIV",
                "provincia": "Valencia",
                "id_competicion": 903498670,
                "id_torneo": 903498671,   # XIV (tu enlace)
                "jornadas": 30,
            },
        },
    },

    "2025-2026": {
    "id_temp": 21,
    "id_modalidad": 33332,
    "jornadas": 30,

    "id_competicion": 29509429,   # Tercera
    "id_torneo": 29509432,        # XV (OK)

    "grupos": {
        "XV": {
            "grupo_nombre": "Grupo XV",
            "provincia": "Alicante",
            "id_competicion": 29509429,
            "id_torneo": 29509432,  # XV
            "jornadas": 30,
        },
        "XIV": {
            "grupo_nombre": "Grupo XIV",
            "provincia": "Valencia",
            # 👇 ESTE es el que debes poner bien (el del XIV 2025/26)
            "id_competicion": 29509429,
            "id_torneo": 29509431,  # <-- EJEMPLO: pon aquí el ID REAL del XIV
            "jornadas": 30,
        },
    },

        # Solo 2025/26: Preferente, Primera Regional y Segunda Regional (Regional 2)
        "otras_competiciones": {
            "Preferente": {
                "id_competicion": 29509245,
                "grupos": {
                    "G1": {
                        "grupo_nombre": "Preferente - Grupo 1",
                        "id_torneo": 29509250,
                        "jornadas": 26,  # 14 equipos
                    },
                    "G2": {
                        "grupo_nombre": "Preferente - Grupo 2",
                        "id_torneo": 29509251,
                        "jornadas": 26,
                    },
                    "G3": {
                        "grupo_nombre": "Preferente - Grupo 3",
                        "id_torneo": 29509252,
                        "jornadas": 26,
                    },
                },
            },

            "Primera Regional": {
                "id_competicion": 29509253,
                "grupos": {
                    "G1": {
                        "grupo_nombre": "1ª Regional - Grupo 1",
                        "id_torneo": 29509254,
                        "jornadas": 26,  # 14 equipos
                    },
                    "G2": {
                        "grupo_nombre": "1ª Regional - Grupo 2",
                        "id_torneo": 29509255,
                        "jornadas": 26,  # 13 equipos + Descansa → 26 jornadas
                    },
                    "G3": {
                        "grupo_nombre": "1ª Regional - Grupo 3",
                        "id_torneo": 29509256,
                        "jornadas": 30,  # hay retirado; mantenemos 30 como indicas
                    },
                    "G4": {
                        "grupo_nombre": "1ª Regional - Grupo 4",
                        "id_torneo": 29509257,
                        "jornadas": 26,  # hay retirado; 26 jornadas
                    },
                },
            },

            "Segunda Regional": {  # “Regional 2”
                "id_competicion": 29509258,
                "grupos": {
                    "G1": {
                        "grupo_nombre": "2ª Regional - Grupo 1",
                        "id_torneo": 29509260,
                        "jornadas": 34,
                    },
                    "G2": {
                        "grupo_nombre": "2ª Regional - Grupo 2",
                        "id_torneo": 29509261,
                        "jornadas": 34,
                    },
                    "G3": {
                        "grupo_nombre": "2ª Regional - Grupo 3",
                        "id_torneo": 29509262,
                        "jornadas": 30,
                    },
                    "G4": {
                        "grupo_nombre": "2ª Regional - Grupo 4",
                        "id_torneo": 29509259,
                        "jornadas": 30,
                    },
                },
            },
        },
    },
}
