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
    '/user',"User"
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
        return render.login()

    def POST(self):
        i = web.input()
        email = i.get('email')
        passwd = i.get('passwd')
        check = db.query('select * from user where account = $email and password = $passwd', vars = {'email':email, 'passwd': passwd})
        if check:
            session.logged_in = True
            session.user = email
            return render.user(session.user)
        else:
            return render.login()

class Onshow:
    def GET(self):
        onshow_movies = db.select("on_show")
        return render.onshow(onshow_movies)


class Logout:
    def GET(self):
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
        res = db.query('select * from actor where name = $key',vars = {"key":key})
        if res:
            return render.actor(res)
        else:
            return "can not find"





if __name__ == "__main__": 
    app.run()