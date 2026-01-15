# ROADMAP: Sistema de MVP y Reconocimientos Fantasy

**Fecha de Creación del Roadmap:** 2025-11-29  
**Objetivo:** Implementar sistema de almacenamiento de MVP del partido, MVP de jornada, goleador de jornada y mejor equipo de jornada, tanto por división como global.

**IMPORTANTE:** 
- La fecha **29 de noviembre de 2025** es únicamente la fecha de registro de creación de este roadmap.
- El cálculo retrospectivo debe realizarse desde la **jornada 1** y **semana 1** de la temporada actual, no desde una fecha específica.
- Los reconocimientos se calcularán y almacenarán desde el inicio de la temporada, y luego se calcularán automáticamente semana a semana los domingos con el cron.
- Los **MVP de cada partido** se calcularán seleccionando al jugador con más puntos en ese partido.
- **Criterios de desempate para MVP del partido** (en caso de empate a puntos):
  1. Jugador del equipo que ganó el partido
  2. Jugador que marcó más goles
  3. Jugador que recibió menos tarjetas
  4. Si aún hay empate, el jugador con más puntos MVP acumulados en la temporada

---

## 1. ANÁLISIS DE LO EXISTENTE

### 1.1 Endpoints de Valoraciones Disponibles

#### Jugadores
- **`JugadoresJornadaView`** (`/api/valoraciones/jugadores-jornada/`)
  - Calcula puntos de jugadores por jornada y grupo
  - Devuelve `jugador_de_la_jornada` (MVP de la jornada por división)
  - Devuelve `ranking_jugadores` con puntos calculados
  - Usa coeficientes de club y división

- **`JugadoresJornadaGlobalView`** (`/api/valoraciones/jugadores-jornada-global/`)
  - Calcula puntos globales de jugadores (todas las divisiones)
  - Devuelve `jugador_de_la_jornada` (MVP global)
  - Usa coeficientes de división para ponderar

- **`MVPGlobalView`** (`/api/valoraciones/mvp-global/`)
  - Ranking global de MVP por temporada
  - Soporta filtros por semana, rango de fechas, etc.

#### Equipos
- **`EquipoJornadaView`** (`/api/valoraciones/equipo-jornada/`)
  - Calcula puntos de equipos por jornada y grupo
  - Devuelve `equipo_de_la_jornada` (mejor equipo de la jornada por división)
  - Devuelve `ranking_clubes` con puntos calculados

- **`EquipoJornadaGlobalView`** (`/api/valoraciones/equipo-jornada-global/`)
  - Calcula puntos globales de equipos (todas las divisiones)
  - Devuelve `equipo_de_la_jornada` (mejor equipo global)

#### Goleadores
- **`GoleadoresJornadaView`** (`/api/estadisticas/goleadores-jornada/`)
  - Devuelve goleadores de una jornada por grupo
  - Incluye `goleador_de_la_jornada` (goleador de la jornada por división)

### 1.2 Modelos Fantasy Existentes

- **`PuntosMVPJornada`**: Almacena puntos MVP por jornada (ya existe)
- **`PuntosMVPTotalJugador`**: Almacena total acumulado de puntos MVP (ya existe)
- **`PuntosEquipoJornada`**: Almacena puntos de equipos por jornada (ya existe)
- **`PuntosEquipoTotal`**: Almacena total acumulado de puntos de equipos (ya existe)

### 1.3 Coeficientes Disponibles

- **`CoeficienteClub`**: Coeficientes por club
- **`CoeficienteDivision`**: Coeficientes por división

---

## 2. MODELOS NUEVOS A CREAR

### 2.1 MVP del Partido

```python
class MVPPartido(models.Model):
    """
    Almacena el MVP de cada partido.
    Se calcula seleccionando al jugador con más puntos en ese partido.
    
    Criterios de desempate (en caso de empate a puntos):
    1. Jugador del equipo que ganó el partido
    2. Jugador que marcó más goles
    3. Jugador que recibió menos tarjetas
    4. Jugador con más puntos MVP acumulados en la temporada
    """
    partido = models.OneToOneField(
        "partidos.Partido",
        on_delete=models.CASCADE,
        related_name="mvp_partido"
    )
    
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="mvp_partidos"
    )
    
    puntos = models.FloatField()  # Puntos obtenidos en ese partido
    
    # Metadatos
    goles = models.IntegerField(default=0)
    tarjetas_amarillas = models.IntegerField(default=0)
    tarjetas_rojas = models.IntegerField(default=0)
    mvp_evento = models.BooleanField(default=False)  # Si tuvo evento MVP
    
    # Para desempate
    equipo_ganador = models.BooleanField(default=False)  # Si su equipo ganó el partido
    puntos_mvp_acumulados = models.FloatField(default=0)  # Puntos MVP acumulados en temporada (al momento del cálculo)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["jugador", "-fecha_creacion"]),
            models.Index(fields=["partido"]),
        ]
```

### 2.2 MVP de la Jornada (por División)

```python
class MVPJornadaDivision(models.Model):
    """
    Almacena el MVP de la jornada por división/grupo.
    Se calcula los domingos por la noche cuando terminan todos los partidos.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_division"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas"
    )
    
    jornada = models.IntegerField()
    
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_division"
    )
    
    puntos = models.FloatField()  # Puntos totales en esa jornada
    puntos_con_coef = models.FloatField()  # Puntos con coeficiente división
    
    coef_division = models.FloatField()  # Coeficiente usado
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    goles = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "grupo", "jornada")
        indexes = [
            models.Index(fields=["jugador", "-fecha_creacion"]),
            models.Index(fields=["temporada", "grupo", "jornada"]),
        ]
```

### 2.3 MVP Global de la Semana (PC FUTSAL)

```python
class MVPJornadaGlobal(models.Model):
    """
    Almacena el MVP global de la semana (todas las divisiones).
    Se calcula los domingos por la noche.
    
    IMPORTANTE: Los reconocimientos globales se calculan por SEMANAS
    (Miércoles 19:00 - Domingo 21:00), NO por jornadas numéricas.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_global"
    )
    
    # Semana: fecha del martes de esa semana (formato YYYY-MM-DD)
    # Ejemplo: Si la semana es Mi 15/01 - Do 19/01, semana = "2025-01-21" (martes)
    semana = models.DateField()  # Fecha del martes de la semana
    
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_global"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="mvp_jornadas_globales"
    )
    
    puntos = models.FloatField()  # Puntos totales con coeficiente división aplicado
    puntos_base = models.FloatField()  # Puntos sin coeficiente
    coef_division = models.FloatField()  # Coeficiente de división usado
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    goles = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "semana")
        indexes = [
            models.Index(fields=["jugador", "-fecha_creacion"]),
            models.Index(fields=["temporada", "semana"]),
        ]
```

### 2.4 Goleador de la Jornada (por División)

```python
class GoleadorJornadaDivision(models.Model):
    """
    Almacena el goleador de la jornada por división/grupo.
    Se calcula los domingos por la noche.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="goleadores_jornadas_division"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="goleadores_jornadas"
    )
    
    jornada = models.IntegerField()
    
    jugador = models.ForeignKey(
        "jugadores.Jugador",
        on_delete=models.CASCADE,
        related_name="goleador_jornadas_division"
    )
    
    goles = models.IntegerField()  # Goles en esa jornada
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "grupo", "jornada")
        indexes = [
            models.Index(fields=["jugador", "-fecha_creacion"]),
            models.Index(fields=["temporada", "grupo", "jornada"]),
        ]
```

### 2.5 Mejor Equipo de la Jornada (por División)

```python
class MejorEquipoJornadaDivision(models.Model):
    """
    Almacena el mejor equipo de la jornada por división/grupo.
    Se calcula los domingos por la noche.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="mejores_equipos_jornadas_division"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="mejores_equipos_jornadas"
    )
    
    jornada = models.IntegerField()
    
    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="mejor_equipo_jornadas_division"
    )
    
    puntos = models.FloatField()  # Puntos totales en esa jornada
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    victorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    goles_favor = models.IntegerField(default=0)
    goles_contra = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "grupo", "jornada")
        indexes = [
            models.Index(fields=["club", "-fecha_creacion"]),
            models.Index(fields=["temporada", "grupo", "jornada"]),
        ]
```

### 2.6 Mejor Equipo Global de la Semana (PC FUTSAL)

```python
class MejorEquipoJornadaGlobal(models.Model):
    """
    Almacena el mejor equipo global de la semana (todas las divisiones).
    Se calcula los domingos por la noche.
    
    IMPORTANTE: Los reconocimientos globales se calculan por SEMANAS
    (Miércoles 19:00 - Domingo 21:00), NO por jornadas numéricas.
    """
    temporada = models.ForeignKey(
        "nucleo.Temporada",
        on_delete=models.CASCADE,
        related_name="mejores_equipos_jornadas_global"
    )
    
    # Semana: fecha del martes de esa semana (formato YYYY-MM-DD)
    # Ejemplo: Si la semana es Mi 15/01 - Do 19/01, semana = "2025-01-21" (martes)
    semana = models.DateField()  # Fecha del martes de la semana
    
    club = models.ForeignKey(
        "clubes.Club",
        on_delete=models.CASCADE,
        related_name="mejor_equipo_jornadas_global"
    )
    
    grupo = models.ForeignKey(
        "nucleo.Grupo",
        on_delete=models.CASCADE,
        related_name="mejores_equipos_jornadas_globales"
    )
    
    puntos = models.FloatField()  # Puntos totales con coeficiente división aplicado
    puntos_base = models.FloatField()  # Puntos sin coeficiente
    coef_division = models.FloatField()  # Coeficiente de división usado
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)
    victorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    goles_favor = models.IntegerField(default=0)
    goles_contra = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("temporada", "semana")
        indexes = [
            models.Index(fields=["club", "-fecha_creacion"]),
            models.Index(fields=["temporada", "semana"]),
        ]
```

---

## 3. MANAGEMENT COMMAND: Calcular Reconocimientos de Jornada

### 3.1 Comando: `calcular_reconocimientos_jornada`

**Ubicación:** `backend/fantasy/management/commands/calcular_reconocimientos_jornada.py`

**Funcionalidad:**
- Se ejecuta los domingos por la noche (cron job)
- Calcula y almacena todos los reconocimientos de la jornada/semana que acaba de terminar
- Procesa todos los grupos/divisiones
- Calcula reconocimientos por división (por jornada) y globales (por semana)

**Parámetros:**
- `--temporada_id`: ID de la temporada (opcional, usa la actual por defecto)
- `--grupo_id`: ID del grupo específico (opcional, procesa todos si no se especifica)
- `--jornada`: Número de jornada (opcional, usa la última jornada jugada por defecto)
- `--semana`: Fecha del martes de la semana (formato YYYY-MM-DD) para cálculos globales
- `--retrospectivo`: Calcular todas las jornadas/semanas desde la jornada 1 y semana 1 de la temporada actual
- `--force`: Forzar recálculo aunque ya exista

**Flujo para reconocimientos por DIVISIÓN (por jornada):**
1. Identificar la última jornada jugada (o usar la especificada)
2. Para cada grupo:
   - Calcular MVP del partido para cada partido de la jornada (usando criterios de desempate)
   - Calcular MVP de la jornada (usando `JugadoresJornadaView`)
   - Calcular goleador de la jornada (usando `GoleadoresJornadaView`)
   - Calcular mejor equipo de la jornada (usando `EquipoJornadaView`)

**Flujo para reconocimientos GLOBALES (por semana):**
1. Identificar la última semana con partidos (Miércoles 19:00 - Domingo 21:00)
2. Para cada semana:
   - Calcular MVP global de la semana (usando `JugadoresJornadaGlobalView` con filtro de semana)
   - Calcular mejor equipo global de la semana (usando `EquipoJornadaGlobalView` con filtro de semana)
   - **Aplicar coeficiente de división** a los puntos antes de determinar el ganador

**Modo Retrospectivo:**
- Si se usa `--retrospectivo`, el comando:
  1. Identifica todas las jornadas jugadas desde la **jornada 1** de la temporada actual
  2. Identifica todas las semanas con partidos desde la **semana 1** de la temporada actual
  3. Procesa cada jornada/semana en orden cronológico
  4. Almacena todos los reconocimientos históricos

**Cálculo de MVP del Partido:**
1. Para cada partido jugado (`jugado=True`):
   - Obtener todos los jugadores que participaron en el partido
   - Calcular puntos de cada jugador en ese partido
   - Seleccionar al jugador con más puntos
   - **En caso de empate a puntos**, aplicar criterios de desempate:
     1. Jugador del equipo que ganó el partido
     2. Jugador que marcó más goles
     3. Jugador que recibió menos tarjetas (amarillas + rojas)
     4. Jugador con más puntos MVP acumulados en la temporada (consultar `PuntosMVPTotalJugador`)
   - Almacenar el MVP del partido en `MVPPartido`

---

## 4. ENDPOINTS NUEVOS EN FANTASY

### 4.1 Obtener Reconocimientos de un Jugador

**Endpoint:** `GET /api/fantasy/jugador/{jugador_id}/reconocimientos/`

**Respuesta:**
```json
{
  "jugador": {
    "id": 123,
    "nombre": "Juan Pérez",
    "slug": "juan-perez"
  },
  "mvp_partidos": 15,  // Número de veces MVP del partido
  "mvp_jornadas_division": 3,  // Número de veces MVP de jornada por división
  "mvp_jornadas_global": 1,  // Número de veces MVP global
  "goleador_jornadas_division": 5,  // Número de veces goleador de jornada
  "detalle": {
    "mvp_partidos": [
      {
        "partido_id": 456,
        "fecha": "2025-01-15",
        "puntos": 12.5,
        "local": "Equipo A",
        "visitante": "Equipo B"
      }
    ],
    "mvp_jornadas_division": [
      {
        "temporada": "2024-25",
        "grupo": "Primera División - Grupo I",
        "jornada": 7,
        "fecha": "2025-01-15",
        "puntos": 45.2
      }
    ],
    "mvp_jornadas_global": [
      {
        "temporada": "2024-25",
        "semana": "2025-01-21",  // Fecha del martes de esa semana
        "fecha_inicio": "2025-01-15",  // Miércoles
        "fecha_fin": "2025-01-19",  // Domingo
        "puntos": 45.2,
        "puntos_base": 40.0,
        "coef_division": 1.13,
        "grupo": "Primera División - Grupo I"
      }
    ],
    "goleador_jornadas_division": [
      {
        "temporada": "2024-25",
        "grupo": "Primera División - Grupo I",
        "jornada": 7,
        "fecha": "2025-01-15",
        "goles": 5
      }
    ]
  }
}
```

### 4.2 Obtener Reconocimientos de un Equipo

**Endpoint:** `GET /api/fantasy/equipo/{club_id}/reconocimientos/`

**Respuesta:**
```json
{
  "club": {
    "id": 45,
    "nombre": "Equipo A",
    "slug": "equipo-a"
  },
  "mejor_equipo_jornadas_division": 8,  // Número de veces mejor equipo de jornada por división
  "mejor_equipo_jornadas_global": 2,  // Número de veces mejor equipo global
  "detalle": {
    "mejor_equipo_jornadas_division": [
      {
        "temporada": "2024-25",
        "grupo": "Primera División - Grupo I",
        "jornada": 7,
        "fecha": "2025-01-15",
        "puntos": 12.5
      }
    ],
    "mejor_equipo_jornadas_global": [
      {
        "temporada": "2024-25",
        "semana": "2025-01-21",  // Fecha del martes de esa semana
        "fecha_inicio": "2025-01-15",  // Miércoles
        "fecha_fin": "2025-01-19",  // Domingo
        "puntos": 12.5,
        "puntos_base": 11.0,
        "coef_division": 1.13,
        "grupo": "Primera División - Grupo I"
      }
    ]
  }
}
```

### 4.3 Obtener MVP del Partido

**Endpoint:** `GET /api/fantasy/partido/{partido_id}/mvp/`

**Respuesta:**
```json
{
  "partido": {
    "id": 456,
    "local": "Equipo A",
    "visitante": "Equipo B",
    "fecha": "2025-01-15"
  },
  "mvp": {
    "jugador": {
      "id": 123,
      "nombre": "Juan Pérez",
      "slug": "juan-perez",
      "foto": "/media/fotos/juan-perez.jpg"
    },
    "puntos": 12.5,
    "goles": 2,
    "tarjetas_amarillas": 0,
    "tarjetas_rojas": 0,
    "mvp_evento": true,
    "equipo_ganador": true
  }
}
```

---

## 5. INTEGRACIÓN EN FRONTEND

### 5.1 Hook: `useJugadorReconocimientos`

**Ubicación:** `frontend/hooks/useJugadorReconocimientos.ts`

**Funcionalidad:**
- Obtiene todos los reconocimientos de un jugador
- Devuelve contadores y detalles

### 5.2 Hook: `useEquipoReconocimientos`

**Ubicación:** `frontend/hooks/useEquipoReconocimientos.ts`

**Funcionalidad:**
- Obtiene todos los reconocimientos de un equipo
- Devuelve contadores y detalles

### 5.3 Componente: `JugadorReconocimientosCard`

**Ubicación:** `frontend/components/JugadorReconocimientosCard.tsx`

**Funcionalidad:**
- Muestra badges/medallas con los reconocimientos
- Muestra contadores (ej: "3x MVP de Jornada")
- Opcionalmente muestra detalles expandibles

**Diseño:**
- Badges con iconos para cada tipo de reconocimiento
- Contador grande y visible
- Sección colapsable con detalles históricos

### 5.4 Componente: `EquipoReconocimientosCard`

**Ubicación:** `frontend/components/EquipoReconocimientosCard.tsx`

**Funcionalidad:**
- Similar a `JugadorReconocimientosCard` pero para equipos
- Muestra "Mejor Equipo de Jornada" y "Mejor Equipo Global"

### 5.5 Integración en Fichas

**Jugador (`JugadorDetailClient.tsx`):**
- Añadir `JugadorReconocimientosCard` después del header
- Mostrar reconocimientos destacados en el perfil

**Equipo (`ClubDetailClient.tsx`):**
- Añadir `EquipoReconocimientosCard` después del header
- Mostrar reconocimientos destacados en el perfil

---

## 6. PLAN DE IMPLEMENTACIÓN

### Fase 1: Backend - Modelos y Migraciones
1. Crear modelos en `backend/fantasy/models.py`
2. Crear migraciones: `python manage.py makemigrations fantasy`
3. Aplicar migraciones: `python manage.py migrate fantasy`
4. Registrar modelos en `admin.py`

### Fase 2: Backend - Management Command
1. Crear `calcular_reconocimientos_jornada.py`
2. Implementar cálculo de MVP del partido con criterios de desempate
3. Implementar cálculo de reconocimientos de jornada por división (usando endpoints existentes)
4. Implementar cálculo de reconocimientos globales por semana (usando endpoints existentes con filtro de semana)
5. Implementar aplicación de coeficiente de división para reconocimientos globales
6. Implementar modo retrospectivo (desde jornada 1 y semana 1)
7. Añadir validaciones y manejo de errores
8. Probar con datos reales (primero modo retrospectivo, luego modo normal)

### Fase 3: Backend - Endpoints
1. Crear `ReconocimientosJugadorView`
2. Crear `ReconocimientosEquipoView`
3. Crear `MVPPartidoView`
4. Añadir URLs en `backend/fantasy/urls.py`
5. Probar endpoints con Postman/curl

### Fase 4: Frontend - Hooks y Componentes
1. Crear `useJugadorReconocimientos.ts`
2. Crear `useEquipoReconocimientos.ts`
3. Crear `JugadorReconocimientosCard.tsx`
4. Crear `EquipoReconocimientosCard.tsx`
5. Añadir traducciones en todos los idiomas

### Fase 5: Frontend - Integración
1. Integrar `JugadorReconocimientosCard` en `JugadorDetailClient.tsx`
2. Integrar `EquipoReconocimientosCard` en `ClubDetailClient.tsx`
3. Ajustar estilos y diseño
4. Probar en diferentes dispositivos

### Fase 6: Ejecución Retrospectiva
1. Ejecutar comando en modo retrospectivo: `python manage.py calcular_reconocimientos_jornada --retrospectivo`
2. Verificar que se hayan calculado todos los reconocimientos desde la jornada 1 y semana 1
3. Revisar logs y corregir errores si los hay
4. Validar datos en base de datos

### Fase 7: Automatización
1. Configurar cron job para ejecutar el comando los domingos por la noche (después de las 21:00)
2. Añadir logging y monitoreo
3. Documentar proceso de cálculo
4. Crear script de verificación para comprobar que el cálculo se ejecutó correctamente

---

## 7. PREGUNTAS Y ACLARACIONES

### 7.1 Sobre MVP del Partido
- **Pregunta:** ¿El MVP del partido se calcula solo para partidos jugados?
- **Respuesta:** Sí, solo para partidos con `jugado=True`
- **Pregunta:** ¿Cómo se determina el MVP si hay empate a puntos?
- **Respuesta:** Se aplican los siguientes criterios de desempate en orden:
  1. Jugador del equipo que ganó el partido
  2. Jugador que marcó más goles
  3. Jugador que recibió menos tarjetas (amarillas + rojas)
  4. Jugador con más puntos MVP acumulados en la temporada

### 7.2 Sobre Jornadas vs Semanas
- **Pregunta:** ¿Las jornadas globales se refieren a semanas (Mi-Do) o a jornadas numéricas?
- **Respuesta:** 
  - **Por división:** Se calculan por JORNADA numérica (cada grupo tiene sus propias jornadas)
  - **Globales (PC FUTSAL):** Se calculan por SEMANA (Miércoles 19:00 - Domingo 21:00)
  - Los reconocimientos globales usan el coeficiente de división para ponderar los puntos

### 7.3 Sobre Goleador
- **Pregunta:** ¿El goleador de la jornada es el que más goles marcó en esa jornada, o el que más puntos tiene?
- **Respuesta:** El que más goles marcó en esa jornada (no puntos)

### 7.4 Sobre Recálculo
- **Pregunta:** ¿Qué pasa si se recalcula una jornada que ya tiene reconocimientos?
- **Respuesta:** El comando debe actualizar los reconocimientos existentes si `--force` está activado, o crear nuevos si no existen

### 7.5 Sobre Temporadas
- **Pregunta:** ¿Los reconocimientos se almacenan por temporada?
- **Respuesta:** Sí, todos los modelos incluyen `temporada` como ForeignKey

### 7.6 Sobre Cálculo Retrospectivo
- **Pregunta:** ¿Desde qué fecha se calculan los reconocimientos retrospectivos?
- **Respuesta:** Desde la **jornada 1** y **semana 1** de la temporada actual, no desde una fecha específica. El comando identifica automáticamente la primera jornada y semana con partidos jugados.

---

## 8. NOTAS TÉCNICAS

### 8.1 Uso de Endpoints Existentes
- **NO** recrear la lógica de cálculo de puntos
- **SÍ** usar los endpoints de valoraciones existentes para obtener los datos
- El management command hará peticiones internas a estos endpoints

### 8.2 Coeficientes
- Los coeficientes de división se obtienen de `CoeficienteDivision`
- Los coeficientes de club se obtienen de `CoeficienteClub`
- Se almacenan en los modelos para trazabilidad
- **IMPORTANTE:** Para reconocimientos globales (PC FUTSAL), los puntos se multiplican por el coeficiente de división antes de determinar el ganador
- El coeficiente de división se obtiene del endpoint `JugadoresJornadaGlobalView` o `EquipoJornadaGlobalView` que ya lo aplica

### 8.3 Performance
- Usar `select_related` y `prefetch_related` en las queries
- Crear índices en campos frecuentemente consultados
- Considerar cacheo de reconocimientos si es necesario

### 8.4 Validaciones
- Verificar que todos los partidos de la jornada estén jugados antes de calcular
- Manejar casos edge (empates en puntos, múltiples goleadores con mismo número de goles, etc.)
- Para reconocimientos globales, verificar que la semana tenga suficientes partidos (usar mismo umbral que `MVPGlobalView`)
- **Criterios de desempate para MVP del partido:**
  - Si hay empate a puntos, aplicar criterios en orden:
    1. Jugador del equipo ganador
    2. Jugador con más goles
    3. Jugador con menos tarjetas
    4. Jugador con más puntos MVP acumulados

### 8.5 Cálculo Retrospectivo
- **Fecha de inicio:** Jornada 1 y Semana 1 de la temporada actual
- Identificar todas las jornadas jugadas desde la jornada 1
- Identificar todas las semanas con partidos desde la semana 1
- Procesar en orden cronológico
- Manejar casos donde ya existan reconocimientos (usar `--force` para sobrescribir)

### 8.6 Cálculo de MVP del Partido
- Se calcula para cada partido jugado
- Se selecciona al jugador con más puntos en ese partido
- En caso de empate, se aplican los criterios de desempate definidos
- Se almacena en `MVPPartido` con todos los metadatos necesarios
- Los MVP de partido se calculan inmediatamente cuando el partido se marca como jugado, no esperan al domingo

---

## 9. PRÓXIMOS PASOS

1. Revisar y aprobar este roadmap
2. Comenzar con Fase 1 (Modelos y Migraciones)
3. Iterar según feedback

