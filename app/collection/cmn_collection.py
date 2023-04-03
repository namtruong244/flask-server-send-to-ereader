from abc import ABC, abstractmethod
from flask import g


class CmnCollection(ABC):
    def __init__(self):
        self.collection = g.mongo_client[g.params['APPLICATION']['DATABASE_NAME']][self.get_collection()]

    @abstractmethod
    def get_collection(self):
        pass
