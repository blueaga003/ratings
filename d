                                         Table "public.movies"
   Column    |            Type             |                         Modifiers                         
-------------+-----------------------------+-----------------------------------------------------------
 movie_id    | integer                     | not null default nextval('movies_movie_id_seq'::regclass)
 title       | character varying(64)       | not null
 released_at | timestamp without time zone | not null
 imbd_url    | character varying(64)       | not null
Indexes:
    "movies_pkey" PRIMARY KEY, btree (movie_id)

