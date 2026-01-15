# PC FUTSAL

Plataforma completa de datos, análisis, rankings, valoraciones y fantasy para el fútbol sala amateur y semiprofesional.

## 🎯 Descripción

PC FUTSAL es un ecosistema digital integral diseñado para transformar el fútbol sala amateur y semiprofesional con una mezcla única de datos, gamificación, comunidad y cultura futsal.

### Características principales

- **Scraping automatizado** de datos de FFCV (Federación de Fútbol de la Comunidad Valenciana)
- **Sistema de valoraciones FIFA-like** para jugadores y clubes
- **Fantasy semanal** con jugadores reales
- **Rankings y clasificaciones** en tiempo real
- **Perfiles públicos** de jugadores y clubes
- **Frontend multilenguaje** (7 idiomas: es, en, de, fr, it, pt, val)
- **Análisis estadísticos avanzados** (goleadores, sanciones, fair play, etc.)

## 🛠️ Stack Tecnológico

### Backend
- **Django 5.2.7** + Django REST Framework
- **MySQL** (utf8mb4)
- **Python 3.10+**
- Scraping con Requests + BeautifulSoup

### Frontend
- **Next.js 15.5.6** + React 18.3.1
- **TypeScript 5.3.0**
- **Tailwind CSS 3.4.0** + shadcn/ui
- **Recharts** (gráficas)
- **Framer Motion** (animaciones)

### Infraestructura
- **Nginx** (reverse proxy)
- **Gunicorn** (servidor WSGI)
- **PM2** (gestión de procesos Node.js)

## 📋 Requisitos Previos

- Python 3.10 o superior
- Node.js 18 o superior
- MySQL 8.0 o superior
- Git

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/RubenMaestre/pcfutsal.git
cd pcfutsal
```

### 2. Backend

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
cd backend
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de base de datos

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 3. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno (si es necesario)
# Crear .env.local con NEXT_PUBLIC_API_BASE_URL si es necesario

# Ejecutar en desarrollo
npm run dev
```

## ⚙️ Configuración

### Variables de entorno

#### Backend (`backend/.env`)

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306
```

#### Frontend

Por defecto, el frontend usa URLs relativas (`/api/...`) en cliente y `https://pcfutsal.es` en SSR. Para cambiar esto, crear `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=https://tu-dominio.com
```

## 📁 Estructura del Proyecto

```
pcfutsal/
├── backend/                 # Django backend
│   ├── administracion/      # Settings y configuración
│   ├── arbitros/            # Gestión de árbitros
│   ├── clubes/              # Información de clubes
│   ├── clasificaciones/     # Histórico de clasificaciones
│   ├── destacados/          # Distintivos y reconocimientos
│   ├── estadisticas/        # Estadísticas y KPIs
│   ├── fantasy/              # Sistema fantasy
│   ├── historial/           # Aportes históricos
│   ├── jugadores/           # Fichas de jugadores
│   ├── nucleo/              # Modelos base (temporadas, competiciones)
│   ├── partidos/            # Partidos y eventos
│   ├── scraping/            # Scraping automatizado de FFCV
│   ├── staff/               # Staff técnico
│   ├── status/              # Estado del sistema
│   ├── usuarios/            # Gestión de usuarios
│   └── valoraciones/        # Sistema de valoraciones FIFA-like
│
├── frontend/                # Next.js frontend
│   ├── app/                 # App Router (rutas)
│   ├── components/          # Componentes React
│   ├── hooks/               # Hooks personalizados
│   ├── i18n/               # Traducciones (7 idiomas)
│   ├── lib/                 # Utilidades
│   └── public/             # Assets estáticos
│
└── .cursor/                 # Documentación técnica
    ├── PROJECT_SPEC.md     # Especificación completa
    ├── AGENT_GLOBAL_PLAYBOOK.md
    └── DOCUMENTACION/       # Documentación de APIs y hooks
```

## 🔧 Comandos Útiles

### Backend

```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Aplicar migraciones
python manage.py migrate

# Crear migraciones
python manage.py makemigrations

# Scraping de datos
python manage.py scrape_equipos
python manage.py scrape_jugadores
python manage.py scrape_partidos

# Recalcular clasificación
python manage.py recalcular_clasificacion

# Generar histórico de clasificaciones
python manage.py generar_historico_clasificaciones --retrospectivo
```

### Frontend

```bash
# Desarrollo
npm run dev

# Build de producción
npm run build

# Iniciar en producción
npm start

# Linting
npm run lint

# Type checking
npm run typecheck
```

## 📡 APIs Principales

El proyecto expone múltiples endpoints REST organizados por funcionalidad:

- **Status**: `/api/status/last_update/`
- **Núcleo**: `/api/nucleo/filter-context/`
- **Estadísticas**: `/api/estadisticas/*` (14 endpoints)
- **Clubes**: `/api/clubes/*` (4 endpoints)
- **Valoraciones**: `/api/valoraciones/*` (8 endpoints)
- **Jugadores**: `/api/jugadores/*` (5 endpoints)

Ver documentación completa en `.cursor/DOCUMENTACION/APIS.md`

## 🧪 Desarrollo

### Hooks Personalizados

El frontend incluye 20+ hooks personalizados para data-fetching:

- Clasificaciones: `useMiniClasificacion`, `useClasificacionCompleta`, etc.
- Estadísticas: `useMatchdayKPIs`, `useTopScorerMatchday`, etc.
- Valoraciones: `useMVPGlobal`, `useJugadoresJornada`, etc.
- Clubes: `useClubFull`, `useClubHistorico`
- Jugadores: `useJugadorFull`

Ver documentación completa en `.cursor/DOCUMENTACION/HOOKS.md`

## 📝 Estilo de Código

El proyecto sigue una guía de estilo específica para comentarios. Ver `.cursor/TONO_Y_ESTILO_COMMENTS.md` para más detalles.

**Principios:**
- Comentar el **por qué**, no el qué
- Comentarios directos y honestos
- Sin postureo técnico
- Español de España

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado. Todos los derechos reservados.


## 👤 Autor

**Rubén Maestre**
- Email: data@rubenmaestre.com
- GitHub: [@RubenMaestre](https://github.com/RubenMaestre)

## 🌐 Enlaces

- **PC FUTSAL**: https://pcfutsal.es
- **Digital Rubén Maestre**: https://digital.rubenmaestre.com
- **Rumaza**: https://www.rumaza.io

---

**PC FUTSAL** - La referencia digital del futsal español
