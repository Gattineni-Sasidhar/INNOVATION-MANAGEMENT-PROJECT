import random
from app import app
from models import db, Service

base_coords = {
    "Hyderabad": (17.3850, 78.4867),
    "Bangalore": (12.9716, 77.5946),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.7041, 77.1025),
    "Chennai": (13.0827, 80.2707),
    "Pune": (18.5204, 73.8567),
    "Kolkata": (22.5726, 88.3639),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Surat": (21.1702, 72.8311)
}

with app.app_context():
    if Service.query.count() < 40:
        areas = ["Central", "North", "South", "East", "West", "Downtown", "Suburbs", "IT Park", "Plaza", "Hills", "Banjara Hills", "Ameerpet", "Connaught Place", "Bandra", "Koramangala"]
        service_types = ["Plumber", "Electrician", "Mechanic", "Tutor", "Cleaning", "IT Support", "AC Repair", "Painter", "Carpenter", "Pest Control"]
        adjectives = ["Quick", "Elite", "Prime", "Master", "Pro", "Reliable", "City", "Urban", "Express", "Premium"]
        
        services_to_add = []
        cities = list(base_coords.keys())
        
        for i in range(100):
            city = random.choice(cities)
            area = random.choice(areas)
            stype = random.choice(service_types)
            adj = random.choice(adjectives)
            
            name = f"{adj} {stype}s {city}"
            location = f"{area}, {city}, India"
            phone = f"+91 {random.randint(7000000000, 9999999999)}"
            rating = round(random.uniform(3.5, 5.0), 1)
            price = random.randint(100, 1000)
            
            # Spread pins specifically around Hyderabad
            base_lat, base_lng = base_coords[city]
            lat = base_lat + random.uniform(-0.1, 0.1)
            lng = base_lng + random.uniform(-0.1, 0.1)
            
            services_to_add.append(
                Service(name=name, service_type=stype, phone=phone, location=location, rating=rating, price=price, lat=lat, lng=lng)
            )
            
        for s in services_to_add:
            db.session.add(s)
            
        db.session.commit()
        print(f"Added {len(services_to_add)} geographically mapped services to V4 Database!")
    else:
        print("Sufficient spatial services already exist.")
