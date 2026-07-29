# Admin Manual

Log in at `/auth/login` with an admin account (default demo: `admin@flyhappytravels.com` / `Admin@123`). You'll be redirected to `/admin/`.

## 1. Dashboard
The landing page shows:
- Today's bookings, monthly bookings, total customers, total revenue, pending payments, cancelled bookings, upcoming flights, most popular destination and most booked airline.
- Three Chart.js graphs: **Revenue**, **Bookings**, and **Customer Growth**, each covering the last 6 months.
- A table of the 8 most recent bookings with quick links to their detail pages.

## 2. Bookings
**Sidebar → Bookings**
- Search by Booking ID, passenger name, passport number or phone.
- Filter by status, destination or airline.
- Click **Manage** to open a booking's full detail: passenger info, trip info, payment history, and a status-update form (Pending/Confirmed/Cancelled/Completed).
- Use **Export CSV** to download the full booking list, or **Print** for a hard copy report.

## 3. Payments
**Sidebar → Payments** — search by receipt/booking ID, filter by status, export to CSV, or print. Each row links back to its parent booking.

## 4. Catalog Management
**Sidebar → Destinations / Airlines / Packages / Hotels**
- Each page lists all records with an **Add** button (opens a modal form) and per-row **Edit**/**Delete** actions (Edit also opens a modal, pre-filled).
- Destinations: city, country, airport name/code, region, starting price, visa requirement, flight duration, weather, best season, popular flag, description.
- Airlines: name, IATA code, country, website, rating, business/economy availability.
- Packages: name, destination, category, duration, price, inclusions, description, featured flag.
- Hotels: name, destination, star rating, price/night, amenities, description, featured flag.

## 5. People
- **Customers** — search by name/email/phone/passport, activate/deactivate accounts.
- **Employees** — add new staff (creates a login + designation/department), activate/deactivate.
- **All Users** — read-only view of every account, filterable by role (admin/employee/customer).

## 6. Content Management
- **Gallery** — add an image (by static path) with caption/category, or remove one.
- **Testimonials** — add a testimonial, approve/hide it from the public Testimonials page, or delete it.
- **News** — publish articles (title, slug, summary, content, author).
- **FAQs** — maintain the question bank shown on the public FAQ page (and used as chatbot reference content).

## 7. Support
- **Contact Messages** — view messages submitted via the public Contact form or the customer Support form; mark as read or delete.
- **Chatbot Logs** — review every chatbot conversation (session, message, response, timestamp) to spot gaps in the bot's knowledge.

## 8. Reports
**Sidebar → Reports** shows daily/monthly/yearly revenue plus top-5 tables for destinations, airlines and customers by spend. Use **Print Report** for a clean, sidebar-free printout.

## 9. Adding a New Admin
There's no dedicated "add admin" form in the UI (by design, to avoid privilege escalation from the browser). To promote a user to admin, use the Flask shell:
```bash
flask shell
>>> from app.models import User
>>> from app.extensions import db
>>> u = User.query.filter_by(email="someone@example.com").first()
>>> u.role = "admin"
>>> db.session.commit()
```

## 10. Security Notes for Admins
- Change the default demo passwords before using this system with real customer data.
- Set a strong, unique `SECRET_KEY` environment variable in production.
- Deactivate (don't delete) customer accounts you want to preserve for historical reporting.
