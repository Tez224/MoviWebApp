import requests
import os

from requests import RequestException
from sqlalchemy.exc import SQLAlchemyError

from models import db, User, Movie

OMDB_API_KEY = os.environ.get("OMDB_API_KEY")

class DataManager():
    """Handles CRUD operations for Users and Movies"""
# ----------- User Methods -----------

    def get_users(self):
        """
        Retrieve all users from the database.
        Returns: List of User objects.
        """
        return User.query.all()

    def add_user(self, name):
        """
        Add a new user to the database.
        Args: name (str): Name of the user.
        Returns: User object if successful, None otherwise.
        """
        try:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error adding user: {e}")
            return None

    def get_user_by_id(self, user_id):
        """
        Fetch a user by their ID.
        Args: user_id (int): The ID of the user.
        Returns: User object or None.
        """
        return User.query.get(user_id)


    def delete_user(self, user_id):
        """
        Delete a user from the database.
        Args: user_id (int): The ID of the user to delete.
        """
        user = self.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
    # ----------- Movie Methods -----------

    def get_movies(self, user_id):
        """
        Retrieve all movies for a specific user.
        Args: user_id (int): The ID of the user.
        Returns: List of Movie objects.
        """
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, title, publication_year=None, genre=None, rating=None, user=None):
        """
        Add a new movie to the database.
        Args:
            title (str): Movie title.
            publication_year (int, optional): Year of release.
            genre (str, optional): Genre.
            rating (float, optional): Rating.
            user (User, optional): SQLAlchemy user instance.

        Returns: Movie object if successful, None otherwise.
        """
        try:
            movie = Movie(
                title=title,
                publication_year=publication_year,
                genre=genre,
                rating=rating,
                user=user
            )
            db.session.add(movie)
            db.session.commit()
            return movie
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error adding movie: {e}")
            return None


    def get_movie_by_id(self, movie_id):
        """
        Fetch a movie by their ID.
        Args: movie_id (int): The ID of the movie.
        Returns: Movie object or None.
        """
        return Movie.query.get(movie_id)

    def delete_movie(self, movie_id):
        """
        Delete a movie from the database.
        Args: movie_id (int): The ID of the movie.
        """
        try:
            movie = self.get_movie_by_id(movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error deleting movie: {e}")
    # ----------- Movie API Methods -----------

    def fetch_movie_info(self, title):
        """
        Fetch a movie by their title.
        Args: title (str): Movie title.
        Returns: Movie object or None.
        """
        if not OMDB_API_KEY:
            raise ValueError("OMDB_API_KEY not set in environment")

        try:
            url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
        except RequestException as e:
            print(f"Error fetching from OMDb: {e}")
            return {}
        except ValueError as e:
            print(f"Error parsing OMDb response: {e}")
            return {}

        if data.get("Response") == "True":
            genre = data.get('Genre', "Unknown")
            year = data.get('Year', None)
            rating = data.get('imdbRating', None)  # fix: should be 'imdbRating'
            poster_url = data.get('Poster', None)
            director = data.get('Director', None)
            runtime = data.get('Runtime', None)

            return {
                "title": data.get("Title", title),
                "genre": genre,
                "publication_year": int(year) if year and year.isdigit() else None,
                "rating": float(rating) if rating and rating != "N/A" else None,
                "poster_url": poster_url,
                "director": director,
                "runtime": runtime
            }

        return {}

    def add_movie_from_omdb(self, title, user_id):
        """
        Add a new movie from OMDB.
        Args:
            title (str): Movie title.
            user_id (int): The ID of the user.
        Returns: Movie object if successful, None otherwise.
        """
        movie_info = self.fetch_movie_info(title)
        if not movie_info:
            return None  # handle failure in the route

        movie = Movie(
            title=movie_info["title"],
            genre=movie_info["genre"],
            publication_year=movie_info["publication_year"],
            rating=movie_info["rating"],
            poster_url=movie_info["poster_url"],
            user_id=user_id
        )
        db.session.add(movie)
        db.session.commit()
        return movie