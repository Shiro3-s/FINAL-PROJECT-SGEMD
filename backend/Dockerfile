# Imagen del backend: compila `shared` y `backend`, y ejecuta el JavaScript emitido.
# Incluye el cliente de PostgreSQL 17 (pg_dump) y rsync para el job de respaldos (D22).
# El contexto de build es la raíz del repositorio.

FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
COPY shared/package.json shared/
COPY backend/package.json backend/
RUN npm ci --workspace shared --workspace backend --include-workspace-root

COPY tsconfig.base.json ./
COPY shared shared
COPY backend backend
RUN npm run build -w shared && npm run build -w backend

FROM node:22-alpine AS runtime
WORKDIR /app

# tzdata: la aplicación muestra America/Bogota. rsync: instantáneas de respaldo.
# postgresql-client: pg_dump de la misma versión mayor que el servidor (17).
RUN apk add --no-cache tzdata rsync postgresql-client \
    && cp /usr/share/zoneinfo/America/Bogota /etc/localtime \
    && echo "America/Bogota" > /etc/timezone

ENV NODE_ENV=production

COPY package.json package-lock.json ./
COPY shared/package.json shared/
COPY backend/package.json backend/
RUN npm ci --omit=dev --workspace shared --workspace backend --include-workspace-root \
    && npm cache clean --force

COPY --from=build /app/shared/dist shared/dist
COPY --from=build /app/backend/dist backend/dist

RUN mkdir -p /app/storage /app/backups \
    && chown -R node:node /app/storage /app/backups

USER node

EXPOSE 3000

CMD ["node", "backend/dist/server.js"]
