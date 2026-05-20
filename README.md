# Intelligent Content Aggregator & Recommendation Engine

An enterprise-ready, asynchronous full-stack content aggregator built with Python and Django. The platform runs a non-blocking ingestion data pipeline to crawl external RSS/API content feeds periodically and applies custom relational database aggregations to compute real-time, personalized reading recommendations for authenticated users.

## 🏗️ System Architecture & Data Flow

1. **Automation Layer**: `Celery Beat` wakes up every 5 minutes and pushes an asynchronous cron-execution token into `Redis`.
2. **Ingestion Pipeline**: A background `Celery Worker` picks up the token, polls external APIs asynchronously, handles content normalization, and safely handles data insertion.
3. **Storage Gatekeeper**: `PostgreSQL` enforces strict database-level idempotency via specialized SHA-256 URL hashing constraints to reject duplicate records and prevent write clutter.
4. **Algorithmic Engine**: Custom Django `ModelManagers` process user interaction weights (`VIEW`=1, `LIKE`=3, `BOOKMARK`=5) to compute algorithmic recommendations using SQL aggregate features (`Coalesce`, `Sum`).
5. **Caching & Delivery Layer**: Exposes an advanced, per-user dynamically cached `Django REST Framework` API endpoint backed by an in-memory `Redis Cache` to drop latency down to $O(1)$ response times under concurrent system stress.

---

## 🛠️ Tech Stack & Infrastructure

* **Backend Core**: Python 3.10, Django 4.2, Django REST Framework
* **Task Automation Queue**: Celery 5.3, Celery Beat
* **Message Broker & Cache**: Redis (Alpine distribution)
* **Primary Relational Store**: PostgreSQL 15
* **Frontend Layer**: Vanilla JS, HTML5, Tailwind CSS CDN
* **Containerization**: Docker, Docker Compose

---

## 🚀 One-Command Local Deployment

The absolute isolation of our multi-service ecosystem is completely managed using Docker. Follow these steps to clone and launch the entire enterprise microservice cluster:

### Prerequisites
Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine.

### Execution Instructions
1. Clone this repository to your local workspace.
2. Open your terminal inside the root project directory.
3. Run the master orchestration command:
   ```bash
   docker-compose up --build
