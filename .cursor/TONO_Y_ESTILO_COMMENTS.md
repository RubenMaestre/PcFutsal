# Guía de Tono y Estilo de Comentarios — PC FUTSAL

Este documento define el **tono y estilo** de los comentarios dentro del código en proyectos desarrollados por Rubén Maestre.

**No es una guía académica.**  
Es una guía práctica para **entender el código meses después**, facilitar el mantenimiento y que otros desarrolladores entiendan **por qué se hizo algo**, no solo qué hace.

---

## 1. Principios Básicos

### 1.1. El código se explica solo, las decisiones no

No se comenta lo obvio.  
Se comenta:
- el **por qué**
- las **limitaciones**
- las **decisiones de diseño**
- los **casos raros**

**❌ Mal:**
```python
# Suma dos números
total = a + b
```

**✅ Bien:**
```python
# Se suma aquí para evitar recalcular el total en cada iteración
total = a + b
```

### 1.2. Comentarios útiles > comentarios bonitos

Los comentarios no están para quedar bien.  
Están para ahorrar tiempo y errores.

Si un comentario no aporta contexto, se elimina.

### 1.3. Menos comentarios, pero mejores

Un buen comentario puede ahorrar 30 minutos de lectura.  
Diez malos comentarios solo estorban.

---

## 2. Tono de los Comentarios

### 2.1. Directo

Frases claras. Sin adornos. Sin lenguaje corporativo.

```python
# Esto se hace aquí porque Django evalúa el queryset en este punto
```

### 2.2. Honesto

Si algo no es ideal, se dice.

```python
# Solución pragmática: no es la más elegante, pero evita una consulta extra
```

### 2.3. Profesional, pero humano

Puede haber un toque irónico muy leve, nunca infantil ni sarcástico en exceso.

```python
# Sí, esto podría refactorizarse. No hoy.
```

### 2.4. Evitar postureo técnico

Nada de comentarios para demostrar que "sabemos mucho".

**❌ Mal:**
```python
# Aplicamos una abstracción polimórfica desacoplada del core
```

**✅ Bien:**
```python
# Se separa esta lógica para poder cambiar la fuente de datos sin romper nada
```

---

## 3. Qué SÍ Comentar

### 3.1. Decisiones de arquitectura

```python
# Se usa servicio separado para no acoplar la vista a la lógica de negocio
```

### 3.2. Workarounds y límites

```python
# Workaround: esta API falla si se envían más de 100 registros
```

### 3.3. Código no intuitivo

```python
# El orden importa: primero se guarda el padre o Django rompe la FK
```

### 3.4. Dependencias externas o comportamientos raros

```python
# WhatsApp Web bloquea si los envíos son demasiado rápidos
```

---

## 4. Qué NO Comentar

### 4.1. Lo evidente

**❌ Mal:**
```python
# Iteramos sobre la lista
for item in items:
    pass
```

### 4.2. Historias personales o comentarios emocionales

El código no es un diario.

### 4.3. Comentarios obsoletos

Si el comentario ya no explica la realidad del código, se elimina.

---

## 5. Estilo de Escritura

- **Frases cortas**
- **Lenguaje natural**
- **Español de España**
- **Sin mayúsculas innecesarias**
- **Sin emojis en código productivo**

---

## 6. Idioma

Comentarios en **español**, salvo:
- librerías open source internacionales
- proyectos explícitamente en inglés

**Consistencia > idioma.**

---

## 7. Ejemplos Completos

### 7.1. Ejemplo Correcto

```python
def calculate_totals(orders):
    # Se precalcula aquí para evitar repetir la lógica en varios endpoints
    totals = {}

    for order in orders:
        # Puede venir None si el pedido está incompleto
        if not order.amount:
            continue

        totals[order.id] = order.amount

    return totals
```

### 7.2. Ejemplo Incorrecto

```python
def calculate_totals(orders):
    # Función para calcular totales
    totals = {}

    for order in orders:
        # Comprobamos si el amount es None
        if not order.amount:
            continue

        # Asignamos el total
        totals[order.id] = order.amount

    # Devolvemos los totales
    return totals
```

---

## 8. Regla Final (La Más Importante)

**Si dentro de 6 meses no recuerdas por qué hiciste algo, el comentario debería explicarlo.**

**Si no aporta eso, sobra.**

---

**Fin del documento.**