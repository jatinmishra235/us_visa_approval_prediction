from us_visa.constant import *
import pymongo
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

filepath = os.path.join(os.getcwd(),'us_visa','notebooks','EasyVisa.csv')
df = pd.read_csv(filepath)
data = df.to_dict(orient='records')

client = pymongo.MongoClient(os.getenv('MONGODB_URL'))
collection = client[DATABASE_NAME][COLLECTION_NAME]
collection.insert_many(data)
print("success")