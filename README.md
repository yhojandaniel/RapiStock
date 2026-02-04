# RapiStock 📦

![Version](https://img.shields.io/badge/version-0.1.1-blue)
![Python](https://img.shields.io/badge/Python-3.10.12-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED)

**RapiStock** is an API designed for efficient **inventory management** and **multi-store order processing**. Built with modern technologies like FastAPI and SQLModel, it provides a scalable backend solution for e-commerce or traditional commerce operations.

---

## ✨ Features

*   **📦 Inventory Management:** Complete CRUD operations for products (`/products`).
*   **🛍️ Order Processing:** Handle orders across multiple stores (`/orders`).
*   **🏪 Seller Management:** Manage seller profiles and details (`/sellers`).
*   **💸 Refund Handling:** Process and track refunds (`/refunds`).
*   **🩺 Health Checks:** Integrated database connection monitoring.
*   **🐳 Dockerized:** Fully containerized setup with PostgreSQL and PgAdmin included (You can avoid PgAdmin if you wanna deploy it on a server or PC with limited resources).

---

## 🛠️ Tech Stack

*   **Backend:** [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/)
*   **Database:** [PostgreSQL](https://www.postgresql.org/) (via [SQLModel](https://sqlmodel.tiangolo.com/))
*   **Migrations:** [Alembic](https://alembic.sqlalchemy.org/) (Coming soon)
*   **Containerization:** [Docker](https://www.docker.com/) & Docker Compose
*   **Admin Tool:** [PgAdmin 4](https://www.pgadmin.org/)

---

## 🚀 Getting Started

### Prerequisites

*   [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.
*   Git (to clone the repository).

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yhojandaniel/RapiStock.git
    cd Rapistock
    ```

2.  **Environment Setup:**
    Create a `.env` file in the root directory based on `.env.example`.
    
    ```bash
    cp .env.example .env
    ```
    
    Ensure your `.env` contains the following keys:
    ```ini
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=rapistock_db
    
    PGADMIN_DEFAULT_EMAIL=admin@admin.com
    PGADMIN_DEFAULT_PASSWORD=admin
    ```

3.  **Run with Docker Compose:**
    ```bash
    docker-compose up -d --build
    ```
    *   This will start the **PostgreSQL** database, **PgAdmin**, and the **FastAPI Backend**.

4.  **Access the Application:**
    *   **API Root:** [http://localhost:8000](http://localhost:8000)
    *   **API Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
    *   **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
    *   **PgAdmin:** [http://localhost:5050](http://localhost:5050)

---

## 📂 Project Structure

```bash
RapiStock/
├── backend/
│   ├── app/
│   │   ├── core/         # Config, Database, Security
│   │   ├── modules/      # Domain modules (Auth, Inventory, Orders, etc.)
│   │   ├── shared/       # Shared utilities and enums
│   │   └── main.py       # Application entry point
│   ├── migrations/       # Alembic migrations   (Coming soon)
│   ├── tests/            # Unit and integration tests
│   └── Dockerfile
├── frontend/             # Frontend application (Coming Soon)
├── docker-compose.yml    # Docker services configuration
└── README.md
```

## 🗺️ Roadmap

- [x] Core API implementation (Inventory, Orders, Sellers).
- [x] Docker integration.
- [ ] Authentication & Authorization (JWT).
- [ ] Frontend implementation (React/Next.js or whatever I'll learn in the path xd).
- [ ] CI/CD Pipelines.

---

## 🤝 About...

This is my first published project, but not the last. I tried to follow best practice and in the future I'll accept pull requests.