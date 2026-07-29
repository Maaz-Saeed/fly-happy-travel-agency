"""Admin panel: dashboard, statistics and full CRUD management."""
from datetime import datetime, timedelta, date

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, or_

from app.extensions import db
from app.models import (
    User, Employee, Destination, Airline, Package, Hotel, Booking, Payment,
    Testimonial, TeamMember, News, FAQ, Gallery, ContactMessage, ChatLog,
)
from app.utils import admin_required, to_csv_response

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
@login_required
@admin_required
def guard():
    pass


# =========================================================================
# DASHBOARD
# =========================================================================
@admin_bp.route("/")
def dashboard():
    today = date.today()
    month_start = today.replace(day=1)

    todays_bookings = Booking.query.filter(func.date(Booking.created_at) == today).count()
    monthly_bookings = Booking.query.filter(Booking.created_at >= month_start).count()
    total_customers = User.query.filter_by(role="customer").count()
    total_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == "completed").scalar()
    pending_payments = Payment.query.filter_by(status="pending").count()
    cancelled_bookings = Booking.query.filter_by(status="cancelled").count()
    upcoming_flights = Booking.query.filter(Booking.departure_date >= today,
                                             Booking.status.in_(["confirmed", "pending"])).count()

    popular_destination = (
        db.session.query(Destination.city, func.count(Booking.id).label("cnt"))
        .join(Booking).group_by(Destination.id).order_by(func.count(Booking.id).desc()).first()
    )
    popular_airline = (
        db.session.query(Airline.name, func.count(Booking.id).label("cnt"))
        .join(Booking).group_by(Airline.id).order_by(func.count(Booking.id).desc()).first()
    )

    # Revenue for last 6 months (for Chart.js)
    revenue_labels, revenue_data = [], []
    for i in range(5, -1, -1):
        month_date = (month_start - timedelta(days=30 * i))
        label = month_date.strftime("%b %Y")
        total = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            func.strftime("%Y-%m", Payment.paid_at) == month_date.strftime("%Y-%m"),
            Payment.status == "completed").scalar()
        revenue_labels.append(label)
        revenue_data.append(float(total))

    # Bookings per month
    booking_labels, booking_data = [], []
    for i in range(5, -1, -1):
        month_date = (month_start - timedelta(days=30 * i))
        label = month_date.strftime("%b %Y")
        count = Booking.query.filter(func.strftime("%Y-%m", Booking.created_at) == month_date.strftime("%Y-%m")).count()
        booking_labels.append(label)
        booking_data.append(count)

    # Customer growth
    cust_labels, cust_data = [], []
    for i in range(5, -1, -1):
        month_date = (month_start - timedelta(days=30 * i))
        label = month_date.strftime("%b %Y")
        count = User.query.filter(User.role == "customer",
                                   func.strftime("%Y-%m", User.created_at) == month_date.strftime("%Y-%m")).count()
        cust_labels.append(label)
        cust_data.append(count)

    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(8).all()

    return render_template(
        "admin/dashboard.html",
        todays_bookings=todays_bookings, monthly_bookings=monthly_bookings,
        total_customers=total_customers, total_revenue=total_revenue,
        pending_payments=pending_payments, cancelled_bookings=cancelled_bookings,
        upcoming_flights=upcoming_flights,
        popular_destination=popular_destination[0] if popular_destination else "N/A",
        popular_airline=popular_airline[0] if popular_airline else "N/A",
        revenue_labels=revenue_labels, revenue_data=revenue_data,
        booking_labels=booking_labels, booking_data=booking_data,
        cust_labels=cust_labels, cust_data=cust_data,
        recent_bookings=recent_bookings,
    )


# =========================================================================
# CUSTOMERS / USERS
# =========================================================================
@admin_bp.route("/customers")
def customers():
    search = request.args.get("q", "").strip()
    query = User.query.filter_by(role="customer")
    if search:
        query = query.filter(or_(User.full_name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"),
                                  User.phone.ilike(f"%{search}%"), User.passport_number.ilike(f"%{search}%")))
    customer_list = query.order_by(User.created_at.desc()).all()
    return render_template("admin/customers.html", customers=customer_list, search=search)


@admin_bp.route("/customers/<int:user_id>/toggle", methods=["POST"])
def toggle_customer(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active_account = not user.is_active_account
    db.session.commit()
    flash(f"Account for {user.full_name} has been {'activated' if user.is_active_account else 'deactivated'}.", "success")
    return redirect(url_for("admin.customers"))


@admin_bp.route("/users")
def users():
    role = request.args.get("role", "").strip()
    query = User.query
    if role:
        query = query.filter_by(role=role)
    user_list = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=user_list, role=role)


# =========================================================================
# BOOKINGS
# =========================================================================
@admin_bp.route("/bookings")
def bookings():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    destination_id = request.args.get("destination_id", type=int)
    airline_id = request.args.get("airline_id", type=int)

    query = Booking.query
    if search:
        query = query.filter(or_(Booking.booking_id.ilike(f"%{search}%"), Booking.passenger_name.ilike(f"%{search}%"),
                                  Booking.passport_number.ilike(f"%{search}%"), Booking.phone.ilike(f"%{search}%")))
    if status:
        query = query.filter_by(status=status)
    if destination_id:
        query = query.filter_by(destination_id=destination_id)
    if airline_id:
        query = query.filter_by(airline_id=airline_id)

    booking_list = query.order_by(Booking.created_at.desc()).all()
    return render_template("admin/bookings.html", bookings=booking_list, search=search, status=status,
                            destinations=Destination.query.order_by(Destination.city).all(),
                            airlines=Airline.query.order_by(Airline.name).all(),
                            destination_id=destination_id, airline_id=airline_id)


@admin_bp.route("/bookings/<int:booking_id>")
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template("admin/booking_detail.html", booking=booking)


@admin_bp.route("/bookings/<int:booking_id>/status", methods=["POST"])
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get("status")
    if new_status in ("pending", "confirmed", "cancelled", "completed"):
        booking.status = new_status
        db.session.commit()
        flash(f"Booking {booking.booking_id} status updated to {new_status}.", "success")
    return redirect(url_for("admin.booking_detail", booking_id=booking.id))


@admin_bp.route("/bookings/export")
def export_bookings():
    rows = [(b.booking_id, b.ticket_number, b.passenger_name, b.destination.city, b.airline.name,
              b.departure_date, b.seat_class, float(b.total_price), b.status)
             for b in Booking.query.order_by(Booking.created_at.desc()).all()]
    headers = ["Booking ID", "Ticket No", "Passenger", "Destination", "Airline", "Departure", "Class", "Total", "Status"]
    return to_csv_response(rows, headers, "bookings_export.csv")


# =========================================================================
# GENERIC CRUD FACTORY (for simpler content entities)
# =========================================================================
def _bool(val):
    return val in ("on", "true", "1", "yes")


@admin_bp.route("/destinations", methods=["GET", "POST"])
def destinations():
    if request.method == "POST":
        d = Destination(
            country=request.form["country"], city=request.form["city"],
            airport_name=request.form.get("airport_name"), airport_code=request.form.get("airport_code"),
            region=request.form.get("region"), starting_price=request.form.get("starting_price", 0),
            visa_required=_bool(request.form.get("visa_required")),
            flight_duration=request.form.get("flight_duration"), weather=request.form.get("weather"),
            best_season=request.form.get("best_season"), is_popular=_bool(request.form.get("is_popular")),
            description=request.form.get("description"),
        )
        db.session.add(d)
        db.session.commit()
        flash("Destination added successfully.", "success")
        return redirect(url_for("admin.destinations"))
    search = request.args.get("q", "").strip()
    query = Destination.query
    if search:
        query = query.filter(or_(Destination.city.ilike(f"%{search}%"), Destination.country.ilike(f"%{search}%")))
    return render_template("admin/destinations.html", destinations=query.order_by(Destination.country).all(), search=search)


@admin_bp.route("/destinations/<int:item_id>/edit", methods=["POST"])
def edit_destination(item_id):
    d = Destination.query.get_or_404(item_id)
    d.country = request.form["country"]
    d.city = request.form["city"]
    d.airport_name = request.form.get("airport_name")
    d.airport_code = request.form.get("airport_code")
    d.region = request.form.get("region")
    d.starting_price = request.form.get("starting_price", 0)
    d.visa_required = _bool(request.form.get("visa_required"))
    d.flight_duration = request.form.get("flight_duration")
    d.weather = request.form.get("weather")
    d.best_season = request.form.get("best_season")
    d.is_popular = _bool(request.form.get("is_popular"))
    d.description = request.form.get("description")
    db.session.commit()
    flash("Destination updated.", "success")
    return redirect(url_for("admin.destinations"))


@admin_bp.route("/destinations/<int:item_id>/delete", methods=["POST"])
def delete_destination(item_id):
    d = Destination.query.get_or_404(item_id)
    db.session.delete(d)
    db.session.commit()
    flash("Destination deleted.", "info")
    return redirect(url_for("admin.destinations"))


@admin_bp.route("/airlines", methods=["GET", "POST"])
def airlines():
    if request.method == "POST":
        a = Airline(
            name=request.form["name"], iata_code=request.form.get("iata_code"),
            country=request.form.get("country"), website=request.form.get("website"),
            rating=request.form.get("rating", 4.0),
            business_class=_bool(request.form.get("business_class")),
            economy_class=_bool(request.form.get("economy_class")),
        )
        db.session.add(a)
        db.session.commit()
        flash("Airline added successfully.", "success")
        return redirect(url_for("admin.airlines"))
    search = request.args.get("q", "").strip()
    query = Airline.query
    if search:
        query = query.filter(Airline.name.ilike(f"%{search}%"))
    return render_template("admin/airlines.html", airlines=query.order_by(Airline.name).all(), search=search)


@admin_bp.route("/airlines/<int:item_id>/edit", methods=["POST"])
def edit_airline(item_id):
    a = Airline.query.get_or_404(item_id)
    a.name = request.form["name"]
    a.iata_code = request.form.get("iata_code")
    a.country = request.form.get("country")
    a.website = request.form.get("website")
    a.rating = request.form.get("rating", 4.0)
    a.business_class = _bool(request.form.get("business_class"))
    a.economy_class = _bool(request.form.get("economy_class"))
    db.session.commit()
    flash("Airline updated.", "success")
    return redirect(url_for("admin.airlines"))


@admin_bp.route("/airlines/<int:item_id>/delete", methods=["POST"])
def delete_airline(item_id):
    a = Airline.query.get_or_404(item_id)
    db.session.delete(a)
    db.session.commit()
    flash("Airline deleted.", "info")
    return redirect(url_for("admin.airlines"))


@admin_bp.route("/packages", methods=["GET", "POST"])
def packages():
    if request.method == "POST":
        p = Package(
            name=request.form["name"], destination_id=request.form.get("destination_id"),
            category=request.form.get("category"), duration_days=request.form.get("duration_days", 5),
            price=request.form.get("price", 0), description=request.form.get("description"),
            inclusions=request.form.get("inclusions"), is_featured=_bool(request.form.get("is_featured")),
        )
        db.session.add(p)
        db.session.commit()
        flash("Package added successfully.", "success")
        return redirect(url_for("admin.packages"))
    return render_template("admin/packages.html", packages=Package.query.order_by(Package.name).all(),
                            destinations=Destination.query.order_by(Destination.city).all())


@admin_bp.route("/packages/<int:item_id>/edit", methods=["POST"])
def edit_package(item_id):
    p = Package.query.get_or_404(item_id)
    p.name = request.form["name"]
    p.destination_id = request.form.get("destination_id")
    p.category = request.form.get("category")
    p.duration_days = request.form.get("duration_days", 5)
    p.price = request.form.get("price", 0)
    p.description = request.form.get("description")
    p.inclusions = request.form.get("inclusions")
    p.is_featured = _bool(request.form.get("is_featured"))
    db.session.commit()
    flash("Package updated.", "success")
    return redirect(url_for("admin.packages"))


@admin_bp.route("/packages/<int:item_id>/delete", methods=["POST"])
def delete_package(item_id):
    p = Package.query.get_or_404(item_id)
    db.session.delete(p)
    db.session.commit()
    flash("Package deleted.", "info")
    return redirect(url_for("admin.packages"))


@admin_bp.route("/hotels", methods=["GET", "POST"])
def hotels():
    if request.method == "POST":
        h = Hotel(
            name=request.form["name"], destination_id=request.form.get("destination_id"),
            star_rating=request.form.get("star_rating", 4), price_per_night=request.form.get("price_per_night", 0),
            description=request.form.get("description"), amenities=request.form.get("amenities"),
            is_featured=_bool(request.form.get("is_featured")),
        )
        db.session.add(h)
        db.session.commit()
        flash("Hotel added successfully.", "success")
        return redirect(url_for("admin.hotels"))
    return render_template("admin/hotels.html", hotels=Hotel.query.order_by(Hotel.name).all(),
                            destinations=Destination.query.order_by(Destination.city).all())


@admin_bp.route("/hotels/<int:item_id>/edit", methods=["POST"])
def edit_hotel(item_id):
    h = Hotel.query.get_or_404(item_id)
    h.name = request.form["name"]
    h.destination_id = request.form.get("destination_id")
    h.star_rating = request.form.get("star_rating", 4)
    h.price_per_night = request.form.get("price_per_night", 0)
    h.description = request.form.get("description")
    h.amenities = request.form.get("amenities")
    h.is_featured = _bool(request.form.get("is_featured"))
    db.session.commit()
    flash("Hotel updated.", "success")
    return redirect(url_for("admin.hotels"))


@admin_bp.route("/hotels/<int:item_id>/delete", methods=["POST"])
def delete_hotel(item_id):
    h = Hotel.query.get_or_404(item_id)
    db.session.delete(h)
    db.session.commit()
    flash("Hotel deleted.", "info")
    return redirect(url_for("admin.hotels"))


# =========================================================================
# PAYMENTS
# =========================================================================
@admin_bp.route("/payments")
def payments():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    query = Payment.query.join(Booking)
    if search:
        query = query.filter(or_(Payment.receipt_number.ilike(f"%{search}%"),
                                  Booking.booking_id.ilike(f"%{search}%")))
    if status:
        query = query.filter(Payment.status == status)
    payment_list = query.order_by(Payment.paid_at.desc()).all()
    return render_template("admin/payments.html", payments=payment_list, search=search, status=status)


@admin_bp.route("/payments/export")
def export_payments():
    rows = [(p.receipt_number, p.booking.booking_id, p.method, p.transaction_id, float(p.amount), p.status,
              p.paid_at.strftime("%Y-%m-%d %H:%M")) for p in Payment.query.order_by(Payment.paid_at.desc()).all()]
    headers = ["Receipt No", "Booking ID", "Method", "Transaction ID", "Amount", "Status", "Paid At"]
    return to_csv_response(rows, headers, "payments_export.csv")


# =========================================================================
# EMPLOYEES
# =========================================================================
@admin_bp.route("/employees", methods=["GET", "POST"])
def employees():
    if request.method == "POST":
        user = User(full_name=request.form["full_name"], email=request.form["email"],
                    phone=request.form.get("phone"), role="employee")
        user.set_password(request.form.get("password", "Employee@123"))
        db.session.add(user)
        db.session.flush()
        db.session.add(Employee(user_id=user.id, designation=request.form.get("designation"),
                                 department=request.form.get("department"), hire_date=date.today()))
        db.session.commit()
        flash("Employee added successfully.", "success")
        return redirect(url_for("admin.employees"))
    employee_list = Employee.query.join(User).order_by(User.full_name).all()
    return render_template("admin/employees.html", employees=employee_list)


@admin_bp.route("/employees/<int:item_id>/toggle", methods=["POST"])
def toggle_employee(item_id):
    emp = Employee.query.get_or_404(item_id)
    emp.is_active = not emp.is_active
    db.session.commit()
    flash("Employee status updated.", "success")
    return redirect(url_for("admin.employees"))


# =========================================================================
# CONTACT MESSAGES / CHATBOT LOGS
# =========================================================================
@admin_bp.route("/messages")
def messages():
    message_list = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages.html", messages=message_list)


@admin_bp.route("/messages/<int:item_id>/read", methods=["POST"])
def mark_message_read(item_id):
    msg = ContactMessage.query.get_or_404(item_id)
    msg.is_read = True
    db.session.commit()
    return redirect(url_for("admin.messages"))


@admin_bp.route("/messages/<int:item_id>/delete", methods=["POST"])
def delete_message(item_id):
    msg = ContactMessage.query.get_or_404(item_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message deleted.", "info")
    return redirect(url_for("admin.messages"))


@admin_bp.route("/chatlogs")
def chatlogs():
    logs = ChatLog.query.order_by(ChatLog.created_at.desc()).limit(300).all()
    return render_template("admin/chatlogs.html", logs=logs)


# =========================================================================
# GALLERY / TESTIMONIALS / NEWS / FAQ
# =========================================================================
@admin_bp.route("/gallery", methods=["GET", "POST"])
def gallery():
    if request.method == "POST":
        db.session.add(Gallery(image=request.form["image"], caption=request.form.get("caption"),
                                category=request.form.get("category", "General")))
        db.session.commit()
        flash("Gallery image added.", "success")
        return redirect(url_for("admin.gallery"))
    return render_template("admin/gallery.html", items=Gallery.query.order_by(Gallery.created_at.desc()).all())


@admin_bp.route("/gallery/<int:item_id>/delete", methods=["POST"])
def delete_gallery(item_id):
    g = Gallery.query.get_or_404(item_id)
    db.session.delete(g)
    db.session.commit()
    flash("Gallery image removed.", "info")
    return redirect(url_for("admin.gallery"))


@admin_bp.route("/testimonials", methods=["GET", "POST"])
def testimonials():
    if request.method == "POST":
        db.session.add(Testimonial(customer_name=request.form["customer_name"], rating=request.form.get("rating", 5),
                                    destination=request.form.get("destination"), message=request.form["message"]))
        db.session.commit()
        flash("Testimonial added.", "success")
        return redirect(url_for("admin.testimonials"))
    return render_template("admin/testimonials.html", items=Testimonial.query.order_by(Testimonial.created_at.desc()).all())


@admin_bp.route("/testimonials/<int:item_id>/toggle", methods=["POST"])
def toggle_testimonial(item_id):
    t = Testimonial.query.get_or_404(item_id)
    t.is_approved = not t.is_approved
    db.session.commit()
    return redirect(url_for("admin.testimonials"))


@admin_bp.route("/testimonials/<int:item_id>/delete", methods=["POST"])
def delete_testimonial(item_id):
    t = Testimonial.query.get_or_404(item_id)
    db.session.delete(t)
    db.session.commit()
    flash("Testimonial deleted.", "info")
    return redirect(url_for("admin.testimonials"))


@admin_bp.route("/news", methods=["GET", "POST"])
def news():
    if request.method == "POST":
        title = request.form["title"]
        slug = request.form.get("slug") or title.lower().replace(" ", "-")[:200]
        db.session.add(News(title=title, slug=slug, summary=request.form.get("summary"),
                             content=request.form.get("content"), author=request.form.get("author", "Fly Happy Team")))
        db.session.commit()
        flash("News article added.", "success")
        return redirect(url_for("admin.news"))
    return render_template("admin/news.html", items=News.query.order_by(News.published_at.desc()).all())


@admin_bp.route("/news/<int:item_id>/delete", methods=["POST"])
def delete_news(item_id):
    n = News.query.get_or_404(item_id)
    db.session.delete(n)
    db.session.commit()
    flash("News article deleted.", "info")
    return redirect(url_for("admin.news"))


@admin_bp.route("/faqs", methods=["GET", "POST"])
def faqs():
    if request.method == "POST":
        db.session.add(FAQ(question=request.form["question"], answer=request.form["answer"],
                            category=request.form.get("category", "General")))
        db.session.commit()
        flash("FAQ added.", "success")
        return redirect(url_for("admin.faqs"))
    return render_template("admin/faqs.html", items=FAQ.query.order_by(FAQ.category).all())


@admin_bp.route("/faqs/<int:item_id>/delete", methods=["POST"])
def delete_faq(item_id):
    f = FAQ.query.get_or_404(item_id)
    db.session.delete(f)
    db.session.commit()
    flash("FAQ deleted.", "info")
    return redirect(url_for("admin.faqs"))


# =========================================================================
# REPORTS
# =========================================================================
@admin_bp.route("/reports")
def reports():
    today = date.today()

    daily_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        func.date(Payment.paid_at) == today, Payment.status == "completed").scalar()
    monthly_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        func.strftime("%Y-%m", Payment.paid_at) == today.strftime("%Y-%m"), Payment.status == "completed").scalar()
    yearly_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        func.strftime("%Y", Payment.paid_at) == today.strftime("%Y"), Payment.status == "completed").scalar()

    top_destinations = (
        db.session.query(Destination.city, Destination.country, func.count(Booking.id).label("cnt"))
        .join(Booking).group_by(Destination.id).order_by(func.count(Booking.id).desc()).limit(5).all()
    )
    top_airlines = (
        db.session.query(Airline.name, func.count(Booking.id).label("cnt"))
        .join(Booking).group_by(Airline.id).order_by(func.count(Booking.id).desc()).limit(5).all()
    )
    top_customers = (
        db.session.query(User.full_name, func.coalesce(func.sum(Booking.total_price), 0).label("total"))
        .join(Booking, Booking.customer_id == User.id).group_by(User.id).order_by(func.sum(Booking.total_price).desc()).limit(5).all()
    )

    return render_template(
        "admin/reports.html",
        daily_revenue=daily_revenue, monthly_revenue=monthly_revenue, yearly_revenue=yearly_revenue,
        top_destinations=top_destinations, top_airlines=top_airlines, top_customers=top_customers,
    )
