

START_TIME_MODIFIED_QUERY = """
WITH timefw AS (SELECT 'filmwork' as table, modified FROM film_work ORDER BY modified LIMIT 1),
    timeg AS (SELECT 'genre', modified FROM genre ORDER BY modified LIMIT 1),
    timep AS (SELECT 'person', modified FROM person ORDER BY modified LIMIT 1)

SELECT fw.* FROM timefw fw
UNION
SELECT g.* FROM timeg g
UNION
SELECT p.* FROM timep p;
"""

PERSONS_QUERY = """
WITH persons AS (
    SELECT p.* 
    FROM person p 
    WHERE p.modified >= %s 
    ORDER BY p.modified DESC
    --LIMIT 100
)
SELECT
    p.full_name,
    p.id as id,
    p.modified as modified,
    pfw.role as role,
    ARRAY_AGG(DISTINCT jsonb_build_object('fwid', pfw.filmwork_id)) AS array_id,
    ARRAY_AGG(DISTINCT pfw.filmwork_id) AS film_ids

FROM persons p
LEFT JOIN person_film_work pfw 
        ON pfw.person_id = p.id

GROUP BY 
    p.full_name,
    p.id,
    p.modified,
	pfw.role
 
ORDER BY p.modified DESC;
"""

MOVIES_QUERY = """
WITH movies as (
    SELECT 
    fw.id, 
    fw.title, 
    fw.description, 
    fw.rating as imdb_rating, 
    fw.type,
    fw.rating as imdb_rating,
    fw.modified,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor') as actors_names,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer') as writers_names,
    ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director') as director,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name, 'modified', p.modified)) FILTER (WHERE pfw.role = 'actor') as actors,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name, 'modified', p.modified)) FILTER (WHERE pfw.role = 'writer') as writers,
    ARRAY_AGG(DISTINCT g.name) AS genres
    
    FROM film_work as fw
    LEFT JOIN person_film_work pfw 
        ON pfw.filmwork_id = fw.id
    LEFT JOIN person p 
        ON p.id = pfw.person_id
    LEFT JOIN genre_film_work gfw 
        ON gfw.filmwork_id = fw.id
    LEFT JOIN genre g 
        ON g.id = gfw.genre_id
    
    GROUP BY
        fw.id
)

SELECT mv.* FROM (
SELECT m.* FROM movies m
    WHERE m.modified > %(lasttime)s
    ORDER BY m.modified DESC
    LIMIT 100) mv
UNION ALL
SELECT mid.* FROM (
SELECT mm.* 
    FROM movies mm 
    WHERE mm.id IN %(movies_id)s
    ORDER BY mm.modified) mid;
"""


GENRES_QUERY = """
WITH genres AS (
    SELECT g.* 
    FROM genre g 
    WHERE g.modified >= %s 
    ORDER BY g.modified DESC
    --LIMIT 100
)

SELECT
    g.name,
    g.id as id,
    g.description as description,
    g.modified,
    ARRAY_AGG(DISTINCT jsonb_build_object('fwid', gfw.filmwork_id)) AS array_id

FROM genres g
LEFT JOIN genre_film_work gfw 
        ON gfw.genre_id = g.id

GROUP BY 
    g.name,
    g.id,
    g.description,
    g.modified

ORDER BY g.modified DESC
--LIMIT 100;
"""