"""Flight booking search + booking creation."""
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.extensions import db
from app.models import Destination, Airline, Booking
from app.forms import BookingForm

booking_bp = Blueprint("booking", __name__, url_prefix="/booking")

SEAT_MULTIPLIER = {"Economy": 1.0, "Business": 1.6, "First": 2.2}
TRIP_MULTIPLIER = {"one_way": 1.0, "round_trip": 1.85}


def calculate_price(base_price, seat_class, trip_type, adults, children, infants):
    multiplier = SEAT_MULTIPLIER.get(seat_class, 1.0) * TRIP_MULTIPLIER.get(trip_type, 1.0)
    payable_heads = (adults or 0) + (children or 0) + 0.25 * (infants or 0)
    return round(Decimal(str(base_price)) * Decimal(str(multiplier)) * Decimal(str(payable_heads)), 2)


@booking_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    query = Destination.query
    if q:
        query = query.filter(or_(Destination.city.ilike(f"%{q}%"), Destination.country.ilike(f"%{q}%")))
    destinations = query.order_by(Destination.is_popular.desc()).limit(24).all()
    return render_template("booking/search.html", destinations=destinations, q=q)


@booking_bp.route("/new/<int:destination_id>", methods=["GET", "POST"])
@login_required
def new(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    form = BookingForm()
    form.destination_id.choices = [(destination.id, f"{destination.city}, {destination.country}")]
    form.destination_id.data = destination.id
    form.airline_id.choices = [(a.id, a.name) for a in Airline.query.order_by(Airline.name).all()]

    if request.method == "GET":
        form.passenger_name.data = current_user.full_name
        form.passport_number.data = current_user.passport_number
        form.cnic.data = current_user.cnic
        form.phone.data = current_user.phone
        form.email.data = current_user.email

    if form.validate_on_submit():
        total_price = calculate_price(
            destination.starting_price, form.seat_class.data, form.trip_type.data,
            form.adults.data, form.children.data, form.infants.data,
        )
        booking = Booking(
            booking_id=Booking.generate_booking_id(),
            ticket_number=Booking.generate_ticket_number(),
            customer_id=current_user.id,
            destination_id=destination.id,
            airline_id=form.airline_id.data,
            trip_type=form.trip_type.data,
            departure_date=form.departure_date.data,
            return_date=form.return_date.data if form.trip_type.data == "round_trip" else None,
            adults=form.adults.data, children=form.children.data or 0, infants=form.infants.data or 0,
            seat_class=form.seat_class.data, meal_preference=form.meal_preference.data,
            passenger_name=form.passenger_name.data, passport_number=form.passport_number.data,
            cnic=form.cnic.data, phone=form.phone.data, email=form.email.data,
            special_requests=form.special_requests.data,
            total_price=total_price, status="pending",
        )
        db.session.add(booking)
        db.session.commit()
        flash(f"Booking created! Your Booking ID is {booking.booking_id}. Please complete payment to confirm.", "success")
        return redirect(url_for("payment.checkout", booking_id=booking.id))

    return render_template("booking/form.html", form=form, destination=destination)


@booking_bp.route("/confirmation/<int:booking_id>")
@login_required
def confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id and not current_user.is_admin:
        flash("You are not authorized to view this booking.", "danger")
        return redirect(url_for("customer.dashboard"))
    return render_template("booking/confirmation.html", booking=booking)
