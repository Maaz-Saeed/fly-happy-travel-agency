# Entity-Relationship Diagram (Description)

Since this is a text-based deliverable, the ER diagram is described below in a copy-pasteable [Mermaid](https://mermaid.js.org/) format. Paste the block into any Mermaid live editor (e.g. mermaid.live) to render it visually, or view it directly in tools that support Mermaid (GitHub, many Markdown viewers).

```mermaid
erDiagram
    USERS ||--o{ BOOKINGS : "makes"
    USERS ||--o| EMPLOYEES : "has profile"
    USERS ||--o{ CHAT_LOGS : "chats"
    DESTINATIONS ||--o{ BOOKINGS : "booked for"
    DESTINATIONS ||--o{ PACKAGES : "offers"
    DESTINATIONS ||--o{ HOTELS : "has"
    AIRLINES ||--o{ BOOKINGS : "operates"
    BOOKINGS ||--o{ PAYMENTS : "paid via"

    USERS {
        int id PK
        string full_name
        string email UK
        string password_hash
        string role
        string phone
        string cnic
        string passport_number
        boolean is_active_account
    }
    EMPLOYEES {
        int id PK
        int user_id FK
        string designation
        string department
        date hire_date
    }
    DESTINATIONS {
        int id PK
        string country
        string city
        string airport_code
        string region
        decimal starting_price
        boolean visa_required
        boolean is_popular
    }
    AIRLINES {
        int id PK
        string name UK
        string iata_code
        string country
        float rating
    }
    PACKAGES {
        int id PK
        int destination_id FK
        string name
        string category
        decimal price
    }
    HOTELS {
        int id PK
        int destination_id FK
        string name
        int star_rating
        decimal price_per_night
    }
    BOOKINGS {
        int id PK
        string booking_id UK
        string ticket_number UK
        int customer_id FK
        int destination_id FK
        int airline_id FK
        string trip_type
        date departure_date
        date return_date
        string seat_class
        decimal total_price
        string status
    }
    PAYMENTS {
        int id PK
        string receipt_number UK
        int booking_id FK
        decimal amount
        string method
        string status
    }
    CHAT_LOGS {
        int id PK
        string session_id
        int user_id FK
        text user_message
        text bot_response
    }
```

## Cardinality Summary
- One **User** (customer) can have many **Bookings** (1:M).
- One **User** (employee) has exactly one **Employee** profile (1:1).
- One **Destination** can appear in many **Bookings**, **Packages**, and **Hotels** (1:M each).
- One **Airline** can operate many **Bookings** (1:M).
- One **Booking** can have multiple **Payment** attempts, e.g. a failed card payment followed by a successful bank transfer (1:M).
- One **User** can generate many **ChatLog** entries; guests (unauthenticated) produce ChatLog rows with `user_id = NULL`.
