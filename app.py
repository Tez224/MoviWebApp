import os

from flask import Flask, flash, redirect, render_template, request
from data_manager import DataManager
from dotenv import load_dotenv
from models import db, Movie, User

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key')

# Create absolute path to the 'data/movies.db' file
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'data', 'movies.db')

# Tell Flask-SQLAlchemy to use that database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Link the database and the app.

data_manager = DataManager() # Create an object of DataManager class

@app.route('/', methods=['Get'])
def home():
    users = data_manager.get_users()
    return render_template('home.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    name = request.form['name']

    if name:
        data_manager.add_user(name)
        flash(f"User {name} added successfully!", "success")
    else:
        flash("Please enter a valid name.", "error")

    return redirect('/')


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    user = data_manager.get_user_by_id(user_id)
    movies = data_manager.get_movies(user_id)

    return render_template('movies.html',user=user, movies=movies)


if __name__ == '__main__':
    # Ensure the 'data/' folder really exists at runtime
    os.makedirs('data', exist_ok=True)

    #with app.app_context():
        #db.create_all()
        #print(Movie.__table__)
        #print(User.__table__)
        #print("Database and tables created.")
    app.run(debug=True)
