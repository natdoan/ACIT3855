from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class CalorieIntake(Base):
    """ Calorie Intake """

    __tablename__ = "calorie_intake"

    id = Column(Integer, primary_key=True)
    client_id = Column(String(250), nullable=False)
    device_id = Column(String(250), nullable=False)
    calorie_intake = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, client_id, device_id, calorie_intake, timestamp):
        """ Initializes a calorie intake report """
        self.client_id = client_id
        self.device_id = device_id
        self.calorie_intake = calorie_intake
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created


    def to_dict(self):
        """ Dictionary Representation of a calorie intake report """
        dict = {}
        dict['id'] = self.id
        dict['client_id'] = self.client_id
        dict['device_id'] = self.device_id
        dict['calorie_intake'] = self.calorie_intake
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
