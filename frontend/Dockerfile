# Многоступенчатая сборка.
#
# Ступень 1 (builder): ставим зависимости и собираем React в статику.
# Ступень 2: чистый nginx, в который кладём только результат сборки.
# Node и node_modules в финальный образ не попадают, поэтому он весит
# десятки мегабайт вместо сотен.

FROM node:22-alpine AS builder

WORKDIR /app

# Сначала только манифесты: если они не менялись, Docker переиспользует
# закэшированный слой с npm ci и не будет качать пакеты заново.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite сам подхватит .env.production, где VITE_API_URL пустой.
# Значение подставляется в код на этапе сборки, а не при запуске контейнера.
RUN npm run build

# --- Финальный образ: самостоятельный сервис со статикой ---
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
