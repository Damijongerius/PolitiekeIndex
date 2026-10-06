# ==========================================
# Stage 1: Build the modern React frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci || npm install

COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Production Python FastAPI runner
# ==========================================
FROM python:3.12-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install minimal system tools (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python modules & backend service
COPY backend/ ./backend/
COPY database.py .
COPY pdf_parser.py .
COPY analyzer.py .
COPY statement_evaluator.py .
COPY cover_extractor.py .
COPY run.py .

# Copy data (PDFs, covers, ChromaDB vector store)
COPY data/ ./data/

# Copy compiled React SPA from frontend-builder
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Launch the FastAPI server hosting both API and React frontend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
