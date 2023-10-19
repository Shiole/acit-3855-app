import mysql.connector

conn = mysql.connector.connect(host="acit3855-kafka.canadacentral.cloudapp.azure.com",
                               user="kitty",
                               password="01273256",
                               database="events")

c = conn.cursor()

c.execute('''
          DROP TABLE orders, deliveries
          ''')

conn.commit()
conn.close()
