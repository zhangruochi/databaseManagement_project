import web
import pymysql
from web import form
from web.contrib.template import render_jinja
import copy
from neo4j import GraphDatabase


web.config.debug = False
pymysql.install_as_MySQLdb()
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lv23623600"))


urls = (
    '/','Index',
    '/index', 'Index',
    '/login','Login',
    '/register','Register',
    '/logout','Logout',
    '/onshow','Onshow',
    '/user',"User",
    '/movies(.*)',"Movies",
    '/moviedetail(.*)',"MovieDetail",
    '/movietag(.*)',"MovieTag",
    '/management(.*)',"Management",
    '/actor(.*)',"Actor",
    '/result',"Result",
    '/order/(.*)/(.*)',"Order",
    '/trans', "Transaction",
    '/profile',"Profile",
    '/delete(.*)',"Delete",
    '/director(.*)',"Director",
    '/statistic',"Statistic"

)


db = web.database(dbn='mysql', user='root', pw='lv23623600', db='movie_infor')


app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'),initializer={'logged_in': 0, 'user':None})


render = web.template.render('templates/',globals={'context':session})



class Index:
    def GET(self):
        return render.index()



class Login:
    def GET(self):
        if session.user and session.logged_in == 2:
            return render.user()
        elif session.user and session.logged_in == 1:
            theaters = db.query("SELECT DISTINCT(name) FROM theater WHERE operator = {}".format(session.id))
            return render.operator(theaters)
        
        error = False
        return render.login(error)

    def POST(self):
        raw_data = web.input()
        email = raw_data.get('email')
        passwd = raw_data.get('passwd')
        check_user = db.query('select * from user where account = $email and password = $passwd', vars = {'email':email, 'passwd': passwd})
        
        check_operator = db.query('select * from operator where account = $email and password = $passwd', vars = {'email':email, 'passwd': passwd})


        if check_user:
            error = False
            session.logged_in = 2
            session.user = email
            session.id = check_user[0].id
            return render.user()
        elif check_operator:
            error = False
            session.logged_in = 1
            session.user = email
            session.id = check_operator[0].id
            theaters = db.query("SELECT DISTINCT(name) FROM theater WHERE operator = {}".format(session.id))

            return render.operator(theaters)
        else:
            error = True
            return render.login(error)


class Management:
    def GET(self,name):
        movies = db.query("SELECT m.title,o.time_schedule,o.seat_limit, o.id,o.price,t.name,t.district,t.operator FROM movies m JOIN on_show o ON m.movie_id = o.movie_id JOIN theater t ON t.id = o.thea_id WHERE t.operator = $operator and t.name = $name ORDER BY m.movie_id, o.time_schedule",vars = {"operator":session.id, "name":name})
        return render.management(movies)




class Delete:
    def GET(self,id):
        db.query("DELETE FROM on_show WHERE id = {}".format(id))
        return render.result(True)




class Register:
    
    def GET(self):
       return render.register(False)

    def POST(self):
        raw_data = web.input()
        account = raw_data.get('account')
        password = raw_data.get('password')
        name = raw_data.get('name')
        gender = raw_data.get('gender')
        birth = raw_data.get('birth')
        district = raw_data.get('district')

        check = db.query('SELECT * FROM user WHERE account = $account and password = $password;', vars = {'account':account, 'password': password})
        
        if check:
            return render.register(True)
        else:
            res = db.insert("user",name = name,gender = gender,password = password, birth = birth, account = account, district = district)
            if res:
                return render.index()
            else:
                return "error"



class Result:
    def GET(self):
        return render.result(True)




class Onshow:
    def GET(self):
    
        res = db.query('SELECT m.title,o.time_schedule,o.seat_limit, o.id,o.price,t.name,t.district FROM movies m JOIN on_show o ON m.movie_id = o.movie_id JOIN theater t ON t.id = o.thea_id ORDER BY m.movie_id, o.time_schedule')
        if res:
            return render.onshow(res)
        else:
            return "can not find any on show movie"
    
    def POST(self):
        raw_data = web.input()
        title = raw_data.get("title",None)
        theater = raw_data.get("theater",None)
        district = raw_data.get("district",None)

        if title:
            res = db.query("SELECT m.title,o.time_schedule,o.seat_limit, o.id,o.price,t.name,t.district FROM movies m JOIN on_show o ON m.movie_id = o.movie_id JOIN theater t ON t.id = o.thea_id WHERE m.title = $title ORDER BY m.movie_id, o.time_schedule",vars = {"title":title})
        elif theater:
            res = db.query("SELECT m.title,o.time_schedule,o.seat_limit, o.id,o.price,t.name,t.district FROM movies m JOIN on_show o ON m.movie_id = o.movie_id JOIN theater t ON t.id = o.thea_id WHERE t.name = $theater ORDER BY m.movie_id, o.time_schedule",vars = {"theater":theater})
        elif district:
            res = db.query("SELECT m.title,o.time_schedule,o.seat_limit, o.id,o.price,t.name,t.district FROM movies m JOIN on_show o ON m.movie_id = o.movie_id JOIN theater t ON t.id = o.thea_id WHERE t.district = $district ORDER BY m.movie_id, o.time_schedule",vars = {"district": district})

        if res:
            return render.onshow(res)
        else:
            return "can not find"



class Movies:
    def GET(self,page = None):
        
        if not session.logged_in:
            return web.seeother("/register")

        if session.logged_in != 2:
            return web.seeother("/")

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

        raw_data = web.input()
        title = raw_data.get("key")
        amb = False
        actors = db.query('SELECT DISTINCT(a.name) FROM movies m JOIN rel_movie_actor r ON m.movie_id = r.movie_id JOIN actor a ON r.actor_id = a.id WHERE title = $title;',vars = {"title": title})
        directors = db.query('SELECT DISTINCT(d.name) FROM director d JOIN movies ON movies.director_id = d.id WHERE title = $title;',vars = {"title": title})
        ratings = db.query('SELECT r.score,r.text,r.user_id FROM rating r JOIN movies m ON  m.movie_id = r.movie_id WHERE m.title = $title',vars = {"title": title})
        movies = db.query('SELECT * FROM movies WHERE title = $title',vars = {"title":title})

        if not movies:
            movies = db.query('SELECT * FROM movies WHERE title LIKE \"%{}%\"'.format(title))
            amb = True

        if actors or directors or ratings or movies:
            return render.moviedetail(movies,actors,directors,ratings,amb)
        else:
            return "no movies"



class MovieTag:
    
    def GET(self,tag):
        if not session.logged_in:
            return web.seeother("/register")

        if session.logged_in != 2:
            return web.seeother("/")

        genre = {"Adventure","Comedy","Action","Drama","Crime","Thriller", "Animation", "Biography","Sci-Fi","Musical","Family","Fantasy","Mystery","War","Romance","Western"}
        rating = {"R","PG-13","PG","G","NC-17","TV-PG","TV-MA","B","B15","TV-14"}
        
        years = {"After2018","2015-2018","2010-2015","2005-2010","2000-2005","1995-2000","1990-1995","Before1990"}

        if tag in genre:
            got_movies = db.select('movies',order='movie_id', where="genre = $tag",vars = {"tag":tag})
        elif tag in rating:
            got_movies = db.query('SELECT * FROM movies WHERE rating = $tag ORDER BY movie_id',vars = {"tag":tag})
        elif tag in years:
            tmp = tag.split("-")
            if len(tmp) == 1 and tmp[0].startswith("After"):
                got_movies = db.query('SELECT * FROM movies WHERE year >= $year ORDER BY movie_id',vars = {"year":tmp[0].lstrip("After")})
            elif len(tmp) == 1 and tmp[0].startswith("Before"):
                got_movies = db.query('SELECT * FROM movies WHERE year < $year ORDER BY movie_id',vars = {"year":tmp[0].lstrip("Before")})
            elif len(tmp) == 2:
                got_movies = db.query('SELECT * FROM movies WHERE year Between $year_left and  $year_right ORDER BY movie_id',vars = {"year_left":tmp[0],"year_right": tmp[1]})
        elif tag == "All" :
            got_movies = db.query('SELECT * FROM movies ORDER BY movie_id')

        if got_movies:
            return render.movietag(got_movies)
        else:
            return "Can not find any movie."

    def POST(self,x):

        raw_data = web.input()
        title = raw_data.get("key")
        amb = False

        actors = db.query('SELECT DISTINCT(a.name) FROM movies m JOIN rel_movie_actor r ON m.movie_id = r.movie_id JOIN actor a ON r.actor_id = a.id WHERE title = $title;',vars = {"title": title})
        directors = db.query('SELECT DISTINCT(d.name) FROM director d JOIN movies ON movies.director_id = d.id WHERE title = $title;',vars = {"title": title})
        ratings = db.query('SELECT r.score,r.text,r.user_id FROM rating r JOIN movies m ON  m.movie_id = r.movie_id WHERE m.title = $title',vars = {"title": title})
        movies = db.query('SELECT * FROM movies WHERE title = $title',vars = {"title":title})
       
        if not movies:
            movies = db.query('SELECT * FROM movies WHERE title LIKE \"%{}%\"'.format(title))
            amb = True


        if actors or directors or ratings or movies:
            return render.moviedetail(movies,actors,directors,ratings,amb)
        else:
            return "no movies"


class Actor:
    def GET(self,name):
        if not session.logged_in:
            return web.seeother("/register")

        if session.logged_in != 2:
            return web.seeother("/")

        res = db.query('SELECT * from actor WHERE name = $name',vars = {"name":name})[0]
        if res:
            return render.actor(res)
        else:
            return "error"


class Director:
    def GET(self,name):
        res = db.query('SELECT * from director WHERE name = $name',vars = {"name":name})[0]
        if res:
            return render.director(res)
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
            return render.user()

    def POST(self):
        i = web.input()
        key = i.get("key")
        res = db.query('SELECT * from actor WHERE name = $key',vars = {"key":key})
        if res:
            return render.actor(res)
        else:
            return "Can not find"


class MovieDetail:
    def GET(self,id):

        if not session.logged_in:
            return web.seeother("/register")

        if session.logged_in != 2:
            return web.seeother("/")

        flag = False
        actors = db.query('SELECT DISTINCT(a.name) FROM movies m JOIN rel_movie_actor r ON m.movie_id = r.movie_id JOIN actor a ON r.actor_id = a.id WHERE m.movie_id = {}'.format(id))
        directors = db.query('SELECT DISTINCT(d.name) FROM director d JOIN movies m ON m.director_id = d.id WHERE m.movie_id = {}'.format(id))
        ratings = db.query('SELECT r.score,r.text,r.user_id FROM rating r JOIN movies m ON  m.movie_id = r.movie_id WHERE m.movie_id = {}'.format(id))
        movies = db.query('SELECT * FROM movies WHERE movie_id = {}'.format(id)) 

        if actors or directors or ratings or movie:
            return render.moviedetail(movies,actors,directors,ratings,False)
        else:
            return "error"

    def POST(self,x):
    
        raw_data = web.input()
        user_id = session.id
        movie_id = db.query('SELECT movie_id FROM movies WHERE title = $title',vars = {"title":session.title})[0].movie_id

        score = raw_data.score
        comment = raw_data.comment
        res = db.insert("rating", user_id = user_id, movie_id = movie_id, score = score, text = comment, time = web.SQLLiteral("NOW()"))

        return render.result(True)
        


class Transaction:
    def GET(self):
        if not session.logged_in:
            return web.seeother("/register")

        if session.logged_in != 2:
            return web.seeother("/")

        res = db.query("SELECT t.id,m.title,t.tran_time,t.quantity,t.total_price FROM transaction_user_onshow t  JOIN on_show o ON t.on_show_id = o.id JOIN movies m ON m.movie_id = o.movie_id where t.user_id = {}".format(session.id))   
        return render.trans(res)



class Order:
    def GET(self,on_show_id, num):
        if not session.logged_in:
            return web.seeother("/register")

        if session.logged_in != 2:
            return web.seeother("/")

        num = int(num)
        res = db.query('SELECT m.title,o.time_schedule,o.seat_limit, o.id,o.price,t.name,t.district FROM movies m JOIN on_show o ON m.movie_id = o.movie_id JOIN theater t ON t.id = o.thea_id WHERE o.id = $on_show_id ORDER BY m.movie_id, o.time_schedule', vars = {"on_show_id": on_show_id})[0]
        
        if res.seat_limit >= num:
            db.query("UPDATE on_show o SET o.seat_limit = o.seat_limit - $num WHERE o.id = $on_show_id",vars = {"num":num,"on_show_id":on_show_id})
            db.query("INSERT INTO transaction_user_onshow (user_id, on_show_id, quantity, total_price) VALUES ({},{},{},{})".format(session.id, on_show_id, num, num*res.price))
            return render.result(True)
        else:
            return render.result(False)


    def POST(self):
        pass


class Profile:
    def GET(self):
        if not session.logged_in:
            return web.seeother("/register")

        if session.logged_in != 2:
            return web.seeother("/")

        user = db.query("SELECT * FROM user u where u.id = {}".format(session.id))[0]
        return render.profile(user)

    def POST(self):
        raw_data = web.input()
        account = session.user
        password = raw_data.get('password', None)
        name = raw_data.get('name', None)
        gender = raw_data.get('gender', None)
        birth = raw_data.get('birth', None)
        district = raw_data.get('district', None)

        
        user_infor = db.query("SELECT * FROM user u where u.id = {}".format(session.id))[0]

        if not password:
            password = user_infor.password

        if not name:
            name = user_infor.name

        if not gender:
            gender = user_infor.gender

        if not birth:
            birth = user_infor.birth

        if not district:
            district = user_infor.district



        res = db.query("UPDATE user SET password = \"{}\", birth = \"{}\", district = {}, name = \"{}\", gender = \"{}\"".format(password,birth,district,name,gender))
        
        if res:
            return render.result(True)
        else:
            return render.result(False)



class Statistic:
    def GET(self):
        if not session.logged_in:
            return web.seeother("/register")

        if session.logged_in != 2:
            return web.seeother("/")

        current_gross = db.query("SELECT m.title, sum(t.total_price) AS total FROM movies m JOIN on_show o ON m.movie_id = o.movie_id JOIN transaction_user_onshow t ON t.on_show_id = o.id GROUP BY m.movie_id ORDER BY total DESC LIMIT 10")
        top_rated = db.query("SELECT m.title, AVG(r.score) AS a FROM movies m JOIN Rating r ON r.movie_id = m.movie_id GROUP BY m.movie_id ORDER BY  a DESC LIMIT 10")


        def read(tx):
            res = tx.run("MATCH P1 = ((user {id:'93'})-[r:rate]->(m:Movie)),P2 = ((m:Movie)-[:same_community]->(m2:Movie)) RETURN P2 LIMIT 3")
            
            ans = []
            for record in res:
                ans.append(record["P2"].start.id)
            return ans

        with driver.session() as neo:
            recommends_id = neo.write_transaction(read)


        recommends_movies = db.query("SELECT * FROM movies WHERE movie_id in ({},{},{})".format(*recommends_id))

        return render.statistic(current_gross,top_rated,recommends_movies)
                

   









if __name__ == "__main__": 
    app.run()