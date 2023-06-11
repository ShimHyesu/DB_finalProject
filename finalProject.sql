create database dbProject;
use dbProject;

grant all privileges on dbProject.*to 'db_test'@'%';

# 2020년에 제작된 다큐멘터리 한국 영화의 영화명과 감독을 영화명 순으로 검색
SELECT m.name, d.name
FROM Movie m, Director d, Movie_Director md, Genre g, Country c, Movie_Country mc
WHERE m.id = md.movie_id and d.id = md.director_id and m.id = mc.movie_id and c.id = mc.country_id and m.id = g.movie_id and g.genre='다큐멘터리' and m.production_year = 2020 and c.name = '한국'
ORDER BY m.name;

# '봉준호’ 감독의 영화를 제작년도 순으로 검색
SELECT m.production_year, m.name
FROM Movie m, Director d, Movie_Director md
WHERE m.id = md.movie_id and d.id = md.director_id and d.name = "봉준호"
ORDER BY m.production_year;

# 각 년도별 제작된 영화의 편수를 검색하되, 년도별로 출력
SELECT m.production_year, COUNT(*) as count
FROM Movie m
GROUP BY m.production_year
ORDER BY m.production_year;

# 각 나라별 가장 많이 제작된 영화 장르를 검색
SELECT c.name, g.genre, COUNT(g.genre) as count
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
    );
    
# 한국, 일본, 중국 세나라에 대하여 각 나라별 영화를 가장 많이 감독한 감독의 이름을 검색
SELECT c.name, d.name, COUNT(d.name) as count
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
    );



