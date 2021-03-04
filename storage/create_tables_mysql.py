import mysql.connector

db_conn = mysql.connector.connect(host="acit3855-kafka.westus2.cloudapp.azure.com", user="root", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE calorie_intake
          (id INT NOT NULL AUTO_INCREMENT, 
           client_id VARCHAR(250) NOT NULL,
           device_id VARCHAR(250) NOT NULL,
           calorie_intake INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT calorie_intake_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE weight
          (id INT NOT NULL AUTO_INCREMENT, 
           client_id VARCHAR(250) NOT NULL,
           device_id VARCHAR(250) NOT NULL,
           weight INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT weight_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
