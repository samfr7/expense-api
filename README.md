# Expense API

A robust personal expense tracking API built with Flask, PostgreSQL (via SQLAlchemy), and Redis caching. It features a complete JWT authentication flow with short-lived access tokens and securable refresh token rotation.

**Project URL** : https://roadmap.sh/projects/expense-tracker-api

## 🚀 Features

*   **JWT Auth:** PyJWT for Access Tokens, urlsafe strings for Refresh Tokens (with rotation/revocation logic).
*   **Transactions/Expenses:** Full CRUD on user-scoped expenses, with advanced querying (duration, categories, pagination, keyword search).
*   **Users/Budgets:** Dedicated profile endpoints; setting a `monthly_budget` synchronizes to a Redis cache for rapid analytics reads.
*   **Analytics:** A synthesized dashboard endpoint combining PostgreSQL spend aggregations and Redis budget caching.
*   **Testing:** Comprehensive `pytest` suite across unit and integration levels. Uses `TestingConfig` with an in-memory SQLite database, enabling isolated and offline testing.
*   **CI/CD:** Preconfigured GitHub Actions testing pipeline running automatically on pushes and pull requests.

## 🛠 Prerequisites

*   Python 3.11+
*   PostgreSQL 14+
*   Redis Server 6+

## ⚙️ Setup & Configuration

1.  **Clone the Repository** and navigate inside.
2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Variables:**
    *   Copy `.env.example` to `.env`
    *   Update values like `DATABASE_URL` (your Postgres credentials), `SECRET_KEY`, and `REDIS_URL`.

## 📦 Database Initialization

Before starting the server, apply the SQLAlchemy schemas via Flask-Migrate:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🚀 Running the API

Start the local development server:

```bash
python run.py
# or
flask run
```

By default it runs on `http://127.0.0.1:5000`.

## 🧪 Running Tests

The test suite runs against a `TestingConfig` which uses **SQLite in-memory** and **mocks Redis**, meaning you can run tests anywhere without external services running.

```bash
pytest tests/ -v
```

## 📚 API Endpoints Overview

| Area | Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | POST | `/auth/register` | Create account | No |
| | POST | `/auth/login` | Receive Access & Refresh Tokens | No |
| | POST | `/auth/refresh-token` | Rotate tokens using refresh_token | No |
| | POST | `/auth/logout` | Revoke a refresh token | No |
| **Expenses**| GET | `/expenses` | List with filters & pagination | Yes |
| | POST | `/expense` | Create new expense | Yes |
| | GET/PUT/DELETE | `/expense/<id>` | Detail operations | Yes |
| **Users** | GET/PUT | `/users/<id>` | Profile ops. Triggers Redis sync. | Yes |
| **Analytics**| GET | `/analytics/<id>`| Aggregates DB spend + Redis budget | Yes |

Every protected route requires the `Authorization` header formatted as:
`Bearer <your_access_token>`
