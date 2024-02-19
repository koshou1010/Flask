import pymongo

class MongodbAction:
    Host: str = None
    Testing: bool = False
    MONGO_DATABASE_NAME:str = None
    MONGO_DATABASE_COLLECTION:str = None
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def setup_host(self, host: str, testing: bool, db_name:str, colletion:str):
        self.Host = host
        self.Testing = testing
        self.MONGO_DATABASE_NAME=db_name
        self.MONGO_DATABASE_COLLECTION = colletion
        self.connect()
        
    def connect(self):
        self.mongo_client = pymongo.MongoClient(self.Host)
        
    def create_data(self, data : dict):
        algorithm_db = self.mongo_client[self.MONGO_DATABASE_NAME]
        seven_days_history_collection = algorithm_db[self.MONGO_DATABASE_COLLECTION]
        return seven_days_history_collection.insert_one(data)
         
    def query_data_id(self, user_id : str):
        history_list = []
        algorithm_db = self.mongo_client[self.MONGO_DATABASE_NAME]
        seven_days_history_collection = algorithm_db[self.MONGO_DATABASE_COLLECTION]
        myquery = {"id" : str(user_id)}
        mydoc = seven_days_history_collection.find(myquery).sort("history.date", -1) # reverse, more recently more front
        for x in mydoc:
            history_list.append(x['history'])
        return history_list 
