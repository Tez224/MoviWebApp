import os

from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from data_manager import DataManager
from dotenv import load_dotenv
from models import db, Movie, User

# ------------------ Load Environment ------------------
try:
    load_dotenv()
    OMDB_API_KEY = os.environ["OMDB_API_KEY"]
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-key")
except KeyError as e:
    raise RuntimeError(f"Missing required environment variable: {e}")

# ------------------ Flask App Setup ------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY

# ------------------ Database Configuration ------------------
try:
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_path = os.path.join(basedir, 'data', 'movies.db')

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # Bind SQLAlchemy to the app
except Exception as e:
    raise RuntimeError(f"Failed to configure database: {e}")

# ------------------ Initialize DataManager ------------------
with app.app_context():
    try:
        data_manager = DataManager()
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to initialize DataManager: {e}")

# Error handling with flask
@app.errorhandler(404)
def not_found_error(error):
    """ Error handler for 404 errors """
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """ Error handler for 500 errors """
    return render_template('errors/500.html'), 500

# ------------------ Routes ------------------

@app.route('/', methods=['Get'])
def home():
    """Home page showing all registered users."""
    users = data_manager.get_users()
    return render_template('home.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """Add a new user and redirect back to the homepage."""
    name = request.form['name']

    if name:
        data_manager.add_user(name)
        flash(f"User {name} added successfully!", "success")
    else:
        flash("Please enter a valid name.", "error")

    return redirect('/')


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    """Show the list of movies for a specific user."""
    user = data_manager.get_user_by_id(user_id)
    movies = data_manager.get_movies(user_id)

    return render_template('movies.html',user=user, movies=movies)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Manually add a new movie to the user's collection."""
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
    """Add a movie via title using the OMDb API."""
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
    """Update the title of a movie for a given user."""
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
def delete_movie(user_id, movie_id):
    """Delete a movie from a user's list."""
    movie = Movie.query.get_or_404(movie_id)

    if movie:
        data_manager.delete_movie(movie_id)
        flash(f"Deleted movie '{movie.title}'.", "success")
        return redirect(url_for('get_movies', user_id=user_id))

    else:
        flash("Movie not found!", "error")
        return redirect(url_for('get_movies', user_id=user_id))


if __name__ == '__main__':
    # Ensure the 'data/' folder really exists at runtime
    os.makedirs('data', exist_ok=True)

    with app.app_context():
        if not os.path.exists(database_path):
            db.create_all()
            print("📁 Database and tables created.")

    app.run(debug=True)
