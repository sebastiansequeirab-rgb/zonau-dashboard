# zonau-dashboard

Dashboard personal para consultar saldo, movimientos y accesos del sistema Zona U UCAB.

## Estructura

```
zonau-dashboard/
├── scraper/          — Python scraper (Firecrawl)
└── dashboard/        — React frontend (Vite)
```

## Setup

### 1. Scraper

```bash
cd scraper
cp .env.example .env
# Edita .env con tus credenciales
pip install -r requirements.txt
python scraper.py
```

El scraper escribe el archivo `dashboard/public/data.json`.

### 2. Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Abre http://localhost:5173 para ver el dashboard.

## Producción

```bash
cd dashboard
npm run build
# Sirve la carpeta dist/ con cualquier hosting estático
npm run preview  # previsualización local del build
```

## Variables de entorno del scraper

| Variable | Descripción |
|---|---|
| `FIRECRAWL_API_KEY` | API key de Firecrawl (fc-...) |
| `UCAB_USERNAME` | Usuario/cédula del portal UCAB |
| `UCAB_PASSWORD` | Contraseña del portal UCAB |
