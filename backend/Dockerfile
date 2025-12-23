# Python'un hafif ve güvenli bir versiyonunu kullanıyoruz
FROM python:3.12-slim

# Gereksiz çıktı ve bytecode üretimini engelliyoruz
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Çalışma dizinini /app olarak belirle
WORKDIR /app

# Önce sadece requirements.txt'yi kopyala ve paketleri kur (cache avantajı için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını kopyala
COPY . .

# Static dosyaları production için topla (gerekirse)
# RUN python manage.py collectstatic --noinput

# 8000 portunu dışarı aç
EXPOSE 8000

# Gunicorn ile production-ready sunucu başlat
CMD ["gunicorn", "main.wsgi:application", "--bind", "0.0.0.0:8000"]