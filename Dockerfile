# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-slim AS frontend-build

WORKDIR /build/dashboard
COPY dashboard/package*.json ./
RUN npm ci
COPY dashboard/ ./
RUN npm run build


# ── Stage 2: Python backend + Playwright ──────────────────────────────────────
FROM python:3.11-slim

# System deps required by Playwright/Chromium
RUN apt-get update && apt-get install -y \
    wget curl gnupg \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 libcairo2 \
    fonts-liberation libappindicator3-1 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright's Chromium browser
RUN playwright install chromium

# Copy backend source
COPY backend/ .

# Copy compiled React frontend into dist/ (served as static files by FastAPI)
COPY --from=frontend-build /build/dashboard/dist ./dist

EXPOSE 8000

# Shell form so $PORT gets expanded by Railway
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
