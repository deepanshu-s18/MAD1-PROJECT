from flask import render_template, request, redirect, url_for, flash
from models import db, User, ParkingLot, ParkingSpot, Reservation 

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')
    
    


