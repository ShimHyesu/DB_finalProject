# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

pip install xlrd
pip install openpyxl
pip install pandas

import pymysql
conn = pymysql.connect(host='localhost', user='db_test', password='hyesu0429@', db='dbProject')

curs = conn.cursor(pymysql.cursors.DictCursor)

# +
import pandas as pd
import numpy as np

fileName='./movieInfo.xlsx'
df = pd.read_excel(fileName,skiprows = 4)
df = df.replace({np.nan : None})

display(df)
# -

# ## 테이블 생성

# +
sql_create_table_movie = "CREATE TABLE IF NOT EXISTS Movie ( id INT primary key NOT NULL AUTO_INCREMENT, name VARCHAR(45) NOT NULL, name_eng TEXT, production_year INT, type VARCHAR(10), production_status VARCHAR(10), production_company VARCHAR(100) )"
sql_create_table_director = "CREATE TABLE IF NOT EXISTS Director ( id INT primary key NOT NULL AUTO_INCREMENT, name VARCHAR(45) NOT NULL ); "
sql_create_table_movieDirector = "CREATE TABLE IF NOT EXISTS Movie_Director ( movie_id INT NOT NULL, director_id INT NOT NULL, PRIMARY KEY (movie_id, director_id), foreign key (movie_id) references Movie(id)  on update cascade on delete cascade, foreign key (director_id) references Director(id) on update cascade on delete cascade );"
sql_create_table_country = "CREATE TABLE IF NOT EXISTS Country ( id INT primary key NOT NULL AUTO_INCREMENT, name VARCHAR(20) NOT NULL );"
sql_create_table_movieCountry = "CREATE TABLE IF NOT EXISTS Movie_Country ( movie_id INT NOT NULL, country_id INT NOT NULL, PRIMARY KEY (movie_id, country_id), foreign key (movie_id) references Movie(id)  on update cascade on delete cascade, foreign key (country_id) references Country(id) on update cascade on delete cascade );"
sql_create_table_genre = "CREATE TABLE IF NOT EXISTS Genre ( movie_id INT NOT NULL ,genre VARCHAR(20) NOT NULL, PRIMARY KEY (movie_id, genre), foreign key (movie_id) references Movie(id) on update cascade on delete cascade );"

curs.execute(sql_create_table_movie)
curs.execute(sql_create_table_director)
curs.execute(sql_create_table_movieDirector)
curs.execute(sql_create_table_country)
curs.execute(sql_create_table_movieCountry)
curs.execute(sql_create_table_genre)
# -

# ## 엑셀 데이터 DB에 삽입

# +
sql_insert_movie = "INSERT IGNORE INTO Movie (name, name_eng, production_year, type, production_status, production_company) values(%s, %s, %s, %s, %s, %s)"

movieSet = set()

# insert into Movie 
for idx,row in df.iterrows():
    name = row['영화명']
    name_eng = row['영화명(영문)']
    production_year = row['제작연도']
    type = row['유형']
    production_status = row['제작상태']
    production_company = row['제작사']

    movie = (name, name_eng, production_year, type, production_status, production_company)
    movieSet.add(movie)
    
curs.executemany(sql_insert_movie, movieSet)
conn.commit()

print("insert success")

# +
sql_insert_director = "INSERT IGNORE INTO Director (name) values(%s)"
sql_insert_country = "INSERT IGNORE INTO Country (name) values(%s)"
sql_insert_genre= "INSERT IGNORE INTO Genre (movie_id, genre) values(%s, %s)"

sql_select_id_movie= "SELECT id FROM Movie WHERE name = %s"

tuples_genre = []

movie_director_list = []
movie_country_list = []

directorSet=set()
countrySet=set()

# select id from Movie
# insert into Country, Director, Genre
for idx,row in df.iterrows():
    name = row['영화명']
    production_year = row['제작연도']
    countries = row['제작국가']
    genres = row['장르']
    directors = row['감독']
    
    curs.execute(sql_select_id_movie,name)
    movie_id = curs.fetchone()

    if directors:
        directors = directors.split(',')
        movie_director_list.append((movie_id['id'], directors))
        for director in directors:
            directorSet.add(director)
                
    if countries:
        countries = countries.split(',')
        movie_country_list.append((movie_id['id'], countries))
        for country in countries:
            countrySet.add(country)
           
    if genres:
        genres = genres.split(',')
        for genre in genres:
            tuples_genre.append((movie_id['id'], genre))


                       
curs.executemany(sql_insert_director, directorSet)
curs.executemany(sql_insert_country, countrySet)
curs.executemany(sql_insert_genre, tuples_genre)
conn.commit()

print("insert success")

# +
sql_insert_movie_director= "INSERT IGNORE INTO Movie_Director (movie_id, director_id) values(%s, %s)"
sql_insert_movie_country= "INSERT IGNORE INTO Movie_Country (movie_id, country_id) values(%s, %s)"

sql_select_id_director = "SELECT id FROM Director WHERE name = %s"
sql_select_id_country = "SELECT id FROM Country WHERE name = %s"

tuples_movie_director = []
tuples_movie_country = []

# select id from Director, Country
# insert into Movie_Director, Movie_Country
for val in movie_director_list:
    movie_id = val[0]
    for director in val[1]:
        curs.execute(sql_select_id_director, director)
        director_id = curs.fetchone()
        tuples_movie_director.append((movie_id,director_id['id']))
        
for val in movie_country_list:
    movie_id = val[0]
    for country in val[1]:
        curs.execute(sql_select_id_country, country)
        country_id = curs.fetchone()
        tuples_movie_country.append((movie_id,country_id['id']))

curs.executemany(sql_insert_movie_director, tuples_movie_director)
curs.executemany(sql_insert_movie_country, tuples_movie_country)
conn.commit()

print("insert success")
# -
# ## 검색


# +
# 2020년에 제작된 다큐멘터리 한국 영화의 영화명과 감독을 영화명 순으로 검색
sql_select_assign1 = """ SELECT m.name, d.name
FROM Movie m, Director d, Movie_Director md, Genre g, Country c, Movie_Country mc
WHERE m.id = md.movie_id and d.id = md.director_id and m.id = mc.movie_id and c.id = mc.country_id and m.id = g.movie_id and g.genre='다큐멘터리' and m.production_year = 2020 and c.name = '한국'
ORDER BY m.name
""" 

print("2020년에 제작된 다큐멘터리 한국 영화의 영화명과 감독을 영화명 순으로 검색 \n")

curs.execute(sql_select_assign1)

row = curs.fetchone()
while row:
    print("영화명: %s, 감독: %s" %(row['name'], row['d.name']))
    row = curs.fetchone()

# +
# '봉준호’ 감독의 영화를 제작년도 순으로 검색
sql_select_assign2 = """ SELECT m.production_year, m.name
FROM Movie m, Director d, Movie_Director md
WHERE m.id = md.movie_id and d.id = md.director_id and d.name = "봉준호"
ORDER BY m.production_year
""" 

print("'봉준호’ 감독의 영화를 제작년도 순으로 검색 \n")

curs.execute(sql_select_assign2)

row = curs.fetchone()
while row:
    print("제작년도: %s, 영화이름: %s" %(row['production_year'], row['name']))
    row = curs.fetchone()

# +
# 각 년도별 제작된 영화의 편수를 검색하되, 년도별로 출력
sql_select_assign3 = """ SELECT m.production_year, COUNT(*) as count
FROM Movie m
GROUP BY m.production_year
ORDER BY m.production_year
""" 

print("각 년도별 제작된 영화의 편수를 검색하되, 년도별로 출력 \n")

curs.execute(sql_select_assign3)

row = curs.fetchone()
while row:
    print("제작년도: %s, 영화 갯수: %s" %(row['production_year'], row['count']))
    row = curs.fetchone()

# +
# 각 나라별 가장 많이 제작된 영화 장르를 검색
sql_select_assign4 = """ SELECT c.name, g.genre, COUNT(g.genre) as count
    FROM Movie m, Country c, Movie_Country mc, Genre g
    WHERE m.id = mc.movie_id and c.id = mc.country_id and m.id = g.movie_id
    GROUP BY c.name, g.genre
    HAVING COUNT(*) = (
        SELECT MAX(genre_count)
        FROM (
            SELECT c1.name, COUNT(*) as genre_count
            FROM Movie m1, Country c1, Movie_Country mc1, Genre g1
            WHERE m1.id = mc1.movie_id and c1.id = mc1.country_id and m1.id = g1.movie_id
            GROUP BY c1.name, g1.genre
        ) as result
        WHERE result.name = c.name
    )
"""


print("각 나라별 가장 많은 제작된 영화 장르를 검색 \n")

curs.execute(sql_select_assign4)

row = curs.fetchone()
while row:
    print("나라: %s, 영화장르: %s, 갯수: %s " %(row['name'], row['genre'],row['count']))
    row = curs.fetchone()


# +
# 한국, 일본, 중국 세나라에 대하여 각 나라별 영화를 가장 많이 감독한 감독의 이름을 검색
sql_select_assign5 = """ SELECT c.name, d.name, COUNT(d.name) as count
    FROM Movie m, Country c, Movie_Country mc, Director d, Movie_Director md
    WHERE m.id = mc.movie_id and c.id = mc.country_id and m.id = md.movie_id and d.id = md.director_id and c.name IN('한국','일본','중국')
    GROUP BY c.name, d.name
     HAVING COUNT(*) = (
        SELECT MAX(director_count)
        FROM (
            SELECT c1.name, COUNT(*) as director_count
            FROM Movie m1, Country c1, Movie_Country mc1, Director d1, Movie_Director md1
            WHERE m1.id = mc1.movie_id and c1.id = mc1.country_id and m1.id = md1.movie_id and d1.id = md1.director_id and c1.name IN('한국','일본','중국')
            GROUP BY c1.name, d1.name
        ) as result
        WHERE result.name = c.name
    )
"""


print("한국, 일본, 중국 세나라에 대하여 각 나라별 영화를 가장 많이 감독한 감독의 이름을 검색 \n")

curs.execute(sql_select_assign5)

row = curs.fetchone()

while row:
    print("나라: %s, 감독: %s, 갯수: %s" %(row['name'], row['d.name'], row['count'] ))
    row = curs.fetchone()
# -

# ## 검색조건 입력받기

# +
movieNameInput = input("영화 제목을 입력하세요")
productionYearInput = input("제작연도를 입력하세요")
countryInput = input("제작국가를 입력하세요")
genreInput = input("장르를 입력하세요")
directorInput = input("감독을 입력하세요")

sql_input = """ SELECT m.name, m.production_year, c.name, g.genre, d.name 
    FROM Movie m, Director d, Country c, Genre g, Movie_Director md, Movie_Country mc 
    WHERE m.id = md.movie_id and d.id = md.director_id and m.id = mc.movie_id and c.id = mc.country_id and m.id = g.movie_id
"""
if(movieNameInput):
    sql_input += f"and m.name like '%{movieNameInput}%'"
if(productionYearInput):
    sql_input += f"and m.production_year = {productionYearInput}"
if(countryInput):
    sql_input += f"and c.name = {countryInput}"
if(genreInput):
    sql_input += f"and g.genre = {genreInput}"
if(directorInput):
    sql_input += f"and d.name = {directorInput}"
    

curs.execute(sql_input)
result = curs.fetchone()
while result:
    print(result)
    result = curs.fetchone()
# -


