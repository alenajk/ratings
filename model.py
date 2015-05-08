"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions
class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):

        return "<User user_id=%s email=%s password=%s>" % (self.user_id, self.email, self.password)


    def assess_similarity(self, other):
        # user1 and user2 are user objects
        # make an empty dictionary to hold user1's ratings and an empty list
        # for pairs of scores for movies shared by user1 and user2 
        user_ratings_dict = {}
        paired_ratings = []

        # Iterate over the list of rating objects for user1 - ie. all ratings
        # user1 has done, add to dictionary: KEY: movie_id, VALUE: rating object 
        for r in self.ratings:
            user_ratings_dict[r.movie_id] = r

        # Iterate over the list of rating objects for user2
        # Checking to see if movie_id for that rating object is in our 
        # dictionary for user1's ratings - ie. checking if user1 rated
        # that movie. Assigning User1's rating object to the variable
        # u_rating for that movie
        for other_rating in other.ratings:
            u_rating = user_ratings_dict.get(other_rating.movie_id)
            # If user1 has not rated that movie, skip. Otherwise...
            if u_rating is not None:
                # Assign a tuple of the two users' scores to variable "pair",
                # and append tuple to "pairings" list.   
                pair = (u_rating.score, other_rating.score)
                paired_ratings.append(pair)

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict a user's rating of a movie."""
        # Parameter movie is a movie object
        # Create list of rating objects for movie:
        other_ratings = movie.ratings
        # Iterate over list of rating objects and putting each user object into a list
        other_users = [r.user for r in other_ratings]

        # Iterate through list of user objects, find similarity coefficient, 
        # add the coefficient and other_user user object into a list as tuples
        similarities = [ 
            (self.assess_similarity(other_user), other_user)
            for other_user in other_users
        ]

        similarities.sort(reverse=True)
        sim, best_match_user = similarities[0]

        matched_rating = None
        for rating in other_ratings:
            if rating.user_id == best_match_user.user_id:
                return rating.score * sim

        







class Movie(db.Model):

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(80))
    released_at = db.Column(db.DateTime)
    imdb_url = db.Column(db.String(150))

    def __repr__(self):

        return "<Movie title=%s imbd_url=%s>" % (self.title, self.imdb_url)

class Rating(db.Model):

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer)

    #Define relationship to user
    user = db.relationship("User", backref=db.backref("ratings", order_by=rating_id))

    #Define relationship to movie
    movie = db.relationship("Movie", backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):

        return "<Rating rating_id=%s movie_id=%s user_id=%s score=%s>" % (
            self.rating_id, self.movie_id, self.user_id, self.score)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."