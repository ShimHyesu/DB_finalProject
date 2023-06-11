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


