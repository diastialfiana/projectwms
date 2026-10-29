# Warehouse Management System (WMS)

A Django-based warehouse inventory and stock movement system for seafood processing and export operations.

## Features

- Product and warehouse master data management
- Inventory stock balances per product and warehouse
- Stock-in and stock-out transaction services with row locking
- Movement history and stock opname reconciliation
- Audit logging and permission-based access control
- Bootstrap-based dashboard and forms

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create a PostgreSQL database named `wms_db`.
4. Copy `.env.example` to `.env` and adjust values.
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Seed demo data:
   ```bash
   python manage.py seed_demo_data
   ```
8. Start the app:
   ```bash
   python manage.py runserver
   ```

## Environment variables

The project reads values from `.env` using `python-dotenv`.

Example values are in `.env.example`.

## Database configuration

Default configuration uses PostgreSQL. For rapid local validation, set `USE_SQLITE=1` in `.env` to fall back to SQLite.

## Running tests

```bash
python manage.py test
```

## Notes

- All stock changes must go through the service layer in `inventory/services.py`.
- Concurrency checks use `transaction.atomic()` and `select_for_update()`.
- The system separates stock movements, stock opname records, and audit logs.
