from flask import render_template, request, redirect, url_for, session
from models import db, User, Admin, ParkingLot, ParkingSpot, Reservation
from datetime import datetime


def init_routes(app):
    # Admin credentials (no registration)
    ADMIN_EMAIL = 'admin@gmail.com'
    ADMIN_PASSWORD = 'admin123'

    # Home page
    @app.route('/')
    def index():
        return render_template('index.html')

    # Admin login
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                session['admin'] = True
                return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html')

    # User register
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            full_name = request.form['full_name']
            email = request.form['email']
            password = request.form['password']
            address = request.form['address']
            pin_code = request.form['pin_code']
            if User.query.filter_by(email=email).first():
                return redirect(url_for('login'))
            user = User(full_name=full_name, email=email, password=password, address=address, pin_code=pin_code)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')

    # User login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email, password=password).first()
            if user:
                session['user_id'] = user.id
                return redirect(url_for('user_dashboard'))
        return render_template('login.html')

    # Admin dashboard
    @app.route('/admin/dashboard')
    def admin_dashboard():
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        lots = ParkingLot.query.all()
        return render_template('admin_dashboard.html', parking_lots=lots)

    # Add parking lot
    @app.route('/admin/parking-lot/add', methods=['GET', 'POST'])
    def add_parking_lot():
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        if request.method == 'POST':
            prime_location_name = request.form['prime_location_name']
            address = request.form['address']
            pin_code = request.form['pin_code']
            price = float(request.form['price'])
            max_spots = int(request.form['max_spots'])
            lot = ParkingLot(prime_location_name=prime_location_name, address=address, pin_code=pin_code, price=price, max_spots=max_spots)
            db.session.add(lot)
            db.session.commit()
            # Create spots
            for _ in range(max_spots):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        return render_template('add_parking_lot.html')

    # Edit parking lot
    @app.route('/admin/parking-lot/edit/<int:lot_id>', methods=['GET', 'POST'])
    def edit_parking_lot(lot_id):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        lot = ParkingLot.query.get_or_404(lot_id)
        if request.method == 'POST':
            lot.prime_location_name = request.form['prime_location_name']
            lot.address = request.form['address']
            lot.pin_code = request.form['pin_code']
            lot.price = float(request.form['price'])
            new_max_spots = int(request.form['max_spots'])
            # Adjust spots
            current_spots = len(lot.spots)
            if new_max_spots > current_spots:
                for _ in range(new_max_spots - current_spots):
                    spot = ParkingSpot(lot_id=lot.id, status='A')
                    db.session.add(spot)
            elif new_max_spots < current_spots:
                removable_spots = [s for s in lot.spots if s.status == 'A'][:current_spots - new_max_spots]
                for spot in removable_spots:
                    db.session.delete(spot)
            lot.max_spots = new_max_spots
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        return render_template('edit_parking_lot.html', lot=lot)

    # Delete parking lot (only if all spots are available)
    @app.route('/admin/parking-lot/delete/<int:lot_id>', methods=['POST'])
    def delete_parking_lot(lot_id):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        lot = ParkingLot.query.get_or_404(lot_id)
        if all(spot.status == 'A' for spot in lot.spots):
            # Delete all reservations for spots in this lot
            for spot in lot.spots:
                Reservation.query.filter_by(spot_id=spot.id).delete()
            db.session.delete(lot)
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    # View spot details
    @app.route('/admin/parking-spot/<int:spot_id>')
    def view_spot_details(spot_id):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        spot = ParkingSpot.query.get_or_404(spot_id)
        reservation = Reservation.query.filter_by(spot_id=spot.id, leaving_timestamp=None).first()
        return render_template('admin_spot_details.html', spot=spot, reservation=reservation)

    # View all users
    @app.route('/admin/users', methods=['GET', 'POST'])
    def admin_users():
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        search_query = request.form.get('search', '').strip() if request.method == 'POST' else ''
        if search_query:
            if search_query.isdigit():
                users = User.query.filter(User.id == int(search_query)).all()
            else:
                users = User.query.filter(User.full_name.ilike(f"%{search_query}%")).all()
        else:
            users = User.query.all()
        return render_template('admin_users.html', users=users, search_query=search_query)

    # Admin summary
    @app.route('/admin/summary')
    def admin_summary():
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        lots = ParkingLot.query.all()
        summary_data = []
        for lot in lots:
            occupied = sum(1 for s in lot.spots if s.status == 'O')
            available = sum(1 for s in lot.spots if s.status == 'A')
            revenue = sum(r.total_cost or 0 for s in lot.spots for r in s.reservations)
            summary_data.append({
                'location': lot.prime_location_name,
                'occupied': occupied,
                'available': available,
                'revenue': revenue
            })
        return render_template('admin_summary.html', summary_data=summary_data)

    # User dashboard
    @app.route('/user/dashboard', methods=['GET', 'POST'])
    def user_dashboard():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        reservations = Reservation.query.filter_by(user_id=user.id).all()
        search_query = request.form.get('search', '').strip() if request.method == 'POST' else ''
        if search_query:
            lots = ParkingLot.query.filter(
                (ParkingLot.address.ilike(f"%{search_query}%")) |
                (ParkingLot.pin_code.ilike(f"%{search_query}%"))
            ).all()
        else:
            lots = ParkingLot.query.all()
        return render_template('user_dashboard.html', user=user, reservations=reservations, lots=lots, search_query=search_query)

    # Book parking spot
    @app.route('/user/book/<int:lot_id>', methods=['GET', 'POST'])
    def book_parking(lot_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        lot = ParkingLot.query.get_or_404(lot_id)
        user = User.query.get(session['user_id'])
        available_spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()
        if not available_spot:
            return render_template('no_spot_available.html')
        if request.method == 'POST':
            vehicle_number = request.form['vehicle_number']
            available_spot.status = 'O'
            reservation = Reservation(
                spot_id=available_spot.id,
                user_id=user.id,
                vehicle_number=vehicle_number,
                parking_timestamp=datetime.utcnow()
            )
            db.session.add(reservation)
            db.session.commit()
            return redirect(url_for('user_dashboard'))
        return render_template('book_parking.html', lot=lot, spot=available_spot)

    # Release parking spot
    @app.route('/user/release/<int:reservation_id>', methods=['GET', 'POST'])
    def release_parking(reservation_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        reservation = Reservation.query.get_or_404(reservation_id)
        spot = ParkingSpot.query.get(reservation.spot_id)
        if request.method == 'POST':
            reservation.leaving_timestamp = datetime.utcnow()
            duration = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
            lot = ParkingLot.query.get(spot.lot_id)
            reservation.total_cost = round(duration * lot.price, 2)
            spot.status = 'A'
            db.session.commit()
            return redirect(url_for('user_dashboard'))
        return render_template('release_parking.html', reservation=reservation, spot=spot)

    # User summary
    @app.route('/user/summary')
    def user_summary():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        reservations = Reservation.query.filter_by(user_id=user.id).all()
        used_spots = len([r for r in reservations if r.leaving_timestamp])
        summary_data = {
            'used_spots': used_spots,
            'total_reservations': len(reservations)
        }
        return render_template('user_summary.html', summary_data=summary_data)

    # Logout
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))