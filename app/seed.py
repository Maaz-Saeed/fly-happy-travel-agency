"""Seed the database with realistic sample data for Fly Happy International Travels.

Run with:  flask --app run.py init-db
"""
import random
from datetime import date, datetime, timedelta

from app.extensions import db
from app.models import (
    User, Employee, Destination, Airline, Package, Hotel, Booking, Payment,
    Testimonial, TeamMember, News, FAQ, Gallery, ContactMessage,
)

# ---------------------------------------------------------------------------
# DESTINATIONS  (country, city, airport_name, airport_code, region,
#                base_price, visa_required, flight_duration, weather, season, popular)
# ---------------------------------------------------------------------------
DESTINATIONS = [
    ("Pakistan", "Islamabad", "Islamabad International Airport", "ISB", "Domestic", 15000, False, "Domestic", "Mild, Four Seasons", "Mar - Oct", True),
    ("Pakistan", "Karachi", "Jinnah International Airport", "KHI", "Domestic", 12000, False, "Domestic", "Hot & Humid", "Nov - Feb", True),
    ("Pakistan", "Lahore", "Allama Iqbal International Airport", "LHE", "Domestic", 12000, False, "Domestic", "Hot Summers, Cool Winters", "Oct - Mar", True),
    ("Saudi Arabia", "Jeddah", "King Abdulaziz International Airport", "JED", "Middle East", 85000, True, "3h 15m", "Hot & Arid", "Nov - Feb", True),
    ("Saudi Arabia", "Madinah", "Prince Mohammad Bin Abdulaziz Airport", "MED", "Middle East", 90000, True, "3h 30m", "Hot & Arid", "Nov - Feb", True),
    ("Saudi Arabia", "Riyadh", "King Khalid International Airport", "RUH", "Middle East", 82000, True, "3h 10m", "Hot & Arid", "Nov - Feb", False),
    ("United Arab Emirates", "Dubai", "Dubai International Airport", "DXB", "Middle East", 65000, True, "3h 05m", "Hot & Sunny", "Nov - Mar", True),
    ("United Arab Emirates", "Abu Dhabi", "Zayed International Airport", "AUH", "Middle East", 63000, True, "3h 00m", "Hot & Sunny", "Nov - Mar", True),
    ("United Arab Emirates", "Sharjah", "Sharjah International Airport", "SHJ", "Middle East", 58000, True, "2h 55m", "Hot & Sunny", "Nov - Mar", False),
    ("Qatar", "Doha", "Hamad International Airport", "DOH", "Middle East", 68000, True, "3h 20m", "Hot & Arid", "Nov - Mar", True),
    ("Bahrain", "Manama", "Bahrain International Airport", "BAH", "Middle East", 70000, True, "3h 10m", "Hot & Humid", "Nov - Mar", False),
    ("Kuwait", "Kuwait City", "Kuwait International Airport", "KWI", "Middle East", 72000, True, "3h 30m", "Hot & Dry", "Nov - Mar", False),
    ("Oman", "Muscat", "Muscat International Airport", "MCT", "Middle East", 60000, True, "2h 30m", "Hot & Arid", "Oct - Mar", True),
    ("Turkey", "Istanbul", "Istanbul Airport", "IST", "Middle East", 95000, True, "6h 45m", "Mediterranean", "Apr - Oct", True),
    ("Turkey", "Antalya", "Antalya Airport", "AYT", "Middle East", 98000, True, "7h 00m", "Mediterranean", "May - Sep", True),
    ("Jordan", "Amman", "Queen Alia International Airport", "AMM", "Middle East", 105000, True, "5h 30m", "Mild & Dry", "Mar - May", False),
    ("Lebanon", "Beirut", "Beirut Rafic Hariri Airport", "BEY", "Middle East", 110000, True, "5h 45m", "Mediterranean", "Apr - Oct", False),
    ("Malaysia", "Kuala Lumpur", "Kuala Lumpur International Airport", "KUL", "Asia", 78000, False, "6h 30m", "Tropical", "Dec - Feb", True),
    ("Thailand", "Bangkok", "Suvarnabhumi Airport", "BKK", "Asia", 82000, False, "6h 00m", "Tropical", "Nov - Feb", True),
    ("Thailand", "Phuket", "Phuket International Airport", "HKT", "Asia", 88000, False, "6h 45m", "Tropical", "Nov - Mar", True),
    ("Singapore", "Singapore", "Changi Airport", "SIN", "Asia", 92000, False, "6h 50m", "Tropical, Humid", "Feb - Apr", True),
    ("Indonesia", "Bali", "Ngurah Rai International Airport", "DPS", "Asia", 105000, False, "8h 30m", "Tropical", "Apr - Oct", True),
    ("Indonesia", "Jakarta", "Soekarno-Hatta Airport", "CGK", "Asia", 98000, False, "7h 45m", "Tropical", "May - Sep", False),
    ("China", "Beijing", "Beijing Capital International Airport", "PEK", "Asia", 88000, True, "7h 00m", "Four Seasons", "Sep - Nov", False),
    ("China", "Shanghai", "Shanghai Pudong Airport", "PVG", "Asia", 90000, True, "7h 30m", "Humid Subtropical", "Mar - May", False),
    ("Japan", "Tokyo", "Narita International Airport", "NRT", "Asia", 145000, True, "9h 30m", "Four Seasons", "Mar - May", True),
    ("Japan", "Osaka", "Kansai International Airport", "KIX", "Asia", 140000, True, "9h 45m", "Four Seasons", "Mar - May", False),
    ("South Korea", "Seoul", "Incheon International Airport", "ICN", "Asia", 135000, True, "8h 15m", "Four Seasons", "Sep - Nov", True),
    ("India", "New Delhi", "Indira Gandhi International Airport", "DEL", "Asia", 25000, True, "2h 00m", "Hot Summers", "Oct - Mar", False),
    ("India", "Mumbai", "Chhatrapati Shivaji Airport", "BOM", "Asia", 28000, True, "2h 30m", "Tropical", "Nov - Feb", False),
    ("Sri Lanka", "Colombo", "Bandaranaike International Airport", "CMB", "Asia", 60000, True, "4h 00m", "Tropical", "Dec - Mar", True),
    ("Nepal", "Kathmandu", "Tribhuvan International Airport", "KTM", "Asia", 45000, True, "2h 30m", "Temperate", "Oct - Nov", False),
    ("Maldives", "Male", "Velana International Airport", "MLE", "Asia", 150000, False, "5h 00m", "Tropical Paradise", "Nov - Apr", True),
    ("Vietnam", "Hanoi", "Noi Bai International Airport", "HAN", "Asia", 95000, True, "7h 15m", "Tropical", "Oct - Dec", False),
    ("Philippines", "Manila", "Ninoy Aquino International Airport", "MNL", "Asia", 100000, True, "8h 00m", "Tropical", "Dec - Feb", False),
    ("Hong Kong", "Hong Kong", "Hong Kong International Airport", "HKG", "Asia", 110000, False, "7h 45m", "Humid Subtropical", "Oct - Dec", False),
    ("Bangladesh", "Dhaka", "Hazrat Shahjalal International Airport", "DAC", "Asia", 35000, False, "3h 30m", "Tropical", "Nov - Feb", False),
    ("Azerbaijan", "Baku", "Heydar Aliyev International Airport", "GYD", "Asia", 75000, False, "3h 45m", "Mild", "Apr - Jun", True),
    ("Kazakhstan", "Almaty", "Almaty International Airport", "ALA", "Asia", 80000, True, "3h 15m", "Continental", "May - Sep", False),
    ("Uzbekistan", "Tashkent", "Islam Karimov Tashkent Airport", "TAS", "Asia", 70000, False, "2h 45m", "Continental", "Apr - Jun", False),
    ("United Kingdom", "London", "Heathrow Airport", "LHR", "Europe", 175000, True, "9h 30m", "Mild, Rainy", "Jun - Aug", True),
    ("Germany", "Frankfurt", "Frankfurt Airport", "FRA", "Europe", 165000, True, "8h 45m", "Temperate", "May - Sep", True),
    ("Germany", "Munich", "Munich Airport", "MUC", "Europe", 168000, True, "9h 00m", "Temperate", "Jun - Aug", False),
    ("France", "Paris", "Charles de Gaulle Airport", "CDG", "Europe", 178000, True, "9h 15m", "Temperate", "Apr - Jun", True),
    ("Italy", "Rome", "Leonardo da Vinci Airport", "FCO", "Europe", 172000, True, "8h 50m", "Mediterranean", "Apr - Jun", True),
    ("Italy", "Milan", "Milan Malpensa Airport", "MXP", "Europe", 170000, True, "8h 40m", "Mediterranean", "May - Sep", False),
    ("Spain", "Madrid", "Adolfo Suarez Madrid-Barajas Airport", "MAD", "Europe", 165000, True, "9h 30m", "Mediterranean", "Apr - Jun", True),
    ("Spain", "Barcelona", "Barcelona-El Prat Airport", "BCN", "Europe", 168000, True, "9h 45m", "Mediterranean", "May - Sep", True),
    ("Portugal", "Lisbon", "Humberto Delgado Airport", "LIS", "Europe", 175000, True, "10h 30m", "Mediterranean", "Jun - Sep", False),
    ("Switzerland", "Zurich", "Zurich Airport", "ZRH", "Europe", 185000, True, "8h 00m", "Alpine", "Jun - Sep", True),
    ("Austria", "Vienna", "Vienna International Airport", "VIE", "Europe", 172000, True, "8h 20m", "Continental", "May - Sep", False),
    ("Netherlands", "Amsterdam", "Amsterdam Schiphol Airport", "AMS", "Europe", 170000, True, "8h 55m", "Temperate, Rainy", "Apr - Aug", True),
    ("Belgium", "Brussels", "Brussels Airport", "BRU", "Europe", 173000, True, "9h 10m", "Temperate", "May - Sep", False),
    ("Norway", "Oslo", "Oslo Airport", "OSL", "Europe", 190000, True, "8h 30m", "Cold, Fjords", "May - Aug", False),
    ("Sweden", "Stockholm", "Stockholm Arlanda Airport", "ARN", "Europe", 188000, True, "8h 40m", "Cold", "Jun - Aug", False),
    ("Denmark", "Copenhagen", "Copenhagen Airport", "CPH", "Europe", 186000, True, "8h 50m", "Temperate", "Jun - Aug", False),
    ("Finland", "Helsinki", "Helsinki Airport", "HEL", "Europe", 182000, True, "6h 45m", "Cold", "Jun - Aug", False),
    ("Russia", "Moscow", "Sheremetyevo International Airport", "SVO", "Europe", 145000, True, "5h 30m", "Continental, Cold", "May - Sep", False),
    ("Greece", "Athens", "Athens International Airport", "ATH", "Europe", 160000, True, "6h 30m", "Mediterranean", "Apr - Oct", True),
    ("Poland", "Warsaw", "Warsaw Chopin Airport", "WAW", "Europe", 155000, True, "7h 45m", "Continental", "May - Sep", False),
    ("Ireland", "Dublin", "Dublin Airport", "DUB", "Europe", 178000, True, "10h 15m", "Mild, Rainy", "May - Sep", False),
    ("Czech Republic", "Prague", "Vaclav Havel Airport", "PRG", "Europe", 162000, True, "8h 10m", "Continental", "May - Sep", False),
    ("Canada", "Toronto", "Toronto Pearson International Airport", "YYZ", "Americas", 210000, True, "14h 30m", "Cold Winters", "Jun - Sep", True),
    ("Canada", "Vancouver", "Vancouver International Airport", "YVR", "Americas", 215000, True, "15h 00m", "Mild, Rainy", "Jun - Sep", False),
    ("United States", "New York", "John F. Kennedy International Airport", "JFK", "Americas", 225000, True, "15h 45m", "Four Seasons", "Apr - Jun", True),
    ("United States", "Los Angeles", "Los Angeles International Airport", "LAX", "Americas", 230000, True, "17h 30m", "Sunny, Mild", "Mar - May", True),
    ("United States", "Chicago", "O'Hare International Airport", "ORD", "Americas", 222000, True, "16h 00m", "Cold Winters", "May - Sep", False),
    ("Mexico", "Cancun", "Cancun International Airport", "CUN", "Americas", 245000, True, "19h 00m", "Tropical", "Nov - Apr", True),
    ("Brazil", "Sao Paulo", "Sao Paulo-Guarulhos Airport", "GRU", "Americas", 260000, True, "18h 30m", "Humid Subtropical", "Sep - Nov", False),
    ("Argentina", "Buenos Aires", "Ministro Pistarini Airport", "EZE", "Americas", 270000, True, "22h 00m", "Temperate", "Oct - Mar", False),
    ("Chile", "Santiago", "Arturo Merino Benitez Airport", "SCL", "Americas", 265000, True, "21h 00m", "Mediterranean", "Sep - Nov", False),
    ("Peru", "Lima", "Jorge Chavez International Airport", "LIM", "Americas", 255000, True, "20h 00m", "Mild, Dry", "May - Sep", False),
    ("Australia", "Sydney", "Sydney Kingsford Smith Airport", "SYD", "Oceania", 195000, True, "13h 30m", "Temperate", "Sep - Nov", True),
    ("Australia", "Melbourne", "Melbourne Airport", "MEL", "Oceania", 198000, True, "14h 00m", "Temperate", "Mar - May", False),
    ("New Zealand", "Auckland", "Auckland Airport", "AKL", "Oceania", 220000, True, "16h 30m", "Temperate Maritime", "Dec - Feb", False),
    ("South Africa", "Johannesburg", "OR Tambo International Airport", "JNB", "Africa", 150000, True, "10h 30m", "Mild, Dry", "Apr - Oct", True),
    ("South Africa", "Cape Town", "Cape Town International Airport", "CPT", "Africa", 155000, True, "11h 00m", "Mediterranean", "Nov - Mar", True),
    ("Egypt", "Cairo", "Cairo International Airport", "CAI", "Africa", 92000, True, "5h 15m", "Hot, Desert", "Oct - Apr", True),
    ("Kenya", "Nairobi", "Jomo Kenyatta International Airport", "NBO", "Africa", 130000, True, "8h 00m", "Tropical Savanna", "Jun - Oct", False),
    ("Morocco", "Casablanca", "Mohammed V International Airport", "CMN", "Africa", 145000, True, "10h 45m", "Mediterranean", "Apr - Oct", False),
    ("Tunisia", "Tunis", "Tunis-Carthage International Airport", "TUN", "Africa", 138000, True, "9h 30m", "Mediterranean", "Apr - Jun", False),
    ("Tanzania", "Zanzibar", "Abeid Amani Karume Airport", "ZNZ", "Africa", 160000, True, "9h 15m", "Tropical", "Jun - Oct", False),
    ("Georgia", "Tbilisi", "Tbilisi International Airport", "TBS", "Europe", 68000, False, "3h 30m", "Continental", "May - Sep", True),
    ("Armenia", "Yerevan", "Zvartnots International Airport", "EVN", "Europe", 72000, False, "3h 45m", "Continental", "May - Sep", False),
    ("Iraq", "Najaf", "Al Najaf International Airport", "NJF", "Middle East", 55000, True, "2h 45m", "Hot, Arid", "Nov - Feb", True),
]

DESTINATION_DESC_TEMPLATE = (
    "Discover {city}, {country} — one of our most requested destinations. Fly Happy "
    "International Travels arranges everything from flights and visas to hotels and "
    "guided experiences so you can enjoy {city} without the hassle of planning."
)

# ---------------------------------------------------------------------------
# AIRLINES  (name, iata, country, rating, business, economy, website)
# ---------------------------------------------------------------------------
AIRLINES = [
    ("Pakistan International Airlines", "PK", "Pakistan", 3.8, True, True, "https://www.piac.com.pk"),
    ("AirBlue", "PA", "Pakistan", 4.0, True, True, "https://www.airblue.com"),
    ("Serene Air", "ER", "Pakistan", 3.9, True, True, "https://www.sereneair.com"),
    ("Fly Jinnah", "9P", "Pakistan", 3.7, False, True, "https://www.flyjinnah.com"),
    ("Emirates", "EK", "United Arab Emirates", 4.7, True, True, "https://www.emirates.com"),
    ("Qatar Airways", "QR", "Qatar", 4.8, True, True, "https://www.qatarairways.com"),
    ("Etihad Airways", "EY", "United Arab Emirates", 4.6, True, True, "https://www.etihad.com"),
    ("Turkish Airlines", "TK", "Turkey", 4.5, True, True, "https://www.turkishairlines.com"),
    ("Saudia", "SV", "Saudi Arabia", 4.1, True, True, "https://www.saudia.com"),
    ("Flynas", "XY", "Saudi Arabia", 3.8, False, True, "https://www.flynas.com"),
    ("Air Arabia", "G9", "United Arab Emirates", 3.9, False, True, "https://www.airarabia.com"),
    ("Oman Air", "WY", "Oman", 4.2, True, True, "https://www.omanair.com"),
    ("Gulf Air", "GF", "Bahrain", 4.0, True, True, "https://www.gulfair.com"),
    ("Kuwait Airways", "KU", "Kuwait", 3.9, True, True, "https://www.kuwaitairways.com"),
    ("British Airways", "BA", "United Kingdom", 4.4, True, True, "https://www.britishairways.com"),
    ("Lufthansa", "LH", "Germany", 4.5, True, True, "https://www.lufthansa.com"),
    ("Air France", "AF", "France", 4.3, True, True, "https://www.airfrance.com"),
    ("KLM Royal Dutch Airlines", "KL", "Netherlands", 4.4, True, True, "https://www.klm.com"),
    ("Virgin Atlantic", "VS", "United Kingdom", 4.3, True, True, "https://www.virginatlantic.com"),
    ("Singapore Airlines", "SQ", "Singapore", 4.8, True, True, "https://www.singaporeair.com"),
    ("Malaysia Airlines", "MH", "Malaysia", 4.2, True, True, "https://www.malaysiaairlines.com"),
    ("Thai Airways", "TG", "Thailand", 4.1, True, True, "https://www.thaiairways.com"),
    ("Cathay Pacific", "CX", "Hong Kong", 4.5, True, True, "https://www.cathaypacific.com"),
    ("Qantas", "QF", "Australia", 4.4, True, True, "https://www.qantas.com"),
    ("American Airlines", "AA", "United States", 4.0, True, True, "https://www.aa.com"),
    ("United Airlines", "UA", "United States", 3.9, True, True, "https://www.united.com"),
    ("Delta Air Lines", "DL", "United States", 4.2, True, True, "https://www.delta.com"),
    ("China Southern Airlines", "CZ", "China", 3.8, True, True, "https://www.csair.com"),
]

TEAM_MEMBERS = [
    ("Ahmed Raza", "General Manager", "With over 18 years in the travel industry, Ahmed leads Fly Happy's strategy, partnerships and service standards.", "ahmed.raza@flyhappytravels.com"),
    ("Sana Malik", "Ticketing Officer", "Sana specializes in domestic and international fare optimization, helping customers get the best possible price.", "sana.malik@flyhappytravels.com"),
    ("Bilal Ahmed", "Visa Consultant", "Bilal has processed thousands of visa applications across Schengen, GCC and North American missions.", "bilal.ahmed@flyhappytravels.com"),
    ("Ayesha Khan", "Travel Consultant", "Ayesha designs custom holiday itineraries tailored to every budget and travel style.", "ayesha.khan@flyhappytravels.com"),
    ("Usman Tariq", "Account Officer", "Usman manages billing, refunds and financial reporting with meticulous accuracy.", "usman.tariq@flyhappytravels.com"),
    ("Hira Siddiqui", "Support Officer", "Hira leads 24/7 customer support, ensuring every traveler's question is answered quickly.", "hira.siddiqui@flyhappytravels.com"),
]

FAQS = [
    ("What are your office timings?", "Our offices are open Monday to Saturday, 9:00 AM to 8:00 PM. We are closed on Sundays and public holidays, except for our 24/7 emergency booking hotline.", "General"),
    ("How do I apply for a visa through Fly Happy?", "Simply visit our Services page, choose the visa type (visit, work, student or business), and submit your documents online or at our office. Our visa consultants will guide you through embassy requirements and appointment scheduling.", "Visa"),
    ("What documents are required for a passport application?", "You typically need your original CNIC/B-Form, previous passport (if renewing), 2 passport-sized photographs, and proof of address. Our team can verify your documents before submission to avoid rejections.", "Documents"),
    ("How do I book a flight ticket online?", "Go to 'Book Now', search your destination and travel dates, choose your airline and seat class, fill in passenger details, and confirm payment. You'll instantly receive a Booking ID and Ticket Number.", "Booking"),
    ("What is your refund and cancellation policy?", "Refunds depend on the airline's fare rules. Fully refundable fares are processed within 7-15 working days. Cancellation charges (if any) will be clearly shown before you confirm cancellation from your dashboard.", "Refund"),
    ("What payment methods do you accept?", "We accept Visa, MasterCard, Debit Cards, JazzCash, EasyPaisa, direct bank transfer, and cash payments at our office.", "Payment"),
    ("Do you offer travel insurance?", "Yes, we offer comprehensive travel insurance covering medical emergencies, trip cancellation, baggage loss and delays for both domestic and international trips.", "Insurance"),
    ("Which destinations do you cover?", "We currently arrange travel to over 80 destinations across Asia, the Middle East, Europe, the Americas, Africa and Oceania — see our full Destinations page for details.", "Destinations"),
    ("Where is your office located?", "Our head office is located at Suite 401, Business Tower, Blue Area, Islamabad, Pakistan. You can also reach us via WhatsApp or phone for a virtual consultation.", "Office"),
    ("What is your contact number?", "You can call us at +92 300 1234567 during office hours, or our 24/7 emergency line at +92 300 9998888 for urgent travel issues.", "Contact"),
    ("How can I check my flight status?", "We recommend checking your airline's official website or app using your ticket number. Our support team can also assist you directly through the Contact page or chatbot.", "Flights"),
    ("Do you offer Hajj and Umrah packages?", "Yes, we offer fully guided Hajj and Umrah packages including flights, visa processing, hotel accommodation near Haramain, and ground transport.", "Packages"),
    ("Can I customize a holiday package?", "Absolutely. Our travel consultants can tailor any package's duration, hotel category, and inclusions to match your preferences and budget.", "Packages"),
    ("How long does visa processing take?", "Processing time varies by country and visa type — typically 3 to 15 working days. Our visa consultants will give you an accurate estimate for your specific application.", "Visa"),
    ("Is my personal information safe with Fly Happy?", "Yes. All passwords are securely hashed and your booking and payment data is stored using industry-standard security practices.", "Security"),
]

TESTIMONIAL_DATA = [
    ("Fatima Noor", "Dubai", 5, "Fly Happy made our Dubai trip completely stress-free. From visa to hotel, everything was handled professionally!"),
    ("Ali Hassan", "Istanbul", 5, "Best travel agency in Islamabad. Got a great deal on Turkish Airlines and the visa was approved within a week."),
    ("Mehreen Siddiqui", "Umrah Package", 5, "Our Umrah package was spiritually fulfilling and hassle-free. The hotel was walking distance from Haram. Highly recommend!"),
    ("Kamran Yousaf", "London", 4, "Smooth UK visa process and excellent customer support throughout. Will book again for our next family trip."),
    ("Sadia Iqbal", "Bangkok", 5, "Amazing holiday package to Thailand! The itinerary was perfectly planned and the support team was always available."),
    ("Zeeshan Baig", "Saudi Arabia", 5, "Efficient Hajj arrangements, transparent pricing, and a very professional team. Jazak Allah Khair!"),
    ("Nida Farooq", "Malaysia", 4, "Great value family package. Kids loved Legoland! Only minor delay in hotel confirmation but resolved quickly."),
    ("Hamza Sheikh", "USA", 5, "Got my US visitor visa processed with complete document guidance. Very knowledgeable visa consultants."),
    ("Rabia Aslam", "Maldives", 5, "Our honeymoon in Maldives was magical, all thanks to Fly Happy's perfectly curated resort package."),
    ("Omar Farooqi", "Doha", 4, "Quick ticket booking and great fare compared to other agencies. Customer support responded within minutes."),
    ("Sidra Yousuf", "Paris", 5, "Excellent Schengen visa assistance — approved on the first attempt! The team double-checked every document."),
    ("Waqas Ahmed", "Domestic - Karachi", 4, "Reliable and quick for domestic bookings. Been using Fly Happy for over 3 years now."),
    ("Iqra Batool", "Bali", 5, "Loved our Bali holiday package! Beautiful resorts and a very well organized itinerary."),
    ("Faisal Mahmood", "Corporate Travel", 5, "Our company relies on Fly Happy for all corporate travel management — always professional and on time."),
    ("Anum Riaz", "Cairo", 4, "Great historical tour package to Egypt. Guides were knowledgeable and hotels were comfortable."),
    ("Tariq Javed", "Australia", 5, "The visa consultant helped us navigate a complex student visa application for my son. Forever grateful."),
    ("Sobia Nasir", "Muscat", 5, "Quick, affordable, and friendly service for our Oman family trip. Highly recommend Fly Happy!"),
    ("Adeel Chaudhry", "Group Tour - Turkey", 5, "Organized a group tour of 15 people to Turkey — everything from flights to hotels was seamless."),
    ("Mahnoor Aziz", "Business Visa - Germany", 4, "Professional guidance for my business visa to Germany. Documents were verified thoroughly before submission."),
    ("Junaid Sarwar", "Cruise Booking", 5, "First time booking a cruise and Fly Happy made it so easy to understand and plan. Wonderful experience!"),
]

NEWS_ITEMS = [
    ("Fly Happy Launches New Umrah Packages for 2026", "umrah-packages-2026", "Discover our newly updated Umrah packages with premium hotel options near Haramain."),
    ("Turkish Airlines Adds New Direct Flights from Islamabad", "turkish-airlines-new-routes", "More convenient scheduling now available for our customers traveling to Istanbul."),
    ("Fly Happy Wins Best Emerging Travel Agency Award 2025", "best-emerging-agency-2025", "We're honored to be recognized for our commitment to customer service excellence."),
    ("New Schengen Visa Requirements: What You Need to Know", "schengen-visa-requirements-update", "Our visa consultants break down the latest changes to Schengen visa applications."),
    ("Top 10 Winter Destinations for Pakistani Travelers", "top-winter-destinations", "From snow-capped Europe to sunny Maldives, explore our top winter picks."),
    ("Fly Happy Partners with Serene Air for Exclusive Fares", "serene-air-partnership", "Enjoy special discounted fares for domestic travel through our new partnership."),
]


def run_seed():
    """Populate all tables with sample/demo data. Assumes tables already created."""
    random.seed(42)

    # ---------------- Users: Admin, Employees, Demo Customer ----------------
    admin = User(full_name="Fly Happy Administrator", email="admin@flyhappytravels.com",
                 phone="+923001234567", role="admin", cnic="61101-1234567-1")
    admin.set_password("Admin@123")
    db.session.add(admin)

    demo_customer = User(full_name="Maaz Saeed", email="customer@flyhappytravels.com",
                          phone="+923451234567", role="customer", cnic="61101-7654321-1",
                          passport_number="AB1234567", address="Islamabad, Pakistan")
    demo_customer.set_password("Customer@123")
    db.session.add(demo_customer)

    employee_users = []
    for name, position, bio, email in TEAM_MEMBERS:
        u = User(full_name=name, email=email, phone="+92300" + str(random.randint(1000000, 9999999)),
                 role="employee")
        u.set_password("Employee@123")
        db.session.add(u)
        employee_users.append((u, position, bio))

    db.session.flush()  # get IDs

    for u, position, bio in employee_users:
        db.session.add(Employee(user_id=u.id, designation=position, department="Operations",
                                 hire_date=date(2020, 1, 1)))

    # ---------------- Team Members (public-facing) ----------------
    for i, (name, position, bio, email) in enumerate(TEAM_MEMBERS):
        db.session.add(TeamMember(name=name, position=position, bio=bio, email=email,
                                   photo=f"team/team{(i % 6) + 1}.jpg", display_order=i))

    # ---------------- Destinations ----------------
    destinations = []
    for (country, city, airport, code, region, price, visa, duration, weather, season, popular) in DESTINATIONS:
        d = Destination(
            country=country, city=city, airport_name=airport, airport_code=code,
            region=region, starting_price=price, visa_required=visa,
            flight_duration=duration, weather=weather, best_season=season,
            is_popular=popular,
            description=DESTINATION_DESC_TEMPLATE.format(city=city, country=country),
            image=f"destinations/{code.lower()}.jpg",
        )
        db.session.add(d)
        destinations.append(d)
    db.session.flush()

    def find_dest(city):
        return next((d for d in destinations if d.city == city), destinations[0])

    # ---------------- Airlines ----------------
    airlines = []
    for (name, code, country, rating, biz, eco, website) in AIRLINES:
        a = Airline(name=name, iata_code=code, country=country, rating=rating,
                    business_class=biz, economy_class=eco, website=website,
                    logo=f"airlines/{code.lower()}.png")
        db.session.add(a)
        airlines.append(a)
    db.session.flush()

    # ---------------- Packages ----------------
    package_defs = [
        ("7-Day Dubai Shopping & City Tour", "Dubai", "Holiday", 7, 165000, True),
        ("5-Day Istanbul & Cappadocia Explorer", "Istanbul", "Holiday", 5, 195000, True),
        ("10-Day Premium Umrah Package", "Madinah", "Umrah", 10, 285000, True),
        ("14-Day Hajj Package (Standard)", "Jeddah", "Hajj", 14, 650000, True),
        ("6-Day Bangkok & Pattaya Family Fun", "Bangkok", "Family", 6, 175000, True),
        ("5-Day Bali Honeymoon Escape", "Bali", "Holiday", 5, 220000, True),
        ("4-Day Maldives Overwater Villa Retreat", "Male", "Holiday", 4, 310000, True),
        ("8-Day London & Paris Grand Tour", "London", "Group", 8, 495000, True),
        ("6-Day Malaysia Family Adventure", "Kuala Lumpur", "Family", 6, 168000, False),
        ("5-Day Corporate Retreat - Doha", "Doha", "Corporate", 5, 210000, False),
        ("9-Day South Africa Safari Experience", "Johannesburg", "Group", 9, 420000, False),
        ("7-Day Egypt Pyramids & Nile Cruise", "Cairo", "Holiday", 7, 235000, True),
        ("6-Day Switzerland Alps Tour", "Zurich", "Holiday", 6, 410000, False),
        ("5-Day Muscat Desert Safari Package", "Muscat", "Family", 5, 145000, False),
        ("10-Day Australia East Coast Tour", "Sydney", "Group", 10, 520000, False),
        ("5-Day Baku City & Gabala Tour", "Baku", "Holiday", 5, 155000, True),
        ("3-Day Kathmandu Mountain Getaway", "Kathmandu", "Family", 3, 95000, False),
        ("7-Day Spain & Portugal Combo Tour", "Madrid", "Group", 7, 460000, False),
    ]
    for name, city, category, days, price, featured in package_defs:
        db.session.add(Package(
            name=name, destination_id=find_dest(city).id, category=category,
            duration_days=days, price=price, is_featured=featured,
            description=f"An expertly curated {days}-day {category.lower()} package to {city}, "
                         f"including flights, accommodation and guided experiences.",
            inclusions="Return Flights, Hotel Stay, Airport Transfers, Daily Breakfast, Guided Tours, Visa Assistance",
            image=f"packages/{city.lower().replace(' ', '_')}.jpg",
        ))

    # ---------------- Hotels ----------------
    hotel_defs = [
        ("Burj Al Arab Jumeirah", "Dubai", 5, 145000),
        ("Address Downtown", "Dubai", 5, 98000),
        ("Hilton Istanbul Bosphorus", "Istanbul", 5, 62000),
        ("Anantara Vacation Club Bangkok", "Bangkok", 4, 38000),
        ("The Ritz-Carlton Bali", "Bali", 5, 88000),
        ("Conrad Maldives Rangali Island", "Male", 5, 195000),
        ("The Savoy London", "London", 5, 120000),
        ("Grand Hyatt Doha", "Doha", 5, 68000),
        ("Steigenberger Al Dau Jeddah", "Jeddah", 5, 55000),
        ("Frontel Al Harithia Madinah", "Madinah", 4, 42000),
        ("Sheraton Kuala Lumpur", "Kuala Lumpur", 5, 45000),
        ("Fairmont Cairo", "Cairo", 5, 50000),
    ]
    for name, city, stars, price in hotel_defs:
        db.session.add(Hotel(
            name=name, destination_id=find_dest(city).id, star_rating=stars,
            price_per_night=price, is_featured=stars >= 5,
            description=f"{stars}-star luxury accommodation in {city} offering premium comfort and service.",
            amenities="Free WiFi, Swimming Pool, Spa, Airport Shuttle, Breakfast Included",
            image=f"hotels/{name.lower().replace(' ', '_').replace('-', '')}.jpg",
        ))

    # ---------------- Testimonials ----------------
    for i, (name, dest, rating, message) in enumerate(TESTIMONIAL_DATA):
        db.session.add(Testimonial(customer_name=name, destination=dest, rating=rating,
                                    message=message, photo=f"testimonials/customer{(i % 10) + 1}.jpg"))

    # ---------------- FAQs ----------------
    for i, (q, a, cat) in enumerate(FAQS):
        db.session.add(FAQ(question=q, answer=a, category=cat, display_order=i))

    # ---------------- News ----------------
    for title, slug, summary in NEWS_ITEMS:
        db.session.add(News(title=title, slug=slug, summary=summary,
                             content=summary + " " + DESTINATION_DESC_TEMPLATE.format(city="your next destination", country="the world"),
                             image=f"news/{slug}.jpg"))

    # ---------------- Gallery ----------------
    gallery_items = [
        ("Sunset over Maldives resort", "Destinations"), ("Burj Khalifa night view", "Destinations"),
        ("Umrah pilgrims at Masjid al-Haram", "Umrah"), ("Istanbul Blue Mosque", "Destinations"),
        ("Family enjoying Bangkok street food tour", "Packages"), ("Fly Happy team at office", "Company"),
        ("Corporate travel client meeting", "Company"), ("Bali beach resort pool", "Destinations"),
        ("London Big Ben sunset", "Destinations"), ("Group tour in Cappadocia hot air balloons", "Packages"),
        ("Cairo pyramids desert tour", "Destinations"), ("Award ceremony - Best Emerging Agency", "Company"),
    ]
    for i, (caption, category) in enumerate(gallery_items):
        db.session.add(Gallery(image=f"gallery/gallery{i + 1}.jpg", caption=caption, category=category))

    # ---------------- Sample Contact Messages ----------------
    db.session.add(ContactMessage(name="Hassan Raza", email="hassan.raza@example.com",
                                   phone="+923001112233", subject="Inquiry about Umrah Package",
                                   message="I would like more details about your 10-day premium Umrah package pricing."))
    db.session.add(ContactMessage(name="Nadia Sheikh", email="nadia.sheikh@example.com",
                                   phone="+923004445566", subject="Visa Assistance",
                                   message="Can you help me with a UK visit visa application for a family of 4?"))

    db.session.flush()

    # ---------------- Sample Bookings + Payments for demo customer ----------------
    sample_bookings = [
        (find_dest("Dubai"), airlines[4], "round_trip", 15, 2, 1, 0, "Business", "confirmed", "Visa", "completed"),
        (find_dest("Istanbul"), airlines[7], "round_trip", 45, 2, 0, 0, "Economy", "pending", "JazzCash", "pending"),
        (find_dest("Jeddah"), airlines[8], "one_way", -20, 1, 0, 0, "Economy", "completed", "Bank Transfer", "completed"),
        (find_dest("Bangkok"), airlines[21], "round_trip", 60, 4, 1, 1, "Economy", "cancelled", "EasyPaisa", "failed"),
    ]
    for dest, airline, trip_type, day_offset, adults, children, infants, seat_class, status, method, pay_status in sample_bookings:
        dep = date.today() + timedelta(days=day_offset)
        ret = dep + timedelta(days=7) if trip_type == "round_trip" else None
        price_per_head = float(dest.starting_price) * (1.6 if seat_class == "Business" else 1.0)
        total = price_per_head * (adults + children + 0.25 * infants)
        booking = Booking(
            booking_id=Booking.generate_booking_id(),
            ticket_number=Booking.generate_ticket_number(),
            customer_id=demo_customer.id, destination_id=dest.id, airline_id=airline.id,
            trip_type=trip_type, departure_date=dep, return_date=ret,
            adults=adults, children=children, infants=infants,
            seat_class=seat_class, meal_preference="Standard",
            passenger_name=demo_customer.full_name, passport_number=demo_customer.passport_number,
            cnic=demo_customer.cnic, phone=demo_customer.phone, email=demo_customer.email,
            total_price=round(total, 2), status=status,
        )
        db.session.add(booking)
        db.session.flush()
        db.session.add(Payment(
            receipt_number=Payment.generate_receipt_number(), booking_id=booking.id,
            amount=booking.total_price, method=method, transaction_id=f"TXN{random.randint(100000, 999999)}",
            status=pay_status,
        ))

    db.session.commit()
