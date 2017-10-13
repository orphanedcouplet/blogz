from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime


app = Flask(__name__)
app.config["DEBUG"] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:blogzdevpassword@localhost:8889/blogz"
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(280))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship("Category", backref=db.backref("posts", lazy="dynamic"))

    def __init__(self, title, body, category, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.now()
        self.pub_date = pub_date
        self.category = category
    
    def __repr__(self):
        return "<Post %r>" % self.title

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return "<Category %r>" % self.name

# class User(db.Model):
    # TODO create User class

@app.route("/blog", methods=["GET"])
def index():
    
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
    # TODO make error messages for if blog title or blog body is empty
    # hint: look at user-signup

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
        # TODO make it post the thing you entered
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


# @app.route("/signup", methods=["POST", "GET"])

# @app.route("/login", methods=["POST", "GET"])

# @app.route("/index", methods=["POST", "GET"])

# @app.route("/logout", methods=["POST", "GET"])


if __name__ == "__main__":
    app.run()
