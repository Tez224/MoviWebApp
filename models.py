from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # One-to-many relationship: one user → many movies
    movies = db.relationship('Movie', backref='user', lazy=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<User %r>' % self.name


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    genre = db.Column(db.String(100), nullable=True, default="Unknown")
    rating = db.Column(db.Float, nullable=True)

    # Link Movie to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __str__(self):
        return self.title
    def __repr__(self):
        return f"<Movie {self.title!r}>"
