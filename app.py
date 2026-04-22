import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Service, Booking
from auth import generate_token, token_required, admin_required

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
# New DB version for across India data seeding
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'qsf_india.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@qsf.com').first():
        admin = User(
            name='Admin',
            email='admin@qsf.com',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered.'}), 400
        
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully. Please login.'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials.'}), 401
        
    token = generate_token(user.id, user.role)
    return jsonify({
        'token': token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}
    }), 200

@app.route('/api/services', methods=['GET'])
def get_services():
    query = request.args.get('q', '')
    if query:
        services = Service.query.filter(Service.name.ilike(f'%{query}%') | Service.service_type.ilike(f'%{query}%') | Service.location.ilike(f'%{query}%')).all()
    else:
        services = Service.query.all()
        
    result = []
    for s in services:
        result.append({
            'id': s.id, 'name': s.name, 'type': s.service_type,
            'phone': s.phone, 'location': s.location, 'rating': s.rating, 'price': s.price,
            'lat': s.lat, 'lng': s.lng
        })
    return jsonify(result), 200

@app.route('/api/services', methods=['POST'])
@admin_required
def add_service(current_user_id):
    data = request.get_json()
    new_service = Service(
        name=data.get('name'), service_type=data.get('type'),
        phone=data.get('phone'), location=data.get('location'),
        rating=data.get('rating', 0.0), price=data.get('price', 500),
        lat=data.get('lat', 20.5937), lng=data.get('lng', 78.9629) # Default to center of India if missing
    )
    db.session.add(new_service)
    db.session.commit()
    return jsonify({'message': 'Service added successfully!'}), 201

@app.route('/api/services/<int:id>', methods=['DELETE'])
@admin_required
def delete_service(current_user_id, id):
    service = Service.query.get(id)
    if not service: return jsonify({'message': 'Service not found'}), 404
    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Service deleted'}), 200

@app.route('/api/bookings', methods=['POST'])
@token_required
def book_service(current_user_id):
    data = request.get_json()
    service_id = data.get('service_id')
    date = data.get('date')
    time_slot = data.get('time_slot')
    payment_method = data.get('payment_method')
    
    if not service_id or not date or not time_slot:
        return jsonify({'message': 'Missing fields.'}), 400
        
    new_booking = Booking(
        user_id=current_user_id, service_id=service_id, booking_date=date, 
        time_slot=time_slot, payment_method=payment_method
    )
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({'message': 'Service booked successfully!'}), 201

@app.route('/api/bookings', methods=['GET'])
@token_required
def get_bookings(current_user_id):
    bookings = Booking.query.filter_by(user_id=current_user_id).all()
    result = []
    for b in bookings:
        service = Service.query.get(b.service_id)
        result.append({
            'id': b.id, 'service_name': service.name if service else 'Unknown',
            'date': b.booking_date, 'time_slot': b.time_slot, 'payment_method': b.payment_method,
            'status': b.status, 'price': service.price if service else 0,
            'customer_feedback': b.customer_feedback, 'customer_rating': b.customer_rating
        })
    return jsonify(result), 200

@app.route('/api/bookings/<int:id>/feedback', methods=['PUT'])
@token_required
def submit_feedback(current_user_id, id):
    data = request.get_json()
    booking = Booking.query.get(id)
    if not booking or booking.user_id != current_user_id:
        return jsonify({'message': 'Access denied'}), 403
    if booking.status.lower() != 'completed':
        return jsonify({'message': 'Can only review completed services'}), 400
        
    booking.customer_feedback = data.get('feedback')
    booking.customer_rating = data.get('rating')
    db.session.commit()
    return jsonify({'message': 'Feedback successfully submitted!'}), 200

@app.route('/api/bookings/<int:id>', methods=['DELETE'])
@token_required
def delete_booking(current_user_id, id):
    booking = Booking.query.get(id)
    if not booking or booking.user_id != current_user_id:
        return jsonify({'message': 'Access denied or booking not found'}), 404
        
    db.session.delete(booking)
    db.session.commit()
    return jsonify({'message': 'Booking deleted successfully!'}), 200

@app.route('/api/admin/bookings', methods=['GET'])
@admin_required
def admin_get_bookings(current_user_id):
    bookings = Booking.query.all()
    result = []
    for b in bookings:
        service = Service.query.get(b.service_id)
        user = User.query.get(b.user_id)
        result.append({
            'id': b.id,
            'service_name': service.name if service else 'Unknown',
            'price': service.price if service else 0,
            'customer_name': user.name if user else 'Unknown',
            'customer_email': user.email if user else 'Unknown',
            'date': b.booking_date,
            'time_slot': b.time_slot,
            'payment_method': b.payment_method,
            'status': b.status,
            'customer_feedback': b.customer_feedback,
            'customer_rating': b.customer_rating,
            'created_at': b.created_at.isoformat()
        })
    result.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(result), 200

@app.route('/api/admin/bookings/<int:id>', methods=['PUT'])
@admin_required
def admin_update_booking(current_user_id, id):
    data = request.get_json()
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
        
    booking.status = data.get('status', booking.status)
    db.session.commit()
    return jsonify({'message': 'Booking status updated!'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
