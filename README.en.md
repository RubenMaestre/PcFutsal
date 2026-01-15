# ⚽ PC FUTSAL

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-15.5.6-black.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3.0-blue.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)

**The digital reference for Spanish futsal**

[Features](#-main-features) • [Installation](#-installation) • [Documentation](#-documentation) • [API](#-api) • [Contributing](#-contributing)

[🇬🇧 English](README.en.md) | [🇪🇸 Español](README.md)

</div>

---

> **⚠️ Note**: This README is available in English for international developers. However, **all technical documentation, code comments, and project documentation are in Spanish**. This includes API documentation, hooks documentation, and all code comments throughout the project.

---

## 📖 Description

**PC FUTSAL** is a complete platform for data, analysis, rankings, ratings, and fantasy for amateur and semi-professional futsal. It integrates automated scraping, advanced data models, FIFA-like rating system, weekly fantasy, and a modern multilingual frontend.

### 🎯 Objective

Create the **digital reference for Spanish futsal**, providing real-time data, advanced statistical analysis, professional rankings, and an exceptional user experience for both fans and futsal professionals.

---

## ✨ Main Features

### 🔄 Automated Scraping
- **Automatic extraction** of data from FFCV (Valencian Community Football Federation)
- **Periodic updates** of matches, players, clubs, and rankings
- **Robust parsers** with error handling and data validation
- **Rate limiting system** to avoid blocking

### 📊 Rating System
- **FIFA-like ratings** for players (attack, defense, pass, dribble, power, intensity, vision, consistency, charisma)
- **Club coefficients** based on historical performance
- **Automatic calculation** of global averages and rankings
- **Community voting system** for ratings

### 🏆 Weekly Fantasy
- **Fantasy with real players** from competitions
- **Points per matchday** based on real performance
- **Global and division rankings**
- **Team of the week** and weekly MVP

### 📈 Advanced Statistics
- **Real-time rankings** with complete history
- **Top scorers** (global and per matchday)
- **Fair Play** (cards, sanctions)
- **Matchday KPIs** (goals, cards, intensity)
- **Position evolution** with interactive charts

### 🌍 Multilingual
- **7 supported languages**: Spanish, English, German, French, Italian, Portuguese, Valencian
- **Complete i18n** with dynamic translations
- **SEO optimized** per language

### 👥 Public Profiles
- **Complete player cards** with historical statistics
- **Club profiles** with detailed information
- **Match history** with events and lineups
- **Individual rankings and achievements**

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.2.7
- **API**: Django REST Framework
- **Database**: MySQL 8.0+ (utf8mb4)
- **Language**: Python 3.10+
- **Scraping**: Requests + BeautifulSoup4
- **WSGI Server**: Gunicorn
- **ORM**: Django ORM with optimizations (select_related, prefetch_related)

### Frontend
- **Framework**: Next.js 15.5.6 (App Router)
- **UI Library**: React 18.3.1
- **Language**: TypeScript 5.3.0
- **Styles**: Tailwind CSS 3.4.0
- **Components**: shadcn/ui
- **Charts**: Recharts 3.5.1
- **Animations**: Framer Motion 12.23.24
- **Icons**: Lucide React 0.548.0

### Infrastructure
- **Web Server**: Nginx (reverse proxy) - **Recommended for production**
- **WSGI Server**: Gunicorn (Django) - **Recommended for production**
- **Process Manager**: systemd (systemctl) for service management
- **Deployment**: Automated bash script
- **Hosting**: DreamHost (production)

### Development Tools
- **Version Control**: Git
- **Linting**: ESLint (frontend), Flake8 (backend)
- **Type Checking**: TypeScript, mypy
- **Package Managers**: npm, pip

---

## 📋 Prerequisites

Before starting, make sure you have installed:

- **Python** 3.10 or higher
- **Node.js** 18 or higher
- **MySQL** 8.0 or higher
- **Git** to clone the repository
- **npm** or **yarn** to manage frontend dependencies

### Verify Versions

```bash
python3 --version  # Must be 3.10+
node --version     # Must be 18+
mysql --version    # Must be 8.0+
git --version
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/RubenMaestre/PcFutsal.git
cd PcFutsal
```

### 2. Configure Backend

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials (see Configuration section)

# Apply migrations
python manage.py migrate

# Create superuser (optional, to access admin)
python manage.py createsuperuser
```

### 3. Configure Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables (optional)
# Create .env.local if you need to change the API URL
# By default uses relative URLs in client and https://pcfutsal.es in SSR
```

### 4. Start Servers

#### Backend (Terminal 1)

```bash
cd backend
source ../venv/bin/activate
python manage.py runserver
```

The backend will be available at the configured URL.

#### Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The frontend will be available at the configured URL.

---

## ⚙️ Configuration

### Backend Environment Variables

Create `backend/.env` file based on `backend/.env.example`:

```env
# Django
SECRET_KEY=your-secret-key-here-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# MySQL Database
DB_NAME=your_database_name
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

**⚠️ Important**: 
- Generate a new `SECRET_KEY` for production (you can use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- Never commit the `.env` file to Git (it's in `.gitignore`)

### Frontend Environment Variables

Create `frontend/.env.local` file (optional):

```env
# API base URL (only needed if you change the default configuration)
NEXT_PUBLIC_API_BASE_URL=https://your-domain.com
```

By default:
- **Client (browser)**: Uses relative URLs (`/api/...`)
- **SSR (server)**: Uses `https://pcfutsal.es`

### Database Configuration

1. Create MySQL database:

```sql
CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Make sure the user has permissions:

```sql
GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_mysql_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## 📁 Project Structure

```
PcFutsal/
├── backend/                      # Django Backend
│   ├── administracion/           # Django settings and configuration
│   ├── arbitros/                 # Referee management
│   ├── clasificaciones/          # Classification history
│   ├── clubes/                   # Club information
│   ├── destacados/               # Awards and recognitions
│   ├── estadisticas/             # Statistics and KPIs
│   ├── fantasy/                  # Fantasy system
│   ├── historial/                # Historical contributions
│   ├── jugadores/                # Player cards
│   ├── nucleo/                   # Base models (seasons, competitions, groups)
│   ├── partidos/                 # Matches and events
│   ├── scraping/                 # Automated FFCV scraping
│   │   ├── core/                 # Parsers and fetchers
│   │   └── management/commands/  # Scraping commands
│   ├── staff/                    # Technical staff
│   ├── status/                   # System status
│   ├── usuarios/                 # User management
│   └── valoraciones/             # FIFA-like rating system
│
├── frontend/                     # Next.js Frontend
│   ├── app/                      # App Router (routes)
│   │   └── [lang]/              # Multilingual routes
│   ├── components/              # Reusable React components
│   ├── home_components/          # Home-specific components
│   ├── rankings_components/      # Rankings components
│   ├── hooks/                    # Custom hooks (20+ hooks)
│   ├── i18n/                     # Translations (7 languages)
│   ├── lib/                      # Utilities and helpers
│   └── public/                   # Static assets
│
├── DOCUMENTACION/                # Technical documentation
│   ├── PROJECT_SPEC.md          # Complete project specification
│   ├── PROJECT_TREE.md          # Detailed file tree
│   ├── PROJECT_VISION.md        # Vision and objectives
│   ├── APIS.md                  # API documentation
│   └── HOOKS.md                 # Hooks documentation
│
├── .env.example                  # Environment variables example (root)
├── backend/.env.example          # Environment variables example (backend)
├── deploy_pcfutsal.sh.example    # Deployment script example
├── .gitignore                    # Files ignored by Git
├── README.md                     # This file (Spanish)
└── README.en.md                  # English version
```

---

## 🔧 Useful Commands

### Backend

```bash
# Development
python manage.py runserver              # Start development server
python manage.py runserver 0.0.0.0:PORT # Accessible from local network (adjust PORT)

# Database
python manage.py migrate                 # Apply migrations
python manage.py makemigrations          # Create new migrations
python manage.py showmigrations          # View migration status
python manage.py migrate --fake          # Mark migrations as applied without executing them

# Scraping
python manage.py scrape_jornada --temporada_id 4 --grupo_id 1 --jornada 5
python manage.py scrape_jornada --temporada_id 4 --grupo_id 1  # Last matchday

# Classifications
python manage.py recalcular_clasificacion --grupo_id 1
python manage.py generar_historico_clasificaciones --grupo_id 1 --retrospectivo

# Fantasy and Ratings
python manage.py calcular_puntos_mvp_jornada --temporada_id 4 --jornada 5
python manage.py calcular_reconocimientos_jornada --temporada_id 4 --jornada 5
python manage.py asignar_coeficientes --temporada_id 4 --jornada_referencia 6

# Utilities
python manage.py shell                   # Django interactive shell
python manage.py createsuperuser        # Create admin user
python manage.py collectstatic          # Collect static files
python manage.py check                  # Verify configuration
```

### Frontend

```bash
# Development
npm run dev          # Development server
npm run build        # Production build
npm run start        # Production server
npm run lint         # Linting with ESLint
npm run typecheck    # TypeScript type checking

# Analysis
npm run build -- --analyze  # Bundle analysis
```

### Git

```bash
# Basic workflow
git status                    # View status
git add .                     # Add changes
git commit -m "Message"       # Commit
git push origin main          # Push to GitHub

# Branches
git checkout -b feature/new-feature
git merge feature/new-feature
```

---

## 📡 API

The project exposes a complete REST API organized by functionality. All endpoints return JSON.

### Main Endpoints

#### Status
- `GET /api/status/last_update/` - Last system update

#### Core
- `GET /api/nucleo/filter-context/` - Filter context (competitions, groups, seasons)

#### Statistics
- `GET /api/estadisticas/clasificacion-mini/?grupo_id=1` - Summary classification
- `GET /api/estadisticas/clasificacion-completa/?grupo_id=1` - Complete classification
- `GET /api/estadisticas/goleadores-jornada/?grupo_id=1&jornada=5` - Matchday top scorers
- `GET /api/estadisticas/pichichi-temporada/?grupo_id=1` - Season top scorers
- `GET /api/estadisticas/kpis-jornada/?grupo_id=1&jornada=5` - Matchday KPIs
- `GET /api/estadisticas/fair-play-equipos/?grupo_id=1` - Fair Play
- `GET /api/estadisticas/sanciones-jornada/?grupo_id=1&jornada=5` - Sanctions
- `GET /api/estadisticas/resultados-jornada/?grupo_id=1&jornada=5` - Results
- `GET /api/estadisticas/grupo-info/?competicion_slug=tercera-division&grupo_slug=grupo-xv` - Complete group info

#### Clubs
- `GET /api/clubes/list/` - Club list
- `GET /api/clubes/full/?id_or_slug=1` - Complete club information
- `GET /api/clubes/clasificacion-evolucion/?grupo_id=1` - Classification evolution

#### Players
- `GET /api/jugadores/list/` - Player list
- `GET /api/jugadores/full/?id_or_slug=1&temporada_id=4&include=valoraciones,historial,partidos` - Complete information

#### Matches
- `GET /api/partidos/list/?scope=GLOBAL&grupo_id=1&jornada=5` - Match list
- `GET /api/partidos/detalle/?partido_id=123` - Complete match details

#### Ratings
- `GET /api/valoraciones/mvp-global/?temporada_id=4` - Global MVP ranking
- `GET /api/valoraciones/mvp-clasificacion/?grupo_id=1&jornada=5` - MVP classification
- `GET /api/valoraciones/jugadores-jornada/?grupo_id=1&jornada=5` - Matchday players
- `GET /api/valoraciones/partido-estrella/?grupo_id=1&jornada=5` - Star match
- `GET /api/valoraciones/equipo-jornada/?grupo_id=1&jornada=5` - Team of the matchday

#### Fantasy
- `GET /api/fantasy/mvp-top3-optimized/?temporada_id=4&from=2025-01-01&to=2025-01-31` - Top 3 MVP
- `GET /api/fantasy/equipo-global-optimized/?temporada_id=4` - Global teams

### Usage Example

```bash
# Get group classification
curl http://your-domain.com/api/estadisticas/clasificacion-mini/?grupo_id=1

# Get complete player information
curl http://your-domain.com/api/jugadores/full/?id_or_slug=123&include=valoraciones,historial

# Get matchday matches
curl http://your-domain.com/api/partidos/list/?grupo_id=1&jornada=5
```

### Complete Documentation

See detailed documentation of all endpoints in [`DOCUMENTACION/APIS.md`](DOCUMENTACION/APIS.md) (in Spanish)

---

## 🧪 Custom Hooks (Frontend)

The frontend includes 20+ custom hooks for optimized data-fetching:

### Classifications
- `useMiniClasificacion(grupoId)` - Summary classification
- `useClasificacionCompleta(grupoId)` - Complete classification
- `useClasificacionEvolucion(grupoId)` - Historical evolution

### Statistics
- `useMatchdayKPIs(grupoId, jornada)` - Matchday KPIs
- `useTopScorerMatchday(grupoId, jornada)` - Matchday top scorer
- `useSeasonTopScorers(grupoId)` - Season top scorers
- `useFairPlayEquipos(grupoId)` - Fair Play
- `useSancionesJornada(grupoId, jornada)` - Sanctions

### Ratings
- `useMVPGlobal(temporadaId, options)` - Global MVP ranking
- `useMVPClassification(grupoId, options)` - MVP classification
- `useJugadoresJornada(grupoId, jornada)` - Matchday players
- `usePartidoEstrella(grupoId, jornada)` - Star match

### Clubs and Players
- `useClubFull(idOrSlug)` - Complete club information
- `useJugadorFull(idOrSlug, temporadaId, include)` - Complete player information
- `usePartidosList(scope, filters)` - Match list
- `usePartidoDetalle(partidoId)` - Match details

### Fantasy
- `useMVPTop3(options)` - Top 3 MVP
- `useEquipoGlobal(options)` - Global teams

### Usage Example

```typescript
import { useMiniClasificacion } from '@/hooks/useMiniClasificacion';

function ClasificacionComponent() {
  const { data, loading, error } = useMiniClasificacion(1);
  
  if (loading) return <div>Loading...</div>;
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

### Complete Documentation

See detailed documentation of all hooks in [`DOCUMENTACION/HOOKS.md`](DOCUMENTACION/HOOKS.md) (in Spanish)

---

## 🐛 Troubleshooting

### Common Problems

#### Backend won't start
```bash
# Verify virtual environment is activated
which python  # Must point to venv/bin/python

# Verify environment variables
python manage.py check

# Verify database connection
python manage.py dbshell

# In production, verify Gunicorn service
sudo systemctl status pcfutsal  # Adjust service name according to your configuration
sudo systemctl restart pcfutsal
```

#### Migration errors
```bash
# Reset migrations (⚠️ CAUTION! Only in development)
python manage.py migrate --fake nombre_app zero
python manage.py migrate nombre_app
```

#### Frontend won't compile
```bash
# Clear cache and reinstall
rm -rf .next node_modules
npm install
npm run build
```

#### CORS errors
- Verify that `ALLOWED_HOSTS` in `backend/.env` includes the domain
- Verify Nginx configuration if you're in production
- Verify that Nginx is correctly configured as reverse proxy

#### Production issues
```bash
# Verify service status
sudo systemctl status pcfutsal        # Backend (Gunicorn)
sudo systemctl status nginx            # Web server

# View logs
sudo journalctl -u pcfutsal -f        # Backend logs
sudo tail -f /var/log/nginx/error.log # Nginx logs

# Restart services
sudo systemctl restart pcfutsal
sudo systemctl restart nginx
```

#### Scraping fails
- Verify internet connection
- Verify that FFCV HTML structure hasn't changed
- Check logs in `backend/logs/`

---

## 🚀 Deployment

### Production

The project is deployed in production at `https://pcfutsal.es` using:

- **Nginx** as reverse proxy (recommended for production)
- **Gunicorn** as WSGI server for Django (recommended for production)
- **systemd (systemctl)** for system service management
- **MySQL** as database

### Recommended Configuration

#### Nginx
Nginx acts as reverse proxy, handling:
- SSL/TLS (HTTPS)
- Load balancing
- Serving static files
- Proxying requests to backend (Gunicorn) and frontend (Next.js)

#### Gunicorn
Gunicorn is the recommended WSGI server for Django in production:
- Better performance than Django development server
- Support for multiple workers
- Robust handling of concurrent requests

#### systemd
Services are managed with systemd using `systemctl`:
- Automatic startup on server boot
- Centralized service management
- Integrated logs with journald

### Deployment Script

See `deploy_pcfutsal.sh.example` for an example of an automated deployment script.

**⚠️ Important**: Do not commit the real script with absolute paths and passwords to Git.

---

## 🤝 Contributing

Contributions are welcome. To contribute:

1. **Fork** the project
2. **Create a branch** for your feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Contribution Guidelines

- Follow project conventions
- Update documentation if necessary
- Test your changes before committing

---

## 📄 License

This project is **private**. All rights reserved.

---

## 👤 Author

**Rubén Maestre**

- 📧 Email: [data@rubenmaestre.com](mailto:data@rubenmaestre.com)
- 🐙 GitHub: [@RubenMaestre](https://github.com/RubenMaestre)
- 🌐 Web: [digital.rubenmaestre.com](https://digital.rubenmaestre.com)

---

## 🌐 Links

- **🌍 PC FUTSAL (Production)**: [https://pcfutsal.es](https://pcfutsal.es)
- **💻 Digital Rubén Maestre**: [https://digital.rubenmaestre.com](https://digital.rubenmaestre.com)
- **🚀 Rumaza**: [https://www.rumaza.io](https://www.rumaza.io)

---

## 📚 Additional Documentation

> **Note**: All technical documentation is in Spanish.

- [`DOCUMENTACION/PROJECT_SPEC.md`](DOCUMENTACION/PROJECT_SPEC.md) - Complete project specification (Spanish)
- [`DOCUMENTACION/PROJECT_TREE.md`](DOCUMENTACION/PROJECT_TREE.md) - Detailed file tree (Spanish)
- [`DOCUMENTACION/PROJECT_VISION.md`](DOCUMENTACION/PROJECT_VISION.md) - Vision and objectives (Spanish)
- [`DOCUMENTACION/APIS.md`](DOCUMENTACION/APIS.md) - Complete API documentation (Spanish)
- [`DOCUMENTACION/HOOKS.md`](DOCUMENTACION/HOOKS.md) - Complete hooks documentation (Spanish)

---

<div align="center">

**⚽ PC FUTSAL** - The digital reference for Spanish futsal

Made with ❤️ for the futsal community

</div>

