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

@app.route('/', methods=['Get', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']

        if name:
            new_user = User(name=name)
            db.session.add(new_user)
            db.session.commit()
            flash(f"User {name} added successfully!", "success")
            return redirect('/')
        else:
            flash("Please enter a valid name.", "error")

    users = data_manager.get_users()
    return render_template('home.html', users=users)


if __name__ == '__main__':
    # Ensure the 'data/' folder really exists at runtime
    os.makedirs('data', exist_ok=True)

    with app.app_context():
        db.create_all()
        print(Movie.__table__)
        print(User.__table__)
        print("Database and tables created.")
    app.run(debug=True)
