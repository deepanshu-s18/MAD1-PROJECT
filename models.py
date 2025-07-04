from datetime import datetime

from extensions import db



class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    
    reservations = db.relationship("Reservation", back_populates='user')
    

class Admin(db.Model):
      
    __tablename__ = 'admins'


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    
class ParkingLot(db.Model):

    __tablename__ = 'parking_lots'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)

   
    spots = db.relationship("ParkingSpot", back_populates='lot')

class ParkingSpot(db.Model):

    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer,primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    spot_number = db.Column(db.String(20),nullable=False)
    status = db.Column(db.String(10),default='available')

    lot = db.relationship("ParkingLot", back_populates='spots')
    reservation = db.relationship('Reservation', back_populates='spot', uselist=False)


class Reservation(db.Model):

    __tablename__ = 'reservations'



    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates='reservations')
    spot = db.relationship('ParkingSpot', back_populates='reservation')

