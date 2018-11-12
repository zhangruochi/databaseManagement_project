import csv

director = {}
index = 0
with open("movies.csv",encoding='utf-8', errors='ignore') as csvfile:
    reader = csv.reader(csvfile,delimiter=",")
    for line in reader:
        if line[3] not in director:
            if line[3] == "director":
                continue
            director[line[3]] = index 
            index += 1
print(director)


## movies
index = 0
with open("movies.sql","w") as f: 
    with open("movies.csv",encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile,delimiter=",")
        for line in reader:
            if index == 0:
                pass
            else:
                f.write("INSERT INTO movies (title,company,budget,genre,gross,rating,release_time,runtime,year,director_id) VALUES (\"{}\",\"{}\",{},\"{}\",{},\"{}\",\"{}\",{},\"{}\",{});\n".format(" ".join(line[6].split("\""))," ".join(line[1].split("\"")),line[0],line[4],line[5]," ".join(line[7].split("\"")),line[8],line[9],line[14],director[line[3]]))
            index += 1


index = 0
import random
genders = ["male","female"]
birth ="19{}-{}-{}"
with open("director.sql","w") as f:
    f.write("DELETE FROM movies;\n") 
    for name,id_ in director.items():
        f.write("INSERT INTO director (id,name,gender,birth) VALUES ({},\"{}\",\"{}\",\"{}\");\n".format(id_,name,random.choice(genders),birth.format(random.randint(20,99),random.randint(1,12),random.randint(1,29))))



