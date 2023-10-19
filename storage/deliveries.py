from sqlalchemy import Column, Float, Integer, String, DateTime
from base import Base
import datetime


class Deliveries(Base):
    """ Deliveries """

    __tablename__ = "deliveries"

    delivery_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    driver_id = Column(Integer, nullable=False)
    assignment_timestamp = Column(String(100), nullable=False)
    fulfilment_timestamp = Column(String(100), nullable=False)
    delivery_distance = Column(Float, nullable=False)
    delivery_tip = Column(Float, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, order_id, driver_id, assignment_timestamp, fulfilment_timestamp, delivery_distance, delivery_tip, trace_id):
        """ Initializes a delivery """
        self.order_id = order_id
        self.driver_id = driver_id
        self.assignment_timestamp = assignment_timestamp
        self.fulfilment_timestamp = fulfilment_timestamp
        self.delivery_distance = delivery_distance
        self.delivery_tip = delivery_tip
        # Sets the date/time record is created
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a delivery """
        dict = {}
        dict['delivery_id'] = self.delivery_id
        dict['order_id'] = self.order_id
        dict['driver_id'] = self.driver_id
        dict['assignment_timestamp'] = self.assignment_timestamp
        dict['fulfilment_timestamp'] = self.fulfilment_timestamp
        dict['delivery_distance'] = self.delivery_distance
        dict['delivery_tip'] = self.delivery_tip
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
