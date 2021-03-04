import mysql.connector

db_conn = mysql.connector.connect(host="acit3855-kafka.westus2.cloudapp.azure.com", user="root", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
                DROP TABLE calorie_intake, weight
                ''')

db_conn.commit()
db_conn.close()