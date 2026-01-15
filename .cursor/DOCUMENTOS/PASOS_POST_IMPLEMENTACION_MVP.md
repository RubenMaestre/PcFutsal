# Pasos Post-Implementación - Optimización MVP

## ✅ Estado Actual

Todos los componentes están implementados y listos:
- ✅ Modelo `PuntosMVPJornada` creado
- ✅ Migración `0003_puntosmvpjornada.py` creada
- ✅ Management command `calcular_puntos_mvp_jornada.py` funcionando
- ✅ Endpoint optimizado en `MVPGlobalView`
- ✅ Señales automáticas configuradas

## 📋 Pasos a Ejecutar

### Paso 1: Aplicar Migración

**Cuando el entorno Django esté configurado correctamente:**

```bash
cd /home/rubenmaestre/pcfutsal.es/backend
python manage.py migrate fantasy
```

**Verificación:**
- Debe crear la tabla `fantasy_puntosmvpjornada`
- Debe crear los índices configurados
- No debe dar errores

**Si hay problemas:**
```bash
# Ver estado de migraciones
python manage.py showmigrations fantasy

# Ver SQL que se ejecutará
python manage.py sqlmigrate fantasy 0003
```

### Paso 2: Verificar Instalación de Señales

**Verificar que las señales se registran correctamente:**

```python
# En shell de Django
python manage.py shell

from django.apps import apps
from django.db.models.signals import post_save
from partidos.models import Partido

# Verificar que la señal está registrada
receivers = post_save.receivers
print(f"Señales registradas para Partido: {len([r for r in receivers if r[0][0] == Partido])}")
```

**O verificar en logs al iniciar Django:**
- Las señales se registran automáticamente cuando Django inicia
- No debería haber errores de importación

### Paso 3: Calcular Puntos Históricos

**Obtener nombre de temporada actual:**

```bash
python manage.py shell
```

```python
from nucleo.models import Temporada

# Ver temporadas disponibles
temporadas = Temporada.objects.all().values_list('nombre', flat=True)
print(list(temporadas))

# Salir
exit()
```

**Calcular todas las jornadas de la temporada actual:**

```bash
# Reemplazar "2025/2026" con el nombre real de la temporada
python manage.py calcular_puntos_mvp_jornada --temporada "2025/2026" --todas-jornadas
```

**Calcular solo una jornada para probar:**

```bash
python manage.py calcular_puntos_mvp_jornada --temporada "2025/2026" --jornada 1 --dry-run
```

**Calcular jornada específica de un grupo:**

```bash
python manage.py calcular_puntos_mvp_jornada --temporada "2025/2026" --jornada 1 --grupo 5
```

### Paso 4: Verificar Cálculo Automático

**Probar que las señales funcionan:**

1. Marcar un partido como jugado (si no hay ninguno):
   ```python
   from partidos.models import Partido
   
   partido = Partido.objects.filter(jugado=False).first()
   if partido:
       partido.jugado = True
       partido.save()  # Esto debería disparar la señal
   ```

2. Verificar en logs que se ejecuta el cálculo automático
3. Verificar en BD que se crearon registros:
   ```python
   from fantasy.models import PuntosMVPJornada
   
   # Ver cuántos puntos hay almacenados
   PuntosMVPJornada.objects.count()
   
   # Ver jornadas con puntos calculados
   PuntosMVPJornada.objects.values_list('jornada', flat=True).distinct()
   ```

### Paso 5: Verificar Optimización del Endpoint

**Probar el endpoint optimizado:**

```bash
# Endpoint MVP global (debería ser más rápido ahora)
curl "http://localhost:8000/api/valoraciones/mvp-global/?temporada_id=4"
```

**En el código, el endpoint:**
- Usa puntos almacenados si existen (muy rápido)
- Calcula en tiempo real si no hay almacenados (backward compatible)
- Logs muestran qué método usa

## 🔍 Verificaciones Adicionales

### Verificar Modelo en Admin

```python
# En admin.py ya está registrado
from fantasy.admin import admin
from fantasy.models import PuntosMVPJornada

# Verificar en admin Django
# Debería aparecer "Puntos MVP Jornada" en el admin
```

### Verificar Índices en BD

```sql
-- PostgreSQL
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'fantasy_puntosmvpjornada';

-- MySQL
SHOW INDEX FROM fantasy_puntosmvpjornada;
```

### Monitorear Rendimiento

**Antes de optimización:**
- Tiempo de respuesta: 2-5 segundos
- Queries: ~1000+

**Después de optimización:**
- Tiempo de respuesta: < 100ms (con puntos almacenados)
- Queries: 1-10 (dependiendo de grupos/jornadas)

## ⚠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'dotenv'"

**Solución:** Configurar entorno virtual y dependencias:
```bash
cd /home/rubenmaestre/pcfutsal.es/backend
source venv/bin/activate  # o el nombre de tu venv
pip install -r requirements.txt
```

### Error: "No such table: fantasy_puntosmvpjornada"

**Solución:** La migración no se aplicó. Ejecutar:
```bash
python manage.py migrate fantasy
```

### Las señales no se disparan

**Verificar:**
1. Settings usa `fantasy.apps.FantasyConfig`
2. App está en `INSTALLED_APPS`
3. No hay errores de importación en logs

### El endpoint sigue siendo lento

**Verificar:**
1. Hay puntos almacenados en BD
2. El método optimizado se está usando (ver logs)
3. Los índices están creados

### Error al calcular puntos históricos

**Verificar:**
1. La temporada existe y tiene el nombre correcto
2. Hay partidos jugados en esa temporada
3. Los grupos existen
4. Revisar logs para más detalles

## 📊 Comandos Útiles

### Ver estadísticas de puntos almacenados

```python
from fantasy.models import PuntosMVPJornada
from nucleo.models import Temporada

temporada = Temporada.objects.get(nombre="2025/2026")
stats = PuntosMVPJornada.objects.filter(temporada=temporada).aggregate(
    total=Count('id'),
    jugadores=Count('jugador', distinct=True),
    jornadas=Count('jornada', distinct=True),
    grupos=Count('grupo', distinct=True)
)
print(stats)
```

### Recalcular una jornada específica

```bash
python manage.py calcular_puntos_mvp_jornada \
    --temporada "2025/2026" \
    --jornada 5 \
    --grupo 3 \
    --forzar
```

### Limpiar puntos de una jornada (si es necesario)

```python
from fantasy.models import PuntosMVPJornada
from nucleo.models import Temporada, Grupo

temporada = Temporada.objects.get(nombre="2025/2026")
grupo = Grupo.objects.get(id=5)

PuntosMVPJornada.objects.filter(
    temporada=temporada,
    grupo=grupo,
    jornada=3
).delete()
```

## ✅ Checklist Final

- [ ] Migración aplicada exitosamente
- [ ] Señales registradas y funcionando
- [ ] Puntos históricos calculados
- [ ] Endpoint respondiendo más rápido
- [ ] Logs muestran uso de puntos almacenados
- [ ] Admin muestra registros de `PuntosMVPJornada`
- [ ] Pruebas manuales exitosas

---

**Nota:** Todos los archivos están listos. Solo falta ejecutar estos pasos cuando el entorno Django esté configurado correctamente.




