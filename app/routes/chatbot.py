"""Rule-based virtual travel assistant. Every exchange is logged to ChatLog."""
import uuid

from flask import Blueprint, request, jsonify, session, current_app
from flask_login import current_user

from app.extensions import db
from app.models import ChatLog

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")

# Ordered list of (keywords, response-template) — first match wins.
RULES = [
    (["office timing", "office hours", "opening hours", "working hours", "open on"],
     "Our office is open {hours}. We're closed on Sundays and public holidays, but our emergency line stays open 24/7."),

    (["visa process", "how to apply visa", "visa application", "apply for visa", "visa requirement"],
     "To apply for a visa: choose the visa type (visit, work, student or business) on our Services page, submit your documents, "
     "and one of our certified visa consultants will guide you through the embassy requirements and appointment scheduling."),

    (["passport", "passport requirement", "new passport", "renew passport"],
     "For a passport application or renewal, you typically need your original CNIC/B-Form, previous passport (if renewing), "
     "2 passport-sized photographs and proof of address. Visit our office or contact support for full document verification."),

    (["how to book", "booking process", "how do i book", "book a flight", "book a ticket"],
     "Booking is easy! Go to 'Book Now', search your destination, choose your airline, dates and seat class, fill in passenger "
     "details, and confirm payment. You'll instantly receive a Booking ID and Ticket Number."),

    (["refund", "cancellation policy", "cancel my booking", "cancel booking"],
     "Refunds depend on the airline's fare rules. Fully refundable fares are processed within 7-15 working days. "
     "You can request a cancellation any time from your Dashboard > My Bookings."),

    (["payment method", "how to pay", "payment option", "jazzcash", "easypaisa"],
     "We accept Visa, MasterCard, Debit Cards, JazzCash, EasyPaisa, Bank Transfer, and Cash payments at our office."),

    (["insurance", "travel insurance"],
     "Yes, we offer comprehensive travel insurance covering medical emergencies, trip cancellation, baggage loss and delays."),

    (["destination", "where can i travel", "which countries", "available destinations"],
     "We currently arrange travel to over 80 destinations across Asia, the Middle East, Europe, the Americas, Africa and Oceania. "
     "Check our Destinations page for the full list with prices and details."),

    (["office location", "where are you located", "address", "office address"],
     "Our head office is located at {address}. You're welcome to visit us during office hours!"),

    (["phone number", "contact number", "call you", "phone"],
     "You can call us at {phone} during office hours, or our 24/7 emergency line at {emergency} for urgent travel issues."),

    (["email"],
     "You can reach us by email at {email} — we usually respond within a few hours during business days."),

    (["flight status", "is my flight on time", "check flight"],
     "For real-time flight status, please check your airline's official website or app using your ticket number. "
     "Our support team can also assist you directly — just share your Booking ID."),

    (["holiday package", "vacation package", "umrah", "hajj", "tour package"],
     "We offer a wide range of Holiday, Family, Corporate, Group, Umrah and Hajj packages. Visit our Packages page to explore "
     "current offers, or tell me a destination and I can point you in the right direction!"),

    (["hello", "hi", "hey", "assalam", "salam"],
     "Hello! Welcome to {company}. How can I help you today — bookings, visas, packages, or payments?"),

    (["thank", "thanks"],
     "You're most welcome! Is there anything else I can help you with?"),
]

FALLBACK = ("I'm sorry, I didn't quite understand that. I can help with office timings, visa process, passport requirements, "
            "the booking process, refund policy, payment methods, travel insurance, destinations, or contact details. "
            "For anything else, please call us at {phone} or use the Contact page.")


def get_reply(message):
    text = message.lower()
    company = current_app.config["COMPANY_NAME"]
    context = {
        "hours": current_app.config["COMPANY_HOURS"],
        "address": current_app.config["COMPANY_ADDRESS"],
        "phone": current_app.config["COMPANY_PHONE"],
        "emergency": current_app.config["COMPANY_EMERGENCY_PHONE"],
        "email": current_app.config["COMPANY_EMAIL"],
        "company": company,
    }
    for keywords, template in RULES:
        if any(k in text for k in keywords):
            return template.format(**context)
    return FALLBACK.format(**context)


@chatbot_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"reply": "Please type a message so I can help you."})

    if "chat_session_id" not in session:
        session["chat_session_id"] = uuid.uuid4().hex
    session_id = session["chat_session_id"]

    reply = get_reply(message)

    log = ChatLog(
        session_id=session_id,
        user_id=current_user.id if current_user.is_authenticated else None,
        user_message=message[:2000],
        bot_response=reply[:2000],
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"reply": reply})
