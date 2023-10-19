import mysql.connector

conn = mysql.connector.connect(host="acit3855-kafka.canadacentral.cloudapp.azure.com",
                               user="kitty",
                               password="01273256",
                               database="events")

c = conn.cursor()

c.execute('''
          CREATE TABLE orders
          (order_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT, 
           customer_name VARCHAR(250) NOT NULL,
           customer_phone VARCHAR(10) NOT NULL,
           is_delivery BOOLEAN NOT NULL,
           order_address VARCHAR(250) NOT NULL,
           burger_name VARCHAR(100) NOT NULL,
           order_quantity INTEGER NOT NULL,
           order_total DOUBLE NOT NULL,
           order_tip DOUBLE NOT NULL,
           order_timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(250) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE deliveries
          (delivery_id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT, 
           order_id INTEGER NOT NULL,
           driver_id INTEGER NOT NULL,
           assignment_timestamp VARCHAR(100) NOT NULL,
           fulfilment_timestamp VARCHAR(100) NOT NULL,
           delivery_distance DOUBLE NOT NULL,
           delivery_tip DOUBLE NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(250) NOT NULL)
          ''')

conn.commit()
conn.close()
