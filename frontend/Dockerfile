# 1. Build aşaması (React uygulamasını derle)
FROM node:18-alpine as build

WORKDIR /app

# Paket dosyalarını kopyala ve bağımlılıkları kur
COPY package*.json ./
RUN npm install

# Tüm kaynak kodunu kopyala
COPY . .

# Production build oluştur
RUN npm run build

# 2. Servis aşaması (nginx ile static dosyaları sun)
FROM nginx:alpine

# Build aşamasından çıkan dosyaları nginx'in servis klasörüne kopyala
COPY --from=build /app/build /usr/share/nginx/html

# Nginx'in default config'ini override et (isteğe bağlı, gerekirse)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]