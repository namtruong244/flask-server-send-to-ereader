from app.collection.cmn_collection import CmnCollection


class UsersCollection(CmnCollection):
    def get_collection(self):
        return 'users'
