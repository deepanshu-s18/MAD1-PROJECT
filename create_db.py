from app import app
from extensions import db
from models import User, Admin

def create_initial_data():
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not Admin.query.filter_by(email='admin@gmail.com').first():
            admin = Admin(email='admin@gmail.com', password='admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin@gmail.com / admin123")
        else:
            print("Default admin already exists.")

if __name__ == '__main__':
    create_initial_data()