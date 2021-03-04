from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Weight(Base):
    """ Weight """

    __tablename__ = "weight"

    id = Column(Integer, primary_key=True)
    client_id = Column(String(250), nullable=False)
    device_id = Column(String(250), nullable=False)
    weight = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, client_id, device_id, weight, timestamp):
        """ Initializes a Weight report """
        self.client_id = client_id
        self.device_id = device_id
        self.weight = weight
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created


    def to_dict(self):
        """ Dictionary Representation of a Weight report """
        dict = {}
        dict['id'] = self.id
        dict['client_id'] = self.client_id
        dict['device_id'] = self.device_id
        dict['weight'] = self.weight
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
