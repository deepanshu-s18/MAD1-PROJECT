from dotenv import load_dotenv
load_dotenv()  
from flask import Flask
from config import Config
from extensions import db 
from create_db import *
from routes import init_routes 

app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)

import models  


with app.app_context():
    
    db.create_all()

init_routes(app)

if __name__ == '__main__':
    create_initial_data()
    app.run(debug=True)
