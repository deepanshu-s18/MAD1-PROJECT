TO RUN APP
To create a virtual environment, run:
source .venv/bin/activate(which I used)

# For Linux and macOS
python3 -m venv .env
# For Windows
python -m venv .env
To activate the virtual environment, use the following command:

source .env/bin/activate
Once you have activated the virtual environment, you can install the required packages using the following command provided 'requirements.txt' is present in the same directory:

pip install -r requirements.txt
or you can install the packages individually:

pip install flask
pip install flask_sqlalchemy
To run the Flask application, use the following command:

python app.py
provided 'app.py' is the main file of your Flask application.
