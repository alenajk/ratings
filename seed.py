"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
import datetime
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
        current_line = User(user_id=user_id, age=age, zipcode=zip_code)
        db.session.add(current_line)
        
    db.session.commit()



def load_movies():
    """Load movies from u.item into database."""

    movie_data = open("seed_data/u.item")

    for line in movie_data:
        line_list = line.split('|')
        movie_id = line_list[0]
        title = line_list[1][:line_list[1].rfind(" (")]
        released_at = line_list[2]
        if line_list[2] != "":
            stripped_time = datetime.datetime.strptime(released_at, "%d-%b-%Y")
        imdb_url = line_list[4]
        current_line = Movie(movie_id=movie_id, title=title, released_at=stripped_time, imdb_url=imdb_url)
        db.session.add(current_line)
    
    db.session.commit()
    

def load_ratings():
    """Load ratings from u.data into database."""

    # Data is split by tabs!

    rating_data = open("seed_data/u.data")

    for line in rating_data:
        line_list = line.rstrip().split("\t")
        movie_id = line_list[0]
        user_id = line_list[1]
        score = line_list[2]
        current_line = Rating(movie_id=movie_id, user_id=user_id, score=score)
        db.session.add(current_line)

    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    
    load_users()
    load_movies()
    load_ratings()
