# SGEMD — atajos de operación
# Uso: make env && make up

SHELL := /bin/bash

.PHONY: help env up down reset-db logs ps typecheck test build check seed

help:
	@echo "make env        copia .env.example a .env y genera secretos locales"
	@echo "make up         levanta la pila (caddy, backend, postgres)"
	@echo "make down       detiene la pila"
	@echo "make reset-db   borra el volumen de PostgreSQL y reinicializa"
	@echo "make check      comprueba /api/health a través de Caddy"
	@echo "make typecheck  typecheck de los tres workspaces"
	@echo "make test       pruebas del backend"
	@echo "make build      compila shared, backend y frontend"

env:
	@if [ -f .env ]; then echo ".env ya existe; no se sobrescribe"; else \
		cp .env.example .env; \
		JWT=$$(openssl rand -hex 32); OTP=$$(openssl rand -hex 32); \
		sed -i "s|^JWT_SECRET=.*|JWT_SECRET=$$JWT|" .env; \
		sed -i "s|^OTP_HMAC_SECRET=.*|OTP_HMAC_SECRET=$$OTP|" .env; \
		PWD_DB=$$(openssl rand -hex 12); \
		sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$$PWD_DB|" .env; \
		sed -i "s|^DATABASE_URL=.*|DATABASE_URL=postgres://sgemd:$$PWD_DB@postgres:5432/sgemd|" .env; \
		echo ".env creado con secretos locales"; fi

up: env
	docker compose up -d --build

down:
	docker compose down

reset-db:
	docker compose down -v
	docker compose up -d --build

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps

check:
	@curl -sk --fail https://localhost/api/health && echo "" || \
		(echo "healthcheck falló: revisa 'make logs' y la CA interna de Caddy"; exit 1)

typecheck:
	npm run typecheck

test:
	npm run test

build:
	npm run build
