# Claude Code Review & Refactoring Instructions

This document provides instructions for Claude to systematically review and refactor the YA-WAMF (Yet Another WhosAtMyFeeder) codebase.

## Project Overview

- **Purpose**: Real-time bird detection and species classification system integrated with Frigate NVR
- **Backend**: Python 3.12 + FastAPI + SQLite + TensorFlow Lite
- **Frontend**: Svelte 5 + TypeScript + Tailwind CSS + Vite
- **Infrastructure**: Docker Compose with Nginx reverse proxy

---

## Review Checklist

### 1. Backend Code Review (`/backend/app/`)

#### 1.1 Main Application (`main.py`)
- [ ] Check CORS configuration - is wildcard origin safe for production?
- [ ] Verify lifespan management handles all startup/shutdown properly
- [ ] Review exception handling in main app setup
- [ ] Check if health endpoint returns appropriate status codes

#### 1.2 Configuration (`config.py`)
- [ ] Verify all environment variable mappings are correct
- [ ] Check for hardcoded values that should be configurable
- [ ] Ensure sensitive defaults are not exposed
- [ ] Validate configuration validation logic

#### 1.3 Database Layer (`database.py`)
- [ ] Review SQL schema for missing indexes (detection_time, camera_name, display_name)
- [ ] Check for SQL injection vulnerabilities
- [ ] Verify async operations are properly awaited
- [ ] Check connection pool management
- [ ] Review error handling for database operations

#### 1.4 Models (`models.py`)
- [ ] Verify Pydantic model validators
- [ ] Check for proper Optional type annotations
- [ ] Review datetime handling consistency
- [ ] Ensure model serialization works correctly

#### 1.5 Services (`/services/`)

**mqtt_service.py**
- [ ] Check error handling for connection failures
- [ ] Verify reconnection logic handles edge cases
- [ ] Review message parsing for malformed JSON
- [ ] Check for proper resource cleanup on shutdown

**classifier_service.py**
- [ ] Verify image preprocessing is correct for the model
- [ ] Check memory management for large images
- [ ] Review error handling when model is missing
- [ ] Validate normalization logic for different input types
- [ ] Check thread safety if used concurrently

**event_processor.py**
- [ ] Review the filtering logic for camera names
- [ ] Check HTTP timeout settings for Frigate requests
- [ ] Verify error handling when Frigate is unavailable
- [ ] Review detection update vs create logic
- [ ] Check for race conditions in concurrent processing

**broadcaster.py**
- [ ] Verify queue cleanup when clients disconnect
- [ ] Check for memory leaks with long-running connections
- [ ] Review thread/async safety of queue management

#### 1.6 Repositories (`/repositories/`)

**detection_repository.py**
- [ ] Review all SQL queries for correctness
- [ ] Check datetime parsing handles all formats
- [ ] Verify pagination implementation
- [ ] Look for N+1 query issues
- [ ] Check error handling and rollback logic

#### 1.7 Routers (`/routers/`)

**events.py**
- [ ] Validate query parameter handling (limit, offset)
- [ ] Check response model consistency
- [ ] Review error responses

**stream.py**
- [ ] Verify SSE format is correct
- [ ] Check for proper client cleanup on disconnect
- [ ] Review timeout handling

**proxy.py**
- [ ] Check for SSRF vulnerabilities in proxy logic
- [ ] Verify proper error handling for Frigate failures
- [ ] Review content-type handling
- [ ] Check for path traversal issues

**settings.py**
- [ ] Verify config persistence works correctly
- [ ] Check for validation of incoming settings
- [ ] Review file write error handling

**species.py**
- [ ] Verify aggregation query is correct
- [ ] Check response format

### 2. Frontend Code Review (`/apps/ui/src/`)

#### 2.1 Main App (`App.svelte`)
- [ ] Review client-side routing implementation
- [ ] Check SSE reconnection logic for edge cases
- [ ] Verify reactive state management
- [ ] Review error handling for failed API calls
- [ ] Check for memory leaks with SSE connections
- [ ] Verify proper cleanup on component unmount

#### 2.2 Components (`/lib/components/`)

**DetectionCard.svelte**
- [ ] Check accessibility (ARIA labels, keyboard navigation)
- [ ] Review image loading and error states
- [ ] Verify responsive design
- [ ] Check for XSS vulnerabilities in displayed data

**Events.svelte, Species.svelte, Settings.svelte**
- [ ] These appear to be stubs - verify if complete implementation is needed
- [ ] Check for proper API integration
- [ ] Review form validation in Settings

#### 2.3 API Client (`api.ts`)
- [ ] Verify type definitions match backend models
- [ ] Check error handling for API calls
- [ ] Review base URL configuration

### 3. Infrastructure Review

#### 3.1 Docker Configuration

**docker-compose.yml**
- [ ] Review port mappings for conflicts
- [ ] Check volume mounts are correct
- [ ] Verify network configuration
- [ ] Review health check configurations
- [ ] Check environment variable handling

**backend/Dockerfile**
- [ ] Review multi-stage build efficiency
- [ ] Check for security best practices (non-root user, etc.)
- [ ] Verify Python version and dependencies

**apps/ui/Dockerfile**
- [ ] Review build optimization
- [ ] Check nginx configuration
- [ ] Verify static file handling

#### 3.2 Nginx Configuration (`nginx.conf`)
- [ ] Review proxy configuration
- [ ] Check caching headers
- [ ] Verify security headers

### 4. Testing Review (`/backend/tests/`)
- [ ] Check test coverage for critical paths
- [ ] Verify mock implementations are correct
- [ ] Review async test patterns
- [ ] Check for missing edge case tests

---

## Common Issues to Look For

### Security Issues
1. SQL injection in raw queries
2. XSS in frontend rendering
3. SSRF in proxy endpoints
4. Sensitive data in logs
5. Hardcoded credentials or secrets
6. Missing input validation
7. Improper CORS configuration

### Performance Issues
1. Missing database indexes
2. N+1 query patterns
3. Unbounded memory growth
4. Missing pagination limits
5. Large payload responses
6. Inefficient image processing

### Code Quality Issues
1. Inconsistent error handling patterns
2. Missing type annotations
3. Dead code or unused imports
4. Duplicate logic that should be abstracted
5. Missing docstrings for complex functions
6. Inconsistent naming conventions

### Async/Concurrency Issues
1. Missing await keywords
2. Race conditions in shared state
3. Improper resource cleanup
4. Blocking calls in async context

### Robustness Issues
1. Missing retry logic for external services
2. Insufficient timeout handling
3. Poor graceful degradation
4. Missing health/readiness checks

---

## Refactoring Priority Order

1. **Critical Security Fixes** - Address any security vulnerabilities immediately
2. **Data Integrity Issues** - Fix database and data handling problems
3. **Error Handling** - Ensure robust error handling throughout
4. **Performance Bottlenecks** - Optimize slow paths
5. **Code Quality** - Clean up code organization and patterns
6. **Testing Gaps** - Add missing test coverage

---

## Files to Review (In Order)

### Backend (High Priority)
1. `/backend/app/services/event_processor.py` - Core business logic
2. `/backend/app/routers/proxy.py` - Security-sensitive proxy
3. `/backend/app/database.py` - Data layer foundation
4. `/backend/app/repositories/detection_repository.py` - Data access
5. `/backend/app/services/classifier_service.py` - ML inference
6. `/backend/app/services/mqtt_service.py` - External integration
7. `/backend/app/config.py` - Configuration handling
8. `/backend/app/main.py` - App setup
9. `/backend/app/models.py` - Data models
10. `/backend/app/routers/events.py` - API endpoint
11. `/backend/app/routers/stream.py` - SSE endpoint
12. `/backend/app/routers/settings.py` - Config endpoint
13. `/backend/app/routers/species.py` - Stats endpoint
14. `/backend/app/services/broadcaster.py` - Real-time messaging

### Frontend (Medium Priority)
1. `/apps/ui/src/App.svelte` - Main application
2. `/apps/ui/src/lib/api.ts` - API types
3. `/apps/ui/src/lib/components/DetectionCard.svelte` - Card component
4. `/apps/ui/src/lib/components/Settings.svelte` - Settings UI
5. `/apps/ui/src/lib/components/Events.svelte` - Events browser
6. `/apps/ui/src/lib/components/Species.svelte` - Leaderboard

### Infrastructure (Lower Priority)
1. `/docker-compose.yml` - Container orchestration
2. `/backend/Dockerfile` - Backend container
3. `/apps/ui/Dockerfile` - Frontend container
4. `/apps/ui/nginx.conf` - Web server config

### Tests
1. `/backend/tests/` - All test files

---

## How to Use This Document

1. Read each file listed above using the Read tool
2. Compare against the checklist items
3. Document any issues found
4. Create a todo list of fixes needed
5. Implement fixes one at a time
6. Run tests after each change
7. Mark checklist items complete as verified

---

## Notes

- Do not over-engineer or add unnecessary abstractions
- Only fix actual problems, not stylistic preferences
- Preserve existing behavior unless fixing bugs
- Test changes before considering complete
- Document significant changes made
