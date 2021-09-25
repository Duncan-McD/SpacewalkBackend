import pymongo
import json
from .requester import app

def main(args):

  f = open('credentials.json')

  credentials = json.load(f)

  client = pymongo.MongoClient("mongodb+srv://" + credentials.username + ":" + credentials.password + "@bigredhacks2021.cojtr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
  db = client.test

  app.run(debug=True, host='0.0.0.0');