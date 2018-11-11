"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/users/<user_id>')
def show_user(user_id):
    """show user details."""
    user = User.query.filter_by(user_id=user_id).first()

    user_rating = Rating.query.filter_by(user_id=user_id).first()

    user_movies = Movie.query.filter_by()
    print(user_rating.score)
    print("divide")

    return render_template("user_details.html", user=user)


@app.route('/movies')
def movie_list():
    """show list of movies."""

    movies = Movie.query.order_by('title').join(Rating).all()
    # movies = Movie.query.options(db.joinedload('rating')).order_by('title').all()

    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<movie_id>')
def show_movie(movie_id):
    """show movie details."""
    movie = Movie.query.filter_by(movie_id=movie_id).first()

    return render_template("movie_details.html", movie=movie)




@app.route('/register', methods = ['GET'])
def displa_reg_form():
    """user registration."""

    return render_template("registration.html")


@app.route('/register', methods = ['POST'])
def register_user():
    """user registration."""

    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcde')

    if not User.query.filter_by(email=email).first():
        new_user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")

    flash("User already exist")
    return redirect("/register")


@app.route("/login", methods=["GET"])
def show_login():
    """Show login form."""

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def process_login():
    """Log user into site."""

    email = request.form.get('email')
    password = request.form.get('password')

    match_user = User.query.filter_by(email=email).first()


    if not match_user:
        flash("No such email address.")
        return redirect('/login')


    real_password = User.query.filter_by(email=email).first().password

    if password != real_password:
        flash("Incorrect password.")
        return redirect("/login")

    session["logged_in_customer_email"] = email
    flash("Logged in.")
    return redirect("/")


@app.route("/logout")
def process_logout():
    """Log user out."""

    del session["logged_in_customer_email"]
    flash("Logged out.")
    return redirect("/melons")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
