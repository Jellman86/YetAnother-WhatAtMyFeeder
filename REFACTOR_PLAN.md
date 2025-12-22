# WhosAtMyFeeder Refactor Plan

## 1. Goal
Modernize "WhosAtMyFeeder" to a robust, observable, and maintainable state using Python 3.12, FastAPI, and Svelte 5, achieving feature parity with BirdNET-Go's UI.

## 2. Current State Inventory
- **Backend:** Python FastAPI (started refactor).
    - `main.py`: Entry point, lifespan management.
    - `services/`: MQTT, Classifier (TFLite), EventProcessor, Broadcaster.
    - `repositories/`: DetectionRepository (SQLite).
    - `config.py`: Pydantic settings.
- **Frontend:** Svelte (scaffolded in `apps/ui`).
- **Infrastructure:** `docker-compose.yml`, `backend/Dockerfile` (Multi-stage Python 3.12).

## 3. Target Architecture
- **API Gateway:** FastAPI at `/api` handling requests and SSE at `/api/events/stream`.
- **Event Bus:** MQTT listener -> EventProcessor -> Database & Broadcaster -> SSE.
- **Data Layer:** SQLite with `aiosqlite` repository pattern.
- **Frontend:** Svelte 5 SPA consuming API and SSE.
- **Observability:** `/metrics` (Prometheus), structured logs (structlog), `/health`.

## 4. Refactor Roadmap

### Phase 1: Backend Core & API (Current Focus)
- [x] Structure Project & Docker (Done)
- [x] Database Repository Pattern (Done)
- [ ] **Task 1:** Implement `events` router (pagination, filtering).
- [ ] **Task 2:** Implement `stream` router (SSE for real-time updates).
- [ ] **Task 3:** Implement `species` router (Leaderboard/Stats).
- [ ] **Task 4:** Refine `proxy` router (Frigate media access).
- [ ] **Task 5:** Add Prometheus metrics middleware.

### Phase 2: Frontend Implementation (Svelte 5)
- [ ] **Task 6:** Set up API client & Stores.
- [ ] **Task 7:** Implement Dashboard (Real-time feed).
- [ ] **Task 8:** Implement Events Explorer (History).
- [ ] **Task 9:** Implement Species Leaderboard.
- [ ] **Task 10:** Implement Settings & About.

### Phase 3: Ops & Finalization
- [ ] **Task 11:** Harden Docker Compose (Healthchecks, Limits).
- [ ] **Task 12:** Documentation (Migration guide, Readme).
- [ ] **Task 13:** CI/CD Workflows.

## 5. Rollback Strategy
- Git is the primary safety net.
- `docker-compose.yml` changes should be tested locally `docker compose up --build`.
- Database schema is simple; if major changes occur, provide a migration script or clear instructions (currently using `init_db` on startup).
