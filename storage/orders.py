from sqlalchemy import Boolean, Column, Double, Integer, String, DateTime
from base import Base
import datetime


class Orders(Base):
    """ Orders """

    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)
    customer_name = Column(String(250), nullable=False)
    customer_phone = Column(String(9), nullable=False)
    is_delivery = Column(Boolean, nullable=False)
    order_address = Column(String(250), nullable=False)
    burger_name = Column(String(250), nullable=False)
    order_quantity = Column(Integer, nullable=False)
    order_total = Column(Double, nullable=False)
    order_tip = Column(Double, nullable=False)
    order_timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, customer_name, customer_phone, is_delivery, order_address, burger_name, order_quantity, order_total, order_tip, order_timestamp, trace_id):
        """ Initializes a order """
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.is_delivery = is_delivery
        self.order_address = order_address
        self.burger_name = burger_name
        self.order_quantity = order_quantity
        self.order_total = order_total
        self.order_tip = order_tip
        self.order_timestamp = order_timestamp
        # Sets the date/time record is created
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a order """
        dict = {}
        dict['order_id'] = self.order_id
        dict['customer_name'] = self.customer_name
        dict['customer_phone'] = self.customer_phone
        dict['is_delivery'] = self.is_delivery
        dict['order_address'] = self.order_address
        dict['burger_name'] = self.burger_name
        dict['order_quantity'] = self.order_quantity
        dict['order_total'] = self.order_total
        dict['order_tip'] = self.order_tip
        dict['order_timestamp'] = self.order_timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
