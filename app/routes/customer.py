"""Customer-facing dashboard: bookings, payments, profile, password, support."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Booking, Payment, ContactMessage
from app.forms import ProfileForm, ChangePasswordForm, ContactForm

customer_bp = Blueprint("customer", __name__, url_prefix="/dashboard")


@customer_bp.before_request
@login_required
def require_login():
    pass


@customer_bp.route("/")
def dashboard():
    bookings = current_user.bookings.order_by(Booking.created_at.desc()).all()
    stats = {
        "total_bookings": len(bookings),
        "confirmed": len([b for b in bookings if b.status == "confirmed"]),
        "pending": len([b for b in bookings if b.status == "pending"]),
        "cancelled": len([b for b in bookings if b.status == "cancelled"]),
    }
    return render_template("customer/dashboard.html", bookings=bookings[:5], stats=stats)


@customer_bp.route("/bookings")
def bookings():
    status = request.args.get("status", "").strip()
    query = current_user.bookings
    if status:
        query = query.filter_by(status=status)
    booking_list = query.order_by(Booking.created_at.desc()).all()
    return render_template("customer/bookings.html", bookings=booking_list, status=status)


@customer_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id:
        flash("You are not authorized to cancel this booking.", "danger")
        return redirect(url_for("customer.bookings"))
    if booking.status in ("cancelled", "completed"):
        flash("This booking cannot be cancelled.", "warning")
    else:
        booking.status = "cancelled"
        db.session.commit()
        flash(f"Booking {booking.booking_id} has been cancelled.", "success")
    return redirect(url_for("customer.bookings"))


@customer_bp.route("/payments")
def payments():
    booking_ids = [b.id for b in current_user.bookings]
    payment_list = Payment.query.filter(Payment.booking_id.in_(booking_ids)).order_by(Payment.paid_at.desc()).all()
    return render_template("customer/payments.html", payments=payment_list)


@customer_bp.route("/profile", methods=["GET", "POST"])
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.phone = form.phone.data.strip()
        current_user.cnic = form.cnic.data.strip() if form.cnic.data else None
        current_user.passport_number = form.passport_number.data.strip() if form.passport_number.data else None
        current_user.address = form.address.data.strip() if form.address.data else None
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("customer.profile"))
    return render_template("customer/profile.html", form=form)


@customer_bp.route("/change-password", methods=["GET", "POST"])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("customer.dashboard"))
    return render_template("customer/change_password.html", form=form)


@customer_bp.route("/support", methods=["GET", "POST"])
def support():
    form = ContactForm(email=current_user.email, name=current_user.full_name)
    if form.validate_on_submit():
        db.session.add(ContactMessage(
            name=form.name.data.strip(), email=form.email.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else current_user.phone,
            subject=form.subject.data.strip(), message=form.message.data.strip(),
        ))
        db.session.commit()
        flash("Your support request has been submitted. Our team will contact you shortly.", "success")
        return redirect(url_for("customer.support"))
    return render_template("customer/support.html", form=form)
