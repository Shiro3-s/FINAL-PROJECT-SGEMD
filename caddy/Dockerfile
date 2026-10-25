# Imagen de Caddy: compila la SPA y la sirve junto al proxy /api.
# El contexto de build es la raíz del repositorio.

FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
COPY shared/package.json shared/
COPY frontend/package.json frontend/
RUN npm ci --workspace shared --workspace frontend --include-workspace-root

COPY tsconfig.base.json ./
COPY shared shared
COPY frontend frontend
RUN npm run build -w shared && npm run build -w frontend

FROM caddy:2.10.0-alpine

ARG PROXY_MAX_BODY_MB=500
ENV PROXY_MAX_BODY_MB=${PROXY_MAX_BODY_MB}

COPY --from=build /app/frontend/dist /srv
COPY caddy/Caddyfile /etc/caddy/Caddyfile

EXPOSE 80 443
