# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| 1.x     | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability within YA-WAMF, please adhere to the following:

1.  **Do NOT** open a public issue.
2.  Send an email to the project maintainers (insert email here or refer to profile).
3.  Include a detailed description of the vulnerability and steps to reproduce it.

We will acknowledge receipt of your report within 48 hours and strive to provide a fix as soon as possible.

### Common Concerns
*   **API Exposure:** Ensure your `docker-compose.yml` does not expose the backend port (8000) to the public internet without a reverse proxy (Nginx, Traefik) handling authentication.
*   **MQTT Auth:** We recommend using MQTT username/password authentication in production environments.
