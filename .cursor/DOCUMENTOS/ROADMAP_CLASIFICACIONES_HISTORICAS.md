# ROADMAP: App Clasificaciones - Histórico de Posiciones por Jornada

## Objetivo
Crear una nueva app Django `clasificaciones` que registre y almacene la posición de cada equipo en cada división/grupo por jornada, permitiendo generar gráficas de evolución histórica de la clasificación.

## Fase 1: Crear la App y Modelos

### 1.1 Crear nueva app Django
- Crear app `clasificaciones` en `backend/clasificaciones/`
- Registrar en `settings.py` en `INSTALLED_APPS`

### 1.2 Modelos a crear

#### `ClasificacionJornada`
Modelo principal para almacenar la clasificación de cada jornada:

```python
class ClasificacionJornada(models.Model):
    """
    Almacena la clasificación completa de un grupo en una jornada específica.
    Snapshot completo de la tabla en ese momento.
    """
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="clasificaciones_jornada")
    jornada = models.PositiveIntegerField()
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    
    # Metadata
    partidos_jugados_total = models.PositiveIntegerField(default=0)  # Total de partidos jugados hasta esa jornada
    equipos_participantes = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = (("grupo", "jornada"),)
        indexes = [
            models.Index(fields=["grupo", "jornada"]),
            models.Index(fields=["grupo", "-jornada"]),  # Para obtener la última jornada
        ]
        ordering = ["grupo", "jornada"]

    def __str__(self):
        return f"{self.grupo.nombre} - Jornada {self.jornada}"


class PosicionJornada(models.Model):
    """
    Almacena la posición de un equipo en una jornada específica.
    Relación 1:N con ClasificacionJornada (un equipo por jornada).
    """
    clasificacion_jornada = models.ForeignKey(
        ClasificacionJornada, 
        on_delete=models.CASCADE, 
        related_name="posiciones"
    )
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="posiciones_jornada")
    
    # Datos de la clasificación en esa jornada
    posicion = models.PositiveIntegerField()  # 1, 2, 3...
    puntos = models.IntegerField(default=0)
    partidos_jugados = models.PositiveIntegerField(default=0)
    partidos_ganados = models.PositiveIntegerField(default=0)
    partidos_empatados = models.PositiveIntegerField(default=0)
    partidos_perdidos = models.PositiveIntegerField(default=0)
    goles_favor = models.IntegerField(default=0)
    goles_contra = models.IntegerField(default=0)
    diferencia_goles = models.IntegerField(default=0)
    racha = models.CharField(max_length=10, blank=True, default="")  # Últimos 5: "VVEDV"
    
    # Para cálculos de desempate (si los necesitamos)
    enfrentamientos_directos = models.JSONField(null=True, blank=True)  # Datos de enfrentamientos directos
    
    class Meta:
        unique_together = (("clasificacion_jornada", "club"),)
        indexes = [
            models.Index(fields=["clasificacion_jornada", "posicion"]),
            models.Index(fields=["club", "clasificacion_jornada"]),
        ]
        ordering = ["clasificacion_jornada", "posicion"]

    def __str__(self):
        return f"{self.club} - {self.clasificacion_jornada} - Pos {self.posicion}"
```

### 1.3 Migraciones
- Crear migración inicial
- Aplicar migraciones

## Fase 2: Integrar Guardado Histórico en Recalcular Clasificación

### 2.1 Modificar comando existente
**Estrategia:** Modificar `estadisticas/management/commands/recalcular_clasificacion.py` para que, después de actualizar `ClubEnGrupo`, también guarde el snapshot histórico.

**Flujo actual:**
1. `scrape_semana.py` (ejecutado por cron los domingos) → llama `recalcular_clasificacion --grupo=X` para cada grupo
2. `recalcular_clasificacion` calcula y guarda en `ClubEnGrupo`
3. **NUEVO:** Además, guarda snapshot histórico en `ClasificacionJornada` y `PosicionJornada`

### 2.2 Lógica a añadir al final del comando
Después de guardar en `ClubEnGrupo` (línea ~215), añadir:

```python
# 9. Guardar snapshot histórico de la jornada actual
from clasificaciones.models import ClasificacionJornada, PosicionJornada

# Determinar la jornada actual (última jornada jugada)
partidos_jugados = Partido.objects.filter(
    grupo=grupo,
    jugado=True,
    goles_local__isnull=False,
    goles_visitante__isnull=False,
)
if partidos_jugados.exists():
    jornada_actual = partidos_jugados.aggregate(Max('jornada_numero'))['jornada_numero__max']
    
    # Crear/actualizar ClasificacionJornada
    clasif_jornada, _ = ClasificacionJornada.objects.get_or_create(
        grupo=grupo,
        jornada=jornada_actual,
        defaults={
            'partidos_jugados_total': partidos_jugados.count(),
            'equipos_participantes': len(clasificacion_lista),
        }
    )
    
    # Borrar posiciones existentes (si se recalcula, regeneramos todo)
    PosicionJornada.objects.filter(clasificacion_jornada=clasif_jornada).delete()
    
    # Guardar posiciones
    posiciones_a_crear = []
    for idx, row in enumerate(clasificacion_lista, start=1):
        posiciones_a_crear.append(
            PosicionJornada(
                clasificacion_jornada=clasif_jornada,
                club=row["club"],
                posicion=idx,
                puntos=row["puntos"],
                partidos_jugados=row["pj"],
                partidos_ganados=stats[row["club"].id]["ganados"],
                partidos_empatados=stats[row["club"].id]["empatados"],
                partidos_perdidos=stats[row["club"].id]["perdidos"],
                goles_favor=row["gf"],
                goles_contra=row["gc"],
                diferencia_goles=row["dif"],
                racha=row["racha"],
            )
        )
    
    # Bulk create para eficiencia
    PosicionJornada.objects.bulk_create(posiciones_a_crear)
```

**Ventajas:**
- Reutiliza toda la lógica de cálculo existente
- No duplica código
- Se ejecuta automáticamente cuando se recalcula la clasificación
- Mantiene sincronizado el histórico con la clasificación actual

## Fase 3: Command para Histórico Retrospectivo (Opcional)

### 3.1 Command adicional para generar histórico de jornadas pasadas

Para generar el histórico de jornadas pasadas que aún no tienen snapshot, crear un command separado:

```bash
python manage.py generar_historico_clasificaciones --grupo_id=X  # Todas las jornadas del grupo
python manage.py generar_historico_clasificaciones --temporada_id=X  # Todos los grupos de la temporada
python manage.py generar_historico_clasificaciones --retrospectivo  # Todas las temporadas
```

Este command:
- Reutilizará la lógica del comando `recalcular_clasificacion`
- Iterará sobre todas las jornadas históricas
- Solo creará snapshots que no existan (o con `--force` para regenerar)

**Útil para:**
- Generar histórico de temporadas pasadas
- Regenerar datos si hay algún problema
- Rellenar datos faltantes

## Fase 4: Actualizar Modelo ClubSeasonProgress (Opcional)

### 4.1 Opción A: Usar solo nuevos modelos
- Descartar `ClubSeasonProgress` y usar solo `ClasificacionJornada` + `PosicionJornada`

### 4.2 Opción B: Sincronizar ambos
- Mantener `ClubSeasonProgress` sincronizado con los nuevos modelos
- Crear signal o método para actualizar `ClubSeasonProgress` cuando se crea `PosicionJornada`

**Recomendación:** Usar solo los nuevos modelos y actualizar el endpoint de evolución para usar `PosicionJornada` en lugar de `ClubSeasonProgress`.

## Fase 5: Actualizar Endpoint de Evolución

### 5.1 Modificar `ClasificacionEvolucionView`
Cambiar de usar `ClubSeasonProgress` a usar `ClasificacionJornada` + `PosicionJornada`:

```python
def get(self, request, format=None):
    grupo_id = request.GET.get("grupo_id")
    
    # Obtener todas las clasificaciones del grupo
    clasificaciones = ClasificacionJornada.objects.filter(
        grupo_id=grupo_id
    ).prefetch_related("posiciones__club").order_by("jornada")
    
    # Construir estructura por equipo
    equipos_data = {}
    jornadas_unicas = []
    
    for clasif in clasificaciones:
        jornadas_unicas.append(clasif.jornada)
        for posicion in clasif.posiciones.all():
            club_id = posicion.club_id
            if club_id not in equipos_data:
                equipos_data[club_id] = {
                    "club_id": club_id,
                    "nombre": posicion.club.nombre_oficial,
                    "escudo": posicion.club.escudo_url or "",
                    "slug": posicion.club.slug,
                    "posicion_actual": posicion.posicion,
                    "evolucion": [],
                }
            
            equipos_data[club_id]["evolucion"].append({
                "jornada": clasif.jornada,
                "posicion": posicion.posicion,
                "puntos": posicion.puntos,
                "goles_favor": posicion.goles_favor,
                "goles_contra": posicion.goles_contra,
            })
    
    # ...
```

## Fase 6: Automatización

### 6.1 Automatización existente
**No es necesaria nueva automatización** porque:
- El comando `scrape_semana` ya se ejecuta automáticamente (cron los domingos)
- Este comando llama a `recalcular_clasificacion` para cada grupo
- Con la modificación del comando, el histórico se guardará automáticamente

**Flujo automatizado:**
1. Cron ejecuta `scrape_semana` los domingos
2. `scrape_semana` → `recalcular_clasificacion --grupo=X` (para cada grupo)
3. `recalcular_clasificacion` → calcula clasificación + guarda histórico
4. ✅ Datos históricos siempre actualizados

## Fase 7: Admin y Testing

### 7.1 Admin Django
- Registrar modelos en `admin.py`
- Configurar list_display, list_filter, search_fields
- Añadir acciones para recalcular

### 7.2 Tests
- Test unitarios para función de cálculo
- Test de integración para el management command
- Test de la vista API

## Checklist de Implementación

### Backend
- [x] Crear app `clasificaciones`
- [x] Registrar en `INSTALLED_APPS`
- [x] Crear modelos `ClasificacionJornada` y `PosicionJornada`
- [x] Crear y aplicar migraciones
- [x] Modificar `estadisticas/management/commands/recalcular_clasificacion.py` para guardar histórico
- [x] Actualizar endpoint `ClasificacionEvolucionView` en `clubes/views.py` para usar nuevos modelos
- [x] Registrar modelos en admin
- [ ] Crear tests básicos (Pendiente)

### Command retrospectivo
- [x] Crear command `generar_historico_clasificaciones` para generar histórico de jornadas pasadas

### Frontend
- [x] Crear hook `useClasificacionEvolucion`
- [x] Crear componente `ClasificacionEvolucionChart`
- [x] Integrar componente en `ClasificacionShell`
- [x] Añadir traducciones
- [x] Implementar escudos como marcadores en la gráfica
- [x] Ajustar tamaño y márgenes de la gráfica

### Testing
- [x] Ejecutar `recalcular_clasificacion` en grupo de prueba y verificar que guarda histórico
- [x] Verificar que se generan correctamente las posiciones
- [x] Verificar que el endpoint funciona con nuevos datos
- [x] Verificar que la gráfica se muestra correctamente
- [x] Generar histórico retrospectivo para Grupo 1 (11 jornadas)

---

## ✅ Estado de Implementación

**Fecha de finalización:** 30 de noviembre de 2025

**Estado:** ✅ COMPLETADO

Toda la funcionalidad ha sido implementada exitosamente. Ver documentación detallada en `IMPLEMENTACION_CLASIFICACIONES_HISTORICAS.md`.

## Notas Técnicas

### Criterios de Clasificación
La clasificación sigue estos criterios (en orden):
1. **Puntos** (descendente): 3 por victoria, 1 por empate
2. **Diferencia de goles** (descendente): GF - GC
3. **Goles a favor** (descendente): Total de goles marcados
4. **Nombre del club** (ascendente): Para estabilidad/consistencia

**Nota:** No se implementan enfrentamientos directos por ahora, pero el campo `enfrentamientos_directos` está disponible en el modelo para futuras mejoras.

### Racha (Forma)
- Se calcula con los últimos 5 partidos
- Formato: "VVEDV" (Victoria, Victoria, Empate, Derrota, Victoria)
- Se ordena cronológicamente por jornada y fecha_hora

### Rendimiento
- Usar `select_related` y `prefetch_related` para optimizar queries
- Indexar campos críticos (grupo, jornada, posicion)
- Considerar usar `bulk_create` para insertar múltiples posiciones

## Próximos Pasos Después de Implementación

1. **Generar histórico retrospectivo**: Ejecutar command en modo retrospectivo para todos los grupos
2. **Verificar gráficas**: Comprobar que las gráficas se muestran correctamente
3. **Verificar automatización**: El histórico se generará automáticamente con cada `scrape_semana`
4. **Mejoras futuras**: Añadir lógica de enfrentamientos directos si es necesario

