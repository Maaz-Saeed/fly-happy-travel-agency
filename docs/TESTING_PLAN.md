# Testing Plan

## 1. Objective
Verify that every module of the Fly Happy International Travels system functions correctly, securely, and consistently across the customer and admin experience.

## 2. Test Levels
1. **Smoke Testing** — every route returns the expected HTTP status (already executed during build — see Section 5).
2. **Functional Testing** — each use case in `USE_CASES.md` is manually exercised end-to-end.
3. **Security Testing** — CSRF, auth boundaries, password hashing, SQL injection resistance.
4. **UI/Responsiveness Testing** — verify layout on desktop, tablet and mobile breakpoints.

## 3. Test Cases

| ID | Module | Test Case | Expected Result |
|---|---|---|---|
| TC-01 | Auth | Register with an existing email | Warning flashed, redirected to login |
| TC-02 | Auth | Register then login with correct credentials | Redirect to Customer Dashboard |
| TC-03 | Auth | Login with wrong password | "Invalid email or password" error |
| TC-04 | Auth | Admin login | Redirect to `/admin/` |
| TC-05 | Destinations | Filter by region + visa-free | Only matching destinations shown, pagination works |
| TC-06 | Booking | Book with 2 adults, 1 child, Business class, round trip | Price = base × 1.6 × 1.85 × 3, Booking ID/Ticket Number generated |
| TC-07 | Booking | Submit booking without login | Redirected to Login with `next` param preserved |
| TC-08 | Payment | Pay via JazzCash | Booking status → `confirmed`, receipt generated |
| TC-09 | Payment | Pay via Cash | Booking stays `pending`, payment status `pending` |
| TC-10 | Customer Dashboard | Cancel a `pending` booking | Status changes to `cancelled`; cancel button hidden afterward |
| TC-11 | Customer Dashboard | Change password with wrong current password | Error shown, password unchanged |
| TC-12 | Admin | Add a new destination via modal | Appears immediately in destinations list and public site |
| TC-13 | Admin | Search bookings by passport number | Only matching bookings returned |
| TC-14 | Admin | Export bookings CSV | Downloaded file contains all visible columns and rows |
| TC-15 | Admin | Deactivate a customer | That customer can no longer log in |
| TC-16 | Chatbot | Ask "what are your office timings" | Returns configured office hours string; logged in ChatLog |
| TC-17 | Chatbot | Ask an unrelated question | Fallback message returned, still logged |
| TC-18 | Security | Submit a POST form without CSRF token | 400 Bad Request (CSRF validation failure) |
| TC-19 | Security | Attempt SQL-meta characters in search box (`' OR 1=1 --`) | Treated as a literal search string; no error, no data leak |
| TC-20 | Errors | Visit a non-existent URL | Custom 404 page rendered |
| TC-21 | Errors | Non-admin visits `/admin/` | Custom 403 page rendered |
| TC-22 | Responsiveness | Load homepage at 375px width | Navbar collapses to hamburger, hero stacks vertically, no horizontal scroll |

## 4. Regression Checklist (run after any change)
- [ ] `flask init-db` completes without error
- [ ] All public pages return HTTP 200
- [ ] Registration → login → booking → payment → invoice flow completes end-to-end
- [ ] Admin dashboard charts render without console errors
- [ ] Chatbot widget responds to a message
- [ ] No Python tracebacks appear in the server log during the above

## 5. Verified Results (Build-Time Smoke Test)
During development, the following was executed against a live local server and confirmed working:
- All 17 public routes → HTTP 200
- Customer login → HTTP 302 to `/dashboard/`; all 6 dashboard sub-pages → HTTP 200
- Admin login → HTTP 302 to `/admin/`; all 17 admin sub-pages → HTTP 200
- Full booking → payment (JazzCash) → invoice flow completed, invoice correctly displayed the computed total
- Chatbot API returned correct rule-matched replies for "office timings" and "how do I book a flight" queries
- CSV export endpoint returned a valid CSV with booking data
- Admin "Add Destination" modal correctly persisted a new record
- Visiting an unknown URL returned HTTP 404 via the custom error page
- No errors/tracebacks appeared in the server log throughout testing
