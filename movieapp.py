import web
import pymysql
from web import form
from web.contrib.template import render_jinja

web.config.debug = False
pymysql.install_as_MySQLdb()


urls = (
    '/','Index',
    '/index', 'Index',
    '/login','Login',
    '/logout','Logout',
    '/onshow','Onshow',
    '/user',"User",
    '/movies(.*)',"Movies",
    '/moviedetail(.*)',"MovieDetail",
    '/actor(.*)',"Actor"
)


db = web.database(dbn='mysql', user='root', pw='lv23623600', db='movie_infor')
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'),initializer={'logged_in': False})


render = web.template.render('templates/',globals={'context':session})


class Index:
    def GET(self):
        return render.index()


class Login:
    def GET(self):
        if session.logged_in:
            return render.user(session.user)
        error = False
        return render.login(error)

    def POST(self):
        i = web.input()
        email = i.get('email')
        passwd = i.get('passwd')
        check = db.query('select * from user where account = $email and password = $passwd', vars = {'email':email, 'passwd': passwd})
        if check:
            error = False
            session.logged_in = True
            session.user = email
            return render.user(session.user)
        else:
            error = True
            return render.login(error)

class Onshow:
    def GET(self):
        # onshow_movies = db.select("on_show")
        # return render.onshow(onshow_movies)
        res = db.query('select movies.title from movies join on_show where movies.movie_id=on_show.movie_id limit 5;')
        if res:
            return render.onshow(res)
        else:
            return "can not find any on show movie"
    
    def POST(self):
        i = web.input()
        key = i.get("key")
        res = db.query('select * from movies where title = $key',vars = {"key":key})
        if res:
            return render.actor(res)
        else:
            return "can not find"

class Movies:
    def GET(self,page):
        if not page:
            page = 1

        NavNum = 20
        results = db.query("SELECT COUNT(*) AS c FROM movies")
        count = results[0].c

        if count % NavNum==0:
            pages = count // NavNum
        else:
            pages = count // (NavNum + 1)

        off = (int(page)-1) * NavNum
        got_movies = db.select('movies',order='movie_id',limit = NavNum,offset = off)

        if got_movies:
            return render.movies(got_movies,int(page))
        else:
            return "Can not find any movie."

    def POST(self,x):
        i = web.input()
        title = i.get("key")
        
        actors = db.query('SELECT DISTINCT(a.name) FROM movies m JOIN rel_movie_actor r ON m.movie_id = r.movie_id JOIN actor a ON r.actor_id = a.id WHERE title = $title;',vars = {"title": title})
        directors = db.query('SELECT DISTINCT(d.name) FROM director d JOIN movies ON movies.director_id = d.id WHERE title = $title;',vars = {"title": title})
        ratings = db.query('SELECT r.score,r.text FROM rating r JOIN movies m ON  m.movie_id = r.movie_id WHERE m.title = $title',vars = {"title": title})
        movies = db.query('SELECT * FROM movies WHERE title = $title',vars = {"title":title})
        if actors or directors or ratings or movies:
            return render.moviedetail(movies,actors,directors,ratings)
        else:
            return "no movies"


class Actor:
    def GET(self,name):
        res = db.query('SELECT * from actor WHERE name = $name',vars = {"name":name})
        if res:
            return render.actor(res)
        else:
            return "error"



class Logout:
    def GET(self):
        if not session.logged_in:
            return render.login()
        else: 
            session.logged_in = False
            session.user = None
            raise web.seeother("/")


class User:
    def GET(self):
        if not session.logged_in:
            return render.login()
        else:
            return render.user(session.user)

    def POST(self):
        i = web.input()
        key = i.get("key")
        res = db.query('SELECT * from actor WHERE name = $key',vars = {"key":key})
        if res:
            return render.actor(res)
        else:
            return "Can not find"


class MovieDetail:
    def GET(self,title):
        actors = db.query('SELECT DISTINCT(a.name) FROM movies m JOIN rel_movie_actor r ON m.movie_id = r.movie_id JOIN actor a ON r.actor_id = a.id WHERE title = $title;',vars = {"title": title})
        directors = db.query('SELECT DISTINCT(d.name) FROM director d JOIN movies ON movies.director_id = d.id WHERE title = $title;',vars = {"title": title})
        ratings = db.query('SELECT r.score,r.text FROM rating r JOIN movies m ON  m.movie_id = r.movie_id WHERE m.title = $title',vars = {"title": title})
        movies = db.query('SELECT * FROM movies WHERE title = $title',vars = {"title":title})
        if actors or directors or ratings or movies:
            return render.moviedetail(movies,actors,directors,ratings)
        else:
            return "error"





if __name__ == "__main__": 
    app.run()