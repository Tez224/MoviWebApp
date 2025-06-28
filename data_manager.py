from models import db, User, Movie

class DataManager():
    """Handles CRUD operations for Users and Movies"""
# ----------- User Methods -----------

    def get_users(self):
        return User.query.all()

    def add_user(self, username):
        user = User(
            username=username
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

    def add_movie(self, title, publication_year=None, genre=None, rating=None):
        movie = Movie(
            title=title,
            publication_year=publication_year,
            genre=genre,
            rating=rating
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
