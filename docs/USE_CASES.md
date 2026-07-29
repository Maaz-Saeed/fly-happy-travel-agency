# Use Case Descriptions

## Actors
- **Guest** — unauthenticated visitor
- **Customer** — registered traveler
- **Admin** — back-office staff with full access

---

### UC-1: Register Account
- **Actor:** Guest
- **Precondition:** User has a valid, unused email address.
- **Main Flow:** Guest opens Register page → submits name, email, phone, CNIC, password → system hashes password and creates a `customer` role account → redirected to Login.
- **Alternate Flow:** Email already registered → system flashes a warning and redirects to Login.

### UC-2: Login
- **Actor:** Customer/Admin
- **Main Flow:** User submits email/password → system verifies hash via `check_password_hash` → Flask-Login session created → redirected to role-based dashboard (Admin Panel or Customer Dashboard).
- **Alternate Flow:** Invalid credentials → error flashed, form redisplayed. Deactivated account → login blocked.

### UC-3: Search & Browse Destinations
- **Actor:** Guest/Customer
- **Main Flow:** User opens Destinations page → applies keyword/region/visa filters → paginated results shown → clicks a destination to view full detail (packages, hotels, top airlines).

### UC-4: Book a Flight
- **Actor:** Customer (login required)
- **Precondition:** Customer is authenticated.
- **Main Flow:**
  1. Customer searches/select a destination from Book Now.
  2. Fills trip details (airline, dates, trip type, passengers, class, meal) and passenger/document details.
  3. System calculates total price live (client-side estimate + authoritative server-side calculation on submit).
  4. System generates a unique Booking ID and Ticket Number, stores the booking with status `pending`.
  5. Customer is redirected to Payment Checkout.
- **Postcondition:** A `Booking` row exists; no payment yet.

### UC-5: Pay for a Booking
- **Actor:** Customer
- **Main Flow:** Customer selects a payment method (card/JazzCash/EasyPaisa/Bank Transfer/Cash) → system simulates the transaction → on success, `Payment` row created with status `completed` and `Booking.status` set to `confirmed` → receipt and invoice become available for printing.
- **Alternate Flow:** Cash method selected → booking stays `pending` until office visit; a payment row is logged as `pending`.

### UC-6: Manage My Bookings
- **Actor:** Customer
- **Main Flow:** Customer views bookings list, filters by status, opens a booking to view its ticket/confirmation, downloads/prints the invoice, or cancels a booking that is not already cancelled/completed.

### UC-7: Update Profile / Change Password
- **Actor:** Customer
- **Main Flow:** Customer edits profile fields (name, phone, CNIC, passport, address) or submits current+new password (validated against the stored hash) via the dashboard.

### UC-8: Contact Support / Chatbot
- **Actor:** Guest/Customer
- **Main Flow (Chatbot):** User opens the chat widget, types a question → client posts to `/chatbot/ask` → server matches keyword rules (or falls back to a generic reply) → response returned and the full exchange logged to `ChatLog`.
- **Main Flow (Contact Form):** User submits name/email/subject/message → stored as a `ContactMessage` for admin follow-up.

### UC-9: Admin Dashboard Review
- **Actor:** Admin
- **Main Flow:** Admin logs in → views today's/monthly booking counts, revenue, pending payments, cancellations, upcoming flights, most popular destination/airline, and three Chart.js graphs (revenue, bookings, customer growth).

### UC-10: Manage Catalog (Destinations/Airlines/Packages/Hotels)
- **Actor:** Admin
- **Main Flow:** Admin opens a catalog page → adds a new record via modal form, or edits/deletes an existing record → changes are immediately reflected on the public site.

### UC-11: Manage Bookings & Payments
- **Actor:** Admin
- **Main Flow:** Admin searches/filters bookings (by ID, name, passport, phone, destination, airline, status) → opens booking detail → manually updates status (e.g. confirm a bank transfer, mark completed after travel) → can export the full list to CSV or print a report.

### UC-12: Manage Staff & Users
- **Actor:** Admin
- **Main Flow:** Admin adds an employee (creates a `User` with role `employee` + an `Employee` profile), toggles active/inactive status, and reviews all platform users by role.

### UC-13: Manage Content
- **Actor:** Admin
- **Main Flow:** Admin adds/removes gallery images, approves or hides testimonials, publishes news articles, and maintains the FAQ knowledge base used by the chatbot's context.

### UC-14: View Reports
- **Actor:** Admin
- **Main Flow:** Admin opens Reports → views daily/monthly/yearly revenue, top 5 destinations, top 5 airlines and top 5 customers by spend → can print the report.
