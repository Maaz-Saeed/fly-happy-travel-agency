"""Database models for Fly Happy International Travels.

Normalized relational schema (3NF):
    User            -- accounts (customer / admin / employee), auth + profile
    Employee         -- staff profile linked 1:1 to a User with role=employee
    Destination      -- countries/cities served
    Airline          -- airline partners
    Package          -- curated holiday/umrah/corporate packages tied to a destination
    Hotel            -- hotels tied to a destination
    Booking          -- a customer's flight booking (FK: User, Destination, Airline)
    Payment          -- a payment made against a Booking (1 booking : many payment attempts)
    Testimonial      -- customer reviews
    TeamMember       -- staff shown on the Team page
    News             -- news / blog posts
    FAQ              -- chatbot / FAQ page content
    Gallery          -- photo gallery
    ContactMessage   -- messages submitted via the Contact form
    ChatLog          -- chatbot conversation history
    Newsletter       -- newsletter subscribers
"""
import random
import string
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


def _rand_digits(n):
    return "".join(random.choices(string.digits, k=n))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30))
    cnic = db.Column(db.String(20))
    passport_number = db.Column(db.String(20))
    address = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False, default="customer")  # customer / admin / employee
    photo = db.Column(db.String(255), default="default_avatar.png")
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="customer", lazy="dynamic",
                                foreign_keys="Booking.customer_id")
    employee_profile = db.relationship("Employee", backref="user", uselist=False,
                                        cascade="all, delete-orphan")
    chat_logs = db.relationship("ChatLog", backref="user", lazy="dynamic")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_employee(self):
        return self.role == "employee"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    designation = db.Column(db.String(80), nullable=False)  # Manager, Ticketing Officer, ...
    department = db.Column(db.String(80))
    hire_date = db.Column(db.Date, default=datetime.utcnow)
    salary = db.Column(db.Numeric(12, 2))
    is_active = db.Column(db.Boolean, default=True)


class Destination(db.Model):
    __tablename__ = "destinations"

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(80), nullable=False, index=True)
    city = db.Column(db.String(80), nullable=False)
    airport_name = db.Column(db.String(120))
    airport_code = db.Column(db.String(10))
    region = db.Column(db.String(50))  # Middle East, Asia, Europe, Americas, Africa, Oceania
    image = db.Column(db.String(255), default="destinations/default.jpg")
    description = db.Column(db.Text)
    starting_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    visa_required = db.Column(db.Boolean, default=True)
    flight_duration = db.Column(db.String(30))  # e.g. "3h 30m"
    weather = db.Column(db.String(80))
    best_season = db.Column(db.String(80))
    is_popular = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="destination", lazy="dynamic")
    packages = db.relationship("Package", backref="destination", lazy="dynamic",
                                cascade="all, delete-orphan")
    hotels = db.relationship("Hotel", backref="destination", lazy="dynamic",
                              cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Destination {self.city}, {self.country}>"


class Airline(db.Model):
    __tablename__ = "airlines"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    iata_code = db.Column(db.String(5))
    country = db.Column(db.String(80))
    logo = db.Column(db.String(255), default="airlines/default.png")
    website = db.Column(db.String(255))
    rating = db.Column(db.Float, default=4.0)
    business_class = db.Column(db.Boolean, default=True)
    economy_class = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="airline", lazy="dynamic")

    def __repr__(self):
        return f"<Airline {self.name}>"


class Package(db.Model):
    __tablename__ = "packages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id"))
    category = db.Column(db.String(40))  # Holiday, Family, Corporate, Group, Umrah, Hajj
    duration_days = db.Column(db.Integer, default=5)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image = db.Column(db.String(255), default="packages/default.jpg")
    description = db.Column(db.Text)
    inclusions = db.Column(db.Text)  # comma separated
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Hotel(db.Model):
    __tablename__ = "hotels"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id"))
    star_rating = db.Column(db.Integer, default=4)
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    image = db.Column(db.String(255), default="hotels/default.jpg")
    description = db.Column(db.Text)
    amenities = db.Column(db.String(255))
    is_featured = db.Column(db.Boolean, default=False)


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False, index=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id"), nullable=False)
    airline_id = db.Column(db.Integer, db.ForeignKey("airlines.id"), nullable=False)

    trip_type = db.Column(db.String(20), default="one_way")  # one_way / round_trip
    departure_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)

    adults = db.Column(db.Integer, default=1)
    children = db.Column(db.Integer, default=0)
    infants = db.Column(db.Integer, default=0)

    seat_class = db.Column(db.String(20), default="Economy")  # Economy / Business / First
    meal_preference = db.Column(db.String(30), default="Standard")

    passenger_name = db.Column(db.String(120))
    passport_number = db.Column(db.String(20))
    cnic = db.Column(db.String(20))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    special_requests = db.Column(db.Text)

    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(20), default="pending")  # pending/confirmed/cancelled/completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payments = db.relationship("Payment", backref="booking", lazy="dynamic",
                                cascade="all, delete-orphan")

    @staticmethod
    def generate_booking_id():
        year = datetime.utcnow().year
        while True:
            candidate = f"FH-{year}-{_rand_digits(6)}"
            if not Booking.query.filter_by(booking_id=candidate).first():
                return candidate

    @staticmethod
    def generate_ticket_number():
        while True:
            candidate = f"TKT-{_rand_digits(9)}"
            if not Booking.query.filter_by(ticket_number=candidate).first():
                return candidate

    @property
    def total_passengers(self):
        return (self.adults or 0) + (self.children or 0) + (self.infants or 0)

    def __repr__(self):
        return f"<Booking {self.booking_id}>"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(20), unique=True, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(30), nullable=False)  # Visa/MasterCard/Debit/JazzCash/EasyPaisa/Bank/Cash
    transaction_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default="completed")  # pending/completed/failed
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_receipt_number():
        while True:
            candidate = f"RCPT-{_rand_digits(8)}"
            if not Payment.query.filter_by(receipt_number=candidate).first():
                return candidate


class Testimonial(db.Model):
    __tablename__ = "testimonials"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    photo = db.Column(db.String(255), default="testimonials/default.jpg")
    rating = db.Column(db.Integer, default=5)
    destination = db.Column(db.String(120))
    message = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TeamMember(db.Model):
    __tablename__ = "team_members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(255), default="team/default.jpg")
    bio = db.Column(db.Text)
    email = db.Column(db.String(120))
    display_order = db.Column(db.Integer, default=0)


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False)
    summary = db.Column(db.String(300))
    content = db.Column(db.Text)
    image = db.Column(db.String(255), default="news/default.jpg")
    author = db.Column(db.String(120), default="Fly Happy Team")
    published_at = db.Column(db.DateTime, default=datetime.utcnow)


class FAQ(db.Model):
    __tablename__ = "faqs"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), default="General")
    display_order = db.Column(db.Integer, default=0)


class Gallery(db.Model):
    __tablename__ = "gallery"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(200))
    category = db.Column(db.String(60), default="General")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatLog(db.Model):
    __tablename__ = "chat_logs"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Newsletter(db.Model):
    __tablename__ = "newsletter_subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
