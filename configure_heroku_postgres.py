import os
import psycopg2

#Sourcing for this file -
# Psycopg documentation: http://initd.org/psycopg/docs/usage.html
# Autoincrementing key for Postgresql: https://chartio.com/resources/tutorials/how-to-define-an-auto-increment-primary-key-in-postgresql/
# Date datatypes documentation: https://www.postgresql.org/docs/9.1/datatype-datetime.html

#Database connection stuff
conn = psycopg2.connect("postgres://mhheszaljfxliv:7cf27297de378774bdff97aadf0daf58cc20aa0dc5336fb27d5a74dac9911244@ec2-107-20-155-148.compute-1.amazonaws.com:5432/d44pn0a1kcts7q", sslmode='require')
db = conn.cursor()

# Configure database according to this schema
db.execute('CREATE TABLE "history" ("id" integer NOT NULL, "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP, "submitted" integer NOT NULL, "additional" integer NOT NULL, "points" integer NOT NULL)')
db.execute('CREATE TABLE "submitted" ("id" integer NOT NULL, "link" text NOT NULL, "isbot" boolean NOT NULL, "isreported" boolean NOT NULL DEFAULT False)')
db.execute('CREATE TABLE "users" ("id" SERIAL PRIMARY KEY, "name" text NOT NULL, "username" text NOT NULL, "hash" text NOT NULL, "score" integer NOT NULL DEFAULT 0)')
conn.commit()
