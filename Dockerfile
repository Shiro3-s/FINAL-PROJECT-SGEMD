# Imagen del backend standalone: compila `src/` (incluyendo `src/shared/`) y ejecuta `dist/server.js`.
# Incluye el cliente de PostgreSQL 17 (pg_dump) y rsync para el job de respaldos (D22).
# El contexto de build es la raíz de la rama `backend` (`/`).

FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY tsconfig.json ./
COPY src ./src
RUN npm run build \
    && npm prune --omit=dev

FROM node:22-alpine AS runtime
WORKDIR /app

# tzdata: la aplicación muestra America/Bogota. rsync: instantáneas de respaldo.
# postgresql17-client: pg_dump de la MISMA versión mayor que el servidor (17).
RUN apk add --no-cache tzdata rsync postgresql17-client \
    && cp /usr/share/zoneinfo/America/Bogota /etc/localtime \
    && echo "America/Bogota" > /etc/timezone

ENV NODE_ENV=production

COPY package.json package-lock.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist

RUN mkdir -p /app/storage /app/backups \
    && chown -R node:node /app/storage /app/backups

USER node

EXPOSE 3000

CMD ["node", "dist/server.js"]
