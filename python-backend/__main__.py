import sys
import pymongo
import json
from argparse import ArgumentParser
from .requester import app

def main(args):
  parser = ArgumentParser(description='''Private API for Spacewalk''', prog="spacewalk.py")
  parser.add_argument('-d','--debug', action='store_true', 
      help='turns on flask debug setting',
      default=False)
  args = parser.parse_args(args)


  f = open('./python-backend/credentials.json')

  credentials = json.load(f)

  client = pymongo.MongoClient("mongodb+srv://" + credentials["username"] + ":" + credentials["password"] + "@bigredhacks2021.cojtr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
  db = client.SpaceWalk

  app.config["db"] = db
  app.config["users"] = db.Users
  app.config["bodies"] = db.Bodies
  app.run(threaded=True,debug=args.debug, host='0.0.0.0')

if __name__ == "__main__":
  main(sys.argv[1:])
