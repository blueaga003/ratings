"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from correlation import pearson


# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):

        """provide helpful things when printed."""

        return "<User user_id ={} email={}>".format(self.user_id, self.email)

    def feed_pairs_to_pearson(self, user_2):
        paired_ratings = []

        user_rating_dict = {}

        for rating in self.rating:
            user_rating_dict[rating.movie_id] = rating


        for rating in user_2.rating:
            if rating.movie_id in user_rating_dict:
                paired_ratings.append((rating.score, user_rating_dict[rating.movie_id].score))


        if paired_ratings:
            return pearson(paired_ratings)
        else:
            return 0.0

    rating = db.relationship('Rating')

# Put your Movie and Rating model classes here.
class Movie(db.Model):
    """Movie of ratings website."""

    __tablename__ = 'movies'

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    released_at = db.Column(db.DateTime, nullable=True)
    imbd_url = db.Column(db.String(200), nullable=True)

    rating = db.relationship('Rating',
                                backref = db.backref("movies",
                                                    order_by=movie_id))

class Rating(db.Model):
    """Ratings"""

    __tablename__ = 'ratings'

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=True)


    user = db.relationship("User",
                            backref = db.backref("ratings",
                                                    order_by=rating_id))

    movie = db.relationship("Movie",
                            backref = db.backref("ratings",
                                                    order_by=rating_id))

    def update_rating(self, new_rating):
        self.score = new_rating



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)



if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    # db.create_all()
    print("Connected to DB.")
