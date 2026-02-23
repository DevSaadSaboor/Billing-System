# Billing & Invoicing Backend API

A production-grade REST API built with Django REST Framework that manages the complete invoicing lifecycle — from draft creation to secure payment settlement — with strict business rules enforced at both the application and database layers.
Designed as a multi-user billing system where financial correctness, data integrity, and safe concurrent writes are critical.

**Stack:** Python · Django · Django REST Framework · PostgreSQL · Token Auth · django-filter · drf-spectacular

---

## What This Demonstrates

| Area | Implementation |
|------|----------------|
| **Auth & Security** | Token authentication, per-user data isolation at queryset level |
| **Business Logic** | Enforced invoice lifecycle · immutable paid invoices · no manual paid transitions |
| **Financial Safety** | `transaction.atomic` + `select_for_update` — concurrency-safe payment writes |
| **Data Integrity** | DB-level unique constraint on invoice number per user (not serializer-only) |
| **Performance** | Single-query bulk overdue detection · DB aggregation for reporting |
| **API Design** | Nested serializers · dedicated `/send/` action · centralized `InvoiceFilterSet` |
| **Testing** | Business rule enforcement validated by automated tests |

---

## Invoice Lifecycle

```
draft → sent → paid
          ↓
       overdue
```

Only draft invoices can be sent. Paid invoices are immutable. Status cannot be manually set to `paid` — it transitions automatically when the balance reaches zero. Overdue detection runs as a single bulk `UPDATE`, not a per-object loop.

---

## Key Features

- Invoice creation with nested line items; subtotal, tax, and grand total auto-calculated on save
- Partial payments with overpayment prevention and live remaining balance tracking
- Invoice summary endpoint returning counts and revenue metrics aggregated at the DB level
- Filtering by status, customer, and date range; pagination and ordering on all list views

---

## API Endpoints

```
POST   /api/login/                   Obtain token

GET    /api/customers/               List customers
POST   /api/customers/               Create customer

GET    /api/invoices/                List & filter invoices
POST   /api/invoices/                Create invoice with line items
GET    /api/invoices/<id>/           Invoice detail
POST   /api/invoices/<id>/send/      Transition draft → sent
GET    /api/invoices/summary/        Aggregate revenue and status counts

GET    /api/payments/                List payments
POST   /api/payments/                Submit payment

GET    /api/docs/                    Swagger UI
```

---

## Run Locally

```bash
git clone https://github.com/your-username/billing-backend.git
cd billing-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate && python manage.py runserver
```

Swagger UI → `http://127.0.0.1:8000/api/docs/`

---

## Run Tests

```bash
python manage.py test
```

Covers: paid invoice immutability · overpayment rejection · concurrency safety · per-user isolation · lifecycle transitions · duplicate invoice prevention

---

## Architecture Overview

The system is separated into domain-focused Django apps:

| App | Responsibility |
|-----|---------------|
| `users` | Authentication and identity |
| `customers` | Client records scoped per user |
| `invoices` | Invoice lifecycle and line items |
| `payments` | Financial transactions and validation |

Business rules are enforced at the model layer, while filtering and query logic are centralized using a dedicated `InvoiceFilterSet`.

---

## Engineering Focus

This project emphasizes:

- **State-driven business logic** — rules live in models, not views
- **Database-enforced integrity** — constraints at the DB level, not serializer-only validation
- **Concurrency safety** — row-level locking for financial operations
- **Scalable query patterns** — aggregation and bulk updates over Python loops
- **Test coverage that protects domain rules** during refactoring

---

## Why This Project Matters

This is not a CRUD scaffold. It reflects backend engineering thinking — enforcing financial correctness, preventing race conditions, maintaining integrity at the DB layer, and writing tests that protect business rules through refactoring.