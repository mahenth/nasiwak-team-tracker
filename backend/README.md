# Nasiwak Team Tracker (backend)

This repo contains a Django + DRF backend with:
- Multi-tenant model via Organization & Membership
- RBAC via Membership.role (owner, manager, member)
- Project & Issue models
- File attachments for issues
- JWT auth (Simple JWT)
- Real-time notifications via Channels (Redis)
- Background tasks via Celery + Redis
- Docker Compose for local dev

## Quickstart (Docker)
1. Copy .env.example -> .env and edit if needed.
2. Build & start:
   docker-compose build
   docker-compose up -d
3. Run migrations & create superuser:
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
4. Visit API docs: http://localhost:8000/api/docs/
5. Obtain JWT token:
   POST http://localhost:8000/api/token/ with {"username":"...","password":"..."}
   Use returned access token in `Authorization: Bearer <token>`

## Running locally (without Docker)
1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. configure env variables (export or .env)
5. python manage.py migrate
6. python manage.py runserver

## WebSocket
Connect to: ws://localhost:8000/ws/projects/<project_id>/
Channels AuthMiddlewareStack expects session authentication by default. For JWT via query param, implement a small middleware (left as an exercise).

## Celery
Start worker:
  celery -A config.celery_app worker -l info
Start beat:
  celery -A config.celery_app beat -l info

A sample task `send_overdue_reminders` is available in `apps/tracker/tasks.py`.

## Tests
Run:
  docker-compose exec web python manage.py test
or
  pytest

