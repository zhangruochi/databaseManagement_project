from neo4j import GraphDatabase
import pickle

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lv23623600"))



def add_user(tx):
    tx.run("LOAD CSV WITH HEADERS  FROM \"file:///user.csv\" AS line MERGE(user:User{id:line.id, name:line.name, gender:line.gender,birth:line.birth,account:line.account,district:line.district})")

def add_movie(tx):
    tx.run("LOAD CSV WITH HEADERS  FROM \"file:///movies.csv\" AS line MERGE(movie:Movie{id:line.movie_id,title:line.title,company:line.company,genre:line.genre,rating:line.rating,director:line.director_id})")


def add_rating_rela(tx):
    tx.run("LOAD CSV WITH HEADERS  FROM \"file:///rating.csv\" AS line match (from:User{id:line.user_id}),(to:Movie{id:line.movie_id}) merge (from)-[r:rate{score:line.score, text:line.text, time:line.time}]->(to)")


def add_same_dire(tx):
    tx.run("MATCH (m1:Movie),(m2:Movie) where m1.director = m2.director and m1.id <> m2.id CREATE (m1)-[r:same_director]->(m2) RETURN r")

def add_same_genre(tx):
    tx.run("MATCH (m1:Movie),(m2:Movie) where m1.genre = m2.genre and m1.id <> m2.id CREATE (m1)-[r:same_genre]->(m2) RETURN r")

def add_related_movie(tx):
    tx.run("LOAD CSV WITH HEADERS  FROM \"file:///movie_rela.csv\" AS line match (from:Movie{id:line.id1}),(to:Movie{id:line.id2}) merge (from)-[r:related_movie]->(to)")

def read(tx):
    res = tx.run("MATCH P1 = ((user {id:'93'})-[r:rate]->(m:Movie)),P2 = ((m:Movie)-[:same_community]->(m2:Movie)) RETURN P2 LIMIT 3")
    
    ans = []
    for record in res:
        ans.append(record["P2"].start.id)
    return ans

def create_community_attr(tx):
    tx.run("CALL algo.louvain('Movie', 'related_movie', {write:true, writeProperty:'community'}) YIELD nodes, communityCount, iterations, loadMillis, computeMillis, writeMillis;")



def create_community(tx):
    tx.run("MATCH (m1:Movie),(m2:Movie) where m1.community = m2.community and m1.id <> m2.id CREATE (m1)-[r:same_community]->(m2)  RETURN r LIMIT 20")

with driver.session() as session:
    #session.write_transaction(add_friend, "Arthur", "Guinevere")

    session.write_transaction(add_user)
    session.write_transaction(add_movie)
    session.write_transaction(add_rating_rela)
    session.write_transaction(add_related_movie)
    session.write_transaction(create_community_attr)
    session.write_transaction(create_community)





    