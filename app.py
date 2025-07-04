from flask import Flask
from config import Config
from extensions import db 
from routes import init_routes 

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


import models


init_routes(app)

if __name__ == '__main__':
    app.run(debug=True) 
    