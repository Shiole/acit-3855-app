import sqlite3

conn = sqlite3.connect('burger_orders.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE orders
          (order_id INTEGER PRIMARY KEY ASC, 
           customer_name VARCHAR(250) NOT NULL,
           customer_phone VARCHAR(9) NOT NULL,
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
          (delivery_id INTEGER PRIMARY KEY ASC, 
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
