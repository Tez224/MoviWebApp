import os

from flask import Flask
from data_manager import DataManager
from models import db, Movie, User

app = Flask(__name__)

# Create absolute path to the 'data/movies.db' file
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'data', 'movies.db')

# Tell Flask-SQLAlchemy to use that database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Link the database and the app.

data_manager = DataManager() # Create an object of DataManager class

@app.route('/')
def home():
    return "Welcome to MoviWeb App!"

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)

    with app.app_context():
        db.create_all()
        print(Movie.__table__)
        print(User.__table__)
        print("Database and tables created.")
    app.run(debug=True)
