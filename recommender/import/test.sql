INSERT INTO transaction_user_onshow (user_id, on_show_id, quantity, total_price) VALUES ({},{},{},{})


UPDATE rating SET score = rand()*5 WHERE movie_id IN (SELECT movie_id FROM (SELECT movie_id from rating) as c);





CALL algo.louvain.stream('Movie', 'related_movie', {})
YIELD nodeId, community
RETURN algo.getNodeById(nodeId).id AS movie, community
ORDER BY community;


CALL algo.louvain('Movie', 'related_movie', {write:true, writeProperty:'community'})
YIELD nodes, communityCount, iterations, loadMillis, computeMillis, writeMillis;


MATCH p=(m1:Movie)-[r:related_movie]->(m2:Movie) WHERE m1.community = m2.community return p limit 10





# all movie for a user
MATCH (user { id: '1' })--(movie)
RETURN movie.title


# 某个用户评价的所有电影
MATCH (user {id:"1"})-[:rate]->(movie)
RETURN movie.title


#
MATCH (movie1)<-[:same_director | :same_genre]-(movie2)
RETURN movie1.title,movie2.title



MATCH (user { id:'2' })-[:rate]->(movie1)<-[:same_director]-(movie2)
RETURN movie2.title,movie2.director;





MATCH (m1:Movie),(m2:Movie) where m1.community = m2.community and m1.id <> m2.id
CREATE (m1)-[r:same_community]->(m2) 
RETURN m1,m2,same_community LIMIT 20





MATCH p=(u:User)-[r:rate]->(m:Movie) where u.id = "1" and r.score > "1" RETURN p LIMIT 25



MATCH P1 = ((u:User)-[r:rate]->(m:Movie)),P2 = ((m:Movie)-[:same_community]->(m2:Movie)) RETURN P2 LIMIT 3



MATCH P1 = ((user {id:"19"})-[r:rate]->(m:Movie)),P2 = ((m:Movie)-[:same_community]->(m2:Movie)) RETURN P1,P2 LIMIT 3
