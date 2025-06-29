import os

from flask import Flask, flash, redirect, render_template, request, url_for
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


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    user = data_manager.get_user_by_id(user_id)

    if not user:
        flash("User not found!", "error")
        return redirect('/')

    data_manager.add_movie(
        title=request.form['title'],
        publication_year=request.form['publication_year'],
        genre=request.form['genre'],
        rating=request.form['rating'],
        user=user  # SQLAlchemy sets user_id
    )

    flash(f"Movie added successfully!", "success")
    return redirect(url_for('get_movies', user_id=user.id))


@app.route('/users/<int:user_id>/movies/omdb', methods=['POST'])
def add_movie_omdb(user_id):
    title = request.form.get('title')

    if not title:
        flash("Please enter a movie title.", "error")
        return redirect(url_for('get_movies', user_id=user_id))

    movie = data_manager.add_movie_from_omdb(title, user_id)

    if movie:
        flash(f"Movie '{movie.title}' added successfully via OMDb!", "success")
    else:
        flash("Movie not found or OMDb fetch failed.", "error"
              "try again later or add movie manually at bottom of the page.")

    return redirect(url_for('get_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    movie = Movie.query.get_or_404(movie_id)

    # check if movie belongs to user
    #if movie.user_id != user_id:
        #flash("This movie does not belong to this user!", "error")
        #return redirect(url_for('get_movies', user_id=user_id))

    new_title = request.form['title']
    if new_title:
        movie.title = new_title
        db.session.commit()
        flash(f"Updated movie title to '{new_title}'.", "success")
    else:
        flash("Title cannot be empty.", "error")

    return redirect(url_for('get_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if movie:
        data_manager.delete_movie(movie_id)
        flash(f"Deleted movie '{movie.title}'.", "success")
        return redirect(url_for('get_movies', user_id=movie.user_id))

    else:
        flash("Movie not found!", "error")
        return redirect(url_for('get_movies', user_id=movie.user_id))


if __name__ == '__main__':
    # Ensure the 'data/' folder really exists at runtime
    os.makedirs('data', exist_ok=True)

    #with app.app_context():
        #db.create_all()
        #print(Movie.__table__)
        #print(User.__table__)
        #print("Database and tables created.")
    app.run(debug=True)
