"""Payment simulation, receipt and invoice generation."""
import random

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Booking, Payment
from app.forms import PaymentForm

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")


def _authorize(booking):
    return booking.customer_id == current_user.id or current_user.is_admin


@payment_bp.route("/checkout/<int:booking_id>", methods=["GET", "POST"])
@login_required
def checkout(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if not _authorize(booking):
        flash("You are not authorized to pay for this booking.", "danger")
        return redirect(url_for("customer.dashboard"))

    if booking.status in ("confirmed", "completed"):
        flash("This booking has already been paid for.", "info")
        return redirect(url_for("payment.invoice", booking_id=booking.id))

    form = PaymentForm()
    if form.validate_on_submit():
        # Payment simulation: always succeeds unless explicitly "Cash" (marked pending until office visit)
        status = "pending" if form.method.data == "Cash" else "completed"
        payment = Payment(
            receipt_number=Payment.generate_receipt_number(),
            booking_id=booking.id,
            amount=booking.total_price,
            method=form.method.data,
            transaction_id=f"TXN{random.randint(100000000, 999999999)}",
            status=status,
        )
        db.session.add(payment)
        booking.status = "confirmed" if status == "completed" else "pending"
        db.session.commit()

        flash("Payment successful! Your booking is now confirmed." if status == "completed"
              else "Booking noted for Cash payment — please pay at our office to confirm.", "success")
        return redirect(url_for("payment.receipt", payment_id=payment.id))

    return render_template("payment/checkout.html", form=form, booking=booking)


@payment_bp.route("/receipt/<int:payment_id>")
@login_required
def receipt(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if not _authorize(payment.booking):
        flash("You are not authorized to view this receipt.", "danger")
        return redirect(url_for("customer.dashboard"))
    return render_template("payment/receipt.html", payment=payment, booking=payment.booking)


@payment_bp.route("/invoice/<int:booking_id>")
@login_required
def invoice(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if not _authorize(booking):
        flash("You are not authorized to view this invoice.", "danger")
        return redirect(url_for("customer.dashboard"))
    payments = booking.payments.order_by(Payment.paid_at.desc()).all()
    return render_template("payment/invoice.html", booking=booking, payments=payments)
