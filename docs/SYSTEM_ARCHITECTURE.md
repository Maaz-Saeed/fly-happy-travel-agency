# System Architecture

## 1. Architectural Style
The system follows a classic **server-rendered MVC-flavored monolith**:
- **Model** — SQLAlchemy models (`app/models.py`)
- **View** — Jinja2 templates (`app/templates/**`)
- **Controller** — Flask blueprints (`app/routes/*.py`)

This is deliberately simple and dependency-light (no separate frontend build step, no external services) so the whole system can be installed and demonstrated on a single machine.

## 2. High-Level Diagram

```
                         ┌─────────────────────────────┐
                         │        Web Browser          │
                         │  (Bootstrap 5, AOS, Chart.js,│
                         │   Font Awesome, vanilla JS)  │
                         └──────────────┬───────────────┘
                                        │ HTTP(S)
                         ┌──────────────▼───────────────┐
                         │        Flask Application     │
                         │  ┌─────────────────────────┐  │
                         │  │  Blueprints (Controllers)│ │
                         │  │  public / auth / booking │ │
                         │  │  payment / customer /    │ │
                         │  │  admin / chatbot          │ │
                         │  └─────────────┬─────────────┘  │
                         │  ┌─────────────▼─────────────┐  │
                         │  │  Forms (Flask-WTF)         │  │
                         │  │  CSRF + validation         │  │
                         │  └─────────────┬─────────────┘  │
                         │  ┌─────────────▼─────────────┐  │
                         │  │  Models (SQLAlchemy ORM)   │  │
                         │  └─────────────┬─────────────┘  │
                         └────────────────┼─────────────────┘
                                          │
                                ┌─────────▼─────────┐
                                │   SQLite Database  │
                                │ instance/flyhappy.db│
                                └────────────────────┘
```

## 3. Application Factory Pattern
`app/__init__.py` exposes `create_app()`, which:
1. Loads configuration from `config.py` (`DevelopmentConfig`/`ProductionConfig`).
2. Initializes extensions: `SQLAlchemy`, `LoginManager`, `CSRFProtect`.
3. Registers all blueprints.
4. Registers a Jinja context processor that injects company info (name, license, contact details) into every template.
5. Registers 404/403/500 error handlers.
6. Exposes a `flask init-db` CLI command that drops, recreates, and seeds the schema.

This pattern avoids circular imports (extensions live in `app/extensions.py` and are imported by both `app/__init__.py` and `app/models.py`) and allows multiple app configurations (e.g. testing) in future.

## 4. Blueprint Responsibilities
| Blueprint | URL Prefix | Responsibility |
|---|---|---|
| `public` | `/` | Marketing site: home, about, services, destinations, airlines, packages, hotels, gallery, team, portfolio, news, FAQ, testimonials, contact |
| `auth` | `/auth` | Register, login, logout |
| `booking` | `/booking` | Destination search, booking form, price calculation, confirmation |
| `payment` | `/payment` | Checkout, receipt, invoice |
| `customer` | `/dashboard` | Customer self-service (bookings, payments, profile, password, support) |
| `admin` | `/admin` | Full back-office CRUD, dashboard analytics, reports |
| `chatbot` | `/chatbot` | JSON API for the chat widget, logs every exchange |

## 5. Security Architecture
- **Authentication:** Flask-Login manages the session; `User.check_password` verifies a Werkzeug PBKDF2-SHA256 hash.
- **Authorization:** `admin_required` decorator (`app/utils.py`) + a blueprint-level `before_request` guard enforce that only `role == "admin"` users reach `/admin/*`; customer routes require `@login_required` and enforce booking/payment ownership checks (`booking.customer_id == current_user.id`).
- **CSRF:** `Flask-WTF`'s `CSRFProtect` is applied globally; every state-changing form (WTForms-rendered or plain HTML) includes a CSRF token. The chatbot JSON API is explicitly exempted since it carries no session-mutating side effects beyond logging.
- **Input Validation:** WTForms validators (`DataRequired`, `Email`, `Length`, `NumberRange`, `EqualTo`) validate all user-facing forms server-side.
- **SQL Injection:** All queries go through the SQLAlchemy ORM query builder — no raw string-interpolated SQL anywhere in the codebase.
- **Session Hardening:** `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE=Lax`, bounded `PERMANENT_SESSION_LIFETIME`.

## 6. Front-End Architecture
- **Templates:** `base.html` (public) and `admin/_base.html` (back office) define the shared shell; every page extends one of these and overrides `content`/`extra_js` blocks.
- **Styling:** `static/css/style.css` (site-wide green & white theme) + `static/css/admin.css` (sidebar/topbar admin layout) — both hand-written, no CSS framework rebuild step required beyond the Bootstrap 5 CDN import.
- **Interactivity:** `static/js/main.js` (loading screen, AOS init, navbar scroll shadow, animated counters, live price estimator, print buttons) and `static/js/chatbot.js` (chat widget fetch logic).
- **Charts:** Chart.js is loaded only on the admin dashboard and driven by data serialized from the Flask view via `tojson`.

## 7. Data Flow Example — Booking → Payment
1. `GET /booking/new/<destination_id>` renders the booking form pre-filled from the logged-in user's profile.
2. `POST /booking/new/<destination_id>` validates via `BookingForm`, computes `total_price` server-side (`calculate_price`), generates a unique `booking_id`/`ticket_number`, persists the `Booking`, and redirects to `/payment/checkout/<booking_id>`.
3. `POST /payment/checkout/<booking_id>` validates via `PaymentForm`, creates a `Payment` row, flips `Booking.status` to `confirmed` (or leaves `pending` for Cash), and redirects to the receipt page.
4. The invoice page (`/payment/invoice/<booking_id>`) aggregates the booking plus all its payment attempts for a full printable record.

## 8. Deployment Topology (Recommended for Production)
```
Client → Reverse Proxy (nginx) → WSGI Server (Gunicorn/Waitress) → Flask App → SQLite/PostgreSQL
```
For a single-branch agency, SQLite behind Waitress (Windows-friendly WSGI server) is sufficient. For multi-branch/high-concurrency use, see `FUTURE_ENHANCEMENTS.md` for the PostgreSQL migration path.
