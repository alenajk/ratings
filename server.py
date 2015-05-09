"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db
import datetime

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    # check to see if anything in session
    # if so , display "logged in" 

    return render_template("homepage.html")

# @app.route('/login')
# def login():

#     # check to see if something in session:
#     # if so, render_template(homepage) OR display "You're already logged in - link to homepage or link to sign out"
#     # if not, render (loginform) 
#     return render_template("login_form.html")


@app.route('/login', methods=["GET","POST"])
def login():

    if request.method == "POST":
        
        email = request.form.get("email")
        password = request.form.get("password")
        
        #alternate query syntax: 
        # pw_in_db = db.session.query(User).filter_by(email=email).one().password

        pw_in_db = User.query.filter_by(email=email).all()

        if pw_in_db == []:
            flash("This email is not registered - please create an account.")
            return redirect("/registration")
        else:
            if pw_in_db[0].password == password:
                session["email"] = email
                session["password"] = password
                user_id = User.query.filter_by(email=email).one().user_id
                path = "/users/" + str(user_id)
                flash("You were successfully logged in!")
                return redirect(path)
            else:
                flash("wrong!")
                return redirect("/login")

    return render_template("login_form.html")

@app.route('/registration', methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        age = request.form.get("age")
        zipcode = request.form.get("zipcode")

        #Check to see if email address is taken
        try: 
            temp = User.query.filter_by(email=email).one()
            flash("Sorry, that email address already has an account")
            return redirect('/registration')
        except:
            #Creating instance of User class with associated info
            current_person = User(email=email, password=password, age=age, zipcode=zipcode)
            
            #adding the user's info to the DB
            db.session.add(current_person)
            db.session.commit()

            flash("You were successfully registered!")
            return redirect("/")

    return render_template("registration.html")

@app.route('/logout', methods=["GET"])
def logout():
    print "LOGGED OUT"
    session["email"] = ""
    session["password"] = ""

    flash("Logged you out!")
    return redirect("/")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<int:user_id>')
def show_user_page(user_id):

    user = User.query.filter_by(user_id=user_id).one()

    titles_and_scores = {}

    user_ratings = Rating.query.filter_by(user_id=user_id).all()
    
    for user_rating in user_ratings:
        movie_id = user_rating.movie_id
        title = Movie.query.filter_by(movie_id=movie_id)[0].title
        titles_and_scores[title] = user_rating.score
    print titles_and_scores
    return render_template("user_profile.html", user=user, titles_and_scores=titles_and_scores)

@app.route('/movies')
def movie_list():
    """Show list of users."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<int:movie_id>')
def show_movie_page(movie_id):
    """Show details about a movie. Allow a user to add or update a rating
    if they are logged in."""

    loggedin = False
    # Get movie object for given movie, assign to variable "movie"    
    movie = Movie.query.filter_by(movie_id=movie_id).one()

    # Check to see if user is logged in. Get user_id for that user if so.
    if session.get("email"):
        loggedin = True
        user_id = User.query.filter_by(email=session["email"]).one().user_id
        # Return rating object for user & movie, or None if user has not rated movie.
        user_rating = Rating.query.filter_by(
            movie_id = movie_id, user_id=user_id).first()
    # If not logged in, set user_rating to None
    else:
        user_rating = None

    # Get average rating of a movie
    rating_scores = [r.score for r in movie.ratings]    
    avg_rating = round(float(sum(rating_scores)) / len(rating_scores), 2)

    # Prediction code: will only predict if user has not rated movie.
    prediction = None

    if (not user_rating) and loggedin:
        print "\n\nHGERE\n\n"
        user = User.query.get(user_id)
        prediction = user.predict_rating(movie)

    mov_ratings = movie.ratings
    movie_ratings =[]

    for each_rating in mov_ratings:
        movie_ratings.append(each_rating.score)
 
    if prediction:
        # If user hasn't rated this movie
        effective_rating = prediction
        prediction = int(round(prediction))

    elif user_rating:
        # If the user has rated this movie
        effective_rating = user_rating.score

    else:
        # User hasn't rated this movie, and we couldn't get a prediction
        effective_rating = None

    # Get evil bunny's rating, either by predicting it or using bunny's real rating 

    # Getting bunny's user object
    evil_bunny = User.query.filter_by(email="bunny@gmail.com").one()
    bunny_rating = Rating.query.filter_by(
        user_id=evil_bunny.user_id, movie_id=movie.movie_id).first()

    # If bunny hasn't rated the movie yet, set bunny_rating to the output of the
    # predict_rating function - called with evil_bunny object.
    if bunny_rating is None:
        bunny_rating = evil_bunny.predict_rating(movie)
    # If bunny has rated the movie, use bunny's actual rating for bunny_rating
    else:
        bunny_rating = bunny_rating.score

    if bunny_rating and effective_rating:
        difference = abs(bunny_rating - effective_rating)

    else:
        # We couldn't get a bunny rating
        difference = None

    BERATEMENT_MESSAGES = [
        "You have ok taste.",
        "Ugh.",
        "You have disappointed bunny very much.",
        "You have enraged me with your taste in cinema.",
        "I. Can't. Even. Please get help."
        ]

    if difference is not None:
        beratement = BERATEMENT_MESSAGES[int(difference)]
    else:
        beratement = None

    title = movie.title
    released = movie.released_at.strftime("%B %d, %Y")
    imdb = movie.imdb_url
    movie_id = movie.movie_id

    return render_template("movie_profile.html", movie_id=movie_id, title = title, 
        movie_ratings=movie_ratings, released=released, imdb=imdb, loggedin=loggedin, 
        user_rating=user_rating, average=avg_rating, prediction=prediction, beratement=beratement)

@app.route('/new_rating/<int:movie_id>', methods = ['GET', 'POST'])
def add_rating(movie_id):

    score = request.form.get("score")
    email = session["email"]
    user_id = User.query.filter_by(email=email).one().user_id

    #check to see if Rating exists in db for which user_id and movie_id match
    #If there's already a rating in the db, update (??) the record
    #If not, add the rating.
    rating_record = Rating.query.filter_by(user_id=user_id,movie_id=movie_id).all()

    if rating_record == []:

        # insert new rating into rating table based on user id
        new_rating_record = Rating(movie_id=movie_id, user_id=user_id, score=score)
        db.session.add(new_rating_record)
        db.session.commit()
    else:
        print rating_record
        rating_record[0].score = score
        db.session.commit()

    return "You rated " + str(movie_id) + str(score) +str(email) +str(user_id)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()