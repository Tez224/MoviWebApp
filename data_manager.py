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
        return User.query.all()

    def add_user(self, name):
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
        return User.query.get(user_id)


    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
    # ----------- Movie Methods -----------

    def get_movies(self, user_id):
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, title, publication_year=None, genre=None, rating=None, user=None):
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
        return Movie.query.get(movie_id)

    def delete_movie(self, movie_id):
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