# Future Enhancements

## Near-Term
- **Real Payment Gateway Integration** — replace the payment simulation with Stripe/PayFast/JazzCash/EasyPaisa live APIs.
- **Email/SMS Notifications** — send booking confirmations, payment receipts and reminders via SMTP/Twilio.
- **PDF Generation** — export invoices/tickets as true PDF files (e.g. via WeasyPrint or ReportLab) instead of print-to-PDF from the browser.
- **File Uploads for Content** — replace the "type an image path" admin workflow (gallery/destinations/packages/hotels) with a real file-upload widget saving into `static/uploads/`.
- **Multi-Currency Support** — store prices with a currency code and support live FX conversion.

## Medium-Term
- **Role-Based Employee Permissions** — restrict employee dashboard access by designation (e.g. Visa Consultant sees only visa-related messages).
- **Seat Map & Real Airline Inventory** — integrate a GDS/NDC API for live fares and seat availability instead of static starting prices.
- **Multi-Branch Support** — add a `branch` dimension to bookings/employees/reports for agencies with multiple physical offices.
- **Audit Trail** — log every admin create/update/delete action (who, what, when) for compliance.
- **Two-Factor Authentication** — optional TOTP-based 2FA for admin accounts.

## Long-Term / Scale-Out
- **Database Migration** — move from SQLite to PostgreSQL/MySQL for concurrent multi-branch write loads; introduce Alembic migrations.
- **Caching Layer** — Redis-backed caching for destination/airline listings and session storage.
- **API-First Rearchitecture** — expose a REST/GraphQL API and rebuild the front end as a SPA (React/Vue) for a native mobile app to consume.
- **AI-Powered Chatbot** — replace the rule-based chatbot with an LLM-backed assistant (retaining the same ChatLog schema) capable of live booking lookups.
- **Automated Testing Suite** — add pytest-based unit/integration tests and CI (GitHub Actions) covering the test cases in `TESTING_PLAN.md`.
- **Internationalization (i18n)** — Urdu/Arabic/English localization via Flask-Babel.
