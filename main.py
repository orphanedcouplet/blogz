from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime


app = Flask(__name__)
app.config["DEBUG"] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:blogzdev@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "kaljf#ojfm/@iop1j32rmvop+90r8w.........34gfer14@~#$jcehellooperatorcanyougivemenumber9"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    posts = db.relationship("Post", backref="user")

    def __init__(self, username, password): # do i need to put posts in here?
        self.username = username
        self.password = password
        # self.posts = posts #???
    
    def __repr__(self):
        return "<User %r>" % self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", backref="author_posts", foreign_keys=[author_id])

    def __init__(self, title, body, author, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.now()
        self.pub_date = pub_date
        self.author = author
    
    def __repr__(self):
        return "<Post %r>" % self.title


@app.before_request
def require_login():
    allowed_routes = ["login", "register", "all_blogs", "index"]
    if request.endpoint not in allowed_routes and "username" not in session:
        flash("Must log in to access page!", category='error')
        return redirect("/login")


@app.route("/register", methods=["POST", "GET"])
def register():

    # page title
    title = "Sign up!"
    
    if request.method == "POST":
        username = request.form["username"]
        init_password = request.form["init_password"]
        verify_password = request.form["verify_password"]

        username_error = ""
        init_password_error = ""
        verify_password_error = ""

        # TODO validate user inputs

        # validate username
        if not username:
            username_error = "Must enter a username!"
        elif len(username) < 5:
            username_error = "Username is too short! (Min: 5 characters)"
            username = ""
        elif len(username) > 50:
            username_error = "Username is too long! (Max: 50 characters)"
            username = ""
        elif " " in username:
            username_error = "Username must not contain spaces!"
            username = ""
        
        # validate init_password
        if not init_password:
            init_password_error = "Must enter a password!"
        elif len(init_password) < 5:
            init_password_error = "Password is too short! (Min: 5 characters)"
        elif len(init_password) > 50:
            init_password_error = "Password is too long! (Max: 50 characters)"
        elif " " in init_password:
            init_password_error = "Password must not contain spaces!"
        elif init_password == username:
            init_password_error = "Password must be different from username!"
        
        # validate verify_password
        if init_password != verify_password:
            verify_password_error = "Passwords do not match!"

        # form validation success:
        if not username_error and not init_password_error and not verify_password_error:

            # but does the user already exist??
            existing_username = User.query.filter_by(username=username).first()

            # they're new! they're in! add them and redirect to new post page!
            if not existing_username:
                new_user = User(username, init_password)
                db.session.add(new_user)
                db.session.commit()
                session["username"] = username
                flash("Success! Signed in as {username}".format(username=username), category='message')
                return redirect("/newpost")
            else:
                flash("User already exists! Try logging in?", category='error')
                return redirect("/login")

        # the inputs weren't valid, re-render register template with error messages
        else:
            # clear password fields if ANYTHING wasn't validated
            init_password = ""
            verify_password = ""
            return render_template(
                "register.html", 
                title=title, 
                username=username, 
                username_error=username_error, 
                init_password_error=init_password_error, 
                verify_password_error=verify_password_error
                )
    
    return render_template("register.html", title=title)


@app.route("/login", methods=["POST", "GET"])
def login():

    # page title
    title = "Log in!"

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                session["username"] = username
                flash("Logged in successfully!", category='message')
                return redirect("/newpost")
            else:
                flash("Incorrect password!", category='error')
                return redirect("/login")
        else:
            flash("Username does not exist! Try signing up?", category='error')
            return redirect("/register")
    
    # TODO "Create Account" button

    return render_template("login.html", title=title)


@app.route("/logout", methods=["GET"])
def logout():
    del session["username"]
    flash("Logged out!")
    return redirect("/blog")

@app.route("/", methods=["POST", "GET"])
def index():

    # page title
    title = "All the bloggers!"

    authors = User.query.order_by(User.username).all()

    return render_template("index.html", title=title, authors=authors)


@app.route("/blog", methods=["GET"])
def all_blogs():
    
    entry_id = request.args.get("id")
    user_id = request.args.get("user")

    # single entry
    if entry_id:
        # blog entry info:
        blog_entry = Post.query.filter_by(id=entry_id).first()
        entry_title = blog_entry.title
        entry_body = blog_entry.body
        author = blog_entry.author
        pub_date = blog_entry.pub_date
        # make pub_date readable
        entry_date = pub_date.date()
        entry_hour_24 = pub_date.time().hour
        entry_hour = entry_hour_24 % 12
        entry_minute = pub_date.time().minute
        if entry_minute < 10:
            entry_minute = "0" + str(entry_minute)
        entry_time = "{hour}:{minute}".format(hour=entry_hour, minute=entry_minute)
        if entry_hour_24 > 11:
            entry_time += " pm"
        else:
            entry_time += " am"
        # page title:
        title=author.username + ": " + entry_title

        return render_template(
            "blog-entry.html", 
            title=title, 
            entry_title=entry_title, 
            entry_body=entry_body, 
            author=author, 
            entry_date=entry_date, 
            entry_time=entry_time
            )

    # single user page
    elif user_id:
        author = User.query.filter_by(id=user_id).first()
        entries = author.posts
        title = author.username + "'s blog entries!"
        return render_template(
            "single-user.html", 
            title=title, 
            author=author, 
            entries=entries
            )

    # all entries
    else:
        entries = Post.query.order_by(desc(Post.id)).all()
        return render_template("blog.html", title="The Blog", entries=entries)


@app.route("/newpost", methods=["POST", "GET"])
def new_post():

    #page title
    title="Write a new post!"

    # validation errors
    if request.method == "POST":
        entry_title = request.form["title"]
        entry_title_error = ""
        entry_body = request.form["body"]
        entry_body_error = ""

        # validate title
        if not entry_title:
            entry_title_error = "Your post must have a title!"
        
        # validate body
        if not entry_body:
            entry_body_error = "Your post must have text!"
        
        # make it post the thing you entered (& redirect to new post URL after it's created)
        if not entry_title_error and not entry_body_error:

            author = User.query.filter_by(username=session["username"]).first()
            
            new_entry = Post(entry_title, entry_body, author)
            db.session.add(new_entry)
            db.session.commit()
            entry_id = new_entry.id
            return redirect("/blog?id={}".format(entry_id))
        else:
            return render_template(
            "newpost.html", 
            title=title,
            entry_title_error=entry_title_error, 
            entry_body_error=entry_body_error
            )

    return render_template("newpost.html", title=title)





if __name__ == "__main__":
    app.run()
