# 1. Build aşaması (React uygulamasını derle)
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 2. Servis aşaması (nginx ile static dosyaları sun)
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
# Nginx config'ini override et (eğer buraya koymak istersen, ama docker-compose'da mount etmek daha iyi)
# COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]