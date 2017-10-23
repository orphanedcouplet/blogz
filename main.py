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

# !!!
# "Note how we never defined a __init__ method on the User class? That’s because SQLAlchemy adds an implicit constructor to all model classes which accepts keyword arguments for all its columns and relationships."
# source: http://flask-sqlalchemy.pocoo.org/2.3/quickstart/#simple-relationships
# !!!
    # def __init__(self, username, password): #do i need to put posts in here?
    #     self.username = username
    #     self.password = password
    #     # self.posts = posts #???
    
    def __repr__(self):
        return "<User %r>" % self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", backref="owner_posts", foreign_keys=[owner_id])

    # tags = db.relationship("Tag", lazy="subquery", backref=db.backref("posts"))

    # category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    # category = db.relationship("Category", backref=db.backref("posts"))

# !!! see above
    # def __init__(self, title, body, pub_date, user): #do i put tags in the initialization function?
    #     self.title = title
    #     self.body = body
    #     self.pub_date = pub_date
    #     self.user = user # changed from "self.user_id = user_id" after looking at the completed "Get It Done" code - so maybe finish those lessons
    #     # self.tags = tags #???
    
    def __repr__(self):
        return "<Post %r>" % self.title

# "Category" class is for making different kinds of posts
# like "video post" or "text post" etc
# but I'm commenting it out because that's TOO AMBITIOUS for right now
# class Category(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)

# # !!! see above
#     # def __init__(self, name):
#     #     self.name = name
    
#     def __repr__(self):
#         return "<Category %r>" % self.name

# class Tag(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(300), nullable=False)

# # !!! see above
#     # def __init__(self, id, name):
#     #     self.name = name
    
#     def __repr__(self):
#         return "<Tag %r>" % self.name

# # many-to-many helper table (may need to go BEFORE class definitions??!?)
# post_tag_table = db.Table(
#     "post_tag_table", 
#     db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True), 
#     db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True)
#     )

# # not that i understand it really, but tags (many-to-many relationship with posts) are basically copied from the example in the docs:
# # http://flask-sqlalchemy.pocoo.org/2.3/models/


@app.before_request
def require_login():
    allowed_routes = ["login", "register", "all_blogs", "index"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")


@app.route("/register", methods=["POST", "GET"])
def register():
    
    if request.method == "POST":
        username = request.form["username"]
        password_initial = request.form["password_initial"]
        password_verify = request.form["password_verify"]

        # TODO validate user inputs

        existing_username = User.query.filter_by(username=username).first()
        if not existing_username:
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
            flash("Username does not exist!", category='error')
            return redirect("/login")
    
    # TODO "Create Account" button

    return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    del session["username"]
    return redirect("/")

@app.route("/", methods=["POST", "GET"])
def index():

    user = User.query.filter_by(username=session["username"]).first()

    # TODO display a list of all usernames
    

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
