"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    # Get the data from u.user, split it on "|" into a list
    # For loop iterate through list to create a statement that creates a row object
    # add the object to the db.session
    # Commit after for loop
    user_data = open("seed_data/u.user")

    for line in user_data:
        line_list = line.split('|')
        user_id, age, gender, occupation, zip_code = line_list
        print user_id, age




def load_movies():
    """Load movies from u.item into database."""


def load_ratings():
    """Load ratings from u.data into database."""

    # Data is split by tabs!

if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_movies()
    load_ratings()
