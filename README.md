# Yet Another WhosAtMyFeeder (YA-WAMF) 🐦

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Svelte](https://img.shields.io/badge/svelte-5.0-orange.svg)
![Docker](https://img.shields.io/badge/docker-compose-green.svg)

**YA-WAMF** is a modern, real-time bird classification system designed to work alongside [Frigate NVR](https://frigate.video/). It listens for "bird" detection events, fetches high-quality snapshots, classifies the species using TensorFlow Lite, and displays the results in a beautiful, reactive dashboard.

Inspired by the UI/UX of [BirdNET-Go](https://github.com/t飕t/birdnet-go), this project aims to provide a robust and visually appealing way to catalog your backyard visitors.

---

## ✨ Features

*   **Real-time Dashboard:** Live updates of bird detections via Server-Sent Events (SSE). No page refreshes needed.
*   **Frigate Integration:** Seamlessly fetches snapshots and clips from your existing Frigate instance.
*   **Species Classification:** Uses TFLite models to identify bird species with configurable confidence thresholds.
*   **Leaderboard:** Track which species visit most frequently.
*   **Events Explorer:** Browse historical detections with filtering and date ranges.
*   **Modern Stack:** Built with Python 3.12 (FastAPI) and Svelte 5 (Vite + Tailwind CSS).
*   **Docker First:** Easy deployment with Docker Compose.

## 🚀 Quick Start

### Prerequisites
*   Docker & Docker Compose
*   A running instance of [Frigate](https://frigate.video/) with MQTT enabled.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/YA-WAMF.git
    cd YA-WAMF
    ```

2.  **Configure environment:**
    Copy the example environment file (or just create a .env):
    ```bash
    cp .env.example .env
    ```
    *Note: If no example exists, create one with:*
    ```env
    FRIGATE_URL=http://your-frigate-ip:5000
    MQTT_SERVER=your-mqtt-broker-ip
    ```

3.  **Run with Docker Compose:**
    ```bash
    docker compose up -d
    ```

4.  **Access the Dashboard:**
    Open `http://localhost:3000` in your browser.

## ⚙️ Configuration

You can configure YA-WAMF via the Web UI (Settings page) or by editing `config.json` directly.

| Setting | Description | Default |
|---------|-------------|---------|
| `frigate_url` | URL to your Frigate NVR | `http://localhost:5000` |
| `mqtt_server` | MQTT Broker address | `mqtt` |
| `classification_threshold` | Minimum confidence to save a detection | `0.7` |

## 🏗️ Architecture

*   **Backend:** Python 3.12, FastAPI, SQLite (aiosqlite), Pydantic. Handles MQTT ingestion, image processing, and API requests.
*   **Frontend:** Svelte 5, Tailwind CSS, Vite. A Single Page Application (SPA) served via Nginx.
*   **Data:** SQLite database stored in `/data/speciesid.db`.

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 🛡️ License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 🙏 Acknowledgements

*   Original [WhosAtMyFeeder](https://github.com/simonmaggio/WhosAtMyFeeder) project.
*   [BirdNET-Go](https://github.com/t飕t/birdnet-go) for UI inspiration.
*   [Frigate](https://frigate.video/) for the amazing NVR platform.
