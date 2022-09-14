CREATE SCHEMA IF NOT EXISTS content;
SET search_path TO content,public;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- "content".film_work definition

-- Drop table

-- DROP TABLE "content".film_work;

CREATE TABLE IF NOT EXISTS "content".film_work (
	id uuid NOT NULL,
	title text NOT NULL,
	description text NULL,
	creation_date date NULL,
	rating float8 NULL,
	"type" text NOT NULL,
	created timestamptz NULL,
	modified timestamptz NULL,
	certificate varchar(512) NULL,
	file_path varchar(100) NULL,
	CONSTRAINT film_work_pkey PRIMARY KEY (id)
);
CREATE INDEX film_work_creation_date_idx ON content.film_work USING btree (creation_date);
CREATE INDEX film_work_title_idx ON content.film_work USING btree (title);

-- "content".person definition

-- Drop table

-- DROP TABLE "content".person;

CREATE TABLE IF NOT EXISTS "content".person (
	modified timestamptz NOT NULL,
	created timestamptz NOT NULL,
	id uuid NOT NULL,
	full_name text NOT NULL,
	"gender" text NULL,
	CONSTRAINT person_pkey PRIMARY KEY (id)
);
CREATE INDEX person_full_name_idx ON content.person USING btree (full_name);

-- "content".person_film_work definition

-- Drop table

-- DROP TABLE "content".person_film_work;

CREATE TABLE IF NOT EXISTS "content".person_film_work (
	created timestamptz NOT NULL,
	id uuid NOT NULL,
	"role" varchar(50) NOT NULL,
	film_work_id uuid NOT NULL,
	person_id uuid NOT NULL,
	CONSTRAINT film_work_person_role_uniq UNIQUE (film_work_id, person_id, role),
	CONSTRAINT person_film_work_pkey PRIMARY KEY (id)
);
CREATE INDEX film_work_person_role_idx ON content.person_film_work USING btree (film_work_id, person_id, role);
CREATE INDEX person_film_work_film_work_id_1724c536 ON content.person_film_work USING btree (film_work_id);
CREATE INDEX person_film_work_person_id_196d24de ON content.person_film_work USING btree (person_id);


-- "content".person_film_work foreign keys

ALTER TABLE "content".person_film_work ADD CONSTRAINT person_film_work_person_id_196d24de_fk_person_id
FOREIGN KEY (person_id)
REFERENCES "content".person(id)
ON DELETE CASCADE
DEFERRABLE INITIALLY DEFERRED;

-- "content".genre definition

-- Drop table

-- DROP TABLE "content".genre;

CREATE TABLE IF NOT EXISTS "content".genre (
	modified timestamptz NOT NULL,
	created timestamptz NOT NULL,
	id uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	description text NULL,
	CONSTRAINT genre_pkey PRIMARY KEY (id)
);

-- "content".genre_film_work definition

-- Drop table

-- DROP TABLE "content".genre_film_work;

CREATE TABLE  IF NOT EXISTS "content".genre_film_work (
	created timestamptz NOT NULL,
	id uuid NOT NULL,
	film_work_id uuid NOT NULL,
	genre_id uuid NOT NULL,
	CONSTRAINT film_work_genre_uniq UNIQUE (film_work_id, genre_id),
	CONSTRAINT genre_film_work_film_work_id_genre_id_uniq UNIQUE (film_work_id, genre_id),
	CONSTRAINT genre_film_work_pkey PRIMARY KEY (id)
);
CREATE INDEX film_work_genre_idx ON content.genre_film_work USING btree (film_work_id, genre_id);
CREATE INDEX genre_film_work_film_work_id_65abe300 ON content.genre_film_work USING btree (film_work_id);
CREATE INDEX genre_film_work_genre_id_88fbcf0d ON content.genre_film_work USING btree (genre_id);


-- "content".genre_film_work foreign keys

ALTER TABLE "content".genre_film_work
ADD CONSTRAINT genre_film_work_genre_id_88fbcf0d_fk_genre_id
FOREIGN KEY (genre_id)
REFERENCES "content".genre(id)
ON DELETE CASCADE
DEFERRABLE INITIALLY DEFERRED;