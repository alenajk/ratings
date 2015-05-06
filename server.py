"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


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

                flash("You were successfully logged in!")
                return redirect("/")
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

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()