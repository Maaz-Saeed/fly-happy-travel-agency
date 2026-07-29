# Viva Questions & Answers

### Q1. What is the purpose of this project?
A commercial-grade Travel Agency Management System for Fly Happy International Travels, covering the full customer journey (browse → book → pay → manage) and a complete admin back-office (catalog, bookings, payments, staff, content, reports), built with Python Flask.

### Q2. Why Flask instead of Django?
Flask is a micro-framework, giving full control over project structure with minimal boilerplate — appropriate for a scoped academic/commercial deliverable where every route, model and template is intentionally hand-designed rather than scaffolded. SQLAlchemy, Flask-Login, Flask-WTF and Flask-SQLAlchemy provide the same core building blocks Django would give out of the box, chosen individually.

### Q3. Why SQLite instead of MySQL/PostgreSQL?
SQLite is file-based and needs no separate server process, making the project trivially installable on any machine for demonstration/evaluation. The schema is designed with standard SQL types so migrating to PostgreSQL/MySQL later only requires changing `SQLALCHEMY_DATABASE_URI` and adding Alembic migrations (see `FUTURE_ENHANCEMENTS.md`).

### Q4. How are passwords secured?
Passwords are never stored in plaintext. `User.set_password()` calls Werkzeug's `generate_password_hash()` (PBKDF2-SHA256 with a random salt) and `User.check_password()` calls `check_password_hash()` for verification — both from `werkzeug.security`.

### Q5. How is CSRF handled?
`Flask-WTF`'s `CSRFProtect` is initialized globally in `app/extensions.py` and applied to the whole app in `create_app()`. Every state-changing form — whether rendered via a WTForms `FlaskForm` (`form.hidden_tag()`) or a plain HTML `<form>` (manual `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`) — carries a valid token, so any POST without one is rejected with 400.

### Q6. How is SQL injection prevented?
No raw SQL string concatenation is used anywhere in the codebase. All database access goes through the SQLAlchemy ORM's query builder (`Model.query.filter(...)`), which parameterizes every value automatically.

### Q7. How does the Booking ID / Ticket Number generation work?
`Booking.generate_booking_id()` builds a candidate string `FH-<year>-<6 random digits>` and loops until it finds one not already in the table (uniqueness guaranteed at generation time, further enforced by a UNIQUE column constraint). `generate_ticket_number()` follows the same pattern with prefix `TKT-` and 9 digits.

### Q8. How is the total price calculated?
`calculate_price()` in `app/routes/booking.py` multiplies the destination's `starting_price` by a seat-class multiplier (Economy 1.0, Business 1.6, First 2.2), a trip-type multiplier (One Way 1.0, Round Trip 1.85), and the "payable head count" (adults + children counted fully, infants at 25%). The same formula is mirrored in JavaScript (`main.js`) for the live estimate the customer sees before submitting, but the server always recalculates authoritatively on submit — the client-side number is cosmetic only.

### Q9. How does the admin dashboard get its statistics?
`app/routes/admin.py`'s `dashboard()` view uses SQLAlchemy aggregate functions (`func.count`, `func.sum`, `func.strftime`) grouped by month to build the revenue/booking/customer-growth series, which are passed to the template as JSON via Jinja's `tojson` filter and rendered as Chart.js line/bar charts.

### Q10. How does the chatbot work — is it AI-powered?
No — it's a deliberately simple, transparent **rule-based** matcher (`app/routes/chatbot.py`): an ordered list of `(keywords, response-template)` pairs is scanned for substring matches against the lowercased user message, with a fallback for unmatched input. Every exchange (session id, optional user id, message, response, timestamp) is persisted to the `ChatLog` table and viewable in the admin panel. This was a deliberate design choice for predictability, zero external API cost, and full auditability — an LLM-backed upgrade path is documented in `FUTURE_ENHANCEMENTS.md`.

### Q11. How do customer and admin authorization differ?
Both use the same `User` model with a `role` column (`customer`/`employee`/`admin`). `flask_login.login_required` guards any authenticated-only route; a custom `admin_required` decorator plus a blueprint-level `before_request` guard on the `admin` blueprint additionally checks `current_user.is_admin`, aborting with 403 otherwise. Booking/payment routes further check row-level ownership (`booking.customer_id == current_user.id`) so customers cannot view or pay for someone else's booking by guessing a URL.

### Q12. Why does the loading screen only appear once per visit?
`main.js` checks `sessionStorage.getItem("flyhappy_loaded")` — if unset, it plays the animation and sets the flag; if set (e.g. navigating to another page in the same browser tab session), the loader is hidden immediately. `sessionStorage` clears when the tab/browser closes, so the animation naturally replays on a fresh visit.

### Q13. How would you scale this system for multiple branches / high traffic?
Migrate SQLite → PostgreSQL with Alembic migrations, introduce a Redis cache for read-heavy catalog pages, move file uploads to object storage (S3-compatible), add a `branch` foreign key across bookings/employees for multi-branch reporting, and deploy behind a WSGI server (Gunicorn) with a reverse proxy (nginx) and horizontal scaling.

### Q14. What was the biggest design trade-off?
Choosing simulated payments over a real gateway: it keeps the project runnable offline with zero external accounts/API keys (ideal for demonstration and evaluation) while still modeling the full data lifecycle (Payment status transitions, receipts, invoices) realistically enough to swap in a real gateway later without changing the schema.

### Q15. How is data integrity maintained across related tables?
Foreign keys (`destination_id`, `airline_id`, `customer_id`, `booking_id`, etc.) enforce relational integrity; `cascade="all, delete-orphan"` is set on parent relationships (e.g. deleting a `Booking` deletes its `Payments`; deleting a `Destination` deletes its `Packages`/`Hotels`) so the database never accumulates orphaned rows.
