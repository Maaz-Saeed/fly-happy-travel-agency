"""WTForms form definitions. Flask-WTF provides automatic CSRF protection."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField, IntegerField,
    DateField, BooleanField, EmailField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange


class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=120)])
    email = EmailField("Email Address", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=7, max=30)])
    cnic = StringField("CNIC", validators=[Optional(), Length(max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )


class LoginForm(FlaskForm):
    email = EmailField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match")],
    )


class ProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=120)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=7, max=30)])
    cnic = StringField("CNIC", validators=[Optional(), Length(max=20)])
    passport_number = StringField("Passport Number", validators=[Optional(), Length(max=20)])
    address = StringField("Address", validators=[Optional(), Length(max=255)])


class ContactForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = EmailField("Email Address", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=30)])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=200)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=2000)])


class BookingForm(FlaskForm):
    destination_id = SelectField("Destination", coerce=int, validators=[DataRequired()])
    airline_id = SelectField("Airline", coerce=int, validators=[DataRequired()])
    trip_type = SelectField("Trip Type", choices=[("one_way", "One Way"), ("round_trip", "Round Trip")],
                             default="round_trip")
    departure_date = DateField("Departure Date", validators=[DataRequired()])
    return_date = DateField("Return Date", validators=[Optional()])

    adults = IntegerField("Adults", validators=[DataRequired(), NumberRange(min=1, max=9)], default=1)
    children = IntegerField("Children", validators=[Optional(), NumberRange(min=0, max=9)], default=0)
    infants = IntegerField("Infants", validators=[Optional(), NumberRange(min=0, max=9)], default=0)

    seat_class = SelectField("Seat Class", choices=[("Economy", "Economy"), ("Business", "Business"), ("First", "First Class")])
    meal_preference = SelectField("Meal Preference", choices=[
        ("Standard", "Standard"), ("Vegetarian", "Vegetarian"), ("Halal", "Halal"),
        ("Vegan", "Vegan"), ("No Meal", "No Meal"),
    ])

    passenger_name = StringField("Full Name (as on Passport)", validators=[DataRequired(), Length(max=120)])
    passport_number = StringField("Passport Number", validators=[DataRequired(), Length(max=20)])
    cnic = StringField("CNIC", validators=[DataRequired(), Length(max=20)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(max=30)])
    email = EmailField("Email Address", validators=[DataRequired(), Email()])
    special_requests = TextAreaField("Special Requests", validators=[Optional(), Length(max=1000)])


class PaymentForm(FlaskForm):
    method = SelectField("Payment Method", choices=[
        ("Visa Card", "Visa Card"), ("MasterCard", "MasterCard"), ("Debit Card", "Debit Card"),
        ("JazzCash", "JazzCash"), ("EasyPaisa", "EasyPaisa"), ("Bank Transfer", "Bank Transfer"),
        ("Cash", "Cash"),
    ])
    card_number = StringField("Card Number", validators=[Optional(), Length(max=20)])
    card_name = StringField("Name on Card", validators=[Optional(), Length(max=120)])
    card_expiry = StringField("Expiry (MM/YY)", validators=[Optional(), Length(max=7)])
    card_cvv = StringField("CVV", validators=[Optional(), Length(max=4)])
    mobile_account_number = StringField("Mobile Account Number", validators=[Optional(), Length(max=20)])
