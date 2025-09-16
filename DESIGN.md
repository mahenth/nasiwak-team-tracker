# 🏗️ Nasiwak Team Tracker – Design Document

## 📌 Overview
The **Team Tracker** is a Django + DRF + Channels based application that enables organizations to manage projects, issues, and team collaboration in real time.  

Key features:
- Multi-organization, multi-project structure.
- User authentication & membership system.
- RESTful APIs for managing organizations, projects, issues.
- WebSocket channels for **real-time issue updates & notifications**.
- Background task handling via **Celery + Redis**.
- PostgreSQL as the main database.

---

## 🛠️ Tech Stack

- **Backend Framework**: Django 4.x + Django REST Framework (DRF)  
- **Database**: PostgreSQL 15  
- **Cache/Queue**: Redis 7  
- **Task Queue**: Celery (worker + beat)  
- **Realtime**: Django Channels + Daphne (ASGI)  
- **Containerization**: Docker + Docker Compose  
- **API Docs**: drf-spectacular (OpenAPI/Swagger)  

---

## 📂 Project Structure

```
nasiwak-team-tracker/
├─ backend/
│  ├─ apps/
│  │  └─ tracker/
│  │     ├─ models.py        # DB models (Org, Project, Membership, Issue)
│  │     ├─ views.py         # DRF ViewSets
│  │     ├─ serializers.py   # DRF serializers
│  │     ├─ routing.py       # WebSocket routes
│  │     ├─ consumers.py     # Channels consumers
│  │     ├─ tasks.py         # Celery tasks
│  │     └─ urls.py
│  ├─ config/
│  │  ├─ settings.py         # Django + DRF + Channels config
│  │  ├─ urls.py             # API routes
│  │  └─ asgi.py             # Channels ASGI entry
│  ├─ docker-compose.yml
│  ├─ Dockerfile
│  └─ requirements.txt
├─ DESIGN.md
└─ .env.example
```

---

## 🗄️ Data Model

### Organization
- Represents a company or team.
- Fields: `id`, `name`, `created_at`.

### Project
- Belongs to an **Organization**.
- Fields: `id`, `name`, `description`, `organization`.

### Membership
- Links a **User** to an **Organization**.
- Fields: `id`, `user`, `organization`, `role`.

### Issue
- Represents a task or bug in a project.
- Fields: `id`, `title`, `description`, `status`, `project`, `created_by`, `assigned_to`.

---

## 🌐 REST API Design

Base path: `/api/v1/`

- `POST /organizations/` → Create organization  
- `GET /organizations/` → List organizations  
- `POST /projects/` → Create project under org  
- `GET /projects/` → List projects  
- `POST /issues/` → Create issue  
- `GET /issues/` → List issues  
- `PATCH /issues/{id}/` → Update issue  

Authentication:
- JWT / Token-based auth for API access.  
- Only members of an organization can manage its projects/issues.

---

## 🔌 WebSockets (Realtime)

Base path: `/ws/`

- `/ws/notifications/`  
  → Generic broadcast channel (system-wide notifications).  

- `/ws/projects/{project_id}/`  
  → Project-specific channel.  
  → Only users who are members of the project’s organization can connect.  
  → Events pushed:
  ```json
  { "type": "issue.created", "issue_id": 101, "title": "Fix login bug" }
  { "type": "issue.updated", "issue_id": 101, "title": "Fix login bug", "status": "in_progress" }
  ```

---

## ⚙️ Background Jobs

Celery (with Redis broker) handles:
- Sending notifications when issues are created/updated.
- Periodic cleanups (Celery Beat).
- Future integrations (emails, reports, etc.).

---

## 🚀 Deployment

- **Docker Compose** runs 5 services:  
  - `web` → Django app served via Gunicorn/Daphne.  
  - `db` → PostgreSQL database.  
  - `redis` → Redis broker (for Celery + Channels).  
  - `worker` → Celery worker.  
  - `beat` → Celery beat scheduler.  


