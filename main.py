from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime


app = Flask(__name__)
app.config["DEBUG"] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:blogzdevpassword@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "kaljf#ojfm/@iop1j32rmvop+90r8w.........34gfer14@~#$jcehellooperatorcanyougivemenumber9"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    posts = db.relationship("Post", backref="user", lazy=True) # True is equivalent to "select" in this case. See flask-sqlalchemy docs for more info. Page is bookmarked: "Declaring Models". Also: do I even need lazy???

    def __init__(self, username, password): #do i need to put posts in here?
        self.username = username
        self.password = password
        # self.posts = posts #???
    
    def __repr__(self):
        return "<User %r>" % self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(280), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    tags = db.relationship("Tag", secondary=tags, lazy="subquery", backref=db.backref("posts", lazy=True)) # what does "secondary" mean?

    def __init__(self, title, body, pub_date=None, user): #do i put tags in the initialization function?
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.now()
        self.pub_date = pub_date
        self.user = user # changed from "self.user_id = user_id" after looking at the completed "Get It Done" code - so maybe finish those lessons
        # self.tags = tags #???
    
    def __repr__(self):
        return "<Post %r>" % self.title

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tagname = db.Column(db.String(280), nullable=False)

    def __init__(self, id, tagname):
        self.tagname = tagname
    
    def __repr__(self):
        return "<Tag %r>" % self.tagname

# many-to-many helper table (may need to go BEFORE class definitions??!?)
tags = db.Table(
    "tags",
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True)
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True)
    )

# not that i understand it really, but tags (many-to-many relationship with posts) are basically copied from the example in the docs:
# http://flask-sqlalchemy.pocoo.org/2.3/models/


@app.before_request
def require_login():
    allowed_routes = ["login", "register"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")


@app.route("/register", methods=["POST", "GET"])
def register():
    
    if request.method == "POST":
        username = request.form["username"]
        password_initial = request.form["password_initial"]
        password_verify = request.form["password_verify"]

        # TODO validate user inputs

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password_initial)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect("/")
        else:
            # TODO improve response message
            return "<h1>Duplicate user</h1>"
    
    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():

# needs configuring based on html template which is not even partly filled in:
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session["username"] = username
            flash("Logged in")
            return redirect("/")
        else:
            flash("User password incorrect, or user does not exist", category="error")
    
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    del session["email"]
    return redirect("/")

@app.route("/", methods=["POST", "GET"])
def index():

    user = User.query.filter_by(username=session["username"]).first()
    

@app.route("/blog", methods=["GET"])
def all_blogs():
    
    entry_id = request.args.get("id")

    if entry_id:
        blog_entry = Post.query.filter_by(id=entry_id).first()
        entry_title = blog_entry.title
        entry_body = blog_entry.body

        return render_template("blog-entry.html", entry_title=entry_title, entry_body=entry_body)

    else:
        entries = Post.query.order_by(desc(Post.id)).all()
        return render_template("blog.html", title="The Blog", entries=entries)


@app.route("/newpost", methods=["POST", "GET"])
def new_post():
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
        
        if not entry_title_error and not entry_body_error:
        # make it post the thing you entered (& redirect to new post URL after it's created)
            new_entry = Post(entry_title, entry_body)
            db.session.add(new_entry)
            db.session.commit()
            entry_id = new_entry.id
            return redirect("/blog?id={}".format(entry_id))
        else:
            return render_template(
            "newpost.html", 
            entry_title_error=entry_title_error, 
            entry_body_error=entry_body_error
            )

    return render_template("newpost.html")





if __name__ == "__main__":
    app.run()
