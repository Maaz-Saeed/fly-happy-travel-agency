# Database Design

The system uses a normalized (3NF) relational schema implemented with SQLAlchemy models in `app/models.py`, backed by SQLite (`instance/flyhappy.db`).

## Tables

### users
Central account table for customers, employees and admins (differentiated by `role`).
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| full_name | VARCHAR(120) | |
| email | VARCHAR(120) | UNIQUE, indexed |
| password_hash | VARCHAR(255) | Werkzeug hash, never plaintext |
| phone | VARCHAR(30) | |
| cnic | VARCHAR(20) | |
| passport_number | VARCHAR(20) | |
| address | VARCHAR(255) | |
| role | VARCHAR(20) | customer / employee / admin |
| photo | VARCHAR(255) | |
| is_active_account | BOOLEAN | soft-disable flag |
| created_at | DATETIME | |

### employees
1:1 extension of `users` for staff-specific fields.
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| user_id | INTEGER FK → users.id | UNIQUE |
| designation | VARCHAR(80) | Manager, Ticketing Officer, ... |
| department | VARCHAR(80) | |
| hire_date | DATE | |
| salary | NUMERIC(12,2) | |
| is_active | BOOLEAN | |

### destinations
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| country, city | VARCHAR(80) | indexed on country |
| airport_name, airport_code | VARCHAR | |
| region | VARCHAR(50) | Asia / Middle East / Europe / Americas / Africa / Oceania |
| image | VARCHAR(255) | |
| description | TEXT | |
| starting_price | NUMERIC(10,2) | |
| visa_required | BOOLEAN | |
| flight_duration, weather, best_season | VARCHAR | |
| is_popular | BOOLEAN | featured flag |
| created_at | DATETIME | |

### airlines
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| name | VARCHAR(100) | UNIQUE |
| iata_code | VARCHAR(5) | |
| country, website, logo | VARCHAR | |
| rating | FLOAT | |
| business_class, economy_class | BOOLEAN | |

### packages
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| name | VARCHAR(150) | |
| destination_id | INTEGER FK → destinations.id | |
| category | VARCHAR(40) | Holiday/Family/Corporate/Group/Umrah/Hajj |
| duration_days | INTEGER | |
| price | NUMERIC(10,2) | |
| image, description, inclusions | TEXT/VARCHAR | |
| is_featured | BOOLEAN | |

### hotels
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| name | VARCHAR(150) | |
| destination_id | INTEGER FK → destinations.id | |
| star_rating | INTEGER | |
| price_per_night | NUMERIC(10,2) | |
| image, description, amenities | TEXT/VARCHAR | |
| is_featured | BOOLEAN | |

### bookings
The transactional core of the system.
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| booking_id | VARCHAR(20) | UNIQUE, `FH-YYYY-NNNNNN` |
| ticket_number | VARCHAR(20) | UNIQUE, `TKT-NNNNNNNNN` |
| customer_id | INTEGER FK → users.id | |
| destination_id | INTEGER FK → destinations.id | |
| airline_id | INTEGER FK → airlines.id | |
| trip_type | VARCHAR(20) | one_way / round_trip |
| departure_date, return_date | DATE | |
| adults, children, infants | INTEGER | |
| seat_class | VARCHAR(20) | Economy/Business/First |
| meal_preference | VARCHAR(30) | |
| passenger_name, passport_number, cnic, phone, email | VARCHAR | snapshot of traveler details at booking time |
| special_requests | TEXT | |
| total_price | NUMERIC(10,2) | auto-calculated |
| status | VARCHAR(20) | pending/confirmed/cancelled/completed |
| created_at | DATETIME | |

### payments
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| receipt_number | VARCHAR(20) | UNIQUE, `RCPT-NNNNNNNN` |
| booking_id | INTEGER FK → bookings.id | one booking can have multiple payment attempts |
| amount | NUMERIC(10,2) | |
| method | VARCHAR(30) | Visa Card/MasterCard/Debit Card/JazzCash/EasyPaisa/Bank Transfer/Cash |
| transaction_id | VARCHAR(50) | simulated |
| status | VARCHAR(20) | pending/completed/failed |
| paid_at | DATETIME | |

### testimonials, team_members, news, faqs, gallery, contact_messages, chat_logs, newsletter_subscribers
Supporting content tables for the public site and chatbot, each independent (no complex FKs) except `chat_logs.user_id → users.id` (nullable, for guest chats).

## Relationships (Entity Overview)
```
users (1) ────< (M) bookings >──── (1) destinations
users (1) ── (1) employees          bookings (M) >──── (1) airlines
bookings (1) ────< (M) payments
destinations (1) ────< (M) packages
destinations (1) ────< (M) hotels
users (1) ────< (M) chat_logs
```

## Normalization Notes
- 1NF: all columns hold atomic values (no repeating groups).
- 2NF: all non-key attributes depend on the whole primary key (single-column surrogate PKs throughout).
- 3NF: no transitive dependencies — e.g. destination pricing lives only on `destinations`, not duplicated on `bookings` (bookings store the *computed* `total_price`, which is a derived transactional fact, not a duplicated destination attribute).
