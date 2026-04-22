from app import app
from models import db, Service, Booking

with app.app_context():
    # Clear existing services and bookings for a fresh start
    Booking.query.delete()
    Service.query.delete()
    db.session.commit()

    services = [
        Service(name="Raju's Electrical Repair", service_type="Electrician", phone="91-9876543210", location="Madhapur, Hyderabad", rating=4.8),
        Service(name="Kiran Plumbing Solutions", service_type="Plumber", phone="91-8765432109", location="Banjara Hills, Hyderabad", rating=4.9),
        Service(name="City Auto Care", service_type="Mechanic", phone="91-7654321098", location="Koramangala, Bangalore", rating=4.7),
        Service(name="Sri Math Tutors", service_type="Tutor", phone="91-6543210987", location="Andheri, Mumbai", rating=5.0),
        Service(name="Hyderabad Home Cleaners", service_type="Cleaning", phone="91-5432109876", location="Kukatpally, Hyderabad", rating=4.5),
        Service(name="Tech Gurus IT Support", service_type="IT Support", phone="91-4321098765", location="Gachibowli, Hyderabad", rating=4.6),
    ]
    
    for s in services:
        db.session.add(s)
        
    db.session.commit()
    print("Indian mock services injected successfully!")
