# ANÁLISIS Y OPTIMIZACIÓN DEL RANKING MVP — PC FUTSAL

**Fecha:** 2025-11-25  
**Problema:** El ranking MVP global tarda mucho en cargar  
**Solución propuesta:** Almacenar puntos por jornada en el jugador

---

## 🔍 ANÁLISIS ACTUAL

### Cómo funciona actualmente

#### Frontend (`MVPGlobalPageClient.tsx`)
1. **Dos llamadas al endpoint:**
   - **Llamada 1 (semanal):** `/api/valoraciones/mvp-global/?from=...&to=...&temporada_id=4`
     - Obtiene puntos de la semana seleccionada
   - **Llamada 2 (global):** `/api/valoraciones/mvp-global/?temporada_id=4`
     - Obtiene puntos totales acumulados (sin filtro de fechas)

2. **Problema:** Ambas llamadas son lentas porque el backend recalcula todo cada vez.

#### Backend (`MVPGlobalView._compute_ranking_for_range`)

**Flujo actual (INE ficiente):**

1. Recibe rango de fechas (`start_dt`, `end_dt`)
2. Obtiene todos los grupos de la temporada
3. Para cada grupo:
   - Obtiene TODOS los partidos en ese rango
   - Para cada partido:
     - Carga alineaciones
     - Carga eventos
     - **Recalcula puntos de cada jugador desde cero:**
       - Puntos presencia (titular/suplente)
       - Puntos eventos (goles, tarjetas, MVP)
       - Bonos (resultado, rival fuerte, duelo fuertes, intensidad)
       - Penalizaciones porteros (goles encajados)
       - Extras porteros (goles marcados)
   - Multiplica por coeficiente de división
   - Acumula en diccionario `ranking_jornada`
4. Agrupa por jugador y suma puntos
5. Devuelve ranking ordenado

**⚠️ PROBLEMA PRINCIPAL:**
- Cada vez que se carga el ranking, **recalcula TODOS los puntos recorriendo TODOS los partidos**
- Si hay 50 grupos × 20 partidos/grupo = 1000 partidos, recorre los 1000
- Para cada partido, calcula puntos de ~14 jugadores
- Esto es **O(n×m×p)** donde n=grupos, m=partidos, p=jugadores

---

## 💡 SOLUCIÓN PROPUESTA

### Almacenar puntos por jornada en el jugador

**Idea:** Una vez que termina una jornada, los puntos ya no cambian. Podemos almacenarlos.

### Arquitectura propuesta

#### 1. Nuevo modelo: `PuntosMVPJornada`

```python
class PuntosMVPJornada(models.Model):
    """
    Almacena los puntos MVP de un jugador en una jornada específica.
    Se crea/actualiza cuando termina la jornada.
    """
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    jornada = models.IntegerField()  # Número de jornada
    
    # Puntos calculados (sin coeficiente división)
    puntos_base = models.FloatField(default=0.0)
    
    # Puntos con coeficiente división aplicado
    puntos_con_coef = models.FloatField(default=0.0)
    
    # Coeficiente de división usado
    coef_division = models.FloatField(default=1.0)
    
    # Metadatos
    partidos_jugados = models.IntegerField(default=0)  # En esa jornada
    goles = models.IntegerField(default=0)  # En esa jornada
    
    # Fecha de cálculo (última vez que se actualizaron)
    fecha_calculo = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("jugador", "temporada", "grupo", "jornada")
        indexes = [
            models.Index(fields=["jugador", "temporada"]),
            models.Index(fields=["temporada", "jornada"]),
        ]
```

#### 2. Proceso de cálculo y almacenamiento

**Trigger:** Cuando termina una jornada (todos los partidos jugados)

**Management command o signal:**

```python
# backend/valoraciones/management/commands/calcular_puntos_jornada.py
def calcular_y_guardar_puntos_jornada(temporada_id, grupo_id, jornada):
    """
    Calcula los puntos MVP de todos los jugadores de una jornada
    y los almacena en PuntosMVPJornada.
    """
    # Obtener partidos de la jornada
    partidos = Partido.objects.filter(
        grupo_id=grupo_id,
        jornada=jornada,
        jugado=True
    )
    
    # Calcular puntos usando la misma lógica que MVPGlobalView
    puntos_por_jugador = calcular_puntos_jornada(partidos)
    
    # Guardar en base de datos
    for jugador_id, puntos_data in puntos_por_jugador.items():
        PuntosMVPJornada.objects.update_or_create(
            jugador_id=jugador_id,
            temporada_id=temporada_id,
            grupo_id=grupo_id,
            jornada=jornada,
            defaults={
                'puntos_base': puntos_data['puntos_base'],
                'puntos_con_coef': puntos_data['puntos_con_coef'],
                'coef_division': puntos_data['coef_division'],
                'partidos_jugados': puntos_data['partidos'],
                'goles': puntos_data['goles'],
            }
        )
```

#### 3. Nuevo endpoint optimizado

**Opción A: Endpoint híbrido (recomendado)**
- Si hay puntos almacenados → usar suma de almacenados
- Si no hay almacenados → calcular en tiempo real (backward compatible)

**Opción B: Solo almacenados**
- Forzar que siempre se almacenen antes de mostrar ranking
- Más rápido pero requiere proceso previo

#### 4. Query optimizado para ranking global

```python
def obtener_ranking_global_optimizado(temporada_id, from_date=None, to_date=None):
    """
    Obtiene ranking global sumando puntos almacenados por jornada.
    MUCHO más rápido que recalcular todo.
    """
    query = PuntosMVPJornada.objects.filter(
        temporada_id=temporada_id
    )
    
    if from_date:
        # Filtrar jornadas en rango (necesitamos mapear fechas → jornadas)
        jornadas = obtener_jornadas_en_rango(grupo_id, from_date, to_date)
        query = query.filter(jornada__in=jornadas)
    
    # Agrupar por jugador y sumar
    ranking = query.values('jugador_id', 'jugador__nombre', 'jugador__foto_url') \
                   .annotate(
                       puntos_totales=Sum('puntos_con_coef'),
                       puntos_base_totales=Sum('puntos_base'),
                       partidos_totales=Sum('partidos_jugados'),
                       goles_totales=Sum('goles')
                   ) \
                   .order_by('-puntos_totales')
    
    return ranking
```

**Ventajas:**
- ✅ **Query simple:** Solo un SUM en base de datos
- ✅ **Muy rápido:** Indexes en jugador_id y temporada_id
- ✅ **Escalable:** Funciona igual si hay 10 o 1000 jornadas
- ✅ **Consistente:** Puntos no cambian una vez almacenados

---

## 📋 PLAN DE IMPLEMENTACIÓN

### Fase 1: Modelo y migración
1. ✅ Crear modelo `PuntosMVPJornada`
2. ✅ Crear migración Django
3. ✅ Añadir índices para optimizar queries

### Fase 2: Management command
1. ✅ Crear command `calcular_puntos_jornada`
2. ✅ Reutilizar lógica de cálculo de `MVPGlobalView`
3. ✅ Probar con una jornada

### Fase 3: Endpoint optimizado
1. ✅ Modificar `MVPGlobalView` para usar puntos almacenados si existen
2. ✅ Mantener backward compatibility (calcular si no hay almacenados)
3. ✅ Añadir flag `use_cached=True` para forzar uso de almacenados

### Fase 4: Proceso automático
1. ✅ Crear management command para calcular jornadas pendientes
2. ✅ Ejecutar después de cada scraping/actualización de partidos
3. ✅ O crear signal que se dispare cuando termina una jornada

### Fase 5: Migración de datos históricos (opcional)
1. ✅ Crear command para calcular y almacenar todas las jornadas pasadas
2. ✅ Ejecutar una vez para poblar datos históricos

---

## 🔧 MEJORAS ADICIONALES

### 1. Cache de ranking completo
- Almacenar ranking global completo en cache (Redis/Memcached)
- Invalidar cuando se calculen nuevos puntos
- TTL de 1 hora

### 2. Paginación en frontend
- Actualmente carga top 100 jugadores
- Implementar paginación para mejorar rendimiento

### 3. Lazy loading
- Cargar primero top 20
- Cargar resto en background

---

## 📊 ESTIMACIÓN DE MEJORA

### Antes (recalcular):
- **Tiempo estimado:** 2-5 segundos (depende de partidos)
- **Queries:** ~1000 queries (una por partido)
- **CPU:** Alto (cálculos complejos)

### Después (sumar almacenados):
- **Tiempo estimado:** 50-200ms
- **Queries:** 1 query con GROUP BY y SUM
- **CPU:** Mínimo (solo sumas)

**Mejora estimada:** 10-40x más rápido

---

## ⚠️ CONSIDERACIONES

### 1. Consistencia de datos
- ¿Qué pasa si se corrigen datos de un partido después?
- **Solución:** Recalcular jornada completa cuando se modifique partido

### 2. Jornadas no cerradas
- Algunos partidos pueden jugarse fuera de fecha
- **Solución:** Marcar jornadas como "cerradas" solo cuando todos los partidos estén jugados

### 3. Coeficientes cambiantes
- ¿Qué pasa si cambia el coeficiente de división?
- **Solución:** Almacenar coeficiente usado en el momento del cálculo

---

**Última actualización:** 2025-11-25

