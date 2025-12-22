# Migration Guide

If you are coming from the original `WhosAtMyFeeder` (v1), please note that **YA-WAMF (v2)** is a complete rewrite.

## Configuration Changes

*   **Format:** `config.yml` is deprecated. We now use a combination of Environment Variables (`.env`) for infrastructure and a web-based `config.json` for runtime settings.
*   **Frigate:** Instead of complex mapping, we simply ask for the Frigate URL. Camera names are automatically detected from the MQTT events.

## Database Migration

*   **Incompatible Schema:** The v1 database schema is not directly compatible with v2.
*   **Recommendation:** It is highly recommended to start with a fresh database (`speciesid.db`) to ensure the new "Leaderboard" and "Explorer" features work correctly with standardized species names.
*   **Legacy Data:** If you absolutely must keep your old data, you will need to manually export your v1 SQLite data and map it to the new `detections` table structure defined in `backend/app/repositories/detection_repository.py`.

## Docker Changes

*   **Service Name:** The main service is now split into `backend` and `frontend`.
*   **Ports:** The web interface is now served on port `3000` (or `80` inside the container) instead of the previous Flask default.
