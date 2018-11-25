from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap

from datetime import datetime

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/movielist.html")
def movielist():
    return render_template("movie_list.html")

@app.route("/moviedetail.html")
def moviedetail():
    return render_template("movie_detail.html")

@app.route("/actor.html")
def actor():
    return render_template("actor.html")

@app.route("/director.html")
def director():
    return render_template("actor.html")

@app.route("/onshow.html")
def onshow():
    return render_template("on_show.html")

@app.route("/user.html")
def user():
    return render_template("account.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),400

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"),500


if __name__ == '__main__':
    app.run()        