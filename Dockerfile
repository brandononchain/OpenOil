FROM python:3.11-slim

WORKDIR /app

# System deps if needed (none critical for this)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway uses PORT env
ENV PORT=8000
EXPOSE 8000

CMD ["python", "oil_super_intelligence.py"]
