FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ถ้าอนาคตเลือกใช้ psycopg2 (ไม่ใช่ binary) ควรมีบรรทัดด้านล่างนี้
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ติดตั้งไลบรารี
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# คัดลอกซอร์สโค้ด
COPY . .

EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
