"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db

import correlation


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
    user = User.query.options(db.joinedload('ratings').joinedload('movies')).filter_by(user_id=user_id).one()

    return render_template("user_details.html", user=user)


@app.route('/movies')
def movie_list():
    """show list of movies."""

    movies = Movie.query.order_by('title').join(Rating).all()
    # movies = Movie.query.options(db.joinedload('rating')).order_by('title').all()

    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<movie_id>', methods = ['GET'])
def show_movie(movie_id):
    """show movie details."""

    movie = Movie.query.filter_by(movie_id=movie_id).first()

    user_id = session.get("user_id")

    user = User.query.get(user_id)

    current_rating = Rating.query.filter_by(movie_id = movie_id,
                                            user_id = user_id).first()

    prediction = None

    if current_rating is not None:
        user_rating = current_rating.score
    else:
        user_rating = None
        prediction = user.predict_rating(movie)

    return render_template("movie_details.html",
                            movie=movie,
                            user_rating = user_rating,
                            prediction = prediction,
                            beratement = None)


@app.route('/movies/<movie_id>', methods = ['POST'])
def rate_movie(movie_id):
    """allow user to rate movie"""
    movie = Movie.query.filter_by(movie_id=movie_id).first()

    user_id = session.get("user_id")
    user = User.query.options(db.joinedload('ratings').joinedload('movies')).filter_by(user_id=user_id).one()

    user_rating = request.form.get('rating')
    prediction = None

    current_rating = Rating.query.filter_by(movie_id = movie_id,
                                        user_id = user_id).first()

    # other_ratings = Rating.query.filter_by(movie_id = movie_id).all()

    # other_users = [r.user for r in other_ratings]

    if not current_rating:
        new_rating = Rating(score=user_rating, movie_id=movie_id, user_id=user_id)
        db.session.add(new_rating)
        db.session.commit()
    else:
        current_rating.update_rating(user_rating)
        db.session.commit()

        # evil eye
    if prediction:
        # User hasn't scored; use our prediction if we made one
        effective_rating = prediction

    elif current_rating:
        # User has already scored for real; use that
        effective_rating = current_rating.score

    else:
        # User hasn't scored, and we couldn't get a prediction
        effective_rating = None

    print("effective_rating: ", effective_rating)

    # Get the eye's rating, either by predicting or using real rating

    the_eye = (User.query.filter_by(email="eye.com")
                         .one())
    eye_rating = Rating.query.filter_by(
        user_id=the_eye.user_id, movie_id=movie.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie)

    else:
        eye_rating = eye_rating.score

    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)

    else:
        # We couldn't get an eye rating, so we'll skip difference
        difference = None

    BERATEMENT_MESSAGES = [
        "I suppose you don't have such bad taste after all.",
        "I regret every decision that I've ever made that has " +
            "brought me to listen to your opinion.",
        "Words fail me, as your taste in movies has clearly " +
            "failed you.",
        "That movie is great. For a clown to watch. Idiot.",
        "Words cannot express the awfulness of your taste."
    ]

    print("Diff:", difference)

    if difference:
        beratement = BERATEMENT_MESSAGES[int(difference)]

    else:
        beratement = None

    return render_template("movie_details.html",
                            movie=movie,
                            user_rating = user_rating,
                            prediction = prediction,
                            beratement = beratement)

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
    user_id = User.query.filter_by(email=email).first().user_id
    print(user_id)

    if password != real_password:
        flash("Incorrect password.")
        return redirect("/login")

    session["user_id"] = user_id
    flash("Logged in.")
    return redirect("/users/{}".format(user_id))


@app.route("/logout")
def process_logout():
    """Log user out."""

    del session["user_id"]
    flash("Logged out.")
    return redirect("/")



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
