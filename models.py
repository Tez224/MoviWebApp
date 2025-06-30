from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """
    Represents a user in the application.

    Attributes:
        id (int): Primary key.
        name (str): The user's name.
        movies (list): One-to-many relationship to Movie.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # One-to-many relationship: one user → many movies
    movies = db.relationship('Movie', backref='user', lazy=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<User %r>' % self.name


class Movie(db.Model):
    """
    Represents a movie added by a user.

    Attributes:
        id (int): Primary key.
        title (str): Movie title.
        publication_year (int): Year of release.
        genre (str): Genre of the movie.
        rating (float): Rating (e.g. IMDb).
        poster_url (str): URL to the movie poster image.
        director (str): Movie director.
        runtime (str): Runtime in minutes (e.g., '120 min').
        user_id (int): Foreign key linking to the user who added the movie.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    genre = db.Column(db.String(100), nullable=True, default="Unknown")
    rating = db.Column(db.Float, nullable=True)
    poster_url = db.Column(db.String(500), nullable=True)
    director = db.Column(db.String(100), nullable=True)
    runtime = db.Column(db.String(30), nullable=True)

    # Link Movie to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __str__(self):
        return self.title
    def __repr__(self):
        return f"<Movie {self.title!r}>"
