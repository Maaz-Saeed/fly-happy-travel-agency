# Software Requirements Specification (SRS)
## Fly Happy International Travels — Travel Agency Management System

**License No:** PR-5199
**Version:** 1.0
**Prepared for:** Fly Happy International Travels

---

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements for the Fly Happy International Travels Management System — a web-based platform that allows customers to search destinations, book flights, pay for bookings, and manage their travel history, while giving administrators full control over bookings, catalog data, payments, staff and content.

### 1.2 Scope
The system covers:
- Public marketing website (home, about, services, destinations, airlines, packages, hotels, gallery, team, news, FAQs, testimonials, contact, portfolio)
- Customer registration, authentication and self-service dashboard
- Flight booking with automatic price calculation, Booking ID and Ticket Number generation
- Simulated payment processing (cards, mobile wallets, bank transfer, cash) with receipts and invoices
- Administrative back-office for managing customers, bookings, catalog (destinations/airlines/packages/hotels), payments, employees, content (gallery/testimonials/news/FAQs), contact messages and chatbot logs
- A rule-based chatbot assistant for common customer queries
- Reporting and CSV export of operational data

### 1.3 Intended Audience
Travel agency staff (admins, ticketing officers, visa consultants), customers, and the development/evaluation team (academic supervisors, viva panel).

### 1.4 Definitions
- **Booking ID** — Unique human-readable identifier for a reservation (format `FH-YYYY-NNNNNN`).
- **Ticket Number** — Unique identifier representing the issued ticket (format `TKT-NNNNNNNNN`).
- **Admin** — A staff user with full back-office access.
- **Customer** — A registered traveler who can create bookings.

---

## 2. Overall Description

### 2.1 Product Perspective
A self-contained Flask monolith using server-rendered Jinja2 templates, Bootstrap 5 for layout, and SQLite for storage — designed to be installable on a single machine with no external service dependencies (payment processing is simulated).

### 2.2 User Classes
| Role | Description |
|---|---|
| Guest | Unauthenticated visitor browsing public content |
| Customer | Registered traveler; can book, pay, manage bookings/profile |
| Employee | Staff record for internal reporting (ticketing officer, visa consultant, etc.) |
| Admin | Full administrative access to all modules |

### 2.3 Operating Environment
- Python 3.10+
- Flask 3.x, SQLAlchemy ORM, SQLite (file-based, zero-config)
- Runs locally via `python run.py`; deployable behind any WSGI server (Gunicorn/Waitress) for production

### 2.4 Assumptions & Constraints
- Payments are simulated for demonstration; no real payment gateway is integrated.
- Single-currency (PKR) pricing model.
- SQLite is adequate for the target scale (a single agency branch); a migration to PostgreSQL/MySQL is recommended for high-concurrency production use (see Future Enhancements).

---

## 3. Functional Requirements

### FR-1 Authentication
- FR-1.1 Users can register with name, email, phone, CNIC and password.
- FR-1.2 Passwords are hashed with Werkzeug (`generate_password_hash` / `check_password_hash`); plaintext is never stored.
- FR-1.3 Users can log in/out; sessions are managed via Flask-Login.
- FR-1.4 Deactivated accounts cannot log in.

### FR-2 Destinations, Airlines, Packages, Hotels
- FR-2.1 The system stores 80+ destinations with country, city, airport, airport code, description, starting price, visa requirement, flight duration, weather and best season.
- FR-2.2 The system stores 25+ airlines with logo, country, website, rating and cabin availability.
- FR-2.3 Admins can add, edit and delete destinations, airlines, packages and hotels.
- FR-2.4 Public users can search and filter destinations by keyword, region and visa requirement.

### FR-3 Booking
- FR-3.1 Authenticated customers can create a booking by selecting a destination, airline, trip type, dates, passenger counts, seat class and meal preference.
- FR-3.2 The system automatically calculates the total price based on base fare, seat class multiplier, trip type multiplier, and passenger composition (infants charged at 25%).
- FR-3.3 The system automatically generates a unique Booking ID and Ticket Number.
- FR-3.4 Bookings are persisted with status `pending`, `confirmed`, `cancelled` or `completed`.

### FR-4 Payment
- FR-4.1 Customers can pay via Visa/MasterCard/Debit Card, JazzCash, EasyPaisa, Bank Transfer or Cash.
- FR-4.2 Successful payment updates booking status to `confirmed` and generates a receipt number.
- FR-4.3 Cash payments leave the booking `pending` until settled at the office.
- FR-4.4 The system generates a printable invoice and receipt, including company logo, license number, and itemized charges.

### FR-5 Customer Dashboard
- FR-5.1 Customers can view all bookings, filter by status, and cancel bookings that are not already cancelled/completed.
- FR-5.2 Customers can view payment history and print invoices/receipts.
- FR-5.3 Customers can update their profile and change their password.
- FR-5.4 Customers can submit a support request.

### FR-6 Admin Panel
- FR-6.1 Dashboard shows today's/monthly bookings, total customers, total revenue, pending payments, cancelled bookings, upcoming flights, most popular destination/airline, and revenue/booking/customer-growth charts (Chart.js).
- FR-6.2 Admins can manage customers, bookings, airlines, destinations, packages, hotels, payments, employees, contact messages, chatbot logs, users, gallery, testimonials, news and FAQs.
- FR-6.3 Admins can search/filter bookings by Booking ID, customer name, passport, phone, destination, airline, date, and status.
- FR-6.4 Admins can export bookings and payments as CSV and print reports.

### FR-7 Chatbot
- FR-7.1 A floating chat widget answers common questions (office timings, visa process, passport requirements, booking process, refund policy, payment methods, insurance, destinations, office location, phone, email, flight status guidance, packages).
- FR-7.2 Every conversation turn is logged (session id, user id if authenticated, message, response, timestamp) and viewable by admins.

### FR-8 Contact & Content
- FR-8.1 Public contact form stores messages for admin follow-up.
- FR-8.2 Newsletter subscription capture.
- FR-8.3 Public pages for team, portfolio, gallery, testimonials, news and FAQs are database-driven and manageable from the admin panel.

---

## 4. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Security | Passwords hashed (Werkzeug/PBKDF2); CSRF protection on all state-changing forms (Flask-WTF); parameterized queries via SQLAlchemy ORM (no raw SQL); session cookies are HttpOnly and SameSite=Lax. |
| Usability | Responsive Bootstrap 5 layout; consistent green & white branding; accessible iconography (Font Awesome); animated but unobtrusive (AOS + CSS transitions). |
| Performance | Server-rendered pages, paginated destination listing, indexed lookup columns (email, booking_id, ticket_number). |
| Reliability | Custom 404/403/500 error pages; database rollback on server error. |
| Maintainability | Modular Flask blueprints per domain (public, auth, booking, payment, customer, admin, chatbot); single source of truth for company info via Flask config + context processor. |
| Portability | SQLite requires no external DB server; runs identically on Windows/macOS/Linux. |

---

## 5. External Interface Requirements
- **UI:** HTML5, CSS3, Bootstrap 5, Font Awesome icons, Chart.js graphs, AOS scroll animations.
- **Templates:** Jinja2 template inheritance (`base.html` for the public site, `admin/_base.html` for the back office).
- **Data:** SQLite file at `instance/flyhappy.db`, created and seeded via `flask init-db`.

---

## 6. Appendix — Company Information
- **Company:** Fly Happy International Travels
- **License Number:** PR-5199
- **Theme:** Professional Green & White
