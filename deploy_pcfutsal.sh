#!/usr/bin/env bash
set -e

PROJECT_ROOT="/home/rubenmaestre/pcfutsal.es"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_DIR="$PROJECT_ROOT/venv"

# Cargar GUNICORN_PASSWORD del .env
if [ -f "$PROJECT_ROOT/.env" ]; then
  export $(grep GUNICORN_PASSWORD "$PROJECT_ROOT/.env" | sed 's/"//g' | xargs)
fi

echo "== PC FUTSAL DEPLOY =="

echo "[1/4] Build frontend (Next.js)..."
cd "$FRONTEND_DIR"
npm run build

echo "[2/4] Restart PM2 (pcfutsal-frontend)..."
# Si ya existe, reinicia; si no, lo crea
if pm2 list | grep -q "pcfutsal-frontend"; then
  pm2 restart pcfutsal-frontend
else
  pm2 start npm --name pcfutsal-frontend -- start -- -p 3055
fi

echo "[3/4] Restart Gunicorn backend (pcfutsal.service)..."
echo "$GUNICORN_PASSWORD" | sudo -S systemctl restart pcfutsal

echo "[4/4] Test & reload Nginx..."
echo "$GUNICORN_PASSWORD" | sudo -S nginx -t
echo "$GUNICORN_PASSWORD" | sudo -S systemctl reload nginx

echo "== Deploy completado correctamente =="





