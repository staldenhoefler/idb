import psycopg2 as db

conn = db.connect(dbname="temperatur_sensor", user="postgres", password="vQVXEEnnhC", host="192.168.0.206", port="5433" )

cursor = conn.cursor()

#cursor.execute("CREATE TABLE TEST_PI (id serial PRIMARY KEY, test_pi_name varchar);")

cursor.execute("INSERT INTO TEST_PI (test_pi_name) VALUES (%s)", ("Test_pi",))

conn.commit()

cursor.close()
conn.close()