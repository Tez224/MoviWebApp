import requests
import os

from models import db, User, Movie

OMDB_API_KEY = os.environ.get("OMDB_API_KEY")

class DataManager():
    """Handles CRUD operations for Users and Movies"""
# ----------- User Methods -----------

    def get_users(self):
        return User.query.all()

    def add_user(self, name):
        user = User(
            name=name
        )

        db.session.add(user)
        db.session.commit()
        return user


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


    def get_movie_by_id(self, movie_id):
        return Movie.query.get(movie_id)


    def delete_movie(self, movie_id):
        movie = self.get_movie_by_id(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
    # ----------- Movie API Methods -----------

    def fetch_movie_info(self, title):
        if not OMDB_API_KEY:
            raise ValueError("OMDB_API_KEY not set in environment")

        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
        response = requests.get(url)
        data = response.json()

        if data.get("Response") == "True":
            genre = data.get('Genre', "Unknown")
            year = data.get('Year', None)
            rating = data.get('Rating', None)
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
        else:
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