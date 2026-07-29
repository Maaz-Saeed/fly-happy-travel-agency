"""Public-facing marketing & content routes (no login required)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_

from app.extensions import db
from app.models import (
    Destination, Airline, Package, Hotel, Testimonial, TeamMember, News, FAQ,
    Gallery, ContactMessage, Newsletter,
)
from app.forms import ContactForm

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    featured_destinations = Destination.query.filter_by(is_popular=True).limit(8).all()
    featured_packages = Package.query.filter_by(is_featured=True).limit(6).all()
    featured_hotels = Hotel.query.filter_by(is_featured=True).limit(6).all()
    top_airlines = Airline.query.order_by(Airline.rating.desc()).limit(10).all()
    testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).limit(6).all()
    latest_news = News.query.order_by(News.published_at.desc()).limit(3).all()
    gallery_preview = Gallery.query.order_by(Gallery.created_at.desc()).limit(8).all()
    return render_template(
        "public/home.html",
        featured_destinations=featured_destinations,
        featured_packages=featured_packages,
        featured_hotels=featured_hotels,
        top_airlines=top_airlines,
        testimonials=testimonials,
        latest_news=latest_news,
        gallery_preview=gallery_preview,
    )


@public_bp.route("/about")
def about():
    team_preview = TeamMember.query.order_by(TeamMember.display_order).limit(4).all()
    return render_template("public/about.html", team_preview=team_preview)


@public_bp.route("/services")
def services():
    return render_template("public/services.html")


@public_bp.route("/destinations")
def destinations():
    query = Destination.query
    search = request.args.get("q", "").strip()
    region = request.args.get("region", "").strip()
    visa = request.args.get("visa", "").strip()

    if search:
        query = query.filter(or_(Destination.city.ilike(f"%{search}%"),
                                  Destination.country.ilike(f"%{search}%")))
    if region:
        query = query.filter(Destination.region == region)
    if visa == "yes":
        query = query.filter(Destination.visa_required.is_(True))
    elif visa == "no":
        query = query.filter(Destination.visa_required.is_(False))

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Destination.is_popular.desc(), Destination.country).paginate(
        page=page, per_page=12, error_out=False)
    regions = [r[0] for r in db.session.query(Destination.region).distinct().order_by(Destination.region)]

    return render_template("public/destinations.html", pagination=pagination,
                            destinations=pagination.items, regions=regions,
                            search=search, region=region, visa=visa)


@public_bp.route("/destinations/<int:destination_id>")
def destination_detail(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    related = Destination.query.filter(Destination.region == destination.region,
                                        Destination.id != destination.id).limit(4).all()
    packages = destination.packages.all()
    hotels = destination.hotels.all()
    airlines = Airline.query.order_by(Airline.rating.desc()).limit(6).all()
    return render_template("public/destination_detail.html", destination=destination,
                            related=related, packages=packages, hotels=hotels, airlines=airlines)


@public_bp.route("/airlines")
def airlines():
    search = request.args.get("q", "").strip()
    query = Airline.query
    if search:
        query = query.filter(or_(Airline.name.ilike(f"%{search}%"), Airline.country.ilike(f"%{search}%")))
    airline_list = query.order_by(Airline.rating.desc()).all()
    return render_template("public/airlines.html", airlines=airline_list, search=search)


@public_bp.route("/packages")
def packages():
    category = request.args.get("category", "").strip()
    query = Package.query
    if category:
        query = query.filter(Package.category == category)
    package_list = query.order_by(Package.is_featured.desc()).all()
    categories = [c[0] for c in db.session.query(Package.category).distinct()]
    return render_template("public/packages.html", packages=package_list, categories=categories, category=category)


@public_bp.route("/hotels")
def hotels():
    hotel_list = Hotel.query.order_by(Hotel.star_rating.desc()).all()
    return render_template("public/hotels.html", hotels=hotel_list)


@public_bp.route("/gallery")
def gallery():
    category = request.args.get("category", "").strip()
    query = Gallery.query
    if category:
        query = query.filter(Gallery.category == category)
    items = query.order_by(Gallery.created_at.desc()).all()
    categories = [c[0] for c in db.session.query(Gallery.category).distinct()]
    return render_template("public/gallery.html", items=items, categories=categories, category=category)


@public_bp.route("/team")
def team():
    members = TeamMember.query.order_by(TeamMember.display_order).all()
    return render_template("public/team.html", members=members)


@public_bp.route("/portfolio")
def portfolio():
    return render_template("public/portfolio.html")


@public_bp.route("/news")
def news():
    news_list = News.query.order_by(News.published_at.desc()).all()
    return render_template("public/news.html", news_list=news_list)


@public_bp.route("/news/<slug>")
def news_detail(slug):
    item = News.query.filter_by(slug=slug).first_or_404()
    others = News.query.filter(News.id != item.id).order_by(News.published_at.desc()).limit(3).all()
    return render_template("public/news_detail.html", item=item, others=others)


@public_bp.route("/faq")
def faq():
    faqs = FAQ.query.order_by(FAQ.category, FAQ.display_order).all()
    categories = sorted({f.category for f in faqs})
    return render_template("public/faq.html", faqs=faqs, categories=categories)


@public_bp.route("/testimonials")
def testimonials():
    items = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).all()
    return render_template("public/testimonials.html", testimonials=items)


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data.strip(), email=form.email.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            subject=form.subject.data.strip(), message=form.message.data.strip(),
        )
        db.session.add(msg)
        db.session.commit()
        flash("Thank you for reaching out! Our team will contact you shortly.", "success")
        return redirect(url_for("public.contact"))
    return render_template("public/contact.html", form=form)


@public_bp.route("/newsletter/subscribe", methods=["POST"])
def newsletter_subscribe():
    email = request.form.get("email", "").strip().lower()
    if email:
        if not Newsletter.query.filter_by(email=email).first():
            db.session.add(Newsletter(email=email))
            db.session.commit()
        flash("You're subscribed! Watch your inbox for the best travel deals.", "success")
    return redirect(request.referrer or url_for("public.home"))
