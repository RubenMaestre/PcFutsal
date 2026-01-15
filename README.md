# ⚽ PC FUTSAL

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-15.5.6-black.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3.0-blue.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)

**La referencia digital del futsal español**

[Características](#-características-principales) • [Instalación](#-instalación) • [Documentación](#-documentación) • [API](#-api) • [Contribuir](#-contribución)

</div>

---

## 📖 Descripción

**PC FUTSAL** es una plataforma completa de datos, análisis, rankings, valoraciones y fantasy para el fútbol sala amateur y semiprofesional. Integra scraping automatizado, modelos avanzados de datos, sistema de valoraciones estilo FIFA, fantasy semanal y un frontend multilenguaje moderno.

### 🎯 Objetivo

Crear la **referencia digital del futsal español**, proporcionando datos en tiempo real, análisis estadísticos avanzados, rankings profesionales y una experiencia de usuario excepcional tanto para aficionados como para profesionales del fútbol sala.

---

## ✨ Características Principales

### 🔄 Scraping Automatizado
- **Extracción automática** de datos de FFCV (Federación de Fútbol de la Comunidad Valenciana)
- **Actualización periódica** de partidos, jugadores, clubes y clasificaciones
- **Parsers robustos** con manejo de errores y validación de datos
- **Sistema de rate limiting** para evitar bloqueos

### 📊 Sistema de Valoraciones
- **Valoraciones FIFA-like** para jugadores (ataque, defensa, pase, regate, potencia, intensidad, visión, regularidad, carisma)
- **Coeficientes de clubes** basados en rendimiento histórico
- **Cálculo automático** de medias globales y rankings
- **Sistema de votación** para valoraciones comunitarias

### 🏆 Fantasy Semanal
- **Fantasy con jugadores reales** de las competiciones
- **Puntos por jornada** basados en rendimiento real
- **Rankings globales** y por división
- **Equipo de la jornada** y MVP semanal

### 📈 Estadísticas Avanzadas
- **Clasificaciones en tiempo real** con histórico completo
- **Goleadores** (global y por jornada)
- **Fair Play** (tarjetas, sanciones)
- **KPIs de jornada** (goles, tarjetas, intensidad)
- **Evolución de posiciones** con gráficas interactivas

### 🌍 Multilenguaje
- **7 idiomas soportados**: Español, Inglés, Alemán, Francés, Italiano, Portugués, Valenciano
- **i18n completo** con traducciones dinámicas
- **SEO optimizado** por idioma

### 👥 Perfiles Públicos
- **Fichas completas** de jugadores con estadísticas históricas
- **Perfiles de clubes** con información detallada
- **Historial de partidos** con eventos y alineaciones
- **Rankings y logros** individuales

---

## 🛠️ Stack Tecnológico

### Backend
- **Framework**: Django 5.2.7
- **API**: Django REST Framework
- **Base de datos**: MySQL 8.0+ (utf8mb4)
- **Lenguaje**: Python 3.10+
- **Scraping**: Requests + BeautifulSoup4
- **Servidor WSGI**: Gunicorn
- **ORM**: Django ORM con optimizaciones (select_related, prefetch_related)

### Frontend
- **Framework**: Next.js 15.5.6 (App Router)
- **UI Library**: React 18.3.1
- **Lenguaje**: TypeScript 5.3.0
- **Estilos**: Tailwind CSS 3.4.0
- **Componentes**: shadcn/ui
- **Gráficas**: Recharts 3.5.1
- **Animaciones**: Framer Motion 12.23.24
- **Iconos**: Lucide React 0.548.0

### Infraestructura
- **Web Server**: Nginx (reverse proxy) - **Recomendado para producción**
- **WSGI Server**: Gunicorn (Django) - **Recomendado para producción**
- **Process Manager**: systemd (systemctl) para gestión de servicios
- **Deployment**: Script automatizado con bash
- **Hosting**: DreamHost (producción)

### Herramientas de Desarrollo
- **Versionado**: Git
- **Linting**: ESLint (frontend), Flake8 (backend)
- **Type Checking**: TypeScript, mypy
- **Package Managers**: npm, pip

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python** 3.10 o superior
- **Node.js** 18 o superior
- **MySQL** 8.0 o superior
- **Git** para clonar el repositorio
- **npm** o **yarn** para gestionar dependencias del frontend

### Verificar Versiones

```bash
python3 --version  # Debe ser 3.10+
node --version     # Debe ser 18+
mysql --version    # Debe ser 8.0+
git --version
```

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/RubenMaestre/PcFutsal.git
cd PcFutsal
```

### 2. Configurar Backend

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
cd backend
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales (ver sección de Configuración)

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional, para acceder al admin)
python manage.py createsuperuser
```

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno (opcional)
# Crear .env.local si necesitas cambiar la URL de la API
# Por defecto usa URLs relativas en cliente y https://pcfutsal.es en SSR
```

### 4. Iniciar Servidores

#### Backend (Terminal 1)

```bash
cd backend
source ../venv/bin/activate
python manage.py runserver
```

El backend estará disponible en la URL configurada (por defecto `http://localhost:8000` en desarrollo)

#### Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

El frontend estará disponible en la URL configurada (por defecto `http://localhost:3000` en desarrollo)

---

## ⚙️ Configuración

### Variables de Entorno Backend

Crear archivo `backend/.env` basado en `backend/.env.example`:

```env
# Django
SECRET_KEY=tu-clave-secreta-aqui-genera-una-nueva
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com

# Base de Datos MySQL
DB_NAME=nombre_de_tu_base_de_datos
DB_USER=usuario_mysql
DB_PASSWORD=contraseña_mysql
DB_HOST=localhost
DB_PORT=3306
```

**⚠️ Importante**: 
- Genera una nueva `SECRET_KEY` para producción (puedes usar `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- Nunca subas el archivo `.env` a Git (está en `.gitignore`)

### Variables de Entorno Frontend

Crear archivo `frontend/.env.local` (opcional):

```env
# URL base de la API (solo necesario si cambias la configuración por defecto)
NEXT_PUBLIC_API_BASE_URL=https://tu-dominio.com
```

Por defecto:
- **Cliente (navegador)**: Usa URLs relativas (`/api/...`)
- **SSR (servidor)**: Usa `https://pcfutsal.es`

### Configuración de Base de Datos

1. Crear base de datos MySQL:

```sql
CREATE DATABASE nombre_de_tu_base_de_datos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Asegúrate de que el usuario tenga permisos:

```sql
GRANT ALL PRIVILEGES ON nombre_de_tu_base_de_datos.* TO 'usuario_mysql'@'localhost';
FLUSH PRIVILEGES;
```

---

## 📁 Estructura del Proyecto

```
PcFutsal/
├── backend/                      # Django Backend
│   ├── administracion/           # Settings y configuración Django
│   ├── arbitros/                 # Gestión de árbitros
│   ├── clasificaciones/          # Histórico de clasificaciones
│   ├── clubes/                   # Información de clubes
│   ├── destacados/               # Distintivos y reconocimientos
│   ├── estadisticas/             # Estadísticas y KPIs
│   ├── fantasy/                  # Sistema fantasy
│   ├── historial/                # Aportes históricos
│   ├── jugadores/                # Fichas de jugadores
│   ├── nucleo/                   # Modelos base (temporadas, competiciones, grupos)
│   ├── partidos/                 # Partidos y eventos
│   ├── scraping/                 # Scraping automatizado de FFCV
│   │   ├── core/                 # Parsers y fetchers
│   │   └── management/commands/  # Comandos de scraping
│   ├── staff/                    # Staff técnico
│   ├── status/                   # Estado del sistema
│   ├── usuarios/                 # Gestión de usuarios
│   └── valoraciones/             # Sistema de valoraciones FIFA-like
│
├── frontend/                     # Next.js Frontend
│   ├── app/                      # App Router (rutas)
│   │   └── [lang]/              # Rutas multilenguaje
│   ├── components/              # Componentes React reutilizables
│   ├── home_components/          # Componentes específicos de home
│   ├── rankings_components/      # Componentes de rankings
│   ├── hooks/                    # Hooks personalizados (20+ hooks)
│   ├── i18n/                     # Traducciones (7 idiomas)
│   ├── lib/                      # Utilidades y helpers
│   └── public/                   # Assets estáticos
│
├── DOCUMENTACION/                # Documentación técnica
│   ├── PROJECT_SPEC.md          # Especificación completa del proyecto
│   ├── PROJECT_TREE.md          # Árbol de archivos detallado
│   ├── PROJECT_VISION.md        # Visión y objetivos
│   ├── APIS.md                  # Documentación de APIs
│   └── HOOKS.md                 # Documentación de hooks
│
├── .env.example                  # Ejemplo de variables de entorno (raíz)
├── backend/.env.example          # Ejemplo de variables de entorno (backend)
├── deploy_pcfutsal.sh.example    # Ejemplo de script de deployment
├── .gitignore                    # Archivos ignorados por Git
└── README.md                     # Este archivo
```

---

## 🔧 Comandos Útiles

### Backend

```bash
# Desarrollo
python manage.py runserver              # Iniciar servidor de desarrollo
python manage.py runserver 0.0.0.0:8000 # Accesible desde red local

# Base de Datos
python manage.py migrate                 # Aplicar migraciones
python manage.py makemigrations          # Crear nuevas migraciones
python manage.py showmigrations          # Ver estado de migraciones
python manage.py migrate --fake          # Marcar migraciones como aplicadas sin ejecutarlas

# Scraping
python manage.py scrape_jornada --temporada_id 4 --grupo_id 1 --jornada 5
python manage.py scrape_jornada --temporada_id 4 --grupo_id 1  # Última jornada

# Clasificaciones
python manage.py recalcular_clasificacion --grupo_id 1
python manage.py generar_historico_clasificaciones --grupo_id 1 --retrospectivo

# Fantasy y Valoraciones
python manage.py calcular_puntos_mvp_jornada --temporada_id 4 --jornada 5
python manage.py calcular_reconocimientos_jornada --temporada_id 4 --jornada 5
python manage.py asignar_coeficientes --temporada_id 4 --jornada_referencia 6

# Utilidades
python manage.py shell                   # Django shell interactivo
python manage.py createsuperuser        # Crear usuario admin
python manage.py collectstatic          # Recopilar archivos estáticos
python manage.py check                  # Verificar configuración
```

### Frontend

```bash
# Desarrollo
npm run dev          # Servidor de desarrollo
npm run build        # Build de producción
npm run start        # Servidor de producción
npm run lint         # Linting con ESLint
npm run typecheck    # Verificación de tipos TypeScript

# Análisis
npm run build -- --analyze  # Análisis del bundle
```

### Git

```bash
# Flujo de trabajo básico
git status                    # Ver estado
git add .                     # Añadir cambios
git commit -m "Mensaje"       # Commit
git push origin main          # Push a GitHub

# Ramas
git checkout -b feature/nueva-funcionalidad
git merge feature/nueva-funcionalidad
```

---

## 📡 API

El proyecto expone una API REST completa organizada por funcionalidad. Todos los endpoints devuelven JSON.

### Endpoints Principales

#### Status
- `GET /api/status/last_update/` - Última actualización del sistema

#### Núcleo
- `GET /api/nucleo/filter-context/` - Contexto de filtros (competiciones, grupos, temporadas)

#### Estadísticas
- `GET /api/estadisticas/clasificacion-mini/?grupo_id=1` - Clasificación resumida
- `GET /api/estadisticas/clasificacion-completa/?grupo_id=1` - Clasificación completa
- `GET /api/estadisticas/goleadores-jornada/?grupo_id=1&jornada=5` - Goleadores de jornada
- `GET /api/estadisticas/pichichi-temporada/?grupo_id=1` - Goleadores de temporada
- `GET /api/estadisticas/kpis-jornada/?grupo_id=1&jornada=5` - KPIs de jornada
- `GET /api/estadisticas/fair-play-equipos/?grupo_id=1` - Fair Play
- `GET /api/estadisticas/sanciones-jornada/?grupo_id=1&jornada=5` - Sanciones
- `GET /api/estadisticas/resultados-jornada/?grupo_id=1&jornada=5` - Resultados
- `GET /api/estadisticas/grupo-info/?competicion_slug=tercera-division&grupo_slug=grupo-xv` - Info completa del grupo

#### Clubes
- `GET /api/clubes/list/` - Lista de clubes
- `GET /api/clubes/full/?id_or_slug=1` - Información completa de un club
- `GET /api/clubes/clasificacion-evolucion/?grupo_id=1` - Evolución de clasificación

#### Jugadores
- `GET /api/jugadores/list/` - Lista de jugadores
- `GET /api/jugadores/full/?id_or_slug=1&temporada_id=4&include=valoraciones,historial,partidos` - Información completa

#### Partidos
- `GET /api/partidos/list/?scope=GLOBAL&grupo_id=1&jornada=5` - Lista de partidos
- `GET /api/partidos/detalle/?partido_id=123` - Detalle completo de un partido

#### Valoraciones
- `GET /api/valoraciones/mvp-global/?temporada_id=4` - Ranking MVP global
- `GET /api/valoraciones/mvp-clasificacion/?grupo_id=1&jornada=5` - Clasificación MVP
- `GET /api/valoraciones/jugadores-jornada/?grupo_id=1&jornada=5` - Jugadores de la jornada
- `GET /api/valoraciones/partido-estrella/?grupo_id=1&jornada=5` - Partido estrella
- `GET /api/valoraciones/equipo-jornada/?grupo_id=1&jornada=5` - Equipo de la jornada

#### Fantasy
- `GET /api/fantasy/mvp-top3-optimized/?temporada_id=4&from=2025-01-01&to=2025-01-31` - Top 3 MVP
- `GET /api/fantasy/equipo-global-optimized/?temporada_id=4` - Equipos globales

### Ejemplo de Uso

```bash
# Obtener clasificación de un grupo
curl http://localhost:8000/api/estadisticas/clasificacion-mini/?grupo_id=1

# Obtener información completa de un jugador
curl http://localhost:8000/api/jugadores/full/?id_or_slug=123&include=valoraciones,historial

# Obtener partidos de una jornada
curl http://localhost:8000/api/partidos/list/?grupo_id=1&jornada=5
```

### Documentación Completa

Ver documentación detallada de todos los endpoints en [`DOCUMENTACION/APIS.md`](DOCUMENTACION/APIS.md)

---

## 🧪 Hooks Personalizados (Frontend)

El frontend incluye 20+ hooks personalizados para data-fetching optimizado:

### Clasificaciones
- `useMiniClasificacion(grupoId)` - Clasificación resumida
- `useClasificacionCompleta(grupoId)` - Clasificación completa
- `useClasificacionEvolucion(grupoId)` - Evolución histórica

### Estadísticas
- `useMatchdayKPIs(grupoId, jornada)` - KPIs de jornada
- `useTopScorerMatchday(grupoId, jornada)` - Goleador de jornada
- `useSeasonTopScorers(grupoId)` - Goleadores de temporada
- `useFairPlayEquipos(grupoId)` - Fair Play
- `useSancionesJornada(grupoId, jornada)` - Sanciones

### Valoraciones
- `useMVPGlobal(temporadaId, options)` - Ranking MVP global
- `useMVPClassification(grupoId, options)` - Clasificación MVP
- `useJugadoresJornada(grupoId, jornada)` - Jugadores de la jornada
- `usePartidoEstrella(grupoId, jornada)` - Partido estrella

### Clubes y Jugadores
- `useClubFull(idOrSlug)` - Información completa de club
- `useJugadorFull(idOrSlug, temporadaId, include)` - Información completa de jugador
- `usePartidosList(scope, filters)` - Lista de partidos
- `usePartidoDetalle(partidoId)` - Detalle de partido

### Fantasy
- `useMVPTop3(options)` - Top 3 MVP
- `useEquipoGlobal(options)` - Equipos globales

### Ejemplo de Uso

```typescript
import { useMiniClasificacion } from '@/hooks/useMiniClasificacion';

function ClasificacionComponent() {
  const { data, loading, error } = useMiniClasificacion(1);
  
  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      {data?.clasificacion.map((equipo, idx) => (
        <div key={equipo.club_id}>
          {idx + 1}. {equipo.club_nombre} - {equipo.puntos} pts
        </div>
      ))}
    </div>
  );
}
```

### Documentación Completa

Ver documentación detallada de todos los hooks en [`DOCUMENTACION/HOOKS.md`](DOCUMENTACION/HOOKS.md)

---

## 🐛 Troubleshooting

### Problemas Comunes

#### Backend no inicia
```bash
# Verificar que el entorno virtual esté activado
which python  # Debe apuntar a venv/bin/python

# Verificar variables de entorno
python manage.py check

# Verificar conexión a base de datos
python manage.py dbshell

# En producción, verificar servicio Gunicorn
sudo systemctl status pcfutsal  # Ajustar nombre del servicio según tu configuración
sudo systemctl restart pcfutsal
```

#### Errores de migraciones
```bash
# Resetear migraciones (¡CUIDADO! Solo en desarrollo)
python manage.py migrate --fake nombre_app zero
python manage.py migrate nombre_app
```

#### Frontend no compila
```bash
# Limpiar caché y reinstalar
rm -rf .next node_modules
npm install
npm run build
```

#### Errores de CORS
- Verificar que `ALLOWED_HOSTS` en `backend/.env` incluya el dominio
- Verificar configuración de Nginx si estás en producción
- Verificar que Nginx esté configurado correctamente como reverse proxy

#### Problemas en producción
```bash
# Verificar estado de servicios
sudo systemctl status pcfutsal        # Backend (Gunicorn)
sudo systemctl status nginx            # Web server

# Ver logs
sudo journalctl -u pcfutsal -f        # Logs del backend
sudo tail -f /var/log/nginx/error.log # Logs de Nginx

# Reiniciar servicios
sudo systemctl restart pcfutsal
sudo systemctl restart nginx
```

#### Scraping falla
- Verificar conexión a internet
- Verificar que la estructura HTML de FFCV no haya cambiado
- Revisar logs en `backend/logs/`

---

## 📝 Estilo de Código

El proyecto sigue una guía de estilo específica para comentarios. Ver [`DOCUMENTACION/TONO_Y_ESTILO_COMMENTS.md`](DOCUMENTACION/TONO_Y_ESTILO_COMMENTS.md) para más detalles.

### Principios

- **Comentar el por qué, no el qué**: Explicar decisiones y razones, no obviedades
- **Comentarios directos y honestos**: Sin postureo técnico
- **Español de España**: Todos los comentarios en español
- **Contexto suficiente**: Incluir limitaciones y decisiones de diseño

### Ejemplo

```python
# Headers personalizados para simular un navegador real y evitar bloqueos de FFCV.
# Es crucial para que el scraping no sea detectado y bloqueado.
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0...",
    # ...
}
```

---

## 🚀 Deployment

### Producción

El proyecto está desplegado en producción en `https://pcfutsal.es` usando:

- **Nginx** como reverse proxy (recomendado para producción)
- **Gunicorn** como servidor WSGI para Django (recomendado para producción)
- **systemd (systemctl)** para gestionar servicios del sistema
- **MySQL** como base de datos

### Configuración Recomendada

#### Nginx
Nginx actúa como reverse proxy, manejando:
- SSL/TLS (HTTPS)
- Balanceo de carga
- Servir archivos estáticos
- Proxy de peticiones al backend (Gunicorn) y frontend (Next.js)

#### Gunicorn
Gunicorn es el servidor WSGI recomendado para Django en producción:
- Mejor rendimiento que el servidor de desarrollo de Django
- Soporte para múltiples workers
- Manejo robusto de peticiones concurrentes

#### systemd
Los servicios se gestionan con systemd usando `systemctl`:
- Inicio automático al arrancar el servidor
- Gestión centralizada de servicios
- Logs integrados con journald

### Script de Deployment

Ver `deploy_pcfutsal.sh.example` para un ejemplo de script de deployment automatizado.

**⚠️ Importante**: No subir el script real con rutas absolutas y contraseñas a Git.

---

## 🤝 Contribución

Las contribuciones son bienvenidas. Para contribuir:

1. **Fork** el proyecto
2. **Crea una rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre un Pull Request**

### Guías de Contribución

- Sigue el estilo de código existente
- Añade comentarios según la guía de estilo
- Actualiza la documentación si es necesario
- Prueba tus cambios antes de hacer commit

---

## 📄 Licencia

Este proyecto es **privado**. Todos los derechos reservados.

---

## 👤 Autor

**Rubén Maestre**

- 📧 Email: [data@rubenmaestre.com](mailto:data@rubenmaestre.com)
- 🐙 GitHub: [@RubenMaestre](https://github.com/RubenMaestre)
- 🌐 Web: [digital.rubenmaestre.com](https://digital.rubenmaestre.com)

---

## 🌐 Enlaces

- **🌍 PC FUTSAL (Producción)**: [https://pcfutsal.es](https://pcfutsal.es)
- **💻 Digital Rubén Maestre**: [https://digital.rubenmaestre.com](https://digital.rubenmaestre.com)
- **🚀 Rumaza**: [https://www.rumaza.io](https://www.rumaza.io)

---

## 📚 Documentación Adicional

- [`DOCUMENTACION/PROJECT_SPEC.md`](DOCUMENTACION/PROJECT_SPEC.md) - Especificación completa del proyecto
- [`DOCUMENTACION/PROJECT_TREE.md`](DOCUMENTACION/PROJECT_TREE.md) - Árbol de archivos detallado
- [`DOCUMENTACION/PROJECT_VISION.md`](DOCUMENTACION/PROJECT_VISION.md) - Visión y objetivos
- [`DOCUMENTACION/APIS.md`](DOCUMENTACION/APIS.md) - Documentación completa de APIs
- [`DOCUMENTACION/HOOKS.md`](DOCUMENTACION/HOOKS.md) - Documentación completa de hooks

---

<div align="center">

**⚽ PC FUTSAL** - La referencia digital del futsal español

Hecho con ❤️ para la comunidad del fútbol sala

</div>
